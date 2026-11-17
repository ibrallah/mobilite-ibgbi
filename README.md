# Venir à la fac, émettre moins — IBGBI

Compagnon du poster scientifique de M1 CNS, Université Évry Paris-Saclay.

**Mafaly Diop · Adem Djebbar · Adlane Lazib · Abdallah-Ibrahim Titt**

Ce dépôt contient une page statique avec un prompt personnalisable à copier dans une IA et un projet Python reproductible. La page ne calcule pas les itinéraires et ne transmet pas les champs à une IA. L’utilisateur copie puis envoie lui-même son texte au service choisi. Aucune clé d’API n’est nécessaire.

## Étudiants

Ouvrir le site compagnon, renseigner ses contraintes, copier le prompt et le coller dans son IA favorite. Les réponses doivent être vérifiées : horaires, météo, tarifs, disponibilité des vélos et aides ne sont pas garantis. Une adresse approximative ou une gare suffit pour commencer.

## Enseignants : voir le calcul effectif

- `python/src/model.py` : moteur multi-étiquette utilisant horaires, marche, émissions, montées et statut PMR.
- `python/data/network.json.gz` : extrait GTFS figé du 16/11/2026, 51 lignes ; périmètre partiel.
- `python/scripts/benchmark.py` : 60 requêtes et comparaison avec une référence rapide.
- `python/results/routes.json` : étapes, distances, facteurs et émissions de chaque option.
- `python/tests/test_model.py` : 22 tests sur des cas contrôlés.
- `python/scenarios/calculs.py` : comparaisons conventionnelles voiture/covoiturage/vélo et coût carburant à 2 €/L.
- `python/scenarios/REFERENCES.md` : sources, limites, hypothèses et conditions des dispositifs cités.

Le moteur recherche le plus rapide sous les contraintes, puis le moins émetteur dans le surtemps autorisé et une option avec peu de changements. Il ne calcule pas encore le covoiturage, le routage voiture, des itinéraires cyclables ou les coûts personnels : les chiffres correspondants du poster sont des scénarios distincts.

## Reproduire

Python 3.10+ ; aucun package externe pour le moteur.

```sh
cd python
python -m unittest discover -s tests -v
python scripts/check_evidence.py
python scripts/benchmark.py
python scenarios/calculs.py
```

Le benchmark recalcule et remplace ses sorties. Les latences dépendent de la machine ; le réseau figé et les paramètres permettent de reproduire les itinéraires. Les calculs de scénarios sont indépendants du benchmark.

## Résultat illustré sur le poster

Massy → IBGBI, 17/11/2026 à 08:00 : référence T12 + bus 4122 + marche, 61,40 min et 243,560 g CO2e ; variante T12 + marche, 67,33 min et 93,206 g. Soit −61,73 % d’émissions modélisées, +5,93 min et davantage de marche. Les deux derniers critères peuvent sélectionner la même variante : les trois cartes ne garantissent pas trois trajets distincts.

## Limites à conserver

Horaires prévus figés, marche approchée sans graphe de voirie, motorisation thermique de bus supposée, facteurs moyens et chaîne PMR non certifiée. L’étude ne mesure pas l’adoption, les économies réelles ou l’empreinte totale actuelle du campus. Les statistiques générales du poster viennent d’une enquête volontaire Évry 2022 ; elles ne décrivent pas exclusivement l’IBGBI. La page fournit un accompagnement, pas une garantie de trajet.

## Sources et droits des tiers

GTFS : Île-de-France Mobilités et opérateurs contributeurs, **Licence Mobilité**, texte inclus dans `python/2021_LicenceMobilites.pdf`, provenance dans `python/data/provenance.json`.

Facteurs : ADEME / Impact CO2, instantané du 16/11/2026, provenance et références dans `python/scenarios/`. Les tarifs et aides doivent être vérifiés sur leurs pages officielles avant usage.

Les noms d’IA renvoient à des services tiers indépendants de ce projet. L’illustration est conceptuelle et générée par IA. Le badge IBGI est un élément personnalisé, pas un logo institutionnel officiel.
