# Changelog

## Unreleased

## 1.19.1 - 2024-03-06

* Correction de l'export PDF avec une utilisation QGIS > 3.30

## 1.19.0 - 2023-12-14

* Correction de l'import des données sans les données MAJIC
* Augmentation de la version minimum de QGIS à 3.22 au lieu de 3.18 qui était une non LTR

## 1.18.2 - 2023-10-17

* Utilisation du code commune de la parcelle dans parcelle_info MAJIC
* Correction des DROP d'indexes
* Correction de la clé primaire de la table proprietaire
* Ajout d'un index sur le champ voie de la table parcelle_info
* Import - Amélioration des performances pour l'EDIGEO
  L'import des données EDIGEO via ogr2ogr n'utilisait plus l'option `PG_USE_COPY`

## 1.18.1 - 2023-09-27

* Corrections SQL

## 1.18.0 - 2023-08-02

* Support du MAJIC 2023 (contribution de @landryb et @MaelREBOUX)

## 1.17.3 - 2023-02-07

* bugfix - La colonne RC TEOM au tableau des propriétés baties est le champ `bateom` et pas `baeteom`

## 1.17.2 - 2023-01-26

* bugfix - La colonne RC TEOM au tableau des propriétés baties est le champ `baeteom` et pas `mvltieomx` de `pevtaxation`
* bugfix - homogénéisation des adresses de propriétaires
* Tableau des indivisions comme sous partie du tableau des propriétaires
* Indivisions pour un tiers

## 1.17.1 - 2022-12-15

* bugfix - Correction du compte communal abrégé affiché dans les relevés
* Ajout de la colonne RC TEOM au tableau des propriétés baties
* bugfix - Server - Accès à la fiche HTML complète sans les infos sensibles des propriétaires

## 1.17.0 - 2022-11-25

* Server - Ajout de la carte au relevé parcellaire
* Server - Support du relevé parcellaire pour un tiers et réduction de la fiche HTML

## 1.16.1 - 2022-10-19

* Correction d'un bug si le dossier de stockage temporaire dans les préférences n'existait plus

## 1.16.0 - 2022-09-05

* Export des relevés - Ajout d'une option "Les relevés sont destinés à des tiers"
  qui permet de ne pas faire figurer la date et le lieu de naissance des propriétaires dans les PDF.
* Annulation d'une fonctionnalité de la version 1.14.0 concernant l'ajout automatique des noms courts.
  Il y a un problème sur Lizmap Web Client https://github.com/3liz/lizmap-web-client/issues/2985

## 1.15.1 - 2022-08-12

* Identification de la parcelle (MAJIC): ajout du statut 'Parcelle bâtie' dans la fiche (issue du champ `gparbat`).
  Cette modification ne nécessite pas de réimport pour être fonctionnelle.
* Table `parcelle_info`: ajout du champ `parcelle_batie` (Oui/Non) à partir du champ `gparbat` (MAJIC).
  Cette modification nécessite un réimport des données, ou un remplacement manuel de la table `parcelle_info`.

## 1.15.0 - 2022-08-02

* Support du MAJIC 2022

## 1.14.2 - 2022-05-10

* Correction de l'import Edigeo si les parcelles sont trop grandes (en Guyane par exemple, ticket https://github.com/3liz/QgisCadastrePlugin/issues/206)
* Correction d'une erreur Python si l'utilisateur utilise QGIS Process

## 1.14.1 - 2022-03-21

* Correction d'une régression côté serveur pour le logging

## 1.14.0 - 2022-03-09

* Ajout de la colonne `contenance` à la table `parcelle_info` même lorsqu'il n'y a pas de données MAJIC
* Correction de la recherche par propriétaire lorsque le schéma Postgres nécessite des doubles quotes
* Ajout d'une clé primaire à la table `geo_label`
* Modification de la clé primaire de la table `geo_batiment` et `geo_subdsect` pour être de type entier
* Ajout des noms courts sur les couches et les groupes pour rendre le projet valide par défaut lors d'une publication
  sur Lizmap
