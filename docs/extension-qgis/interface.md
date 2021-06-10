# Interface

## La barre d'outil

![alt](../media/cadastre_toolbar.png)

La barre d'outil peut s'afficher ou se masquer à partir :

* du menu **Vue > Barres d'outils > Cadastre**
* d'un clic droit à côté d'une des barres d'outils de QGIS, et sélectionner **Cadastre**

Elle contient :

* Un outil pour **identifier une parcelle** sur la carte
* Des boutons qui reprennent les sous-menus du plugin : Importer, Charger, Rechercher, Exporter la vue,
  Configurer, À propos

Pour connaître l'action d'une des icônes, il suffit de laisser la souris un moment au-dessus pour voir
apparaître une bulle d'information.

### Identifier une parcelle

Pour avoir des informations complètes sur une parcelle, il faut avoir au préalable importé des données MAJIC
dans la base de données. Sinon, seules les informations principales issues de l'EDIGEO seront affichées et
certains boutons d'action sont désactivés.

Pour faire apparaître la fiche d'information d'une parcelle, il faut :

* activer l'outil **Identifier une parcelle** de la barre d'outil
* **Zoomer à une échelle** pour laquelle les parcelles sont visibles (à partir de 1/20 000).
* **Cliquer sur une des parcelles** de la carte.

La fenêtre d'identification s'affiche alors,

![alt](../media/cadastre_parcelle_info.png)

Elle présente plusieurs onglets :

* un onglet avec les **informations générales de la parcelle**
* un onglet avec les **propriétaires** de la parcelle
* un onglet avec les **subdivisions fiscales**
* un onglet avec les **locaux** et leurs informations détaillées

Ainsi qu'une zone contenant des **boutons d'action** :

* 2 boutons pour **exporter** au format PDF :
  - le **relevé parcellaire**
  - le **relevé de propriété** avec une option pour réalisé un export sur toutes les communes ou seulement à la commune de la parcelle
* 3 boutons pour **interagir avec l'objet géométrique** lié à la parcelle : centrer la carte sur la
  parcelle, zoomer sur la parcelle, ou sélectionner l'objet dans la couche
* Un dernier bouton pour **sélectionner dans la couche toutes les parcelles du propriétaire**



> Si vous n'avez pas importé de données FANTOIR, la commune de la parcelle ne sera pas affichée dans la
> fenêtre et l'adresse pourra être tronquée (de même pour les relevés exportés)

>Si vous n'avez pas de données MAJIC, seule les informations sur la parcelle (1er onglet) seront présentées.


### Exporter la vue

Dans la barre d'outil Cadastre, ainsi que dans le menu, vous pouvez exporter la vue courante de la carte en
PDF via le menu **Exporter la vue**.

Cette fonctionnalité s'appuie sur un **modèle de composeur d'impression**, configurable dans les options du
plugin (voir ci-dessus). Si vous n'avez pas configuré de composeur personnalisé, celui installé par le plugin
est utilisé.

> Cette fonctionnalité est basique, et ne gère pas pour l'instant les composeurs complexes, avec des tables
> attributaires et des configurations d'atlas.


## Le panneau de recherche

![alt](../media/cadastre_search_dialog.png)

### Principe

Le panneau de recherche propose des outils pour rechercher des parcelles via 3 entrées principales

* une recherche par **objet géographique** : commune, section, adresse et parcelles
* une recherche par **propriétaire**

Les différentes recherches seront détaillées dans les sous-chapitres suivants.

Pour afficher le panneau de recherche:

* Utiliser le menu **Cadastre > Outils de recherche** ou cliquer sur l'**icône loupe** de la barre d'outils

Une bulle d'information affiche la fonction des boutons au survol de la souris.

> Si la base de données ne contient aucune donnée MAJIC, alors les recherches par adresse et par propriétaire
> sont désactivés.

### Recherche de lieux

L'outil présente 3 listes déroulantes :

* **Commune**
* **Section**
* **Adresses**
* **Parcelles**

Il est possible de **sélectionner une entité** dans les listes :

