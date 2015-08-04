===========================================
Plugin Cadastre - Documentation utilisateur
===========================================

:Auteurs: Michaël DOUCHIN - 3liz
:Date:   2013
:Copyright: CC-BY-SA
:Contact: info@3liz.com
:Résumé: Ce document contient la documentation du plugin Cadastre pour le logiciel QGIS.

.. image:: MEDIA/logo-qgis.jpg
   :align: center
   :width: 100px

.. meta::
  :keywords: documentation, QGIS, plugin, cadastre, 3liz

.. image:: MEDIA/cadastre_financeurs.png
   :align: center

Installation
===========================================

Le plugin Cadastre est dans les dépôts officiels du projet QGIS. Pour l'installer, il faut :

* **Lancer QGIS**
* Menu **Extension > Installer/Gérer les extensions**
* Onglet **Paramètres** > Vérfier que la case *Afficher les extensions expérimentales* est bien cochée
* Onglet **En obtenir plus** : chercher le plugin **cadastre**, le sélectionner et cliquer sur installer

Une fois le plugin installé, un nouveau menu **Cadastre** apparaît dans la barre de menu de QGIS. Il comporte les sous-menus suivants :

* **Importer des données**
* **Charger des données**
* **Outils de recherche**
* **Configurer le plugin**
* **Notes de version**
* **À propos**

Ces sous-menus sont détaillés dans les chapitres suivants.

Configurer le plugin
===========================================

Avant d'importer les premières données cadastrales dans la base de données, il faut au préalable configurer le plugin :

* Menu **Cadastre > Configurer le plugin** ou **icône outils** de la barre d'outil Cadastre

.. image:: MEDIA/cadastre_option_dialog.png
   :align: center


Interface
-----------

Les 2 boutons **Interface Cadatre** et **Interface QGIS** permettent d'ouvrir une aide pour appliquer une interface simplifiée adaptée à une utilisation de consultation du Cadastre.

A ce jour, QGIS ne permet pas de modifier dynamiquement l'interface via un plugin. Nous incorporerons cette fonctionnalité lorsque ce sera possible. En attendant, il faut donc le faire manuellement, comme expliqué dans la fenêtre d'aide.

Nom des fichiers MAJIC
-----------------------

Cette partie permet de spécifier comment sont appelés les fichiers MAJIC sur votre poste de travail. En effet, les conventions de nommage peuvent changer d'un département à l'autre. Souvent, les fichiers se terminent par une extension relative au département et à la direction, par exemple .800 pour les fichiers du département de la Somme.

.. note::  Il est important de bien configurer ces noms de fichiers avant votre premier import.

Si le plugin ne trouve pas les fichiers MAJIC pendant l'import, alors que vous aviez spécifié le bon répertoire d'import, un message vous avertira et vous proposera d'annuler l'import.

Répertoire temporaire
----------------------

Vous pouvez choisir le répertoire dans lequel les scripts seront copiés, et les fichiers décompressés. Choisisez un répertoire contenant assez de place pour stocker les fichiers temporaires, surtout si vous souhaitez charger des données volumineuses.

Ce répertoire est aussi celui dans lequel les **relevés parcellaires** et les **relevés de propriété** seront exportés.


Performances
-------------

Vous pouvez modifier dans ce groupe les options suivantes pour adapter le plugin aux performances de votre matériel :

* **Taille maximum des requêtes INSERT** : C'est le nombre total de requêtes INSERT lancées dans un groupe de modification ( BEGIN/COMMIT) . Vous pouvez baisser le chiffre jusqu'à 10000 si vous avez une machine légère et un gros volume de données à importer. Plus le chiffre est bas, plus l'import initial peut prendre du temps.

* **Stockage temporaire** : Le mode *MEMORY* est plus rapide, mais nécessite assez de mémoire vive pour stocker les données à traiter. Le mode *DEFAULT* est plus lent et adapté à des ordinateurs avec peu de mémoire vive.


Importer des données
===========================================

Cette boite de dialogue permet de réaliser un **import de données EDIGEO et MAJIC**.

.. image:: MEDIA/cadastre_import_dialog.png
   :align: center


Principe
------------

Le plugin permet l'import de données **MAJIC de 2012 à 2015 et des données EDIGEO** . Il est possible d'importer des données de manière incrémentale, **étape par étape**, ou bien d'importer **en une seule fois**.