* Refactorisation du code côté QGIS Serveur
* Mise à jour de https://docs.3liz.org

## 1.13.5 - 2021-12-14

* Amélioration du message d'erreur sur le fichier n'est pas être décompressé, ticket #339
* Correction de la table `commune_majic` pour les millésimes 2019 à 2021, ticket #333

## 1.13.4 - 2021-12-06

* Ajout du financeur de la métropole de Clermont-Ferrand
* Correction d'une régression suite à la version 1.13.3 sur les champs `*_bipevla`

## 1.13.3 - 2021-11-18

* Corrections orthographiques
* Correction sur les "Locaux : Informations détaillées"
* Correction des exports PDF depuis le panneau de recherche
* Amélioration du message d'erreur s'il n'y a pas assez de mémoire sur l'ordinateur
* Amélioration de la documentation concernant les paramètres au niveau global de l'extension

## 1.13.2 - 2021-08-25

* Mise à jour de https://docs.3liz.org/QgisCadastrePlugin/ pour les financeurs de l'extension
* Correction d'une erreur si l'extension est utilisée pour la première fois
* Correction d'une erreur possible pour ouvrir les fichiers en UTF-8 par défaut

## 1.13.1 - 2021-08-10

* Correction d'un chemin dans le script standalone concernant l'export

## 1.13.0 - 2021-08-10

* Ajout du support MAJIC 2021 (Contribution de Maël Reboux)
* Refactorisation du code interne à l'extension
* Mise à jour de la documentation https://docs.3liz.org/QgisCadastrePlugin/

## 1.12.1 - 2021-06-24

* Correction du chargement de l'extension avec QGIS < 3.10

## 1.12.0 - 2021-06-21

* Correction de l'export propriétaire à une commune
* Mise à jour de la documentation sur le module Lizmap

## 1.11.1 - 2021-06-01

* Sauvegarde et restoration des paramètres de la dernière base utilisée dans l'interface graphique

## 1.11.0 - 2021-05-21

* Correction d'un espace dans l'adresse dans les propriétés baties, non baties
* Correction d'une erreur SQL lors de la consultation des infos parcelle sur QGIS 3.16 bureautique et serveur
* Ajout du support QGIS 3.16
* Ajout d'un bouton pour ouvrir l'aide depuis le menu principal d'aide de QGIS
* Ajout de la recherche d'un propriétaire
  * par nom d'usage ou de naissance
  * par ville
* Ajout d'un téléchargeur Edigéo communal dans la boite à outils Processing
* Documentation https://docs.3liz.org/QgisCadastrePlugin/
  * Mise de la documentation au format MkDocs
  * Intégration de la documentation du module Lizmap
  * Ajout de la documentation automatique concernant les traitements Processing
  * Ajout de la documentation concernant la base de données avec SchémaSpy
* Ajout d'une infrastructure de tests

## 1.10.2 - 2020-12-10

* Correction sur la documentation
* Ajout d'une table de matières sur https://docs.3liz.org/QgisCadastrePlugin/
* Afficher un message dans les logs si un fichier SQLite est manquant
* Prévenir l'utilisateur sur les fichiers bz2 lors de l'import des fichiers Édigéo.

## 1.10.1 - 2020-11-05

* Ajout de la documentation de la base de données sur https://docs.3liz.org/QgisCadastrePlugin/
* Petites corrections sur la publication de l'extension

## 1.10.0 - 2020-11-04

* Import - Optimisation de l'import Spatialite et de l'affichage du temps passé
* Ajout de l'extraction de détails sur les propriétaires (indivisions)
* Widget "Outils de Recherche" : Ajout du bouton Infos parcelle
* Dialogue "infos parcelle" : Ajout des actions imprimer / copier /sauvegarder des infos des onglets
* Révision barre d'outils (position actions) et réécriture code menu / barre d'outils
* Fix - bug connexion (relevé parcellaire, première instanciation)