* soit *à la souris* en cliquant sur la flèche pour ouvrir la liste déroulante puis sélectionner un item.
* soit en *tapant les premières lettres* et en sélectionnant l'item choisi dans la liste d'autocomplétion qui
  s'affiche alors. Il faut avoir au préalable vider le contenu de la liste déroulante.

Les listes déroulantes sont **hiérarchiques** :

* Lorsqu'on choisit une commune, la liste des sections est rafraîchie et ne montre que les sections de la
  commune choisie. La recherche d'adresse est aussi filtrée sur cette commune.
* lorsqu'on choisit une section, la liste des parcelles est rafraîchie et montre les parcelles sur la section.

Des **boutons d'actions** sont positionnés sous les 3 listes déroulantes et permettent de lancer l'action
choisie sur le dernier objet sélectionné dans les 3 listes :

* *Centrer sur l'objet* : la carte est déplacée vers l'objet sélectionné, mais l'échelle est conservée
* *Zoomer sur l'objet* : la carte est déplacée et mise à l'échelle pour afficher l'objet sélectionné
* *Sélectionner l'objet* : l'objet est sélectionné dans la couche de données correspondante (Communes,
  Sections ou Parcelles)

À côté des listes, un bouton **croix rouge** permet de remettre la liste à son état initial, c'est-à-dire sans
objet sélectionné. Par exemple, si on avait sélectionné une commune dans la première liste et une section
dans la seconde, on peut cliquer sur la croix rouge à côté de la section pour désélectionner la section dans
la liste. Ainsi si on utilise le bouton de Zoom, on zoomera sur la commune et non sur la section qui était
précédemment sélectionnée

Si une parcelle a été sélectionnée dans la liste **Parcelles**, il est possible d'**exporter le relevé
parcellaire** en cliquant sur le bouton *icône PDF* situé en bas à droite du bloc de recherche de lieux.
Le **PDF est généré et ouvert** avec le lecteur PDF par défaut du système.


### Recherche d'adresse

