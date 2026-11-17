"""Calculs du poster, sans dépendance et sans requête réseau.

Les comparaisons à 22,5 km sont conventionnelles. La moyenne publiée tous modes
ne décrit pas spécifiquement les automobilistes, ni les seuls étudiants IBGBI.
"""
from pathlib import Path
import json,math

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path(__file__).parent/'impactco2_2026-11-16.json'

def compute():
    rows=json.loads(SOURCE.read_text(encoding='utf-8'))['data'];f={r['id']:r['value'] for r in rows}
    d=22.5;occupants=2;detour=1.1
    scenarios=[{'mode':'Voiture solo','distance_km':d,'occupants':1,'kg_co2e':d*f[4],'api_id':4},
               {'mode':'Covoiturage à deux','distance_km':d*detour,'occupants':occupants,'kg_co2e':d*detour*f[22],'api_id':22},
               {'mode':'Bus thermique','distance_km':d,'occupants':'facteur moyen','kg_co2e':d*f[9],'api_id':9},
               {'mode':'RER / Transilien','distance_km':d,'occupants':'facteur moyen','kg_co2e':d*f[14],'api_id':14}]
    solo=scenarios[0]['kg_co2e'];shared=scenarios[1]['kg_co2e'];gain=(1-shared/solo)*100
    weekly_solo=solo*2*5;weekly_mixed=solo*2*3+shared*2*2
    # Explicit illustrative cost assumptions, not the current fuel price nor the
    # actual consumption of any group member's car. Fixed costs are excluded.
    litres_per_100=6.;euro_per_litre=2.0
    fuel_solo=d/100*litres_per_100*euro_per_litre
    fuel_shared=d*detour/100*litres_per_100*euro_per_litre/occupants
    assert abs(gain-45)<1e-10
    assert abs((1-weekly_mixed/weekly_solo)*100-18)<1e-10
    carpool_ranges=[1-(1+detour)/n for n in [2,3] for detour in [0,.2]]
    bike_ranges=[km*(f[4]-f[bike]) for km in [2,5] for bike in [7,8]]
    return {'distance_convention_km':d,'source_distance':'Moyenne publiée, enquête Université d’Évry 2022, tous modes. Réutilisée uniquement pour standardiser la comparaison.',
            'scenarios':scenarios,'carpool_gain_pct':gain,'carpool_detour_pct':10,'weekly':{'days':5,'round_trips_per_day':1,'solo_kg':weekly_solo,'mixed_kg':weekly_mixed,'mixed_carpool_days':2,'gain_pct':18},
            'cost_scenario':{'consumption_l_per_100km':litres_per_100,'fuel_euro_per_litre_assumed':euro_per_litre,'solo_euro_one_way':fuel_solo,'carpool_euro_per_person_one_way':fuel_shared,'scope':'Carburant seulement ; ni prix constaté, ni coût total. Assurance, entretien, amortissement, péage et parking non inclus.'},
            'survey':{'year':2022,'respondents':561,'participation_pct':5,'mean_distance_km':22.5,'mean_time_min':51.2,'modal_share_pct':{'Train / RER':40,'Bus':32,'Voiture':21,'Marche':6,'Vélo / VAE':1,'Covoiturage':1},'scope':'Université d’Évry, pas uniquement IBGBI ; dénominateurs variables ; arrondis ; enquête volontaire historique.'},
            'parking':{'integrated':True,'source':'Information déclarée par le groupe','price':'non renseigné'},
            'ranges':{'carpool_reduction_pct':[min(carpool_ranges)*100,max(carpool_ranges)*100],'carpool_conditions':'2 à 3 occupants, détour de 0 à 20 %, trajets solo remplacés ; même facteur véhicule.','private_bike_or_ebike_avoided_kg_per_trip':[min(bike_ranges),max(bike_ranges)],'bike_conditions':'Vélo/VAE personnel remplaçant une voiture sur 2 à 5 km ; facteurs et périmètre figés. Ne vaut pas pour un vélo partagé.','bus_segment_2km_g':2*f[9]*1000,'shared_bike_conditions':'Le gain net du Vélib nécessite sa distance réelle et son facteur propre, incluant notamment la logistique. La distance de quatre arrêts n’est pas connue.'},
            'personal_cases':{'car_driver':{'names':'Abdallah et Adem','duration_car_declared_min':45,'duration_rer_declared_min':90,'source':'Durées indicatives déclarées par le groupe, sans vérification GTFS de leurs origines.'},'multimodal_student':{'names':'Mafaly et Adlane','chain':'Marche + bus + RER D + marche','bus_stops_declared':4,'velib_city':'Service disponible dans la ville de départ selon le groupe ; commune non fournie.'}},
            'limitations':['Ne pas multiplier une distance moyenne tous modes par une part de personnes pour inventer une empreinte totale du campus.','Les facteurs sont moyens, pas marginaux. Le bus est un scénario thermique générique.','Le gain de covoiturage suppose un trajet partagé et des trajets de référence réellement remplacés.','Aucune durée, météo, économie personnelle ou adoption étudiante n’est fabriquée.']}

if __name__=='__main__':
    data=compute();(Path(__file__).parent/'resultats_calcules.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Comparaisons kg CO2e / personne / aller :',[(r['mode'],round(r['kg_co2e'],3)) for r in data['scenarios']])
    print('Semaine conventionnelle :',data['weekly'])
    print('Coût carburant hypothétique :',data['cost_scenario'])
