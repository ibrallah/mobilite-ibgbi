"""Independent consistency checks over exported itineraries and tables."""
from pathlib import Path
import json,math
ROOT=Path(__file__).resolve().parents[1]
summary=json.loads((ROOT/'results'/'summary.json').read_text(encoding='utf-8'))
details=json.loads((ROOT/'results'/'routes.json').read_text(encoding='utf-8'))
assert len(details)==len(summary['rows'])==60
for r,row in zip(details,summary['rows']):
    assert r['date']==row['date'] and r['start']==row['time']
    if not r['options']:continue
    ref,sober,simple=r['options']
    assert sober['duration_min']<=ref['duration_min']+10.02
    assert sober['emissions_g']<=ref['emissions_g']+.002
    for option in r['options']+r['pareto']:
        seq=option['segments'];last=-1;g=0;walk=0;rides=0
        for seg in seq:
            assert seg['departure']>=last,(row['query_id'],'time travel')
            assert seg['arrival']>=seg['departure'];last=seg['arrival']
            if seg['kind']=='transit':
                rides+=1;g+=seg['emissions_g']
                assert abs(seg['distance_m']/1000*seg['factor_g_per_pkm']-seg['emissions_g'])<.02
            else:walk+=seg['walk_s']
        assert abs(g-option['emissions_g'])<.002
        assert abs(walk/60-option['walk_min'])<.011
        assert walk<=1800 and max(0,rides-1)==option['changes']<=2
        h,m=map(int,r['start'].split(':'));assert abs((last-h*3600-m*60)/60-option['duration_min'])<.011
assert sum(q.get('gain_g',0)>.001 for q in summary['rows'])==summary['useful']
print('60 queries: chronology, units, carbon sums, walking budgets, changes and paired comparison verified.')
