# Strand & Zee voor Home Assistant

Watertemperatuur, golfhoogte, golfperiode, windsnelheid en windrichting voor jouw strand, als sensoren.

## Databronnen (kies bij installatie)

| Bron | Wat | Opmerking |
|---|---|---|
| **Rijkswaterstaat** (standaard) | Echte metingen van het dichtstbijzijnde live meetstation, per grootheid apart. Het station en de afstand staan in de attributen. | CC0, geen sleutel nodig. Geen uptime-garantie. |
| **Open-Meteo** | Modelwaarden precies op jouw coördinaten. | Gratis voor niet-commercieel gebruik, CC BY 4.0. Niet bruikbaar voor commerciële toepassingen. Landinwaarts is er geen zeedata. |

Elke sensor toont de bronvermelding in het attribuut `attribution`.

## Installatie

1. HACS, Custom repositories, voeg deze repo toe als type Integration.
2. Installeer "Strand & Zee" en herstart Home Assistant.
3. Instellingen, Apparaten & diensten, Integratie toevoegen, "Strand & Zee".
4. Vul een naam, de coördinaten van je strand, de bron en de maximale afstand tot een meetstation in.

## Sensoren

Watertemperatuur (°C), golfhoogte (m), golfperiode (s), windsnelheid (m/s) en windrichting (°, met `compass` als attribuut). Update elke 10 minuten.

## Stationslijst verversen

`stations.json` bevat de RWS-stations die live data leveren. Verversen kan met `tools/generate_stations.py` (eenmalig, ongeveer 2300 verzoeken; houd het zuinig vanwege fair use).

## Niet inbegrepen

Zwemwaterkwaliteit (blauwalg, E. coli): Zwemwater.nl heeft geen officiële API en eist bronvermelding. Eerst toestemming vragen bij BIJ12 (communicatie@bij12.nl) voordat dit wordt toegevoegd.

## Bronnen en licenties

- Rijkswaterstaat WaterWebservices, CC0: https://rijkswaterstaatdata.nl/waterdata/
- Weather data by [Open-Meteo.com](https://open-meteo.com/), CC BY 4.0
