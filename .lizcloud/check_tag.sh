#!/bin/bash

VERSION=$1
METADATA=$(cat cadastre/metadata.txt | grep "version=" |  cut -d '=' -f2)

if [ "$METADATA" != "$VERSION" ];
then
    echo "The metadata file has ${METADATA} while the requested tag is ${VERSION}."
    echo "Aborting"
    exit 1
fi

echo "The metadata.txt is synced with ${VERSION}"
exit 0
