
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

#schemaspy:
#	@rm -rf docs/database/ && mkdir docs/database/
#	{ \
#		cd .docker; \
#		export DB_COMMAND="./install_db_and_wait.sh"; \
#		docker compose --profile=schemaspy up  \
#			--quiet-pull \
#			--abort-on-container-exit \
#			--exit-code-from schemaspy; \
#		docker compose --profile=schemaspy down -v; \
#	}


