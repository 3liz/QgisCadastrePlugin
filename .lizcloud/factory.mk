#
# Makefile for building/packaging qgis for lizmap hosting
#
.PHONY: files

VERSION=$(shell ./metadata_key ../cadastre/metadata.txt version)

main:
	echo "Makefile for packaging infra components: select a task"

PACKAGE=qgis_cadastre
FILES = cadastre/* README.md
PACKAGEDIR=cadastre

clean:
	@rm -rf build/$(PACKAGEDIR)

build/$(PACKAGEDIR):
	@rm -rf build/$(PACKAGEDIR)
	@mkdir -p build/$(PACKAGEDIR)
	@echo "Building package $(PACKAGE)"
	@cd .. &&  cp -rLp $(FILES) .lizcloud/build/$(PACKAGEDIR)/

files: clean build/$(PACKAGEDIR)

package: files
	$(FACTORY_SCRIPTS)/make-package $(PACKAGE) $(VERSION) $(PACKAGEDIR) ./build

version:
	@echo $(VERSION)
