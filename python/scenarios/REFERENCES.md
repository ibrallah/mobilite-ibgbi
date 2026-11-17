# Références du poster

## [1] Mobilité étudiante : données locales publiées

Université d’Évry et ekodev, **Résultats de l’enquête étudiants**, enquête du 10 octobre au 4 novembre 2022. Pages 1–2 pour l’Université d’Évry ; les autres pages portent sur d’autres établissements, non confondus avec cette population.

https://www.univ-evry.fr/fileadmin/mediatheque/ueve-institutionnel/000_Actus/Imgs/2023/Campus/Universite_d_Evry_-_Etudiants_-_Fiche_synthese_enquete.pdf

Document original accessible au lien officiel ci-dessus. Consultation et contrôle visuel de la page des chiffres le 17/11/2026. Le nombre de répondants, la participation, les moyennes, les dénominateurs variables et la portée historique sont conservés.

## [2] Facteurs d’émission

ADEME / Impact CO2, documentation de l’API : https://impactco2.fr/doc/api

Réponse source du 16/11/2026, incluse sous `impactco2_2026-11-16.json` :

https://impactco2.fr/api/v1/transport?km=1&displayAll=1&includeConstruction=1

Facteurs utilisés pour le graphique à distance conventionnelle : voiture thermique id 4 ; covoiturage thermique à deux id 22 ; bus thermique id 9 ; RER/Transilien id 14. La réponse donne un impact en kg pour 1 km ; il n’y a pas de seconde division par l’occupation d’un facteur déjà exprimé par voyageur. Le détour de 10 % est appliqué à la distance covoiturée.

Le facteur moyen de bus ne préjuge pas de la motorisation locale. Les facteurs ne constituent pas des émissions marginales ni une preuve d’économies effectives. La construction du véhicule est incluse selon le paramètre demandé ; ne pas y voir une ACV exhaustive de toute l’activité et des infrastructures.

## [3] Horaires, réseau et calcul technique

Île-de-France Mobilités, **Horaires prévus sur les lignes de transport en commun d’Île-de-France (GTFS Datahub)** :

https://data.iledefrance-mobilites.fr/explore/dataset/offre-horaires-tc-gtfs-idfm/information/

Spécification officielle GTFS : https://gtfs.org/documentation/schedule/reference/

Instantané initial du 16/11/2026. Archive complète SHA-256 : `6f450814afc92907680fbfcda3eb70e29e24f0e8419fb92e8057895be1984128`. Le réseau réduit nécessaire est remis dans `code_transport/data/`. Résultat Massy : ligne `massy-2026-11-17-08:00` du benchmark, sous les contraintes explicitées dans le poster et le dossier.

Métadonnées de licence : Licence Mobilité ; document original joint dans `code_transport/`. Les données restent attribuées à IDFM et aux opérateurs contributeurs ; elles ne sont pas présentées comme appartenant au groupe.

## [4] Vélib’ : offre standard V-Plus

Vélib’ Métropole, tableau officiel des offres consulté le 17/11/2026 : V-Plus standard à 4,30 €/mois avec engagement de 12 mois, soit 51,60 €/an. Les 30 premières minutes de chaque trajet en vélo mécanique sont incluses. Les dépassements et les vélos électriques ont une tarification distincte. Aucun tarif jeune n’est supposé.

https://www.velib-metropole.fr/fr_FR/offers

La disponibilité de Vélib’ dans la commune de départ est déclarée par le groupe ; la commune n’est pas renseignée. Ce service n’est pas présenté comme disponible au pied de l’IBGBI. La distance des quatre arrêts, le temps de déverrouillage, la disponibilité des vélos et places ainsi que le gain personnel restent à mesurer. Le facteur d’un vélo personnel ne doit pas être appliqué automatiquement à un vélo partagé : fabrication, maintenance et redistribution peuvent différer.

Le repère « 2 km de bus thermique ≈ 245 g » est illustratif : ce n’est ni une distance mesurée entre les quatre arrêts ni un gain net démontré. Il faut soustraire l’empreinte propre du vélo partagé et comparer les distances réellement parcourues.

## [5] Covoit IDFM et abonnements éligibles

Île-de-France Mobilités, avantages Navigo : https://www.iledefrance-mobilites.fr/actualites/avantages-passe-navigo

FAQ officielle Covoit IDFM : https://intercom-help.eu/covoit-idfm-help-center/fr/articles/470897-quel-est-le-prix-d-un-covoiturage-sur-covoit-idfm

Conditions consultées le 17/11/2026 : deux trajets passagers offerts par jour aux abonnés Navigo mensuel, annuel ou imagine R pour les trajets éligibles. La FAQ précise notamment un trajet de plus de 2 km, un départ et une arrivée en Île-de-France hors trajet intégralement intra-Paris, une prise en charge jusqu’à 80 km et au moins une heure entre les trajets. Les conditions peuvent évoluer. Ce n’est pas un droit à deux trajets gratuits avec tout titre Navigo, dans toute application et sans conditions.

