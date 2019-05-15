#
# Makefile for building/packaging qgis for 3liz
#

ifndef FABRIC
FABRIC:=$(shell [ -e .fabricrc ] && echo "fab -c .fabricrc" || echo "fab")
endif

VERSION=$(shell ./metadata_key ../metadata.txt version)

main:
	echo "Makefile for packaging infra components: select a task"

PACKAGE=qgis_cadastre
FILES = ../composers ../filters ../forms ../icons ../interface ../scripts ../styles ../templates ../*.py ../*.qrc ../icon.png ../metadata.txt ../README.md ../CHANGELOG.md


build/cadastre:
	@rm -rf build/cadastre
	@mkdir -p build/cadastre


.PHONY: package
package: build/cadastre
	@echo "Building package $(PACKAGE)"
	@cp -rLp $(FILES) build/cadastre/
	$(FABRIC) package:$(PACKAGE),versiontag=$(VERSION),files=cadastre,directory=./build

