---
hide:
  - navigation
---

# Documentation

Ce document contient la documentation de [l'extension Cadastre](./extension-qgis/installation.md) pour le logiciel QGIS
ainsi que la documentation du [module Cadastre](./module-lizmap/installation.md) pour 
[Lizmap](https://github.com/3liz/lizmap-web-client/).

## Description

L'extension Cadastre a été conçu pour faciliter l'utilisation des données cadastrales dans QGIS.
Plusieurs modules aident l'utilisateur à importer des données, les afficher dans QGIS, faire des recherches
et imprimer les relevés :

* L'**import de données cadastrales**, MAJIC et EDIGEO, dans une base de données **PostgreSQL/PostGIS** ou **Sqlite/Spatialite**.
* Un **module de chargement** permet d'ajouter automatiquement l'ensemble des couches cadastrales dans QGIS, avec la
  possibilité de choisir le style appliqué.
* Un **panneau de recherche** offre la possibilité de rechercher des parcelles par adresse, propriétaire ou par situation
  (commune, section) et de naviguer vers ces parcelles cadastrales.
* Un **outil d'identification** permet d'afficher les données liées à une parcelle en cliquant sur le polygone représentant
  la parcelle.
* Il est possible enfin d'exporter les données sous forme de **relevés parcellaires** et de **relevés de propriété**.

## Prérequis

* De préférence, QGIS LTR 3.28, minimum QGIS 3.18
* PostgreSQL : ≥ 13 + PostGIS ≥ 3.X
* Spatialite : 4.3.0

## Financeurs

La réalisation de l'extension Cadastre a été financée par :

* L'**[Union Européenne](http://europa.eu/)**
* Le **[Fonds Européen de Développement Régional de Picardie](http://www.picardie-europe.eu)**
* Le **[Conseil Régional de Picardie](http://www.picardie.fr)**
* L'**[Agence de Développement et d'Urbanisme du Grand Amiénois (ADUGA)](http://www.aduga.org)**

Les évolutions 2020 ont été soutenues par :

* Le **[Ministère de la Transition Écologie](https://www.ecologie.gouv.fr/)**
* L'association **[ASA de France](http://asadefrance.fr/)**
* La **[Communauté d'Agglomération du Grand-Narbonne](https://www.legrandnarbonne.com/)**
* Les **[Agences d'Urbanisme de Bretagne](https://www.datagences-bretagne.bzh/)** et autres : AGAM, AUSB, ADUGA, AUDAT,
  AUD Clermont Métropole, AGAPE Lorraine Nord, Boulogne Développement
* Le **[Conseil Départemental de Meurthe et Moselle](http://www.meurthe-et-moselle.fr/)**

Les structures suivantes ont aidé 3Liz pour la maintenance ou l'ajout de fonctionnalités:

- L'**[ADUGA](https://www.aduga.org/)** : maintenance pour les nouveaux millésimes
- La **[Ville de Megève](https://mairie.megeve.fr/)** : migration du plugin vers QGIS 3
- La **[Communauté d'Agglomération du Soissonnais](http://agglo.grandsoissons.com/accueil-3.html)** : amélioration de la
  recherche et ajout d'informations sur les fiches parcellaires
- Le **[Conseil départemental du Gard](https://www.gard.fr/accueil.html)** : ajout d'informations dans la fiche parcellaire
- La **[Métropole de Rennes](https://metropole.rennes.fr/)** : ajout des supports 2019 et 2020 des millésimes MAJIC
- le **[Ministère de la Transition Écologique](https://www.ecologie.gouv.fr/)** : détails sur les propriétaires (indivisions)

Les évolutions 2021 ont été soutenues par :

- La **[Métropole de Rennes](https://metropole.rennes.fr/)** : ajout du support MAJIC 2021
- La **[Métropole de Brest](https://www.brest.fr/brestfr-accueil-1575.html)** : enrichissement de la recherche de propriétaires
  (par nom d'usage, par nom de naissance, par commune)
- La société **[Éléments](https://www.elements.green/)** pour le téléchargeur Édigéo
- La **[Métropole de Clermont-Ferrand](https://www.clermontmetropole.eu)** :
  maintenance sur l'extension, travail exploratoire sur le remplacement d'ancien code concernant le DBManager et amélioration du code

![Financeurs](media/cadastre_financeurs.png)
