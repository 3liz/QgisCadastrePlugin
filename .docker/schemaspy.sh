#!/usr/bin/env bash

rm -rf "${PWD}"/../docs/database
mkdir "${PWD}"/../docs/database

chmod 777 -R "${PWD}"/../docs/database
docker run \
  -v "${PWD}/../docs/database:/output" \
  --network="host" \
  etrimaille/schemaspy-pg:latest \
  -t pgsql-mat \
  -dp /drivers \
  -host localhost \
  -db qgistest \
  -u "${USER}" \
  -p "${PASSWORD}" \
  -port 5432 \
  -s cadastre
