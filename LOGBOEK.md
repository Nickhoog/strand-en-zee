# Logboek Strand & Zee (HACS)

## 2026-10-19
- Onderzoek licenties:
  - Rijkswaterstaat WaterWebservices: CC0, geen API-sleutel, fair use, geen uptime-garantie (rijkswaterstaatdata.nl/waterdata, github.com/Rijkswaterstaat/WaterWebservices).
  - Zwemwater.nl: geen officiële API; proclaimer eist bronvermelding; contact communicatie@bij12.nl. Niet gebruikt.
  - Open-Meteo: gratis voor niet-commercieel gebruik (o.a. persoonlijke domotica), CC BY 4.0 (bronvermelding), <10.000 calls/dag.
- Dry run RWS (OphalenWaarnemingen, laatste 3 uur): 184 live stations gevonden, opgeslagen in `stations.json`.
  `OphalenLaatsteWaarnemingen` is onbruikbaar: geeft ook archiefreeksen (jaren oud) terug.
- Dry run `api.py` voor Zandvoort, Scheveningen en Vlissingen: alle 5 metingen (watertemp, golfhoogte, golfperiode, windsnelheid, windrichting) leveren live data.
- Dry run Open-Meteo Marine + Forecast voor dezelfde drie plekken: werkt ook, waarde precies op de strandlocatie (model, geen meting).
- Nog niet gedaan: testen in een echte Home Assistant, GitHub-repo, README.
- Open-Meteo toegevoegd als keuzebron (RWS standaard). Config flow heeft een bron-selector, sensoren tonen per bron de juiste bronvermelding.
- Dry run `fetch_open_meteo`: Zandvoort geeft alle 5 metingen, Utrecht (binnenland) alleen wind (geen zeedata, sensoren worden dan onbeschikbaar). Gefixt: floats in aiohttp-params (nu str) en tijdzone (nu GMT, geen zoneinfo nodig).
- README en `tools/generate_stations.py` toegevoegd (generator niet opnieuw gedraaid, syntax gecontroleerd).
- Nog open: testen in echte Home Assistant, GitHub-repo (privé), CHANGE_ME in manifest.json invullen, eventueel zwemwaterkwaliteit na toestemming BIJ12.

## 2026-10-19 (later)
- Besluit gebruiker: alleen Open-Meteo. RWS-bron, `stations.json`, `generate_stations.py`, bron-selector en afstandsinstelling verwijderd.
- Nieuw: dropdown met alle zwemlocaties. Bron: PDOK "Zwemwater provinciaal en rijkswateren" (CC0, ATOM-GML). `tools/generate_swimspots.py` zet de vlakken om naar middelpunten in WGS84 (EPSG:3035 heeft in GML eerst noorden, dan oosten). Resultaat: 739 unieke locaties in `swimspots.json`; Zandvoort en Scheveningen gecontroleerd.
- Dry run Open-Meteo op 6 locaties: kust geeft alles, binnenwater (o.a. Schoonhoven, Langwarder Wielen) alleen wind.
- Een bestaande dienst (Zandvoort, door gebruiker aangemaakt) blijft werken: de coördinator leest alleen lat/lon.
- Manifest-sleutels gesorteerd (hassfest), icoon in brand/ toegevoegd (HACS brands-check), versie 0.2.0.
- Release v0.2.0 gepubliceerd op GitHub (HACS-standaardlijst vereist een release).
- v0.2.1: hacs.json country NL (vereist voor HACS-PR bij landgebonden integraties), Engelse samenvatting in README.
- v0.2.2: sectie 'Niet inbegrepen' (zwemwaterkwaliteit/BIJ12) uit README gehaald op verzoek van de gebruiker.
- v0.2.3: apparaatinfo toonde 'door Open-Meteo'; fabrikant nu 'Strand & Zee', model 'Zwemlocatie (data: Open-Meteo)'. Open-Meteo is alleen de databron.
