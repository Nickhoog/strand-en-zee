"""Client voor Open-Meteo (Marine + Forecast) en de lijst met zwemlocaties."""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

import aiohttp

from .const import OPEN_METEO_FORECAST, OPEN_METEO_MARINE

_SPOTS_FILE = Path(__file__).parent / "swimspots.json"


def load_spots() -> list[dict[str, Any]]:
    """Lees de meegeleverde zwemlocaties (blocking; aanroepen in executor)."""
    return json.loads(_SPOTS_FILE.read_text(encoding="utf8"))["spots"]


async def fetch_open_meteo(
    session: aiohttp.ClientSession, lat: float, lon: float
) -> dict[str, tuple[dt.datetime, float]]:
    """Huidige modelwaarden van Open-Meteo (zee + wind) op de gevraagde locatie."""
    timeout = aiohttp.ClientTimeout(total=30)
    base = {"latitude": str(lat), "longitude": str(lon), "timezone": "GMT"}
    async with session.get(
        OPEN_METEO_MARINE,
        params={**base, "current": "wave_height,wave_period,sea_surface_temperature"},
        timeout=timeout,
    ) as resp:
        resp.raise_for_status()
        marine = (await resp.json()).get("current") or {}
    async with session.get(
        OPEN_METEO_FORECAST,
        params={
            **base,
            "current": "wind_speed_10m,wind_direction_10m",
            "wind_speed_unit": "ms",
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
        ts = dt.datetime.fromisoformat(block["time"]).replace(tzinfo=dt.timezone.utc)
        out[key] = (ts, float(value))
    return out
