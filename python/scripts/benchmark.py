"""Reproduce the 60 scheduled queries and export all evidence, without internet."""
from pathlib import Path
import sys,json,csv,time,statistics,platform,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.model import Network

def main():
    started=time.perf_counter();network=Network();load=time.perf_counter()-started
    days=['2026-11-17','2026-11-21'];hours=['07:30','08:00','08:30'];rows=[];details=[]
    for day in days:
        for origin in network.data['origins']:
            for hour in hours:
                r=network.solve(origin,day,hour,max_walk=30,max_changes=2,extra=10)
                details.append(r);row={'query_id':f'{origin["id"]}-{day}-{hour}','origin_id':origin['id'],'origin_name':origin['name'],'date':day,'time':hour,'solved':bool(r['options']),'latency_ms':r['latency_ms']}
                if r['options']:
                    a,b,c=r['options'];row.update({'fast_min':a['duration_min'],'sober_min':b['duration_min'],'fast_g':a['emissions_g'],'sober_g':b['emissions_g'],'gain_g':round(a['emissions_g']-b['emissions_g'],3),'gain_pct':b['gain_pct'],'extra_min':b['extra_min'],'fast_walk':a['walk_min'],'sober_walk':b['walk_min'],'fast_changes':a['changes'],'sober_changes':b['changes'],'simple_changes':c['changes'],'frontier_size':len(r['pareto']),'pmr_complete':False})
                rows.append(row);print(len(rows),row['query_id'],row.get('gain_g'),r['latency_ms'],flush=True)
    comparable=[r for r in rows if r['solved']];lat=sorted(r['latency_ms'] for r in rows);gains=[r['gain_pct'] for r in comparable if r['gain_pct'] is not None];positive=[r for r in comparable if r['gain_g']>.001]
    summary={'total':len(rows),'solved':len(comparable),'useful':len(positive),'median_gain_pct':statistics.median(gains) if gains else None,'median_gain_g':statistics.median(r['gain_g'] for r in comparable),'median_extra_min':statistics.median(r['extra_min'] for r in comparable),'median_positive_gain_pct':statistics.median(r['gain_pct'] for r in positive) if positive else None,'median_latency_ms':statistics.median(lat),'p95_latency_ms':lat[__import__('math').ceil(.95*len(lat))-1],'load_s':round(load,3),'pmr_complete':0,
             'protocol':'10 origines publiques × 3 départs (07:30, 08:00, 08:30) × 2 jours (17 et 21 novembre 2026). Marche ≤30 min ; ≤2 changements ; R1 = minimum carbone sous +10 min ; R2 = minimum de changements dans cette même fenêtre. Accès au réseau à ≤700 m ; sortie vers le campus à ≤1 500 m géodésiques. Recherche ≤3 h.',
             'notes':'Facteurs ADEME / Impact CO2, construction des véhicules incluse. Bus thermique générique : la motorisation locale réelle n’est pas identifiée. Distances projetées sur shapes GTFS si la qualité est suffisante, sinon cordes inter-arrêts ×1,20. Marche géodésique ×1,25 à 1,25 m/s. Optimalité limitée au réseau extrait et au modèle. Latence en cache progressif après chargement ; pas une mesure de consommation énergétique.',
             'machine':{'platform':platform.platform(),'processor':platform.processor(),'python':platform.python_version()},'distance_patterns':dict(network.distance_quality),'network_sha256':hashlib.sha256((ROOT/'data'/'network.json.gz').read_bytes()).hexdigest(),'rows':rows}
    summary['nonzero_reference_pairs']=len(gains)
    summary['median_positive_extra_min']=statistics.median(r['extra_min'] for r in positive) if positive else None
    summary['median_positive_extra_walk_min']=statistics.median(r['sober_walk']-r['fast_walk'] for r in positive) if positive else None
    out=ROOT/'results';out.mkdir(exist_ok=True)
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'routes.json').write_text(json.dumps(details,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (out/'benchmark.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    print('SUMMARY',{k:v for k,v in summary.items() if k not in ['rows','protocol','notes']},flush=True)

if __name__=='__main__':main()
