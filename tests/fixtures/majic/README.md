# Données MAJIC fictives

> ⚠️ **ATTENTION : TOUTES LES DONNÉES MAJIC DE CE RÉPERTOIRE SONT FICTIVES.**
>
> **Les propriétaires, noms, prénoms, dates et lieux de naissance, adresses, numéros SIREN, comptes,
> locaux, évaluations et montants ont été inventés.** Ils ne décrivent aucune personne, aucune société
> et aucun bien réel. Toute ressemblance avec des personnes ou des propriétés existantes serait
> purement fortuite.
>
> Ces fichiers servent uniquement à tester le plugin. Ils ne doivent pas être utilisés comme
> des données cadastrales.

## Contenu

Le répertoire `13029` contient un jeu de données MAJIC au format 2026 pour la commune de
Cornillon-Confoux (département `13`, direction `2`, code commune `029`) :

| Fichier        | Contenu                                                         |
|----------------|-----------------------------------------------------------------|
| `REVPROP.800`  | Propriétaires (comptes communaux et personnes)                  |
| `REVNBAT.800`  | Propriétés non bâties (parcelles, subdivisions fiscales)        |
| `REVBATI.800`  | Propriétés bâties (locaux, parties d'évaluation, dépendances)  |
| `REVFPDL.800`  | Propriétés divisées en lots (une copropriété)                   |
| `REVD166.800`  | Lots et locaux de la copropriété                                |
| `TOPO_test.csv`| Voies et lieux-dits de la commune                               |

Les **parcelles** sont celles des données EDIGEO de test (`tests/fixtures/edigeo/13029`), avec les mêmes
identifiants et des contenances issues de leur géométrie : les données MAJIC et EDIGEO peuvent donc être
importées ensemble et sont liées entre elles. Le fichier `TOPO_test.csv` est un extrait du fichier TOPO
de la commune, auquel ont été ajoutés les lieux-dits présents dans les données EDIGEO.

**Tout le reste est inventé** : 72 comptes de propriétaires (personnes physiques seules, couples,
indivisions, usufruit et nue-propriété, commune, département, SCI, GFA, copropriété et son syndic),
166 locaux (maisons, dépendances, appartements), les subdivisions fiscales, les exonérations et
les montants. La première maison, par ordre d'invariant, a deux parties d'évaluation (l'habitation et
un garage) et deux exonérations (commune et groupement de communes), pour tester la fiche des locaux.

## Génération

Les fichiers sont produits par le script `generate_majic_13029.py`, à partir de la liste des parcelles
EDIGEO `parcelles_edigeo_13029.csv`. Le tirage aléatoire utilise une graine fixe : le script produit
toujours les mêmes fichiers.

```bash
cd tests/fixtures/majic
python3 generate_majic_13029.py
```

Les positions des champs suivent la description des fichiers MAJIC 2026 (`docs/media/pdf/MAJIC/2026`)
et les scripts d'import du plugin (`cadastre/scripts/plugin/2026/majic3_formatage_donnees.sql`). Seules
les colonnes utilisées par le plugin (import, fiche parcellaire, relevé de propriété, export) et celles
qui servent aux jointures sont remplies.
