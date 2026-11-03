
# Overridable
export POSTGIS_VERSION ?= 15-3
export POSTGIS_IMAGE_TAG ?= $(REGISTRY_PREFIX)postgis:$(POSTGIS_VERSION)

# We need to start the database when running tests locally
start-db:
	@echo "Starting database"
	@cd .docker && docker compose up -d --wait

stop-db:
	@echo "Stopping database"
	@cd .docker && docker compose down -v


run-db-command: 
	{ \
		cd .docker; \
		export DB_COMMAND="${DB_COMMAND}"; \
		docker compose --profile=dbrunner up \
			--quiet-pull \
			--abort-on-container-exit \
			--exit-code-from db-runner; \
		docker compose --profile=dbrunner down -v; \
	}

# Documentation of the database in docs/database, with SchemaSpy, like in the plugin road network:
# the schema cadastre is created by an import of the test data with the plugin (see .docker/schemaspy_import.py)
schemaspy:
	@rm -rf docs/database/ && mkdir docs/database/
	@# The schemaspy container runs with its own user (java, uid 1000): the output directory must be writable
	@chmod 777 docs/database/
	{ \
		cd .docker; \
		docker compose --profile=schemaspy run --rm --quiet-pull schemaspy-import \
			&& docker compose --profile=schemaspy run --rm --quiet-pull schemaspy; \
		status=$$?; \
		docker compose --profile=schemaspy down -v; \
		exit $$status; \
	}
