## Générer la documentation via SchemaSpy

Pour créer la documentation, il faut lancer un script en ligne de commande, sous distribution Linux, en passant les paramètres attendus.

Ce script se base sur l'outil SchemaSpy, qu'il faut donc télécharger et mettre dans le répertoire `schemaspy`, ainsi que sur le driver pour PostgreSQL.
Les binaires java peuvent être téléchargés ici:

* SchemaSpy: https://github.com/schemaspy/schemaspy/releases Par exemple `schemaspy-6.0.0.jar`
* Driver PostgreSQL: https://jdbc.postgresql.org/download.html Par exemple `postgresql-42.2.5.jar`

Une fois les deux fichiers jar mis dans le répertoire schemaspy, on peut lancer la génération de la documentation:

```bash
# Se placer dans ce repertoire contenant le script de génération
cd scripts/

# Lancer la commande avec les bons paramètres
./generation_documentation_schemaspy.sh -h localhost -p 5432 -d cadastre -u cadastre -s schema_cadastre -o "../docs/database"
```

Le mot de passe est demandé, puis la documentation est générée.
