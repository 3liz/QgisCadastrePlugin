===========================================
Plugin Cadastre - Documentation utilisateur
===========================================

:Author: Michaël DOUCHIN - 3liz
:Date:   2013
:Copyright: CC-BY-SA
:Contact: info@3liz.com
:organization: 3liz
:abstract: Ce document contient la documentation du plugin Cadastre pour le logiciel QGIS.

.. meta::
  :keywords: documentation, QGIS, plugin, cadastre, 3liz


Installation
===========================================

Le plugin Cadastre est dans les dépôts officiels du projet QGIS. Pour l'installer, il faut :

* Lancer QGIS
* Menu Extension > Installer/Gérer les extensions
* Onglet Paramètres > Vérfier que la case "Afficher les extensions expérimentales" est bien cochée
* Onglet "En obtenir plus" > Chercher le plugin "cadastre" , le sélectionner et cliquer sur installer

Une fois le plugin installé, un nouveau menu **Cadastre** apparaît dans la barre de menu de QGIS. Il comporte les sous-menus suivants :

* Importer des données
* Charger des données
* Outils de recherche
* Configurer le plugin
* À propos

Ces sous-menus sont détaillés dans les chapitres suivants.

Configurer le plugin
===========================================

Avant d'importer les premières données cadastrales dans la base de données, il faut au préalable configurer le plugin :

* Menu Cadastre > Configurer le plugin

Interface
-----------

Les 2 boutons **Interface Cadatre** et **Interface QGIS** permettent d'ouvrir une aide pour appliquer une interface simplifiée adaptée à une utilisation de consultation du Cadastre.

A ce jour, QGIS ne permet pas de modifier dynamiquement l'interface via un plugin. Nous incorporerons cette fonctionnalité lorsque ce sera possible. En attendant, il faut donc le faire manuellement, comme expliqué dans la fenêtre d'aide.

Nom des fichiers MAJIC
-----------------------

Cette partie permet de spécifier comment sont appelés les fichiers MAJIC sur votre poste de travail. En effet, les conventions de nommage peuvent changer d'un département à l'autre. Souvent, les fichiers se terminent par une extension relative au département et à la direction, par exemple .800 pour les fichiers du département de la Somme.

Note::

   Il est important de bien configurer ces noms de fichiers avant votre premier import.

Répertoire temporaire
----------------------

Vous pouvez choisir le répertoire dans lequel les scripts seront copiés, et les fichiers décompressés. Choisisez un répertoire contenant assez de place pour stocker les fichiers temporaires, surtout si vous souhaitez charger des données volumineuses.

Ce répertoire est aussi celui dans lequel les **relevés parcellaires** et les **relevés de propriété** seront exportés.


Importer des données
===========================================

Cette boite de dialogue permet de réaliser un import de données EDIGEO et MAJIC.

Principe
------------

Le plugin permet l'import de données MAJIC 2012 et 2013, et des données EDIGEO (selon les possibilités de la librairie ogr2ogr ). Il est possible d'importer des données de manière incrémentale, étape par étape, ou bien d'importer en une seule fois.

Le plugin utilise pour cela la notion de **lot**. Un lot regroupe un ensemble de données cohérent pour votre utilisation. Par exemple, le lot peut être le code d'une commune, ou l'acronyme d'une communauté de commune. C'est une chaîne de caractères de longueur 10 maximum.

Vous pouvez par exemple importer les données dans cette ordre :

* données EDIGEO de la commune A, lot "001"
* données EDIGEO de la commune B, lot "002"
* données MAJIC de la commune A, lot "001"
* données EDIGEO de la commune A, lot "001" (réimport et écrasement des données précédentes)
* données EDIGEO de la commune C, lot "003"

Il est donc important de conserver une liste des lots définis pendant les imports successifs. Une version prochaine du plugin pourra intégrer un tableau récapitulatif des imports effectués dans une base de données.

Bases de données
-----------------

Deux SGBD (Systèmes de Gestion de Bases de Données) sont supportés par le plugin Cadastre :