## [6] Aide à l’achat d’un vélo mécanique

Région Île-de-France, FAQ LABAZ : https://www.iledefrance.fr/toutes-les-faq/lapplication-mobile-labaz-faq-jeunes

Île-de-France Mobilités : https://www.iledefrance-mobilites.fr/actualites/velo-nouvelles-aides-et-place-de-stationnement

Consultation le 17/11/2026 : pour les Franciliens de 15 à 25 ans via LABAZ, aide pouvant atteindre 100 €, plafonnée à 50 % du prix d’un vélo mécanique, sous conditions. Il s’agit d’un plafond, pas d’une somme automatiquement versée à chaque étudiant.

## [7] Freins sociaux : interprétation à examiner

GIEC, AR6, groupe III, chapitre 5 : https://www.ipcc.ch/report/ar6/wg3/chapter/chapter-5/

Le chapitre traite notamment de motivation, de capacité d’action, de perception du risque, de normes sociales et d’équité. Le rapprochement avec le sentiment d’injustice face à l’usage de jets privés est une hypothèse proposée par le groupe, à interroger localement ; la source ne démontre pas ce mécanisme chez les étudiants d’Évry. Le poster ne prétend pas que les étudiants seraient indifférents à l’écologie.

## Hypothèses et fourchettes reproductibles

Carburant : 2,00 €/L, valeur demandée par le groupe, et consommation illustrative de 6 L/100 km. Ce n’est pas une cotation vérifiée à une station ni la consommation mesurée d’un membre du groupe. Sur 22,5 km : 2,70 € seul ; avec deux occupants, +10 % de détour et partage égal : 1,485 €, arrondi à 1,49 € par personne. Assurance, entretien, amortissement, péage et parking exclus.

Covoiturage : réduction = 1 − (1 + détour) / occupation, à véhicule comparable et lorsque des trajets solo sont réellement remplacés. Deux à trois occupants et 0–20 % de détour donnent 40–66,7 %, arrondis à 40–67 %. Le facteur Impact CO2 est déjà par voyageur : le script ne le divise pas une seconde fois.

Vélo/VAE personnel : CO2e évité = distance × (facteur voiture − facteur vélo). Le croisement des distances 2 et 5 km et des facteurs vélo mécanique/VAE de l’instantané donne 0,263–0,710 kg par personne et par aller. Il ne s’agit pas d’une fourchette pour Vélib’, ni d’une économie totale du campus. Le remplacement de la marche ou du RER par la voiture partagée ne garantit pas un bénéfice.

Cas Massy, extrait du benchmark archivé : T12 sur 21,7772 km × 4,28 g = 93,2064 g ; bus 4122 sur 1,2282 km × 122,42 g = 150,3538 g. Soit 243,5602 g contre 93,2064 g avec le même T12 et une marche finale : −61,73 % ; 61,40 contre 67,33 minutes, soit +5,93 minutes au total. Les 8,0 et 21,4 minutes de marche ne sont pas les durées totales. Distances modélisées, horaires théoriques et facteurs moyens ; la motorisation thermique du bus est une hypothèse, pas un relevé du véhicule local. Ces estimations n’impliquent pas qu’une personne supplémentaire qui marche supprime immédiatement une circulation de bus.

Les récits d’Abdallah et Adem (45 min en voiture et 1 h 30 en RER) et de Mafaly et Adlane (marche + bus + RER D + marche) sont des déclarations du groupe, pas des itinéraires individuels validés par le calculateur. Le trajet Massy est une démonstration technique distincte.

## Destination et mobilité partagée

IBISC, accès au bâtiment IBGBI : https://www.ibisc.univ-evry.fr/acces/ . Le point publié localise le bâtiment, sans audit de l’entrée piétonne et PMR.

Le parking intégré est une information du groupe. Aucune gratuité n’a été déduite. Pour un futur calcul de disponibilité vélo, le flux Pony Évry constitue une source possible : https://transport.data.gouv.fr/datasets/velos-et-trottinettes-pony-evry . Le poster ne garantit ni la présence d’un vélo ni un tarif de location.

## Références de mise en page consultées

- NIH, Creating a Scientific Poster : https://www.training.nih.gov/creating-a-scientific-poster/
- UC Berkeley Library, Posters, Presentations & Science Writing / Design : https://guides.lib.berkeley.edu/posters/design

Elles ont guidé la hiérarchie et les légendes, sans remplacer le format A0 demandé. Les illustrations sont originales et générées pour ce poster ; aucun poster tiers ni logo institutionnel n’a été copié.
