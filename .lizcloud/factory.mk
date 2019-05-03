#
# Makefile for building/packaging qgis for lizmap hosting
#

VERSION=$(shell ./metadata_key ../metadata.txt version)

main:
	echo "Makefile for packaging infra components: select a task"

PACKAGE=qgis_cadastre
FILES = composers server forms icons interface scripts styles templates *.py *.qrc icon.png metadata.txt README.md
PACKAGEDIR=cadastre

build/$(PACKAGEDIR):
	@rm -rf build/$(PACKAGEDIR)
	@mkdir -p build/$(PACKAGEDIR)


.PHONY: package
package: build/$(PACKAGEDIR)
	@echo "Building package $(PACKAGE)"
	@cd .. &&  cp -rLp $(FILES) .lizcloud/build/$(PACKAGEDIR)/
	$(FACTORY_SCRIPTS)/make-package $(PACKAGE) $(VERSION) $(PACKAGEDIR) ./build

version:
	@echo $(VERSION)
