# Données

## Edigéo

Les données sont disponibles en téléchargement sur https://cadastre.data.gouv.fr
Elles ne comportent pas de données sensibles.

Il existe un traitement dans la boîte à outils Processing pour télécharger automatiquement les feuilles suivant
une liste de code INSEE. Sinon, vous devez télécharger manuellement les fichiers, à l'échelle départemental par
exemple.

* La liste des codes INSEE peut-être `25047` ou `25047,25602`.

* Le filtre est optionnel :
  * S'il est vide, alors toutes les feuilles vont être téléchargées sur toutes les communes.
  * Si `AB,AD`, toutes les feuilles sur toutes les communes qui contiennent `AB` ou `AD` vont être téléchargées.
  * Si `AB,250470000D01`, toutes les feuilles `AB` ou la feuille `250470000D01` vont être téléchargées.

![Télécharger Edigeo](../processing/cadastre-telechargeur_edigeo_communal.jpg)

## Magic

Il faut y avoir un accès. Ce sont des données sensibles.

## OpenMagic

Ces données ne sont pas supportés par l'extension. N'hésitez pas à nous contacter.
