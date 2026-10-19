"""Kleine client voor de Rijkswaterstaat WaterWebservices (geen API-sleutel nodig)."""
from __future__ import annotations

import datetime as dt
import json
import math
from pathlib import Path
from typing import Any

import aiohttp

from .const import (
    API_OBSERVATIONS,
    LOOKBACK_HOURS,
    MISSING_VALUE,
    OPEN_METEO_FORECAST,
    OPEN_METEO_MARINE,
)

_STATIONS_FILE = Path(__file__).parent / "stations.json"


def load_stations() -> list[dict[str, Any]]:
    """Lees de meegeleverde stationslijst (blocking; aanroepen in executor)."""
    return json.loads(_STATIONS_FILE.read_text(encoding="utf8"))["stations"]


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine-afstand in km."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(a))


def nearest_stations(
    stations: list[dict[str, Any]], lat: float, lon: float, grootheid: str, max_km: float
) -> list[tuple[float, dict[str, Any]]]:
    """Stations binnen max_km die deze grootheid meten, dichtstbijzijnde eerst."""
    found = [
        (distance_km(lat, lon, s["lat"], s["lon"]), s)
        for s in stations
        if grootheid in s["q"]
    ]
    return sorted((x for x in found if x[0] <= max_km), key=lambda x: x[0])


async def fetch_open_meteo(
    session: aiohttp.ClientSession, lat: float, lon: float
) -> dict[str, tuple[dt.datetime, float]]:
    """Huidige modelwaarden van Open-Meteo (zee + wind) op de gevraagde locatie."""
    tz = {"timezone": "GMT"}
    timeout = aiohttp.ClientTimeout(total=30)
    async with session.get(
        OPEN_METEO_MARINE,
        params={
            "latitude": str(lat),
            "longitude": str(lon),
            "current": "wave_height,wave_period,sea_surface_temperature",
            **tz,
        },
        timeout=timeout,
    ) as resp:
        resp.raise_for_status()
        marine = (await resp.json()).get("current") or {}
    async with session.get(
        OPEN_METEO_FORECAST,
        params={
            "latitude": str(lat),
            "longitude": str(lon),
            "current": "wind_speed_10m,wind_direction_10m",
            "wind_speed_unit": "ms",
            **tz,
        },
        timeout=timeout,
    ) as resp:
        resp.raise_for_status()
        wind = (await resp.json()).get("current") or {}

    mapping = {
        "water_temperature": (marine, "sea_surface_temperature"),
        "wave_height": (marine, "wave_height"),
        "wave_period": (marine, "wave_period"),
        "wind_speed": (wind, "wind_speed_10m"),
        "wind_direction": (wind, "wind_direction_10m"),
    }
    out: dict[str, tuple[dt.datetime, float]] = {}
    for key, (block, field) in mapping.items():
        value = block.get(field)
        if value is None or "time" not in block:
            continue
        ts = dt.datetime.fromisoformat(block["time"]).replace(
            tzinfo=dt.timezone.utc
        )
        out[key] = (ts, float(value))
    return out


async def fetch_latest(
    session: aiohttp.ClientSession, code: str, compartiment: str, grootheid: str
) -> tuple[dt.datetime, float] | None:
    """Nieuwste waarneming van de afgelopen uren, of None als er geen data is."""
    now = dt.datetime.now(dt.timezone.utc)
    fmt = "%Y-%m-%dT%H:%M:%S.000+00:00"
    body = {
        "Locatie": {"Code": code},
        "AquoPlusWaarnemingMetadata": {
            "AquoMetadata": {
                "Compartiment": {"Code": compartiment},
                "Grootheid": {"Code": grootheid},
            }
        },
        "Periode": {
            "Begindatumtijd": (now - dt.timedelta(hours=LOOKBACK_HOURS)).strftime(fmt),
            "Einddatumtijd": now.strftime(fmt),
        },
    }
    async with session.post(
        API_OBSERVATIONS, json=body, timeout=aiohttp.ClientTimeout(total=30)
    ) as resp:
        if resp.status == 204:
            return None
        resp.raise_for_status()
        raw = await resp.text()
    if not raw.strip():
        return None
    data = json.loads(raw)

    best: tuple[dt.datetime, float] | None = None
    for serie in data.get("WaarnemingenLijst") or []:
        for meting in serie.get("MetingenLijst") or []:
            value = (meting.get("Meetwaarde") or {}).get("Waarde_Numeriek")
            if value is None or abs(value) >= MISSING_VALUE:
                continue
            ts = dt.datetime.fromisoformat(meting["Tijdstip"])
            if best is None or ts > best[0]:
                best = (ts, float(value))
    return best
