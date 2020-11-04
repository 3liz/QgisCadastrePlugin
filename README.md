Description
===========

Le plugin Cadastre a été conçu pour faciliter l'utilisation des données cadastrales dans QGIS. Plusieurs modules aident l'utilisateur à importer des données, les afficher dans QGIS, faire des recherches et imprimer les relevés :

* L'**import de données cadastrales**, MAJIC et EDIGEO, dans une base de données **PostgreSQL/PostGIS** ou **Sqlite/Spatialite**.
* Un **module de chargement** permet d'ajouter automatiquement l'ensemble des couches cadastrales dans QGIS, avec la possibilité de choisir le style appliqué.
* Un **panneau de recherche** offre la possibilité de rechercher des parcelles par adresse, propriétaire ou par situation (commune, section) et de naviguer vers ces parcelles cadastrales.
* Un **outil d'identification** permet d'afficher les données liées à une parcelle en cliquant sur le polygone représentant la parcelle.
* Il est possible enfin d'exporter les données sous forme de **relevés parcellaires** et de **relevés de propriété**.


Documentation
==============

Utilisation
------------

Voir [docs/index.md](docs/index.md)

Base de données
----------------

Documentation sur la structure des tables créées par le plugin

* fichiers source: https://github.com/3liz/QgisCadastrePlugin-documentation
* consulation: https://3liz.github.io/QgisCadastrePlugin-documentation/


Prérequis
=========

* QGIS 3.10 LTR
* PostgreSQL : >= 9.6 + PostGIS >= 1.5 et < 3.x
* Spatialite : 4.3.0


Financeurs
==========

La réalisation du plugin Cadastre a été financée par :

* L'**Union Européenne** ( http://europa.eu/index_fr.htm )
* Le **Fonds Européen de Développement Régional de Picardie** ( http://www.picardie-europe.eu )
* Le **Conseil Régional de Picardie** ( http://www.picardie.fr )
* L'**Agence de Développement et d'Urbanisme du Grand Amiénois (ADUGA)** ( http://www.aduga.org )

Les évolutions 2020 ont été soutenues par :

* Le **Ministère de la Transition Écologie** ( https://www.ecologie.gouv.fr/ )
* L'association **ASA de France** (http://asadefrance.fr/ )
* La **Communauté d'Agglomération du Grand-Narbonne** ( https://www.legrandnarbonne.com/)
* Les **Agences d'Urbanisme de Bretagne** ( https://www.datagences-bretagne.bzh/ ) et autres : AGAM, AUSB, ADUGA, AUDAT, AUD Clermont Métropole, AGAPE Lorraine Nord, Boulogne Développement
* Le **Conseil Départemental de Meurthe et Moselle** ( http://www.meurthe-et-moselle.fr/ )

Les structures suivantes ont aidé 3liz pour la maintenance ou l'ajout de fonctionnalités:

- L'**ADUGA** : maintenance pour les nouveaux millésimes
- La **Ville de Megève**: migration du plugin vers QGIS 3
- La **Communauté d'Agglomération du Soissonnais** : amélioration de la recherche et ajout d'informations sur les fiches parcellaires
- Le **Conseil départemental du Gard** : ajout d'informations dans la fiche parcellaire
- La **Métropole de Rennes** : ajout des supports 2019 et 2020 des millésimes MAJIC
- le **Ministère de la Transition Écologique** : détails sur les propriétaires (indivisions)

Conception
==========

Le plugin Cadastre a été conçu et développé par la Société **3LIZ**.
Site internet : http://www.3liz.com

Auteurs
=======

Michaël DOUCHIN
e-mail: info@3liz.com
twitter : https://twitter.com/kimaidou

Contributeurs
=============

* Landry BREUIL : @landryb , notamment pour ses tests sur de gros volumes de données, et les corrections sur certaines requêtes
* @fred-V13 pour l'aide sur la migration du plugin vers QGIS 3
* Maël REBOUX : @MaelREBOUX
* Étienne ROUVIN : @EtienneRouvin
* Christophe Masse

Sources
=======

GitHub : https://github.com/3liz/QgisCadastrePlugin

Licence
=======

GNU Public License (GPL) Version 2 ou supérieure



Ressources
==========

Les scripts d'import pour PostgreSQL proviennent de l'outil OpenCadastre (licence GPL). Ils ont été adaptés et améliorés pour leur utilisation dans ce plugin. Nos remerciements aux contributeurs.
Dépôt de sources :  https://adullact.net/scm/viewvc.php/trunk/data/pgsql/?root=opencadastre


English short description
==========================

This plugin helps users to use french land registry data ("cadastre") in QGIS. It is only useful in France for people having access to Cadastre data.

It is divided into modules :

* import data into database,
* load data in QGIS with appropriate symbology,
* search among data,
* export to PDF.