> Pour l'instant, cet outil ne fonctionne que si des données MAJIC sont dans la base, et si les données
> FANTOIR ont été importées. Si vous ne possédez pas de données FANTOIR dans votre lot de données MAJIC,
> vous pouvez le télécharger pour votre département ici (et relancer l'import Majic) :
> http://www.collectivites-locales.gouv.fr/mise-a-disposition-fichier-fantoir-des-voies-et-lieux-dits

Pour lancer une **recherche de parcelles par adresse**, il suffit :

* d'*entrer l'adresse cherchée*, sans le numéro de rue dans la liste **Adresse**.
* de cliquer sur le **bouton loupe** situé à côté de la liste, ou d'appuyer sur la **touche entrée**

La recherche est effectuée et la liste déroulante où vous avez tapé l'adresse à chercher est maintenant
rafraîchie et contient l'ensemble des résultats trouvés. Si une commune était sélectionnée dans la liste des
communes, la recherche d'adresse ne renvoie que les voies de cette commune.

Si des résultats ont été trouvés, on peut ensuite :

* **Sélectionner une adresse** dans la liste déroulante via la souris. Cela **rafraîchit la liste des
  parcelles** située en dessous.
* cliquer sur les boutons de **centrage, zoom et sélection**. Chaque action est lancée sur **l'ensemble des
  parcelles correspondantes** à l'adresse choisie
* Sélectionner une des parcelles dans la liste déroulante **Parcelles** et réutiliser les boutons d'action.
* Si une parcelle est sélectionnée, le bouton avec une icône PDF permet d'**exporter le relevé parcellaire**
  pour cette parcelle

Vous pouvez cliquer sur la croix rouge à côté de la recherche d'adresse pour désélectionner l'adresse choisie.

### Recherche de propriétaires

> Ce bloc de recherche ne fonctionne pas si aucune donnée MAJIC n'est présente dans la base

Le principe et le fonctionnement est le même que pour la recherche par adresse, avec les différences
suivantes :

* Un bouton est ajouté à côté de la liste des propriétaires pour **exporter le relevé de propriété** du
  propriétaire sélectionné dans la liste
* Le bouton d'**export du relevé parcellaire** est placé à côté de la liste *Parcelles*

Il est possible d'exporter le relevé de propriété pour les personnes qui ne possèdent pas de propriété non
bâtie.

### Utilisation du plugin QuickFinder pour chercher les parcelles

Vous pouvez installer le plugin QuickFinder pour préparer et utiliser des recherches sur différentes couches
cadastrales. Exemple de configuration intéressante :

* Ouvrir la boîte de dialogue de configuration du plugin : Menu *Extension / QuickFinder / Settings*
* Aller à l'onglet *Project Search*
* Cocher la case *Search in project layers*
* À côté du champ *QuickFinder file*, cliquer sur le bouton avec une icône "page" pour créer un nouveau
  fichier (en anglais, au survol du bouton : *Create a new QuickFinder file*). Enregistrer le fichier dans le
  répertoire du projet QGIS, et lui donner le même nom de fichier (par exemple "cadastre.qfts" pour un projet
  QGIS "cadastre.qgs")
* Cliquer sur le bouton "+" en vert pour ajouter une nouvelle recherche : cela ouvre une boite de dialogue
  *project search*. Configurer une recherche pour les parcelles :
  - *Search name* : Parcelles
  - *Layer*: Parcelles
  - *Field* : vous pouvez utiliser un champ, ou mieux une expression QGIS pour concaténer des informations,
    en cliquant sur le bouton "epsilon", par exemple :
  ```sql
  Concat(
    'COM ', "codecommune", ' / ',
    'SEC ', substr("idu", 7, 2), ' / ',
    'PAR ', substr("idu", 9, 4), ' / ',
    'ADR ', "adresse", ' / ',
    '', "proprietaire",
    ' @@', "codecommune"
  )
  ```
  (la partie avec @@ et le codecommune à la fin sont utiles si vous publiez le cadastre sur internet vers
  l'application Lizmap. Cela permet de filtrer les données)
  - *Geometry storage* : wkt
  - *Priority* : 1
  - *record entries* : laisser coché, cela va lancer la création des données de recherche et leur stockage
    dans le fichier QuickFinder

Une fois cette configuration effectuée, vous pouvez fermer les fenêtres QuickFinder, puis utiliser la barre
d'outil QuickFinder pour chercher des parcelles via leur code, le code commune, le code de section, ou bien
le nom des propriétaires.

## À propos

Le menu **Cadastre > À propos** ouvre une fenêtre d'information sur le plugin Cadastre : financeurs, auteur,
licence, dépôt de sources, etc.

Cette fenêtre est automatiquement affichée lors de la première utilisation du plugin, mais pas les fois
suivantes.

## Notes de version

Le menu **Cadastre > Notes de version** ouvre une fenêtre qui montre les changements effectués sur le plugin
Cadastre entre la version installée et la version précédente. Cette fenêtre est affichée automatiquement une
première fois lors de la montée de version.

## Les parcelles

Dans le modèle, plusieurs tables contiennent des informations sur les parcelles

* **geo_parcelle** : contient les parcelles EDIGEO

* **parcelle** : contient les données MAJIC liées aux parcelles cadastrales

* **parcelle_info** : contient une version consolidée des parcelles EDIGEO et MAJIC : la géométrie EDIGEO, et
  les informations résumées de la parcelle, dont les propriétaires (information séparées par la barre
  verticale | si la parcelle a plusieurs propriétaires)

Les champs parcelle.parcelle et geo_parcelle.geo_parcelle peuvent être utilisés pour les jointures entre la
table parcelle et la table geo_parcelle

L'identifiant **geo_parcelle** (ou parcelle) est unique et constitué comme suit :
*Année (4) + Département (2) + Direction (1) + Commune (3) + Préfixe (3) + Secteur (2) + Numéro de plan (4)*
soit **19 caractères**

![alt](../media/logo_3liz.png)
