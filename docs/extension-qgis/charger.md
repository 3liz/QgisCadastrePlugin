# Charger des données

Une fois les données importées dans la base, vous pouvez les importer dans QGIS via le menu 
**Charger les données**.

![alt](../media/cadastre_load_dialog.png)


## Base de données de travail

Il faut d'abord indiquer au plugin où récupérer les données :

* Choisir le **type de base** de données
* Choisir ensuite **la connexion** vers la base de donnée dans lequel l'import a été fait
* Si PostGIS, choisir **le schéma** contenant les données

## Thème

Puis on peut choisir un **thème** à utiliser pour la symbologie des couches :

* **Classique** : un thème proche du rendu de https://cadastre.gouv.fr
* **Orthophoto** : un thème adapté à un affichage par-dessus un fond orthophoto.

## Couches et filtres

* En cochant la case **Ajouter seulement Commune, sections, parcelles et bâti**, vous indiquez que vous 
  souhaitez ouvrir seulement ces couches dans QGIS (et pas les autres couches comme les bornes, les croix, 
  etc.)

* **Filtrer par expression sur les communes** : cette option vous permet de ne pas charger la totalité des 
  données, mais seulement celles qui correspondent aux communes filtrées via une expression. Vous devez 
  connaître la structure de la table **geo_commune** pour pouvoir réaliser ce filtre. Si l'expression est 
  invalide, alors le plugin chargera l'ensemble des données.

Attention à cette deuxième option, qui est expérimentale, et qui peut poser des soucis de performance. Pour 
information, cette option ajoute un filtre à chaque couche via une sous-requête. Une fois les couches 
chargées, vous pouvez consulter ce filtre via l'onglet *Général* de la boîte de dialogue des propriétés de 
chaque couche.

Exemples d'expression :

* `substr("geo_commune", 5, 6) LIKE '54033%'` -> les communes du département 54, direction 0, dont le code
  INSEE commence par 33
* `"tex2" IN ('AMIENS', 'ALLONVILLE')` -> le nom de la commune est AMIENS ou ALLONVILLE

## Notes

Pensez à **enlever les données cadastrales existantes dans votre projet QGIS** : Le plugin ne sait pas gérer 
la recherche et l'interrogation de données si on a plus qu'une version des couches parcelles, communes et 
sections dans le projet QGIS.

Enfin, cliquez sur le bouton **Charger les données** pour lancer le chargement.

## Charger une couche à partir d'une requête.

L'onglet **Charger une requête** vous donne la possibilité d'utiliser une requête SQL pour récupérer des 
données de la base. Pour cela, il faut bien connaître le modèle de la base de données et les spécificités
des données MAJIC. Cette fonctionnalité vise à évoluer pour proposer une liste de requêtes intéressantes pour 
l'exploitation des données cadastrales.

![alt](../media/cadastre_load_dialog_requete.png)

Une fois la connexion choisie, vous pouvez écrire le texte SQL dans le champ texte.

* La requête peut renvoyer des données spatiales ou seulement des données attributaires.
* Si un des champs retournés est une géométrie, vous devez spécifier son nom dans le champ texte dédié.
* Si vous utilisez une connexion PostGIS, il faut préfixer les tables avec le nom du schéma. Par exemple 
  `cadastre.geo_parcelle`.

La requête suivante retourne par exemple pour chaque code de parcelle la date de l'acte (on suppose que le 
schéma est cadastre). Vous pouvez ensuite utiliser une jointure QGIS pour faire le lien avec la couche 
`Parcelles` :

```sql
SELECT p.parcelle, p.jdatat AS date_acte
FROM cadastre.parcelle p
```

La requête suivante renvoie toutes les parcelles appartenant à des collectivités locales, avec la géométrie 
et les noms des propriétaires

```sql
SELECT gp.geo_parcelle,
string_agg(
   trim(
      concat(
         pr.dnuper || ' - ',
         trim(pr.dqualp) || ' ',
         trim(pr.ddenom)
      )
   ),'|'
) AS proprietaire,
gp.geom AS geom
FROM cadastre.geo_parcelle gp
JOIN cadastre.parcelle p ON gp.geo_parcelle = p.parcelle
JOIN cadastre.proprietaire pr ON p.comptecommunal = pr.comptecommunal
WHERE pr.dnatpr = 'CLL'
GROUP BY gp.geo_parcelle, gp.geom
```