* **PostGreSQL** et son extension spatiale **PostGIS**
* **Sqlite** et son extension spatiale **Spatialite**

Nous conseillons d'utiliser PostGreSQL pour des données volumineuses et pour gérer des accès multiples à la base de données.

Pour les bases de données **PostGIS**, il faut :

* avoir créé **une base de données** sur laquelle on a les droits en écriture, et activer l'extension PostGIS.
* avoir créé au préalable **une connexion QGIS** via le menu **Couches > Ajouter une couche PostGIS** vers cette base de données

Pour les bases de données **Spatialite**, l'interface d'import permet de créer une base de données vide et la connexion QGIS liée si nécessaire.

Les étapes d'importation
------------------------

Pour lancer l'importation, il faut bien avoir au préalable configuré les noms des fichiers MAJIC via le menu *Configurer le plugin*. Ensuite, on ouvre la boite de dialogue

* via la **barre d'outil Cadastre** , icône base de données
* via le menu **Cadastre > Importer des données**

On configure ensuite les options :

* Choisir le type de Base de données : PostGIS ou Spatialite
* Choisir la connexion

 - Pour Postgis, on peut ensuite **choisir un schema**, ou en **créer un nouveau**
 - Pour Spatialite, on peut **créer une nouvelle base de données**

* Choisir le répertoire contenant les **fichiers EDIGEO** :

 - On peut sélectionner le **répertoire parent** qui contient l'ensemble des sous-répertoires vers les communes : le plugin ira chercher les fichiers de manière récursive.
 - seuls les fichiers **zip** et **tar.bz2** sont pour l'instant gérés

* Choisir la **projection source** des fichiers EDIGEO et la **projection cible** désirée

* Choisir le **numéro du Département**, par exemple : 80 pour la Somme
* Choisir le **numéro de la Direction**, par exemple: 0

* Choisir le répertoire contenant **les fichiers MAJIC**

 - Comme pour EDIGEO, le plugin ira chercher les fichiers dans les répertoires et les sous-répertoires et importera l'ensemble des données.

* Choisir la **version du format** en utilisant les flèches haut et bas

 - Dans cette version beta, seul les formats 2012 et 2013 sont pris en compte

* Choisir le **millésime des données**, par exemple 2012

* Choisir le **Lot** : utilisez par exemple le code INSEE de la commune.

* Lancer l'import en cliquant sur le bouton **Lancer l'import**


Le déroulement de l'import est écrit dans le bloc texte situé en bas de la fenêtre.

Note::

   Pendant l'import, il est conseillé de ne pas déplacer ou cliquer dans la fenêtre. Pour l'instant, le plugin n'intègre pas de bouton pour annuler un import.


Charger des données
===========================================



* Menu **Cadastre > Charger des données**
* Choisir le **type de base** de données
* Choisir ensuite **la connexion** vers la base de donnée dans lequel l'import a été fait
* Si PostGIS, choisir **le schéma** contenant les données
* Chosir **le thème** à appliquer

    - *classique* : un thème proche du rendu de cadastre.gouv.fr
    - *Orthophoto* : un thème adapté à un affichage par dessus un fond orthophoto.

* Option **Remplacement des couches ?** : Cette option permet de choisir le comportement du chargement des données en fonction des couches déjà existantes dans le projet QGIS

 - *Conserver* : signifie qu'on ne remplace pas la couche déjà présente dans QGIS par la couche correspondante trouvée dans la base de données
 - *Remplacer* : signifie qu'on supprime la couche déjà présente pour la remplacer par la couche correspondante dans la base de données

