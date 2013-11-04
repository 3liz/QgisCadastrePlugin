Description
===========

Le plugin Cadastre a été conçu pour faciliter l'utilisation des données cadastrales dans QGIS. Plusieurs modules aident l'utilisateur à importer des données, les afficher dans QGIS, faire des recherches et imprimer les relevés :

* L'**import de données cadastrales**, MAJIC et EDIGEO, dans une base de données **PostGreSQL/PostGIS** ou **Sqlite/Spatialite**.
* Un **module de chargement** permet d'ajouter automatiquemet l'ensemble des couches cadastrales dans QGIS, avec la possibilité de choisir le style appliqué.
* Un **panneau de recherche** offre la possibilité de rechercher des parcelles par adresse, propriétaire ou par situation (commune, section) et de naviguer vers ces parcelles cadastrales.
* Un **outil d'identification** permet d'afficher les données liées à une parcelle en cliquant sur le polygone représentant la parcelle.
* Il est possible enfin d'exporter les données sous forme de **relevés parcellaires** et de **relevés de propriété**.


Financeurs
==========

La réalisation du plugin Cadastre a été financée par :

* L'Agence de Développement et  d'Urbanisme du Grand Amiénois ( http://www.aduga.org )
* Le Conseil Régional de Picardie ( http://www.picardie.fr )
* L'Union Européenne ( http://europa.eu/index_fr.htm )
* Le  Fonds Européen de Développement Régional de Picardie ( http://www.picardie-europe.eu )

Conception
==========

Le plugin 3liz a été conçu et développé par la Société 3LIZ.
Site internet : http://www.3liz.com

Auteurs
=======

Michaël DOUCHIN
email: mdouchin@3liz.com
twitter : @kimaidou

Licence
=======

GPL V3
Lien : http://www.gnu.org/licenses/gpl.html

Ressources
==========

Les scripts d'import pour PostGreSQL proviennent de l'outil OpenCadastre (licence GPL). Ils ont été adaptés et améliorés pour leur utilisation dans ce plugin. Nos remerciement aux contributeurs.
Dépôt de sources :  https://adullact.net/scm/viewvc.php/trunk/data/pgsql/?root=opencadastre

English short description
==========================
This plugins helps users to use french land registry data ("cadastre") in QGIS. It is only usefull in France for people having access to Cadastre data.
It is divided into modules :

* import data into database,
* load data in QGIS with appropriate symbology,
* search among data,
* export to PDF.
