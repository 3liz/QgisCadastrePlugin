---
hide:
  - navigation
---

# Processing

## 


### Configuration du projet

Ce traitement permet de configurer un projet QGIS pour de la publication sur le web avec Lizmap https://github.com/3liz/lizmap-web-client/ et son module Cadastre https://github.com/3liz/lizmap-cadastre-module


![algo_id](./cadastre-config_project.jpg)

#### Parameters

| ID | Description | Type | Info | Required | Advanced | Option |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
COMMUNE_LAYER|La couche communes|VectorLayer||✓||Default: Communes <br> Type: TypeVectorPolygon <br>|
COMMUNE_UNIQUE_FIELD|Champs identifiant les communes|Field||✓||Default: geo_commune <br> |
SECTION_LAYER|La couche sections|VectorLayer||✓||Type: TypeVectorPolygon <br>|
SECTION_UNIQUE_FIELD|Champs identifiant les sections|Field||✓||Default: geo_section <br> |
PARCELLE_LAYER|La couche parcelles|VectorLayer||✓||Type: TypeVectorPolygon <br>|
PARCELLE_UNIQUE_FIELD|Champs identifiant les parcelles|Field||✓||Default: geo_parcelle <br> |


#### Outputs

| ID | Description | Type | Info |
|:-:|:-:|:-:|:-:|
SUCCESS|Succès|Number||


***


### Téléchargeur Édigéo communal

Ce traitement permet de télécharger toutes les feuilles Edigéo sur plusieurs communes.
La date peut-être "latest" ou alors une date disponible sur https://cadastre.data.gouv.fr/datasets/plan-cadastral-informatise
L'URL ne doit pas être changé, sauf si l'API de cadastre.gouv.fr change.

![algo_id](./cadastre-telechargeur_edigeo_communal.jpg)

#### Parameters

| ID | Description | Type | Info | Required | Advanced | Option |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
LISTE_CODE_INSEE|Liste des code INSEE à télécharger, séparés par ","|String||✓|||
FILTRE|Filtre sur les feuilles séparés par "," peut-être "050170000C03,AB" qui téléchargent toutes les feuilles AB et 050170000C03|String||✓|||
DOSSIER|Dossier de destination|FolderDestination||✓|||
DATE|Date, disponible sur le site cadastre.data.gouv.fr (exemple "2021-02-01")|String||✓||Default: latest <br> |
URL_TEMPLATE|URL modèle, avec {date}, {departement}, {commune}|String||✓|✓|Default: https://cadastre.data.gouv.fr/data/dgfip-pci-vecteur/{date}/edigeo/feuilles/{departement}/{commune}/ <br> |


#### Outputs

| ID | Description | Type | Info |
|:-:|:-:|:-:|:-:|
DOSSIER|Dossier de destination|Folder||
NB_COMMUNES|Nombre de communes|Number||
NB_FEUILLES|Nombre de feuilles|Number||
DEPARTEMENTS|Départements, séparés par ","|String||


***

