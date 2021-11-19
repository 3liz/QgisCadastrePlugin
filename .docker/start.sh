#!/usr/bin/env bash
export $(grep -v '^#' .env | xargs)

WITH_QGIS=${1:-noqgis}

if [ "$WITH_QGIS" = with-qgis ]; then
  PROFILE="qgis"
else
  PROFILE="db"
fi

docker-compose --profile ${PROFILE} up -d --force-recreate --remove-orphans
echo "Wait 10 seconds"
sleep 10
if [ "$WITH_QGIS" = with-qgis ]; then
  echo "Installation of the plugin ${PLUGIN_NAME}"
  docker exec -t qgis sh -c "qgis_setup.sh ${PLUGIN_NAME}"
  echo "Setup the database link from QGIS"
  docker cp postgis_connexions.ini qgis:/tmp
  docker exec qgis bash -c "cat /tmp/postgis_connexions.ini >> /root/.local/share/QGIS/QGIS3/profiles/default/QGIS/QGIS3.ini"
fi
echo "Containers are running"
