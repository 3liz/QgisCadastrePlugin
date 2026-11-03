URL_TOPO = "https://drive.opendata.craig.fr/s/opendata?path=%2Fadresse%2Ftopo"

URL_DOCUMENTATION = "https://docs.3liz.org/QgisCadastrePlugin/"

# Fields with the owners (names and addresses) in the layer of the parcelles: they are not published by QGIS Server,
# in WMS (GetFeatureInfo, popups of Lizmap) and in WFS. The module cadastre of Lizmap gives them,
# according to the rights of the user
OWNER_FIELDS = ("proprietaire", "proprietaire_info")

REGEX_BATI = "BATI"
REGEX_LOTLOCAL = "LLOC|D166"
REGEX_NBATI = "NBAT"
REGEX_PDL = "PDL"
REGEX_PROP = "PROP"
REGEX_TOPO = "TOPO"

IMPORT_MEMORY_ERROR_MESSAGE = "<b>ERREUR : Mémoire</b></br>"
"Veuillez recommencer l'import en baissant la valeur du "
"paramètre <b>'Taille maximum des requêtes INSERT'</b> selon la "
"documentation : {}/extension-qgis/configuration/#performances</br>".format(URL_DOCUMENTATION)

# Millésime
# Si changement de la valeur ci-dessous,
# penser à mettre à jour toutes les occurrences de l'année N-1 dans le fichier "import.md"
MAXIMUM_YEAR = 2026
MINIMUM_YEAR = 2012
