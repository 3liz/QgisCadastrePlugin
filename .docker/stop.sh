#!/usr/bin/env bash

echo 'Stopping/killing containers'
docker compose -f docker-compose.yml kill
docker compose -f docker-compose.yml rm -f
