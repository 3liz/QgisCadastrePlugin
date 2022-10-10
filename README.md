# Cadastre

[![QGIS.org](https://img.shields.io/badge/QGIS.org-published-green)](https://plugins.qgis.org/plugins/cadastre/)
[![❄ Flake8](https://github.com/3liz/QgisCadastrePlugin/actions/workflows/test-lint.yml/badge.svg)](https://github.com/3liz/QgisCadastrePlugin/actions/workflows/test-lint.yml)
[![🎳 Tests](https://github.com/3liz/QgisCadastrePlugin/actions/workflows/test-python.yml/badge.svg)](https://github.com/3liz/QgisCadastrePlugin/actions/workflows/test-python.yml)
[![📖 Documentation](https://github.com/3liz/QgisCadastrePlugin/actions/workflows/publish-doc.yml/badge.svg)](https://github.com/3liz/QgisCadastrePlugin/actions/workflows/publish-doc.yml)

## Description

L'extension Cadastre a été conçu pour faciliter l'utilisation des données cadastrales dans QGIS.

Pour une description plus complète, lire la documentation de l'extension https://docs.3liz.org/QgisCadastrePlugin/

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
* Les **[Agences d'Urbanisme de Bretagne](https://www.datagences-bretagne.bzh/)** et autres : AGAM, AUSB, ADUGA, AUDAT, AUD Clermont Métropole, AGAPE Lorraine Nord, Boulogne Développement
* Le **[Conseil Départemental de Meurthe et Moselle](http://www.meurthe-et-moselle.fr/)**

Les structures suivantes ont aidé 3Liz pour la maintenance ou l'ajout de fonctionnalités:

- L'**[ADUGA](https://www.aduga.org/)** : maintenance pour les nouveaux millésimes
- La **[Ville de Megève](https://mairie.megeve.fr/)** : migration du plugin vers QGIS 3
- La **[Communauté d'Agglomération du Soissonnais](http://agglo.grandsoissons.com/accueil-3.html)** : amélioration de la recherche et ajout d'informations sur les fiches parcellaires
- Le **[Conseil départemental du Gard](https://www.gard.fr/accueil.html)** : ajout d'informations dans la fiche parcellaire
- La **[Métropole de Rennes](https://metropole.rennes.fr/)** : ajout des supports 2019 et 2020 des millésimes MAJIC
- le **[Ministère de la Transition Écologique](https://www.ecologie.gouv.fr/)** : détails sur les propriétaires (indivisions)

Les évolutions 2021 ont été soutenues par :

- La **[Métropole de Rennes](https://metropole.rennes.fr/)** : ajout du support MAJIC 2021
- La **[Métropole de Brest](https://www.brest.fr/brestfr-accueil-1575.html)** : enrichissement de la recherche de propriétaires (par nom d'usage, par nom de naissance, par commune)
- La société **[Éléments](https://www.elements.green/)** pour le téléchargeur Édigéo
- La **[Métropole de Clermont-Ferrand](https://www.clermontmetropole.eu)** :
  maintenance sur l'extension, travail exploratoire sur le remplacement d'ancien code concernant le DBManager et amélioration du code

## Conception

L'extension Cadastre a été conçu et développé par la Société **3Liz**.
Site internet : https://www.3liz.com

## Auteurs

Michaël DOUCHIN
E-mail: info@3liz.com
Twitter 🐦 : https://twitter.com/kimaidou

## Contributeurs

* [Landry BREUIL](https://github.com/landryb) : notamment pour ses tests sur de gros volumes de données
  et les corrections sur certaines requêtes
* @fred-V13 pour l'aide sur la migration du plugin vers QGIS 3
* [Maël REBOUX](https://github.com/MaelREBOUX)
* [Étienne ROUVIN](https://github.com/EtienneRouvin)
* Christophe Masse

## Licence

GNU Public License (GPL) Version 2 ou supérieure

## Ressources

Les scripts d'import pour PostgreSQL proviennent de l'outil OpenCadastre (licence GPL). Ils ont été adaptés et améliorés pour leur utilisation dans ce plugin. Nos remerciements aux contributeurs.
Dépôt de sources : https://adullact.net/scm/viewvc.php/trunk/data/pgsql/?root=opencadastre

## English short description

This plugin helps users to use french land registry data ("cadastre") in QGIS. It is only useful in France for people having access to Cadastre data.

It is divided into modules :

* import data into database,
* load data in QGIS with appropriate symbology,
* search among data,
* export to PDF.