Le plugin utilise pour cela la notion de **lot**. Un lot regroupe un **ensemble de données cohérent** pour votre utilisation. Par exemple, le lot peut être le code d'une commune, ou l'acronyme d'une communauté de commune. C'est une chaîne de 10 caractères maximum. Vous pouvez utiliser des chiffres ou des lettres.

Vous pouvez par exemple importer les données dans cette ordre :

* données EDIGEO de la commune A, lot "com_a"
* données EDIGEO de la commune B, lot "com_b"
* données MAJIC de la commune A, lot "com_a"
* données EDIGEO de la commune A, lot "com_a" (réimport et écrasement des données précédentes)
* données EDIGEO de la commune C, lot "com_c"

Il est donc important de conserver une liste des lots définis pendant les imports successifs, pour savoir ensuite quel lot utiliser si on souhaite écraser des données. Une version prochaine du plugin pourra intégrer un tableau récapitulatif des imports effectués dans une base de données pour faciliter le suivi des imports réalisés.


.. note::  Il est conseillé d'importer des données de millésime différents dans des bases de données ou des schémas PostGreSQL différents, car la structure peut changer d'un millésime à l'autre ( ajout de colonnes, modification de longueur de champs, etc.

Bases de données
-----------------

Deux **Systèmes de Gestion de Bases de Données** (SGBD) sont supportés par le plugin Cadastre :

* **PostGreSQL** et son extension spatiale **PostGIS**
* **Sqlite** et son extension spatiale **Spatialite**

Nous conseillons d'utiliser PostGreSQL pour des données volumineuses et pour gérer des accès multiples à la base de données.

Pour les bases de données **PostGIS**, il faut :

* avoir créé **une base de données** sur laquelle on a les droits en écriture, et activer l'extension PostGIS.
* avoir créé au préalable **une connexion QGIS** via le menu **Couches > Ajouter une couche PostGIS** vers cette base de données

Pour les bases de données **Spatialite**, l'interface d'import permet de créer une base de données vide et la connexion QGIS liée si nécessaire.


Les étapes d'importation
------------------------

Pour lancer l'importation, il faut bien avoir au préalable configuré les noms des fichiers MAJIC via le menu **Configurer le plugin**. Ensuite, on ouvre la boite de dialogue

* via la **barre d'outil Cadastre** , icône base de données
* via le menu **Cadastre > Importer des données**

On configure ensuite les options :

* Choisir **le type de base de données** : PostGIS ou Spatialite
* Choisir **la connexion**

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
 - Si vous ne possédez pas les données FANTOIR dans votre jeu de données MAJIC, nous conseillons vivement de les télécharger et de configurer le plugin pour donner le bon nom au fichier fantoir : http://www.collectivites-locales.gouv.fr/mise-a-disposition-fichier-fantoir-des-voies-et-lieux-dits

* Choisir la **version du format** en utilisant les flèches haut et bas

 - Seuls les formats de 2012 à 2015 sont pris en compte

* Choisir le **millésime des données**, par exemple 2012

* Choisir le **Lot** : utilisez par exemple le code INSEE de la commune.

* Activer ou désactiver la case à cocher **Corriger les géométries invalides** selon la qualité de votre jeu de données EDIGEO.

* Utiliser la barre de défilement de la fenêtre pour aller tout en bas et afficher tout le bloc texte de log situé sous la barre de progression.

* Lancer l'import en cliquant sur le bouton **Lancer l'import**


Le déroulement de l'import est écrit dans le bloc texte situé en bas de la fenêtre.

.. note::  Pendant l'import, il est conseillé de ne pas déplacer ou cliquer dans la fenêtre. Pour l'instant, le plugin n'intègre pas de bouton pour annuler un import.


Charger des données
===========================================

.. image:: MEDIA/cadastre_load_dialog.png
   :align: center


* Menu **Cadastre > Charger des données**
* Choisir le **type de base** de données
* Choisir ensuite **la connexion** vers la base de donnée dans lequel l'import a été fait
* Si PostGIS, choisir **le schéma** contenant les données
* Chosir **le thème** à appliquer

    - *Classique* : un thème proche du rendu de cadastre.gouv.fr
    - *Orthophoto* : un thème adapté à un affichage par dessus un fond orthophoto.