* **Charger les données** en cliquant sur le bouton : une fois les données chargées, l'emprise de la carte est raffraîchie pour afficher l'ensemble des données (zoom sur l'ensemble des communes trouvées)


La barre d'outil Cadastre
===========================================

La barre d'outil peut s'afficher ou se masquer à partir :

* du menu Vue > Barres d'outils > Cadastre
* d'un clic droit à côté d'une des barres d'outils de QGIS, et sélectionner "Cadastre"

Elle contient :

* Un bouton pour identifier une parcelle sur la carte
* Des boutons qui reprennent les sous-menus du plugin : Importer, Charger, Rechercher, Configurer, A propos

Indentifier une parcelle
--------------------------

Cette fonctionnalité fonctionne mal si les données majic ne sont pas présentes dans la base

* Zoomer sur la carte pour arriver jusqu'à une échelle qui permet de voir les parcelles
* Activer l'outil d'identification en cliquant sur le bouton dans la barre d'outil Cadastre
* Cliquer sur une des parcelles : une fenêtre s'ouvre avec les informations résumées de la parcelles et des boutons :

    - Exporter le relevé parcellaire ou le relevé de propriété
    - Centrer, Zoomer, Sélectionner la parcelle
    - Sélectionner toutes les parcelles du propriétaire


Le panneau de recherche
===========================================

* Menu Cadastre > Outils de recherche
* Passer la souris au dessus des boutons permet d'afficher une info-bulle décrivant la fonction


Recherche de lieux
--------------------

* Les 3 listes déroulantes Commune, Section et Parcelle permettent d'affiner progressivement la recherche
* On peut taper le début du texte recherché dans une des listes, et un menu d'auto-complétion s'affiche
* En face de chaque liste, le bouton "Croix rouge" permet de supprimer la sélection et de revenir en mode non sélectionné
* Les boutons Centrer, Zoomer et Sélectionner agissent sur la dernière liste qui contient une sélection.

    - Par exemple, si on a sélectionné une section, mais pas de parcelle, le bouton Zoomer fait un zoom sur toute la section
    - Si on a ensuite choisi une parcelle, on zoome sur cette parcelle en cliquant sur Zoomer
    - Si on clique ensuite sur la croix rouge en face de la liste parcelle, on supprime la sélection, et le bouton "Zoom" permet alors de rezoomer sur la section


Recherche d'adresse
--------------------

Pour l'instant, ne fonctionne que si des données MAJIC sont dans la base

* Entrer la fin du nom de l'adresse cherchée, sans la mention de rue, boulevard, chemin, etc. : par exemple "du cange" pour "Boulevard du Cange"

    - la version 1 gérera mieux la recherche d'adresse

* Si des résultats ont été trouvés, on peut ensuite

    - Sélectionner une adresse dans la liste déroulante
    - cliquer sur les boutons de centrage, zoom et sélection pour sélectionner toutes les parcelles correspondantes à l'adresse sélectionnée
    - Sélectionner une des parcelles de cette adresse via la liste déroulante "Parcelle", puis utiliser de nouveau les outils de zoom, centrage et sélection sur cette parcelle sélectionnée
    - Si une parcelle est sélectionnée, le bouton avec une icône PDF permet d'exporter le relevé parcellaire pour cette parcelle

Recherche de propriétaires
---------------------------

Ne fonctionne pas si aucune donnée MAJIC n'est présente dans la base

* On écrit les premières lettres du propriétaire recherché dans le champ "Nom"
* Si des résultats ont été trouvé, on peut choisir un des propriétaires dans la liste déroulante (le champ nom est éditable, mais est aussi une liste déroulante)
* On peut utiliser les boutons de Zoom, Centrage et sélection comme pour la recherche de lieux ou d'adresse
* On peut exporter le relevé de propriété via le bouton PDF situé à droite de la liste "Nom"
* On peut ensuite sélectionner une parcelle, et réutiliser les boutons Centrer, Zoomer, Sélectionner, ou bien exporter le relevé parcellaire via le bouton PDF situé à droite de la parcelle sélectionnée


A propos
===========================================

* Menu Cadastre > A propos

Cette boite de dialogue fournit des informations sur le plugin : financeurs, développeurs, licence


Vidéos de démonstration
========================

Pour faciliter la prise en main, vous pouvez consulter les vidéos en ligne :

* Import et chargement : https://vimeo.com/75004889
* Recherche : https://vimeo.com/74807532

