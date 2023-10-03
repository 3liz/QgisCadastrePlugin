# Installation du module

Une fois que Lizmap Web Client est installé et fonctionnel, vous pouvez installer le module **cadastre** et
l'extension QGIS Serveur **cadastre**.

Depuis la version 1.5.2 du module, il est souhaitable de l'installer avec [Composer](https://getcomposer.org),
le système de paquet pour PHP. Si vous ne pouvez pas, ou si vous utilisez
lizmap 3.3 ou inférieur, passez à la section sur l'installation manuelle.

## Extension QGIS Serveur

Pour que le module soit fonctionnel, il faut installer l'extension QGIS Serveur **Cadastre**.
Il s'agit de la même extension que celle sur QGIS Bureautique. Veuillez regarder la
[documentation QGIS](https://docs.qgis.org/3.16/en/docs/server_manual/plugins.html) sur l'utilisation des extensions côté
serveur.

Nous recommandons l'usage de [QGIS-Plugin-Manager](https://pypi.org/project/qgis-plugin-manager/) pour l'installation et
la mise à jour des extensions côté serveur.

## Le module

### Installation automatique avec Composer et lizmap 3.4 ou plus

* dans `lizmap/my-packages`, créer le fichier `composer.json` s'il n'existe pas
  déjà, en copiant le fichier `composer.json.dist`, qui s'y trouve.

```bash
cd lizmap/my-packages/
cp -n composer.json.dist composer.json
```

* en ligne de commande, dans le répertoire `lizmap/my-packages/`, tapez :

```bash
composer require "lizmap/lizmap-cadastre-module"
```

* puis dans le répertoire `lizmap/install/` :

Si vous utilisez **Lizmap 3.6** ou plus, lancez d'abord les commandes :


```bash
php configurator.php cadastre
```

Enfin pour **Lizmap 3.4 à 3.6 et plus**, lancez les scripts d'installation :

```bash
cd ../install
php installer.php
./clean_vartmp.sh
./set_rights.sh
```

### Installation manuelle dans lizmap 3.3 ou 3.4 sans Composer

* Télécharger l'archive ZIP de la dernière version du module cadastre dans
  [la page des releases de Github](https://github.com/3liz/lizmap-cadastre-module/releases).
* Extraire l'archive et copier le répertoire `cadastre` dans le répertoire `lizmap/lizmap-modules/` de l'application
  Lizmap Web Client.
* Éditer le fichier `lizmap/var/config/localconfig.ini.php` et modifier la section `[modules]` en ajoutant la ligne
  `cadastre.access=2` sous la section :

```ini
[modules]
cadastre.access=2
```

* puis dans le répertoire `lizmap/install/`, lancer les commandes suivantes :

```bash
php installer.php
./clean_vartmp.sh
./set_rights.sh
```