## 1.9.0 - 2020-09-07

* Documentation
    * Support de QGIS 3.10 LTR #240
    * Précisions sur les versions PostgreSQL et PostGIS supportées
* Support du millésime MAJIC 2020 #239
* Améliorations et corrections
    * Suppression des doublons de communes et de sections dans les données EDIGEO #196
    * Unités foncières : suppression des enregistrements sans comptes communaux #221
    * Correction d'un bogue dans l'affichage des informations d'une parcelle si le nom de la voie est nul #207
    * Correction d'un bogue affectant le chargement de la couche des parcelles si on utilise du filtrage sur le code de commune #229
    * Maintenance sur le code Python

## 1.8.1 - 2019-10-21

Corrections de bugs essentiellement

* Import - EDIGEO: amélioration des performances geo_batiment_parcelle
* Import - MAJIC: correction bug d'encodage
* Import MAJIC - garder vexen pour compatibilité Spatialite
* Spatialite - Correction des identifiants parcelle, voie et local00 dans la table local10
* Fiche parcellaire - résumé: ajout de coalesce sur l'adresse
* [BUGFIX] Use of QgsMapLayer.VectorLayer in getLayerFromLegendByTableProps
* suppression de code spécifique QGIS 2
* Création couche parcelle_info OK

## 1.8.0 - 2019-09-20

**IMPORTANT**
À partir de cette version seule la version QGIS LTR sera supportée. Pour cette version il s'agit de la version 3.4.x

Nouveautés:

* Prise en charge des évolutions MAJIC 2019 (voir #192 pour les détails). Noter la création de 2 nouvelles tables.
* Précisions sur les versions QGIS, PostgreSQL / PostGIS et Spatialite supportées (#197)
* Mise à jour de la documentation de la structure de la base de données (#204)


## 1.7.1 - 2019-06-06

* Refactorize code for server and Qgis 3+
* Ajouts et mises à jour de tables domaine
* Correction valeur compte communal
* Ajout inspireid
* Amélioration de plugin Server
* Nouvelle table de nomenclature natvoi
* Correction identifiants
* trim code de nature de voie
* [Serveur] Add GetCapabilities method to server CADASTRE service
* Creation d'un provider QgsProcessing

## 1.7.0

* Fiche parcellaire - Ajout des informations des propriétaires, subdivisions et locaux
* Fiche parcelle - Ajout de la surface spatiale bâtie
* Export (version QGIS 2): Ajout d'un script python pour exporter les relevés PDF via ligne de commande
* Fix - Général: Amélioration de la récupération d'informations sur les couches (hôte, base de données, etc.)
* Fix - Import: Suppression de table temporaire ll si besoin
* Fix - Export: relevé de propriété: dédoublonnage des comptes communaux exportés en PDF
* Fix - Correction d'un bug d'encodage
* Divers - Ajout des derniers financeurs dans le dialogue "A propos"

## 1.6.2

* Général - suppression de code inutile suite à la migration QGIS3
* Import - Correction de parcelles en doublons dû au lien avec geo_subdsect
* Export PDF - Correction d'un bug et restauration de l'affichage des propriétaires

## 1.6.1

* Correction de bug sur l'interrogation de propriétaire suite à la gestion des dates en texte
* Correction d'un bug d'encodage sur message d'erreur de requête SQL
* Import - Utilisation d'entiers longs pour les surfaces de parcelle_info (corrige le bug pour les très grandes parcelles)
* Import - Ajout du support du millésime 2018

## 1.6.0

* Compatibilité du plugin avec QGIS 3. Les version compatibles avec QGIS 2 seront des versions de correction uniquement, avec un numéro en 1.5.*

## 1.5.2

* Import - Transformation des champs date en texte pour le MAJIC, par respect de la donnée source
* Correction d'un bug de la 1.5.1 avec QFileDialog, QFileInfo et BaseError manquant

## 1.5.1

* Import - MAJIC : correction de bug si dates mauvaises (30 fév par ex)
* Import - Support partiel des données EDIGEO en projection IGNF
* Import - Correction d'un bug de non remplissage des parcelles si correspondance geo_subdsect manquant
* Import - EDIGEO : conversion en date des champs de geo_subdsect seulement si format correct #120

## 1.5.0

* Chargement - Ajout de couches via requête SQL
* Import - Ajout de la nomenclature pour ccocac
* Import - Correction sur la table pivot geo_batiment_parcelle: restriction par intersection
* Rechercher - Déplacement de la recherche d'adresse sous celle par parcelle
* Chargement - correction d'un bug sur l'ajout dans les groupes Cadastre
* Import - Ajout du support de MAJIC 2017
* Recherche - Support de l'autocomplétion pour les adresses et les propriétaires
* Recherche - Intégration des adresses dans la recherche de lieux
* Import - Correction du bug de récupération des propriétés bâties
* Import/Identification - contournement du bug d'encodage sur requête pour QGIS 2.18.10 et >
* Identification - correction du bug sur chargement de projet QGIS
* Import - Majic : import des propriétaires si et seulement si dnupro est non vide
* Import - Lieudits: utilisation de tous les champs tex
* Recherche - Réapplication de l'ordre dans les listes déroulantes (sections, parcelles)
* BDD - Possibilité de se connecter avec un connexion utilisant un service PostgreSQL

## 1.4.1

* Import/Chargement - correction de bug pour Spatialite sur génération parcelle_info

## 1.4.0

* Menu - Suppression du menu Cadastre et déplacement dans le menu Extensions
* Barre d'outil - Modification de l'icône d'identification (merci @pasqual )
* Structure bdd - Généralisation des codes départements et direction dans les identifiants
* Structure bdd - Parcelles: consolidation des infos propriétaires dans une nouvelle table parcelle_info
* Import - Correction d'un bug de remplissage de geo_sym si ptcanv_id.sym est NULL
* Import - MAJIC: Filtrage des données importées selon département et direction: on peut utiliser le fichier FANTOIR national
* Import - Ajout du support de MAJIC 2016
* Import - Edigeo : amélioration de la jointure de geo_parcelle ave geo_subdsect
* Import - Correction des doublons sur les parcelles (dus au lien geo_subdsect)
* Import - Edigeo: amélioration des performances pour tpoint, tline, tsurf
* Import - Augmentation de la limite max pour le code direction - fixes #94
* Import - Utilisation directe des fichiers sources sans copie préalable
* Import - Suppression des contraintes de taille dans les champs
* Import - Déplacement des scripts SQL d'import et nettoyage
* Import - Fantoir recommandé lors de l'import MAJIC && lien de téléchargement ajouté
* Import - Correction des parcelles dupliquées si plusieurs sous-sections
* Import - correction du bug empêchant la création de base sqlite sous 2.16 - #83
* Chargement - Ajout du filtre par expression sur les communes (expérimental)
* Chargement - possibilité de charger seulement les couches principales
* Chargement - Séparation des étiquettes et des données en groupes & désactivation des couches mineures
* Chargement - Mise à jour et amélioration des styles
* Chargement - Correction de bug sur QgsMapLayer non défini
* Chargement - Styles : masquage de la couche Tronçons de routes aux petites échelles
* Export - Ajout d'un nouveau menu pour exporter la vue courante en PDF
* Export - ajout d'une carte en 1ère page pour le relevé parcellaire
* Export - Ouverture automatique du répertoire après export PDF multiple
* Recherche - La recherche par commune et section utilise le lot pour éviter les doublons si plusieurs départements
* Serveur - Ajout de la capacité "server" pour le plugin

## 1.3.0

* Import - MAJIC : support du millésime 2015. La structure a été un peu modifiée. Il faut réaliser l'import dans un nouveau schéma PostgreSQL ou une nouvelle base de données Spatialite. Un script de migration de la structure est disponible pour PostgreSQL pour ceux qui préfèrent conserver le schéma actuel (faites une sauvegarde avant !) : /.qgis2/python/plugins/cadastre/scripts/plugin/updates/update_structure_postgis_from_1.2.0_to_1.3.0.sql
* Import - Ajout d'un système de création des tables manquantes ( pour les montées de version )
* Edigeo - Ajout des objets TRONROUTE dans la table geo_tronroute
* Import - Éviter l'import des parcelles EDIGEO avec un idu NULL
* Plugin - Suppression de la contrainte de version maximum de QGIS

## 1.2.0

* Import - Amélioration des performances d'imports pour Spatialite
* Import - Ajout d'une option pour activer/désactiver la validation des géométries
* Import - Suppression de l'outil de réparation des multipolygones sur une bdd déja importée (phase de transition terminée )
* Interface - pour l'interface Cadastre, ajout des boutons WMS/WFS - fixes #53
* Export - Debogage des exports PDF vides pour la 2.8 - fixes #60
* Identification parcelle - amélioration interne de l'outil (pas visible dans l'interface)
* Import - Prise en compte des fichiers MAJIC sans contenus dans les premières lignes

## 1.1.1

* Ajout de la compatibilité avec QGIS 2.8

## 1.1.0

* Options - Ajout du menu Vue/Décorations dans l'interface Cadastre
* Chargement - La couche Unités foncières est décochée par défaut
* Import - Ajout des scripts pyogr pour compatibilité QGIS 2.6
* Ajout d'une boite de dialogue d'information lors du 1er chargement. Visible via le menu Cadastre > Notes de version
* Import/Recherche/Export - Modification du lien entre les parcelles EDIGEO et MAJIC (même identifiant unique pour les 2)
* Import - exhaustivité des données de propriétaire MAJIC - fix #47
* Import - Conserver l'orientation des symboles lors d'imports successifs - fix #46
* Import - Correction des géométries invalides - fix #43
* Import - Correction des multipolygones sous Windows - fixes #44
* Info parcelle - option de filtre commune pour le relevé de propriété - fix #42
* Chargement - Ajout des TRONROUTE_ID pour les étiquettes des noms voies - bug #40
* Chargement - Suppression des étiquettes abbérantes - fix #41
* Import - Ajout des unités foncières pour PostGIS (refonte de la requête)
* Import - MAJIC : ajout de la compatibilité des fichiers 2014
* Import - EDIGEO : ajout de la table boulon_id
* Chargement - correction du bug #38 : minidump sous Windows

## 1.0.0

* Import - débogage import PostgreSQL sous Windows
* Recherche - Meilleure gestion de la désactivation des modules de recherche
* Import - MAJIC : possibilité de lancer l'import même si fichiers MAJIC manquants
* Import - Vérifications sur les données MAJIC avant import - bug #37
* Import - Meilleure gestion des chemins des fichiers sources
* Import - Création de bdd spatialite différente selon la version de spatialite - bug #30
* Export - Débogage de l'export PDF pour QGIS 2.4 - bug #36
* Import : MAJIC - arrêt de l'import si aucun fichier trouvé
* Import - Modifications mineures d'interface
* Import - meilleure gestion des imports EDIGEO via ogr2ogr.py au lieu de ogr2ogr.exe (compatibilité MAC + détection des erreurs)


## 0.9.9

* Import - correction de certaines erreurs d'import des MULTIPOLYGONES (PostgreSQL et Spatialite)

## 0.9.8.1

* Export - debug : suppression des 'print' dans le code

## 0.9.8

* Log détaillé : https://github.com/3liz/QgisCadastrePlugin/compare/0.9.7...0.9.8
* Export des relevés - améliorations de mises en forme des données
* Export - propriétaires : ajout de l'époux pour les femmes mariées EX: MME DURAND/Sophie Yvette EP DUPONT Jean
* Export - propriétaires : déplacement des dates et lieu de naissance à droite
* Export - Suppression des zéros au début du numéro de plan et de voirie
* Export - prop. baties : Suppression du code commune au début du numéro INVAR
* Export - Sommes prop. baties : Ajout de zéros si valeurs nulles (au lieu de cases vides)
* Export - prop. non baties : Séparation des HA A CA pour la contenance
* Export - prop. non baties : Calcul de la fraction exo si applicable
* Export - Sommes prop. non baties : Ajout de la somme des contenances
* Export - Pied de page : Ajout de la mention "Ce document est donné à titre indicatif..."
* Export - Suppression de la mention "Expérimental"
* Import - Import des MULTI-POLYGONES et correction de données existantes - bug #29

## 0.9.7

* Log détaillé : https://github.com/3liz/QgisCadastrePlugin/compare/0.9.6...0.9.7
* Documentation - ajout des liens vers la documentation en ligne - bug #3
* Export - recupération infos parcelles : ajout du filtre par département - bug #27
* Export - correction du pourcentage exoneration pour les propriétés non baties - bug #26
* Import - validation préalable des entrées du formulaire d'import - bug #25
* Chargement - ajout des chemins SVG cadastre sans écraser les précédents - bug #19
* Identification - debogage outil si Parcelles n'est pas la couche active
* Export - nettoyage du nom du PDF exporté pour compatibilité Windows - bug #23
* Import - sup contrainte de type sur surface des parcelles - bug #20
* Import - suppression de la contrainte de longueur de champ pour l'attribut tex
* Chargement - gestion d'erreur si pas de table trouvée dans la bdd
* Recherche - correction largeur listes déroulantes (windows) - bug #22
* Export - ouverture des PDF compatible freeBSD - bug #21

## 0.9.6

* Log détaillé : https://github.com/3liz/QgisCadastrePlugin/compare/0.9.5...0.9.6
* Import - actualisation liste des tar.bz2 après décompression de zip
* Documentation - mise à jour
* Recherche/export - meilleurs résultats si fantoir non importé - bug #18
* Export multiple - barre de progression et ouverture du dossier contenant
* Export - optimisation - bug #2
* Chargement - réutilisation du groupe Cadastre si présent - bug #14
* Identification - réinitialisation de l'outil identifier au chargement
* Spatialite - debogage base de données si chemin contient des espaces - bug #17
* Recherche - adresse/propriétaire : gestion des apostrophes - bug #12
* Import - remplacement CREATE TABLE IF NOT EXISTS - bug #13
* Meilleur comportement des outils de recherche sur ouverture d'un (nouveau) projet

## 0.9.5

* Chargement - bug #8: pas d'erreur si présence de couches plugin OpenLayers
* Recherche/Identification - réactivation des outils sur chargement d'un projet Cadastre - #9
* Recherche - Lieux : Liste des sections ordonnées par code
* Import - correction bug Spatialite import relations (*.vec) - bug #7
* Import - Gestion des erreurs de suppression de fichier après extraction - bug #5
* Import - modifications des scripts pour gestion arrondissements (ex: Marseille)

## 0.9.4

* Import - bouton Créer une base Spatialite grisé si aucune connection dans QGIS

## 0.9.3

* Documentation - ajout d'une documentation (avec copies d'écran)
* Chargement - remplacement du panneau par une fenêtre
* Configurer - ajout d'un option pour le type de stockage temporaire de Spatialite
* Import - spatialite : remove disablespatialindex
* Import - Amélioration des imports consécutifs (indexes, erreurs spatialites, etc.)
* Majic - import récursif
* Général - ajout d'un menu d'aide et rédaction de l'aide
* Import - restriction des imports à 2012 et 2013
* Export - amélioration des calculs des sommes
* A propos - correction coquille
* Recherche/Export - gestion des propriétaires sur plusieurs communes
* About - ajout du lien vers le dépôt Github
* A propos - modification de l'ordre des financeurs

## 0.9.2

* Import - suppression des indexes avant ajout Majic incrémental
* Général - rédaction du README et metadata
* Import - amélioration de l'import Spatialite
* A propos - ajout du remerciement aux auteurs d'OpenCadastre
* Général - affichage de la fenêtre 'A propos' à la 1ère utilisation
* Option - ajout de l'aide pour changer d'interface
* Import - amélioration des scripts
* Import - La Direction est bloquée : entier entre 0 et 5
* Chargement - renommage des couches && fermeture des légendes
* Recherche/Identification - désactivation des outils nécessitant MAJIC si pas de données

## 0.9.1

* Chargement - ajout du style Orthophoto
* Import - modification interface du choix du type de bdd
* Import - les fichiers EDIGEO non zip/tar.bz2 sont bien pris en compte
* Import - Ajout d'un bouton pour créer une base de données Spatialite vide
* Toolbar - Ajout import/charger/recherche/about + modification icône
* Styles - Classique : amélioration tsurf

## 0.9.0

* Correction de régression de 0.8.9 : indentification parcelle et recherche propriétaire

## 0.8.9

* Amélioration du support Spatialite : import, recherche, export
* General - désactivation Spatialite si pyspatialite non présent

## 0.8.8

* Import - ajout d'une option pour configurer le nombre de ligne INSERT max
* Propriétaires - debug affichage vide pour les personnes morales
* Recherche - ajout des stopwords pour les natvoi
* Indentification parcelle - textes en lecture seule + code section || dnupla
* Import majic - Vérfication unicité des lotslocaux

## 0.8.7

* Export - changement du calcul du revenu cadastral non bati + numéro voirie
* Import - possibilité d'importer un fichier MAJIC seul
* Import - Ajout des contraintes à la fin d'un import MAJIC seul
* Import - modification mineure nomenclature EDIGEO
* Import - Compatibilité avec les fichiers MAJIC 2013
* Import MAJIC - ajout de quelques colonnes (bati, nbat)
* Export - Calcul des sommes pour bati et nbat
* Recherche/export - ajout du lieu et date de naissance pour les propriétaires
* Chargement - Création d'un groupe 'Cadastre' et chargement des couches dans ce groupe
* Chargement - mise à jour auto des listes déroulantes suite à un import

## 0.8.6

* Recherche/Export - Ajout ccocom dans comptecommunal (dédoublonnage)
* Import - MAJI : suppression des caractères non imprimables et de contrôle

## 0.8.5

* Import - debug utilisation mémoire lors de la leture des fichiers majic volumineux
* Recherche - suppression du bug si ouverture panneau avec couches hors cadastre
* Recherche/Indenfitication - Correction du Zoom/Centrer si reprojection à la volée
* Recherche - adaptation remplissage table voie pour gérer le multi-commune

## 0.8.4

* Import - Modification dynamique de la projection des tables edigeo
* Recherche - Amélioration recherche d'adresse via table voie (fantoir)
* Chargement - utilisation de Times New Roman pour les étiquettes

## 0.8.3

* Import - majic: suppressions de caractères \x00
* Import - debug Windows sur chemins vers scripts contraintes

## 0.8.2

* Import - debug du nom du schéma "a" précédemment écrit en dur (régression 0.8.1)
* Import - utilisation du serial pour geo_commune, geo_parcelle et geo_section : évite les erreurs de rétablissement des clés primaires

## 0.8.1

* Import - possibilité d'import vers une base de données distante
* Import - possibilité d'importer en plusieurs passes