* **Enlever les données cadastrales existantes dans votre projet QGIS** : Le plugin ne sait pas gérer la recherche et l'interrogation de données si on a plus qu'une version des couches parcelles, communes et sections dans le projet QGIS.

* **Charger les données** en cliquant sur le bouton : une fois les données chargées, l'emprise de la carte est raffraîchie pour afficher l'ensemble des données (zoom sur l'ensemble des communes trouvées)


La barre d'outil Cadastre
===========================================

.. image:: MEDIA/cadastre_toolbar.png
   :align: center

La barre d'outil peut s'afficher ou se masquer à partir :

* du menu **Vue > Barres d'outils > Cadastre**
* d'un clic droit à côté d'une des barres d'outils de QGIS, et sélectionner **Cadastre**

Elle contient :

* Un outil pour **identifier une parcelle** sur la carte
* Des boutons qui reprennent les sous-menus du plugin : Importer, Charger, Rechercher, Configurer, A propos

Pour connaître l'action d'une des icônes, il suffit de laisser la souris un moment au-dessus pour voir apparaître une bulle d'information.


Indentifier une parcelle
--------------------------


Pour avoir des informations complètes sur une parcelle, il faut avoir au préalable importé des données MAJIC dans la base de données. Sinon, seules les informations principales issues de l'EDIGEO seront affichées et certains boutons d'action sont désactivés.

Pour faire apparaître la fiche d'information d'une parcelle, il faut:

* activer l'outil **Identifier une parcelle** de la barre d'outil
* **Zoomer à une échelle** pour laquelle les parcelles sont visibles (à partir de 1/20 000).
* **Cliquer sur une des parcelles** de la carte.

La fenêtre d'identification s'affiche alors,

.. image:: MEDIA/cadastre_parcelle_info.png
   :align: center

Elle présente:

* un bloc avec les **informations générales de la parcelle**
* un bloc avec les **propriétaires** de la parcelle
* une zone contenant des **boutons d'action**

 - 2 boutons pour **exporter** le **relevé parcellaire** et le **relevé de propriété** au format PDF
 - 3 boutons pour **interargir avec l'objet géométrique** lié à la parcelle : centrer la carte sur la parcelle, zoomer sur la parcelle, ou sélectionner l'objet dans la couche
 - Un dernier bouton pour **sélectionner dans la couche toutes les parcelles du propriétaire**

.. note::  Si vous n'avez pas importé de données FANTOIR, la commune de la parcelle ne sera pas affichée dans la fenêtre et l'adresse pourra être tronquée (de même pour les relevés exportés)

Le panneau de recherche
===========================================

.. image:: MEDIA/cadastre_search_dialog.png
   :align: center


Principe
----------

Le panneau de recherche propose des outils pour rechercher des parcelles via 3 entrées principales

* une recherche par **objet géographque** : commune et section
* une recherche par **adresse**
* une recherche par **propriétaire**

Les différentes recherches seront détaillées dans les sous-chapitres suivants.

Pour afficher le panneau de recherche:

* Utiliser le menu **Cadastre > Outils de recherche** ou cliquer sur l'**icône loupe** de la barre d'outils

Une bulle d'information affiche la fonction des boutons au survol de la souris.

.. note::  Si la base de données ne contient aucune donnée MAJIC, alors les outils de recherche par adresse et par propriétaire sont désactivés.


Recherche de lieux
--------------------

L'outil présente 3 listes déroulantes :

* **Commune**
* **Section**
* **Parcelles**

Il est possible de **sélectionner une entité**:

* soit *à la souris* en cliquant sur la flèche pour ouvrir la liste déroulante puis sélectionner un item.
* soit en *tapant les premières lettres* et en sélectionnant l'item choisi dans la liste d'autocomplétion qui s'affiche alors.

Les listes déroulantes sont **hiérarchiques** :

* Lorsqu'on choisit une commune, la liste des sections est raffraîchie et ne montre que les sections de la commune choisie.
* lorsqu'on choisit une section, la liste des parcelles est raffraîchie.

Des **boutons d'actions** sont positionnés sous les 3 listes déroulantes et permettent de lancer l'action choisie sur le dernier objet sélectionné dans les 3 listes :

* *Centrer sur l'objet* : la carte est déplacée vers l'objet sélectionné, mais l'échelle est conservée
* *Zoomer sur l'objet* : la carte est déplacée et mise à l'échelle pour afficher l'objet sélectionné
* *Sélectionner l'objet* : l'objet est sélectionné dans la couche de données correspondante ( Communes, Sections ou Parcelles)

A côté des 3 listes, un bouton **croix rouge** permet de remettre la liste à son état initial, c'est-à-dire sans objet sélectionné. Par exemple, si on avait sélectionné une commune dans la premier liste et une section dans la seconde, on peut cliquer sur la croix rouge à côté de la section pour désélectionner la section dans la liste. Ainsi si on utilise le bouton de Zoom, on zoomera sur la commune et non sur la section qui était précédemment sélectionnée

Si une parcelle a été sélectionnée dans la liste **Parcelles**, il est possible d'**exporter le relevé parcellaire** en cliquant sur le bouton *icône PDF* situé en bas à droite du bloc de recherche de lieux. Le **PDF est généré et ouvert** avec le lecteur PDF par défaut du système.


Recherche d'adresse
--------------------

.. note::  Pour l'instant, cet outil ne fonctionne que si des données MAJIC sont dans la base, et si les données FANTOIR ont été importées. Si vous ne possédez pas de données FANTOIR dans votre lot de données MAJIC, vous pouvez le télécharger pour votre département ici (et relancer l'import Majic): http://www.collectivites-locales.gouv.fr/mise-a-disposition-fichier-fantoir-des-voies-et-lieux-dits

