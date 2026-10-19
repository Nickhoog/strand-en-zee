"""Maak swimspots.json: alle officiële zwemlocaties (strand/plas) met coördinaten.

Bron: PDOK "Zwemwater (provinciaal en rijkswateren)", CC0.
Vereist pyproj (alleen voor dit script, niet voor de integratie): pip install pyproj
"""
import json
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter

from pyproj import Transformer

URL = ("https://service.pdok.nl/provincies/zwemwater-provinciaal-rijkswateren/"
       "atom/v1_0/downloads/inspire-pv-am.nlam-lzr.gml")
NS = {
    "gml": "http://www.opengis.net/gml/3.2",
    "am": "http://inspire.ec.europa.eu/schemas/am/4.0",
    "gn": "http://inspire.ec.europa.eu/schemas/gn/4.0",
}
to_wgs = Transformer.from_crs(3035, 4326, always_xy=True)

root = ET.fromstring(urllib.request.urlopen(URL, timeout=120).read())
spots = []
for f in root.iterfind(".//am:ManagementRestrictionOrRegulationZone", NS):
    name = f.findtext(".//gn:text", namespaces=NS)
    pos = f.findtext(".//gml:posList", namespaces=NS)
    if not name or not pos:
        continue
    n = [float(x) for x in pos.split()]
    ys, xs = n[0::2], n[1::2]  # EPSG:3035 in GML: eerst noorden, dan oosten
    lon, lat = to_wgs.transform(sum(xs) / len(xs), sum(ys) / len(ys))
    spots.append({"name": re.sub(r"\s+", " ", name).strip(), "lat": round(lat, 5), "lon": round(lon, 5)})

# Dubbele namen onderscheiden met coördinaten
count = Counter(s["name"] for s in spots)
for s in spots:
    s["label"] = s["name"] if count[s["name"]] == 1 else f'{s["name"]} ({s["lat"]:.3f}, {s["lon"]:.3f})'
spots.sort(key=lambda s: s["label"].casefold())

dest = os.path.join(os.path.dirname(__file__), "..", "custom_components", "strand_en_zee", "swimspots.json")
json.dump({"source": "PDOK Zwemwater provinciaal en rijkswateren (CC0)", "spots": spots},
          open(dest, "w", encoding="utf8"), ensure_ascii=False, indent=0)
print(len(spots), "zwemlocaties geschreven")
