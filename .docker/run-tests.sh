#!/bin/bash

set -e

VENV=/src/.docker-venv-$QGIS_VERSION

if [ ! -e $VENV ]; then
    echo "Creating virtualenv"
    python3 -m venv $VENV --system-site-packages
fi

echo "Installing required packages..."
$VENV/bin/pip install -q -U --no-cache-dir -r requirements/tests.txt

cd tests && $VENV/bin/pytest -v $@