Pour lancer une **recherche de parcelles par adresse**, il suffit:

* d'*entrer l'adresse cherchée*, sans le numéro de rue dans la liste **Adresse**.
* de cliquer sur le **bouton loupe** situé à côté de la liste, ou d'appuyer sur la **touche entrée**

La recherche est effectuée et la liste déroulante où vous avez tapé l'adresse à chercher est maintenant raffraîchie et contient l'ensemble des résultats trouvés.

Si des résultats ont été trouvés, on peut ensuite :

* **Sélectionner une adresse** dans la liste déroulante via la souris. Cela **raffraîchit la liste des parcelles** située en dessous.
* cliquer sur les boutons de **centrage, zoom et sélection** . Chaque action est lancée sur **l'ensemble des parcelles correspondantes** à l'adresse choisie
* Sélectionner une des parcelles dans la liste déroulante **Parcelles** et réutiliser les boutons d'action.
* Si une parcelle est sélectionnée, le bouton avec une icône PDF permet d'**exporter le relevé parcellaire** pour cette parcelle


Recherche de propriétaires
---------------------------

.. note::  Ce bloc de recherche ne fonctionne pas si aucune donnée MAJIC n'est présente dans la base

Le principe et le fonctionnement est le même que pour la recherche par adresse, avec les différences suivantes :

* Un bouton est ajouté à côté de la liste des propriétaire pour **exporter le relevé de propriété** du propriétaire sélectionné dans la liste
* Le bouton d'**export du relevé parcellaire** est placé à côté de la liste *Parcelles*

Il est possible d'exporter le relevé de propriété pour les personnes qui ne possèdent pas de propriété non bâtie.


À propos
===========================================

Le menu **Cadastre > A propos** ouvre une fenêtre d'information sur le plugin Cadastre : financeurs, auteur, licence, dépôt de sources, etc.

Cette fenêtre est automatiquement affichée lors de la première utilisation du plugin, mais pas les fois suivantes.

Notes de version
==================

Le menu **Cadastre > Notes de version** ouvre une fenêtre qui montre les changements effectués sur le plugin Cadastre entre la version installée et la version précédente. Cette fenêtre est affichée automatiquement une première fois lors de la montée de version.


Vidéos de démonstration
========================

Pour faciliter la prise en main, vous pouvez consulter les vidéos en ligne :

* Import et chargement : https://vimeo.com/75004889
* Recherche : https://vimeo.com/74807532



Modèle de données
===================

Les liens suivant permettent de voir comment sont organisées les données cadastrales dans la base de données (tables, contraintes, etc.)

* **Documentation détaillée** : http://demo.3liz.com/plugin_cadastre/SchemaSpyGUI/index.html
* **Image du modèle** : http://demo.3liz.com/plugin_cadastre/schema_cadastre.png
* **Liste simplifiée des tables** : http://demo.3liz.com/plugin_cadastre/schema_cadastre_postgresql_autodoc.html



.. image:: MEDIA/logo_3liz.png
   :align: center
