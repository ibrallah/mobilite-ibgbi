import unittest
from src.model import Network,seconds,clock,active_services,Label,dominates

def fixture():
    stops={s:{'stop_name':s,'stop_lat':str(la),'stop_lon':str(lo),'parent_station':'','wheelchair_boarding':'1'} for s,la,lo in [('A',48.6,2.3),('B',48.65,2.35),('C',48.7,2.4)]}
    routes={'bus':{'route_short_name':'BUS','route_type':'3','route_color':'aa4422'},'rail':{'route_short_name':'D','route_type':'2','route_color':'008855'}}
    trips={'bus1':{'route_id':'bus','service_id':'s','shape_id':'','wheelchair_accessible':'1'},'rail1':{'route_id':'rail','service_id':'s','shape_id':'','wheelchair_accessible':'1'}}
    def c(s,t,i,p='0',d='0'):return [s,t,t,i,p,d]
    calls={'bus1':[c('A','08:00:00',0),c('C','08:18:00',1)],'rail1':[c('A','08:01:00',0),c('B','08:12:00',1),c('C','08:25:00',2)]}
    cal={'service_id':'s','start_date':'20261116','end_date':'20261215',**{d:'1' for d in ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']}}
    return {'stops':stops,'routes':routes,'trips':trips,'calls':calls,'transfers':[],'calendar':[cal],'calendar_dates':[],'shapes':{},'campus':{'name':'Campus','lat':48.7,'lon':2.4},'origins':[{'id':'a','name':'A','lat':48.6,'lon':2.3}],'factors':{'3':{'g_per_pkm':122.42},'2':{'g_per_pkm':9.78}},'factor_source':{'electric_bus_g_per_pkm':21.7},'provenance':{}}

class Tests(unittest.TestCase):
    def solve(self,d=None,**kwargs):
        d=d or fixture();n=Network(data=d);return n.solve(d['origins'][0],'2026-11-17','07:59',**kwargs)
    def test_after_midnight(self):self.assertEqual(seconds('25:10:00'),90600);self.assertEqual(clock(90600),'01:10 (+1j)')
    def test_calendar_remove_add(self):
        d=fixture();self.assertEqual(active_services(d['calendar'],[{'service_id':'s','date':'20261117','exception_type':'2'},{'service_id':'x','date':'20261117','exception_type':'1'}],'2026-11-17'),{'x'})
    def test_no_active_service(self):
        d=fixture();d['calendar_dates']=[{'service_id':'s','date':'20261117','exception_type':'2'}]
        with self.assertRaises(ValueError):self.solve(d)
    def test_real_compromise_and_bounded_window(self):
        r=self.solve();a,b,_=r['options'];self.assertAlmostEqual(a['duration_min'],19);self.assertAlmostEqual(b['duration_min'],26);self.assertGreater(a['emissions_g'],b['emissions_g']);self.assertEqual(b['extra_min'],7)
    def test_zero_extra(self):
        r=self.solve(extra=0);self.assertEqual(r['options'][0]['emissions_g'],r['options'][1]['emissions_g'])
    def test_same_vehicle_not_transfer(self):
        r=self.solve();self.assertEqual(r['options'][1]['changes'],0);self.assertEqual(len([s for s in r['options'][1]['segments'] if s['kind']=='transit']),1)
    def test_no_pickup(self):
        d=fixture();d['calls']['bus1'][0][4]='1';r=self.solve(d);self.assertEqual(r['options'][0]['segments'][1]['route'],'D')
    def test_no_dropoff(self):
        d=fixture();d['calls']['bus1'][1][5]='1';r=self.solve(d);self.assertEqual(r['options'][0]['segments'][1]['route'],'D')
    def test_pmr_chain_unknown(self):
        self.assertTrue(all(x['accessibility'].startswith('inconnue') for x in self.solve()['options']))
    def test_pmr_strict_no_false_positive(self):self.assertEqual(self.solve(profile='strict')['options'],[])
    def test_pmr_exclusion(self):
        d=fixture();d['trips']['bus1']['wheelchair_accessible']='2';r=self.solve(d,profile='avoid');self.assertEqual(r['options'][0]['segments'][1]['route'],'D')
    def test_pmr_inheritance(self):
        d=fixture();d['stops']['A']['wheelchair_boarding']='0';d['stops']['A']['parent_station']='B';self.assertEqual(Network(data=d).pmr_stop('A'),1)
    def test_missed_transfer(self):
        d=fixture();d['calls']['rail1']=d['calls']['rail1'][:2];d['calls']['bus1']=[['B','08:13:00','08:13:00',0,'0','0'],['C','08:20:00','08:20:00',1,'0','0']]
        self.assertFalse(self.solve(d)['options'])
    def test_feasible_transfer(self):
        d=fixture();d['calls']['rail1']=d['calls']['rail1'][:2];d['calls']['bus1']=[['B','08:14:00','08:14:00',0,'0','0'],['C','08:22:00','08:22:00',1,'0','0']]
        r=self.solve(d);self.assertEqual(r['options'][0]['changes'],1)
    def test_changes_limit(self):
        d=fixture();d['calls']['rail1']=d['calls']['rail1'][:2];d['calls']['bus1']=[['B','08:14:00','08:14:00',0,'0','0'],['C','08:22:00','08:22:00',1,'0','0']]
        self.assertFalse(self.solve(d,max_changes=0)['options'])
    def test_carbon_units(self):
        r=self.solve();seg=r['options'][0]['segments'][1];self.assertAlmostEqual(seg['emissions_g'],seg['distance_m']/1000*122.42,delta=.02)
    def test_shape_projection(self):
        d=fixture();d['trips']['bus1']['shape_id']='shape';d['shapes']={'shape':[[0,48.6,2.3],[1,48.65,2.35],[2,48.7,2.4]]};n=Network(data=d);cum,method=n.distances('bus1');self.assertIn('projection',method);self.assertGreater(cum[-1],10000)
    def test_unknown_and_incompatible_not_dominated(self):
        a=Label('A',10,10,5,1,1,0,());b=Label('A',10,10,5,1,1,2,());self.assertFalse(dominates(a,b))
    def test_previous_service_day(self):
        d=fixture();d['calls']['bus1']=[['A','25:00:00','25:00:00',0,'0','0'],['C','25:18:00','25:18:00',1,'0','0']];d['trips'].pop('rail1');d['calls'].pop('rail1');d['calendar_dates']=[{'service_id':'s','date':'20261117','exception_type':'2'}];n=Network(data=d);r=n.solve(d['origins'][0],'2026-11-17','00:59');self.assertEqual(r['options'][0]['duration_min'],19)
    def test_electric_scenario(self):
        a=self.solve()['options'][0]['emissions_g'];b=self.solve(bus_electric=True)['options'][0]['emissions_g'];self.assertLess(b,a)
    def test_forbidden_self_transfer(self):
        d=fixture();d['calls']['rail1']=d['calls']['rail1'][:2];d['calls']['bus1']=[['B','08:14:00','08:14:00',0,'0','0'],['C','08:22:00','08:22:00',1,'0','0']];d['transfers']=[{'from_stop_id':'B','to_stop_id':'B','transfer_type':'3','min_transfer_time':''}]
        self.assertFalse(self.solve(d)['options'])
    def test_gtfs_minimum_self_transfer(self):
        d=fixture();d['calls']['rail1']=d['calls']['rail1'][:2];d['calls']['bus1']=[['B','08:14:00','08:14:00',0,'0','0'],['C','08:22:00','08:22:00',1,'0','0']];d['transfers']=[{'from_stop_id':'B','to_stop_id':'B','transfer_type':'2','min_transfer_time':'300'}]
        self.assertFalse(self.solve(d)['options'])

if __name__=='__main__':unittest.main()
