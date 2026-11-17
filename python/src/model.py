"""Auditable bounded multimodal router. Standard library only.

Labels are compared on time, boarding readiness, carbon, walking and boardings.
Each transit expansion rides an entire scheduled trip to every permitted alighting
stop, so continuing on one vehicle never incurs a fictitious transfer.
"""
from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict
from datetime import date, timedelta
import gzip, json, math, bisect, heapq, time

ROOT=Path(__file__).resolve().parents[1]

def hav(a,b):
    x,y,u,v=map(math.radians,[a[0],a[1],b[0],b[1]])
    return 6371000*2*math.asin(min(1,math.sqrt(math.sin((u-x)/2)**2+math.cos(x)*math.cos(u)*math.sin((v-y)/2)**2)))

def seconds(t):
    h,m,s=map(int,t.split(':'));return h*3600+m*60+s

def clock(t):
    day=int(t)//86400;t=int(t)%86400
    return f'{t//3600:02}:{t%3600//60:02}'+(f' (+{day}j)' if day else '')

def active_services(calendar,exceptions,day):
    d=date.fromisoformat(day);key=d.strftime('%Y%m%d');wd=['monday','tuesday','wednesday','thursday','friday','saturday','sunday'][d.weekday()]
    active={r['service_id'] for r in calendar if r['start_date']<=key<=r['end_date'] and r.get(wd)=='1'}
    for r in exceptions:
        if r['date']==key:
            if r['exception_type']=='1':active.add(r['service_id'])
            elif r['exception_type']=='2':active.discard(r['service_id'])
    return active

@dataclass(eq=False,slots=True)
class Label:
    stop:str; t:int; ready:int; g:float; walk:int; boards:int; pmr:int; path:tuple
    alive:bool=True

def dominates(a,b):
    # Status differences are not numerically ranked. Both remain visible.
    return a.pmr==b.pmr and a.t<=b.t and a.ready<=b.ready and a.g<=b.g+1e-7 and a.walk<=b.walk and a.boards<=b.boards

