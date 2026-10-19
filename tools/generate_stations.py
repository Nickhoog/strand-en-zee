"""Ververs stations.json: welke RWS-stations leveren de laatste 6 uur live data.
Gebruik zuinig (fair use): ongeveer 2300 verzoeken."""
import json, urllib.request, datetime as dt
from concurrent.futures import ThreadPoolExecutor
import urllib.request as _u, os
CAT='https://ddapi20-waterwebservices.rijkswaterstaat.nl/METADATASERVICES/OphalenCatalogus'
_r=_u.Request(CAT,json.dumps({'CatalogusFilter':{'Compartimenten':True,'Grootheden':True,'Parameters':True,'Eenheden':True}}).encode(),{'Content-Type':'application/json'})
d=json.load(_u.urlopen(_r,timeout=120))
loc={l['Locatie_MessageID']:l for l in d['LocatieLijst']}
ids={('OW','T'):1874,('OW','Hm0'):1150,('OW','Tm02'):1886,('LT','WINDSHD'):1906,('LT','WINDRTG'):1904,('LT','WINDST'):1908}
sets={k:set(x['Locatie_MessageID'] for x in d['AquoMetadataLocatieLijst'] if x['AquoMetaData_MessageID']==v) for k,v in ids.items()}
now=dt.datetime.now(dt.timezone.utc)
fmt=lambda t:t.strftime('%Y-%m-%dT%H:%M:%S.000+00:00')
URL='https://ddapi20-waterwebservices.rijkswaterstaat.nl/ONLINEWAARNEMINGENSERVICES/OphalenWaarnemingen'
def q(args):
    lid,(c,g)=args; code=loc[lid]['Code']
    body={"Locatie":{"Code":code},"AquoPlusWaarnemingMetadata":{"AquoMetadata":{"Compartiment":{"Code":c},"Grootheid":{"Code":g}}},
          "Periode":{"Begindatumtijd":fmt(now-dt.timedelta(hours=6)),"Einddatumtijd":fmt(now)}}
    r=urllib.request.Request(URL,json.dumps(body).encode(),{'Content-Type':'application/json'})
    try:
        o=json.load(urllib.request.urlopen(r,timeout=60))
    except Exception as e: return (lid,c,g,None,str(e)[:40])
    last=None
    for w in o.get('WaarnemingenLijst') or []:
        for m in w['MetingenLijst']:
            if last is None or m['Tijdstip']>last[0]: last=(m['Tijdstip'],m['Meetwaarde'].get('Waarde_Numeriek'))
    return (lid,c,g,last,None)
jobs=[(i,k) for k,s in sets.items() for i in s if k!=('OW','T') or True]
# alleen locaties binnen NL kust/meren-box voor T om verzoeken te beperken
jobs=[j for j in jobs if j[1]!=('OW','T') or (loc[j[0]]['Lon']<7.3 and loc[j[0]]['Lat']>50.7)]
print(len(jobs))
with ThreadPoolExecutor(8) as ex: res=list(ex.map(q,jobs))
st={}
for lid,c,g,last,err in res:
    if last:
        l=loc[lid]
        x=st.setdefault(l['Code'],{'code':l['Code'],'name':l['Naam'].strip(),'lat':round(l['Lat'],5),'lon':round(l['Lon'],5),'q':[]})
        x['q'].append(g)
out={'generated':dt.date.today().isoformat(),'stations':sorted(st.values(),key=lambda s:s['code'])}
dest=os.path.join(os.path.dirname(__file__),'..','custom_components','strand_en_zee','stations.json')
json.dump(out,open(dest,'w',encoding='utf8'),ensure_ascii=False,indent=0)
alive=[r for r in res if r[3]]
print('alive',len(alive),'errors',sum(1 for r in res if r[4]))
