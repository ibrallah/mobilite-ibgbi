# Vérifier l’exemple horaire du poster

Ce dossier contient le moteur et le réseau figé du prototype existant. Python 3.10+ suffit, sans installation pip ni accès réseau.

Depuis ce dossier :

```console
python -m unittest discover -s tests -v
python scripts/check_evidence.py
python scripts/benchmark.py
```

Les 22 tests portent sur des cas contrôlés. `check_evidence.py` contrôle les exports fournis (chronologie, unités, sommes et contraintes). `benchmark.py` recalcule les 60 requêtes, dont Massy le 17 novembre à 08:00, et actualise les fichiers de résultats. Les temps d’exécution peuvent changer ; les parcours et calculs doivent correspondre au même réseau figé et aux mêmes paramètres.

Le poster prend le cas `massy-2026-11-17-08:00`, sans l’attribuer à l’un des membres du groupe. La référence est le trajet de durée minimale ; la variante minimise les émissions sous +10 min, avec marche ≤30 min, ≤2 changements et recherche ≤3 h, dans le périmètre extrait de 51 lignes. Les émissions restent estimées. Les accès piétons sont approchés, les données PMR ne certifient pas la chaîne et la motorisation des bus n’est pas identifiée : facteur thermique générique.

`data/provenance.json` contient les informations d’archive et de source IDFM. Le document original de Licence Mobilité est conservé ici. Respecter les attributions et conditions lors de toute redistribution.

Le module de scénarios voiture/covoiturage à distance conventionnelle et le calcul carburant sont distincts : `../sources/calculs.py`. L’interface publique future qui réunirait coûts, covoiturage et météo n’est pas annoncée comme déployée.
