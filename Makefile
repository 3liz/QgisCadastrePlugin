SHELL:=bash

PYTHON_MODULE=cadastre


-include .localconfig.mk

#
# Configure
#

# Check if uv is available
$(eval UV_PATH=$(shell which uv))
ifdef UV_PATH
ifdef VIRTUAL_ENV
# Always prefer active environment
ACTIVE_VENV=--active
endif
RUN=uv run $(ACTIVE_VENV)
endif


REQUIREMENT_GROUPS= \
	dev \
	tests \
	lint \
	packaging \
	doc \
	$(NULL)

.PHONY: update-requirements

REQUIREMENTS=$(patsubst %, requirements/%.txt, $(REQUIREMENT_GROUPS))

update-requirements: $(REQUIREMENTS)

# Require uv (https://docs.astral.sh/uv/) for extracting
# infos from project's dependency-groups
requirements/%.txt: uv.lock
	@echo "Updating requirements for '$*'";\
	uv export --format requirements.txt \
		--no-annotate \
		--no-editable \
		--no-hashes \
		--only-group $* \
		-q -o requirements/$*.txt

#
# Static analysis
#

LINT_TARGETS=$(PYTHON_MODULE) $(EXTRA_LINT_TARGETS)

lint::
	@ $(RUN) ruff check --preview --output-format=concise $(LINT_TARGETS)

lint-fix:
	@ $(RUN) ruff check --preview --fix $(LINT_TARGETS)

format:
	@ $(RUN) ruff format $(LINT_TARGETS)

typecheck:
	@ $(RUN) mypy $(LINT_TARGETS)
	@ $(RUN) mypy --python-version 3.10 tests

scan:
	@ $(RUN) bandit -r $(PYTHON_MODULE) $(SCAN_OPTS)

#
# Tests
#

test:
	$(RUN) pytest -v tests/


ifdef REGISTRY_URL
REGISTRY_PREFIX=$(REGISTRY_URL)/
else
REGISTRY_PREFIX=3liz/
endif 


##
## Test using docker image
##
QGIS_VERSION ?= 3.40
QGIS_IMAGE_REPOSITORY ?= ${REGISTRY_PREFIX}qgis-platform
QGIS_IMAGE_TAG ?= $(QGIS_IMAGE_REPOSITORY):$(QGIS_VERSION)

# Overridable in .localconfig.mk
export QGIS_VERSION
export QGIS_IMAGE_TAG
export UID=$(shell id -u)
export GID=$(shell id -g)

docker-test:
	export DB_COMMAND=true; \
	cd .docker; \
	docker compose --profile=qgis up \
	--quiet-pull \
	--abort-on-container-exit \
	--exit-code-from qgis; \
	docker compose --profile=qgis down -v;

include database.mk