class Network:
    def __init__(self,path=None,data=None):
        if data is None:
            with gzip.open(path or ROOT/'data'/'network.json.gz','rt',encoding='utf-8') as f:data=json.load(f)
        self.data=data;self.stops=data['stops'];self.routes=data['routes'];self.trips=data['trips'];self.calls={};self.coords={}
        for sid,s in self.stops.items():self.coords[sid]=(float(s['stop_lat']),float(s['stop_lon']))
        for tid,seq in data['calls'].items():
            if len(seq)<2 or any(not c[1] or not c[2] for c in seq):continue
            out=[(c[0],seconds(c[1]),seconds(c[2]),c[4] in ('','0'),c[5] in ('','0')) for c in seq]
            if any(out[i][1]<out[i-1][2] for i in range(1,len(out))) or any(c[2]<c[1] for c in out):continue
            self.calls[tid]=out
        self.used={c[0] for seq in self.calls.values() for c in seq}
        self.children=defaultdict(list)
        for s in self.used:
            p=self.stops[s].get('parent_station')
            if p:self.children[p].append(s)
        self.transfers=defaultdict(list);self.forbidden=set();self.raw_transfer={}
        for r in data.get('transfers',[]):
            aa=[r['from_stop_id']] if r['from_stop_id'] in self.used else self.children.get(r['from_stop_id'],[])
            bb=[r['to_stop_id']] if r['to_stop_id'] in self.used else self.children.get(r['to_stop_id'],[])
            for a in aa:
                for b in bb:
                    self.raw_transfer[a,b]=r
                    if r['transfer_type']=='3':self.forbidden.add((a,b));continue
                    if a==b:continue
                    walk=max(1,math.ceil(hav(self.coords[a],self.coords[b])*1.25/1.25))
                    duration=max(walk,int(r.get('min_transfer_time') or 0),30)
                    self.transfers[a].append((b,duration,walk,'GTFS transfers + marche estimée'))
        # Only official declared transfer edges; no invented cross-station links.
        self._days={};self._distances={};self.distance_quality=defaultdict(int)
        self.campus=(data['campus']['lat'],data['campus']['lon'])
        self.egress={s:math.ceil(hav(self.coords[s],self.campus)*1.25/1.25) for s in self.used if hav(self.coords[s],self.campus)<=1500}

    def pmr_stop(self,sid):
        visited=set()
        while sid and sid not in visited:
            visited.add(sid);s=self.stops.get(sid,{})
            v=s.get('wheelchair_boarding','')
            if v in ('1','2'):return int(v)
            sid=s.get('parent_station')
        return 0

    def day(self,day):
        if day in self._days:return self._days[day]
        active=active_services(self.data['calendar'],self.data['calendar_dates'],day)
        prev=active_services(self.data['calendar'],self.data['calendar_dates'],(date.fromisoformat(day)-timedelta(days=1)).isoformat())
        departures=defaultdict(list)
        for tid,seq in self.calls.items():
            service=self.trips[tid]['service_id']
            for offset in ([0] if service in active else [])+([-86400] if service in prev and seq[-1][1]>=86400 else []):
                for i,c in enumerate(seq[:-1]):
                    if c[3] and c[2]+offset>=0:departures[c[0]].append((c[2]+offset,tid,i,offset))
        for seq in departures.values():seq.sort()
        self._days[day]=departures;return departures

    def distances(self,tid):
        trip=self.trips[tid];seq=self.calls[tid];key=(trip.get('shape_id',''),tuple(c[0] for c in seq))
        if key in self._distances:return self._distances[key]
        shape=self.data.get('shapes',{}).get(trip.get('shape_id',''),[])
        coords=[self.coords[c[0]] for c in seq]
        cumulative=None;method='cordes inter-arrêts × 1,20'
        if len(shape)>1:
            points=[(r[1],r[2]) for r in shape];cum=[0.]
            for a,b in zip(points,points[1:]):cum.append(cum[-1]+hav(a,b))
            # Project stops onto polyline segments in a local metric plane.
            scale=111195;cos=math.cos(math.radians(coords[0][0]));positions=[];errors=[];last=0.
            for la,lo in coords:
                best=None
                for j,(a,b) in enumerate(zip(points,points[1:])):
                    ax=(a[1]-lo)*scale*cos;ay=(a[0]-la)*scale;dx=(b[1]-a[1])*scale*cos;dy=(b[0]-a[0])*scale
                    den=dx*dx+dy*dy;u=max(0,min(1,-(ax*dx+ay*dy)/den)) if den else 0
                    pos=cum[j]+u*(cum[j+1]-cum[j])
                    if pos+2<last:continue
                    error=math.hypot(ax+u*dx,ay+u*dy)
                    if best is None or error<best[0]:best=(error,pos)
                if best is None:errors.append(1e9);positions.append(last)
                else:errors.append(best[0]);positions.append(max(last,best[1]));last=positions[-1]
            if max(errors)<400 and all(positions[i]-positions[i-1]>=hav(coords[i-1],coords[i])*.85 for i in range(1,len(seq))):
                cumulative=positions;method='projection monotone sur shapes GTFS'
        if cumulative is None:
            cumulative=[0.]
            for a,b in zip(coords,coords[1:]):cumulative.append(cumulative[-1]+hav(a,b)*1.2)
        self.distance_quality[method]+=1;self._distances[key]=(cumulative,method)
        return cumulative,method

    def solve(self,origin,day,start='08:00',max_walk=30,max_changes=2,extra=10,profile='standard',bus_electric=False):
        started=time.perf_counter();departure=seconds(start if start.count(':')==2 else start+':00')
        # All searches are bounded to three hours and at most max_changes + 1 rides.
        departures=self.day(day);walk_limit=int(float(max_walk)*60);max_boards=int(max_changes)+1
        if not departures:raise ValueError('Aucun service actif dans ce périmètre pour cette date.')
        if profile=='strict':
            return {'options':[],'pareto':[],'message':'Aucun trajet certifiable de bout en bout : accès piétons et entrée IBGBI non audités PMR. Les données inconnues ne valent pas une garantie.','latency_ms':round((time.perf_counter()-started)*1000,2),'stats':{'labels':0},'origin':origin,'date':day,'start':start}

        def search(deadline,pareto):
            labels=defaultdict(list);queue=[];counter=0;solutions=[];best=deadline;created=0
            def push(l):
                nonlocal counter,created
                if l.t>best or l.walk>walk_limit or l.boards>max_boards:return
                existing=labels[l.stop]
                if pareto:
                    if any(dominates(o,l) for o in existing if o.alive):return
                    for o in existing:
                        if o.alive and dominates(l,o):o.alive=False
                else:
                    # Keep walk/board trade-offs even in the reference search;
                    # earliest time alone is not safe under resource constraints.
                    if any(o.alive and o.t<=l.t and o.ready<=l.ready and o.walk<=l.walk and o.boards<=l.boards and o.pmr==l.pmr for o in existing):return
                    for o in existing:
                        if o.alive and l.t<=o.t and l.ready<=o.ready and l.walk<=o.walk and l.boards<=o.boards and l.pmr==o.pmr:o.alive=False
                existing.append(l);counter+=1;created+=1;heapq.heappush(queue,(l.t,counter,l))
            origin_coord=(origin['lat'],origin['lon'])
            # Direct walk is a legitimate alternative, with declared distance model.
            direct=math.ceil(hav(origin_coord,self.campus)*1.25/1.25)
            if direct<=walk_limit:
                solutions.append(Label('@campus',departure+direct,departure+direct,0,direct,0,0,({'kind':'walk','from_name':origin['name'],'to_name':'IBGBI','from_coord':origin_coord,'to_coord':self.campus,'departure':departure,'arrival':departure+direct,'walk_s':direct,'distance_m':direct*1.25,'method':'distance géodésique × 1,25'},)))
                if not pareto:best=min(best,departure+direct)
            for sid in self.used:
                distance=hav(origin_coord,self.coords[sid])
                if distance>700:continue
                walk=math.ceil(distance*1.25/1.25)
                status=self.pmr_stop(sid)
                if profile=='avoid' and status==2:continue
                segment={'kind':'walk','from_name':origin['name'],'to_name':self.stops[sid]['stop_name'],'from_coord':origin_coord,'to_coord':self.coords[sid],'departure':departure,'arrival':departure+walk,'walk_s':walk,'distance_m':walk*1.25,'method':'distance géodésique × 1,25'}
                push(Label(sid,departure+walk,departure+walk,0,walk,0,2 if status==2 else 0,(segment,)))
            while queue:
                _,_,l=heapq.heappop(queue)
                if not l.alive or l.t>best:continue
                if l.stop in self.egress:
                    walk=self.egress[l.stop];arrival=l.t+walk
                    if l.walk+walk<=walk_limit and arrival<=best:
                        seg={'kind':'walk','from_name':self.stops[l.stop]['stop_name'],'to_name':'IBGBI','from_coord':self.coords[l.stop],'to_coord':self.campus,'departure':l.t,'arrival':arrival,'walk_s':walk,'distance_m':walk*1.25,'method':'distance géodésique × 1,25 ; entrée non auditée PMR'}
                        solutions.append(Label('@campus',arrival,arrival,l.g,l.walk+walk,l.boards,l.pmr,l.path+(seg,)))
                        if not pareto:best=arrival
                for target,duration,walk,method in self.transfers.get(l.stop,[]):
                    if l.t+duration>best:continue
                    status=self.pmr_stop(target);pmr=2 if 2 in (status,l.pmr) else 0
                    if profile=='avoid' and pmr==2:continue
                    seg={'kind':'walk','from_name':self.stops[l.stop]['stop_name'],'to_name':self.stops[target]['stop_name'],'from_coord':self.coords[l.stop],'to_coord':self.coords[target],'departure':l.t,'arrival':l.t+duration,'walk_s':walk,'distance_m':walk*1.25,'method':method}
                    push(Label(target,l.t+duration,l.t+duration,l.g,l.walk+walk,l.boards,pmr,l.path+(seg,)))
                if l.boards>=max_boards:continue
                # A self-stop GTFS prohibition forbids changing vehicles here.
                # Staying on the same vehicle is already expanded in one ride.
                if l.path and l.path[-1]['kind']=='transit' and (l.stop,l.stop) in self.forbidden:continue
                events=departures.get(l.stop,[])
                begin=bisect.bisect_left(events,(l.ready,))
                for dep,tid,i,offset in events[begin:]:
                    if dep>best:break
                    trip=self.trips[tid];route=self.routes[trip['route_id']];seq=self.calls[tid]
                    vehicle=int(trip.get('wheelchair_accessible') or 0)
                    status=2 if 2 in (l.pmr,vehicle,self.pmr_stop(l.stop)) else 0
                    if profile=='avoid' and status==2:continue
                    cumulative,method=self.distances(tid)
                    factor=self.data['factors'][route['route_type']]['g_per_pkm']
                    if bus_electric and route['route_type']=='3':factor=self.data['factor_source']['electric_bus_g_per_pkm']
                    for j in range(i+1,len(seq)):
                        sid,arr,_,_,dropoff=seq[j];arr+=offset
                        if arr>best:break
                        if not dropoff:continue
                        pmr=2 if 2 in (status,self.pmr_stop(sid)) else 0
                        if profile=='avoid' and pmr==2:continue
                        distance=max(0,cumulative[j]-cumulative[i]);g=distance/1000*factor
                        seg={'kind':'transit','route':route['route_short_name'],'route_type':int(route['route_type']),'color':'#'+(route.get('route_color') or '147C68'),'trip_id':tid,'from_stop':l.stop,'to_stop':sid,'from_name':self.stops[l.stop]['stop_name'],'to_name':self.stops[sid]['stop_name'],'from_coord':self.coords[l.stop],'to_coord':self.coords[sid],'departure':dep,'arrival':arr,'distance_m':round(distance,1),'emissions_g':round(g,4),'factor_g_per_pkm':factor,'method':method,'vehicle_accessibility':vehicle,'via':[self.coords[c[0]] for c in seq[i:j+1]]}
                        selfrule=self.raw_transfer.get((sid,sid),{})
                        buffer=max(120,int(selfrule.get('min_transfer_time') or 0))
                        push(Label(sid,arr,arr+buffer,l.g+g,l.walk,l.boards+1,pmr,l.path+(seg,)))
            return solutions,created

        fast,refcount=search(departure+3*3600,False)
        if not fast:return {'options':[],'pareto':[],'message':'Aucun trajet dans les limites choisies (périmètre, 3 h, marche, changements).','latency_ms':round((time.perf_counter()-started)*1000,2),'stats':{'labels':refcount},'origin':origin,'date':day,'start':start}
        reference=min(fast,key=lambda l:(l.t,l.g,l.walk,l.boards))
        candidates,count=search(reference.t+int(float(extra)*60),True)
        candidates.append(reference)
        frontier=[]
        for l in sorted(candidates,key=lambda l:(l.t,l.g,l.walk,l.boards)):
            if any(o.t<=l.t and o.g<=l.g+1e-7 and o.walk<=l.walk and o.boards<=l.boards and o.pmr==l.pmr for o in frontier):continue
            frontier=[o for o in frontier if not(l.t<=o.t and l.g<=o.g+1e-7 and l.walk<=o.walk and l.boards<=o.boards and l.pmr==o.pmr)];frontier.append(l)
        sober=min(frontier,key=lambda l:(l.g,l.t,l.walk,l.boards))
        simple=min(frontier,key=lambda l:(l.boards,l.t,l.g,l.walk))
        def serial(l,role):
            return {'role':role,'duration_min':round((l.t-departure)/60,2),'arrival':clock(l.t),'emissions_g':round(l.g,3),'walk_min':round(l.walk/60,2),'changes':max(0,l.boards-1),'accessibility':'incompatible renseignée' if l.pmr==2 else 'inconnue de bout en bout','segments':list(l.path),'extra_min':round((l.t-reference.t)/60,2),'gain_pct':round((reference.g-l.g)/reference.g*100,2) if reference.g>0 else None}
        return {'options':[serial(reference,'Rapide'),serial(sober,'Sobre'),serial(simple,'Peu de changements')],
                'pareto':[serial(l,'Compromis') for l in frontier],
                'message':'Horaires prévus. Marche estimée ; PMR non certifiée. Optimalité dans le modèle et le périmètre documentés.',
                'latency_ms':round((time.perf_counter()-started)*1000,2),'stats':{'labels':refcount+count,'frontier':len(frontier)},'origin':origin,'date':day,'start':start}

    def metadata(self):
        starts=[r['start_date'] for r in self.data['calendar']];ends=[r['end_date'] for r in self.data['calendar']]
        return {'campus':self.data['campus'],'origins':self.data['origins'],'routes':len(self.routes),'stops':len(self.used),'trips':len(self.calls),'min_date':date.fromisoformat(min(starts)).isoformat(),'max_date':date.fromisoformat(max(ends)).isoformat(),'provenance':self.data['provenance'],'factors':self.data['factors'],'factor_source':self.data['factor_source']}
