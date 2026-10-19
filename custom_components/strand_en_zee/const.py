"""Constanten voor Strand & Zee."""
from __future__ import annotations

DOMAIN = "strand_en_zee"

API_BASE = "https://ddapi20-waterwebservices.rijkswaterstaat.nl"
API_OBSERVATIONS = f"{API_BASE}/ONLINEWAARNEMINGENSERVICES/OphalenWaarnemingen"

CONF_NAME = "name"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_MAX_DISTANCE = "max_distance_km"
CONF_SOURCE = "source"

SOURCE_RWS = "rws"
SOURCE_OPEN_METEO = "open_meteo"
DEFAULT_SOURCE = SOURCE_RWS

OPEN_METEO_MARINE = "https://marine-api.open-meteo.com/v1/marine"
OPEN_METEO_FORECAST = "https://api.open-meteo.com/v1/forecast"

DEFAULT_MAX_DISTANCE = 50
SCAN_INTERVAL_MINUTES = 10
LOOKBACK_HOURS = 3
# Aantal alternatieve stations dat geprobeerd wordt als het dichtstbijzijnde geen data heeft
MAX_CANDIDATES = 4
# RWS gebruikt 999999999 als "geen waarde"
MISSING_VALUE = 1e8

ATTRIBUTIONS = {
    SOURCE_RWS: "Data: Rijkswaterstaat (WaterWebservices, CC0)",
    SOURCE_OPEN_METEO: "Weather data by Open-Meteo.com (CC BY 4.0)",
}
