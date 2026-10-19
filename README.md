# Strand & Zee for Home Assistant

*English summary:* water temperature, wave height, wave period, wind speed and wind direction for any of the 739 official Dutch swimming locations (beaches and lakes), picked from a dropdown. Values are model data from [Open-Meteo](https://open-meteo.com/) (CC BY 4.0, free for non-commercial use only). Inland lakes usually only get wind. Netherlands only.

---

# Strand & Zee voor Home Assistant

Watertemperatuur, golfhoogte, golfperiode, windsnelheid en windrichting voor een Nederlands strand of zwemplas, als sensoren. Kies je locatie uit een dropdown met alle 739 officiële zwemlocaties.

## Hoe het werkt

- Je kiest een zwemlocatie (typen om te zoeken werkt). De lijst komt uit de open dataset "Zwemwater (provinciaal en rijkswateren)" van PDOK (CC0) en zit in de integratie, dus er is geen netwerkverzoek nodig om de lijst te tonen.
- De waarden komen van [Open-Meteo](https://open-meteo.com/) (Marine en Forecast API), berekend voor de coördinaten van die locatie. Het zijn modelwaarden, geen metingen.
- Update elke 15 minuten. Geen API-sleutel nodig.

## Installatie

1. HACS, Custom repositories, voeg deze repo toe als type Integration.
2. Installeer "Strand & Zee" en herstart Home Assistant.
3. Instellingen, Apparaten & diensten, Integratie toevoegen, "Strand & Zee", kies je zwemlocatie.

## Sensoren

Watertemperatuur (°C), golfhoogte (m), golfperiode (s), windsnelheid (m/s) en windrichting (°, met `compass` als attribuut).

**Let op bij plassen en binnenwater:** Open-Meteo heeft daar vaak geen zeedata. Wind is er altijd, maar watertemperatuur en golven blijven dan onbeschikbaar.

## Niet inbegrepen

Zwemwaterkwaliteit (blauwalg, E. coli): Zwemwater.nl heeft geen officiële API en eist bronvermelding. Eerst toestemming vragen bij BIJ12 (communicatie@bij12.nl) voordat dit wordt toegevoegd.

## Gebruiksvoorwaarden

De gratis Open-Meteo API is bedoeld voor niet-commercieel gebruik (zoals persoonlijke domotica) en valt onder CC BY 4.0. Gebruik deze integratie dus niet in een commercieel product. Elke sensor toont de bronvermelding.

## Lijst met zwemlocaties verversen

`python tools/generate_swimspots.py` (vereist `pip install pyproj`) haalt de dataset opnieuw op en schrijft `swimspots.json`.

## Bronnen en licenties

- Weather data by [Open-Meteo.com](https://open-meteo.com/), CC BY 4.0
- Zwemlocaties: [PDOK Zwemwater (provinciaal en rijkswateren)](https://service.pdok.nl/provincies/zwemwater-provinciaal-rijkswateren/atom/v1_0/index.xml), CC0
