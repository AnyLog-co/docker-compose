#----------------------------------------------------------------------
# The following provides make commands for support functions
# - Remote-GUI
# - Grafana
# - Postgres
# - Mongodb
#----------------------------------------------------------------------
#!/bin/Makefile
$(info LOADING MAKEFILE)

export SERVICE ?= ""

export CONTAINER_CMD := $(shell if command -v podman >/dev/null 2>&1; then echo "podman"; else echo "docker"; fi)
export DOCKER_COMPOSE_CMD := $(shell if command -v podman-compose >/dev/null 2>&1; then echo "podman-compose"; \
	    elif command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; else echo "docker compose"; fi)

SUPPORT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
export CONTAINER_NAME=$(shell grep -m1 '^container_name: ' "$(SUPPORT_DIR)/$(SERVICE)/docker-compose.yml" | cut -d= -f2- | tr -d '"\r')

all: help

dry-run: ## Generate docker-compose.yml for all (or one) service configs
	@if [ "$(SERVICE)" = "" ]; then \
	    for dir in remote-gui grafana postgres mongodb; do \
	        echo "→ Building compose for $$dir"; \
	        bash $(SUPPORT_DIR)docker_compose_builder.sh $(SUPPORT_DIR)$$dir/configs.yaml $(SUPPORT_DIR)$$dir/docker-compose.yml; \
	    done; \
	elif [ -d "$(SUPPORT_DIR)$(SERVICE)" ]; then \
	    echo "→ Building compose for $(SERVICE)"; \
	    bash $(SUPPORT_DIR)docker_compose_builder.sh $(SUPPORT_DIR)$(SERVICE)/configs.yaml $(SUPPORT_DIR)$(SERVICE)/docker-compose.yml; \
	else \
	    echo "ERROR: No config directory found for service '$(SERVICE)'"; \
	    $(MAKE) help; \
	    exit 1; \
	fi

up: ## Start service(s) — use SERVICE=<name> to target one (gui, grafana, psql/postgres, mongo/mongodb)
	@if [ "$(SERVICE)" = "" ]; then \
	    $(MAKE) up-gui ; \
	    $(MAKE) up-dashboard ; \
	    $(MAKE) up-psql ; \
	    $(MAKE) up-mongo ; \
	elif [ "$(SERVICE)" = "remote-gui" ] || [ "$(SERVICE)" = "gui" ]; then \
	    $(MAKE) up-gui ; \
	elif [ "$(SERVICE)" = "grafana" ]; then \
	    $(MAKE) up-dashboard ; \
	elif [ "$(SERVICE)" = "postgres" ] || [ "$(SERVICE)" = "psql" ]; then \
	    $(MAKE) up-psql ; \
	elif [ "$(SERVICE)" = "mongodb" ] || [ "$(SERVICE)" = "mongo" ]; then \
	    $(MAKE) up-mongo ; \
	elif [ -d "$(SUPPORT_DIR)/$(SERVICE)" ] ; then \
	    $(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)/$(SERVICE)/docker-compose.yml up -d ; \
	else \
	    echo "ERROR: Unsupported service '$(SERVICE)'"; \
	    $(MAKE) help; \
	    exit 1; \
	fi

down: ## Stop service(s) — use SERVICE=<name> to target one
	@if [ "$(SERVICE)" = "" ]; then \
	    $(MAKE) down-gui ; \
	    $(MAKE) down-dashboard ; \
	    $(MAKE) down-psql ; \
	    $(MAKE) down-mongo ; \
	elif [ "$(SERVICE)" = "remote-gui" ] || [ "$(SERVICE)" = "gui" ]; then \
	    $(MAKE) down-gui ; \
	elif [ "$(SERVICE)" = "grafana" ]; then \
	    $(MAKE) down-dashboard ; \
	elif [ "$(SERVICE)" = "postgres" ] || [ "$(SERVICE)" = "psql" ]; then \
	    $(MAKE) down-psql ; \
	elif [ "$(SERVICE)" = "mongodb" ] || [ "$(SERVICE)" = "mongo" ]; then \
	    $(MAKE) down-mongo ; \
	elif [ -d "$(SUPPORT_DIR)/$(SERVICE)" ] ; then \
	    $(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)/$(SERVICE)/docker-compose.yml down ; \
	else \
	    echo "ERROR: Unsupported service '$(SERVICE)'"; \
	    $(MAKE) help; \
	    exit 1; \
	fi

clean: ## Stop and remove volumes for service(s) — use SERVICE=<name> to target one
	@if [ "$(SERVICE)" = "" ]; then \
	    $(MAKE) clean-gui ; \
	    $(MAKE) clean-dashboard ; \
	    $(MAKE) clean-psql ; \
	    $(MAKE) clean-mongo ; \
	elif [ "$(SERVICE)" = "remote-gui" ] || [ "$(SERVICE)" = "gui" ]; then \
	    $(MAKE) clean-gui ; \
	elif [ "$(SERVICE)" = "grafana" ]; then \
	    $(MAKE) clean-dashboard ; \
	elif [ "$(SERVICE)" = "postgres" ] || [ "$(SERVICE)" = "psql" ]; then \
	    $(MAKE) clean-psql ; \
	elif [ "$(SERVICE)" = "mongodb" ] || [ "$(SERVICE)" = "mongo" ]; then \
	    $(MAKE) clean-mongo ; \
	elif [ -d "$(SUPPORT_DIR)/$(SERVICE)" ] ; then \
	    $(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)/$(SERVICE)/docker-compose.yml down -v ; \
	else \
	    echo "ERROR: Unsupported service '$(SERVICE)'"; \
	    $(MAKE) help; \
	    exit 1; \
	fi

clean-all: ## Stop, remove volumes and images for service(s) — use SERVICE=<name> to target one
	@if [ "$(SERVICE)" = "" ]; then \
	    $(MAKE) clean-all-gui ; \
	    $(MAKE) clean-all-dashboard ; \
	    $(MAKE) clean-all-psql ; \
	    $(MAKE) clean-all-mongo ; \
	elif [ "$(SERVICE)" = "remote-gui" ] || [ "$(SERVICE)" = "gui" ]; then \
	    $(MAKE) clean-all-gui ; \
	elif [ "$(SERVICE)" = "grafana" ]; then \
	    $(MAKE) clean-all-dashboard ; \
	elif [ "$(SERVICE)" = "postgres" ] || [ "$(SERVICE)" = "psql" ]; then \
	    $(MAKE) clean-all-psql ; \
	elif [ "$(SERVICE)" = "mongodb" ] || [ "$(SERVICE)" = "mongo" ]; then \
	    $(MAKE) clean-all-mongo ; \
	elif [ -d "$(SUPPORT_DIR)/$(SERVICE)" ] ; then \
	    $(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)/$(SERVICE)/docker-compose.yml down -v --rmi all ; \
	else \
	    echo "ERROR: Unsupported service '$(SERVICE)'"; \
	    $(MAKE) help; \
	    exit 1; \
	fi

logs: ## Print logs for a specific service (SERVICE=<name> required)
	@if [ "$(SERVICE)" = "remote-gui" ] || [ "$(SERVICE)" = "gui" ]; then \
	    $(MAKE) logs-gui ; \
	elif [ "$(SERVICE)" = "grafana" ]; then \
	    $(MAKE) logs-dashboard ; \
	elif [ "$(SERVICE)" = "postgres" ] || [ "$(SERVICE)" = "psql" ]; then \
	    $(MAKE) logs-psql ; \
	elif [ "$(SERVICE)" = "mongodb" ] || [ "$(SERVICE)" = "mongo" ]; then \
	    $(MAKE) logs-mongo ; \
	elif [ -d "$(SUPPORT_DIR)/$(SERVICE)" ] ; then \
	    $(CONTAINER_CMD) logs $(CONTAINER_NAME) ; \
	else \
	    echo "ERROR: Unsupported service '$(SERVICE)'"; \
	    $(MAKE) help; \
	    exit 1; \
	fi

logs-f: ## Follow logs for a specific service (SERVICE=<name> required)
	@if [ "$(SERVICE)" = "remote-gui" ] || [ "$(SERVICE)" = "gui" ]; then \
	    $(MAKE) logs-f-gui ; \
	elif [ "$(SERVICE)" = "grafana" ]; then \
	    $(MAKE) logs-f-dashboard ; \
	elif [ "$(SERVICE)" = "postgres" ] || [ "$(SERVICE)" = "psql" ]; then \
	    $(MAKE) logs-f-psql ; \
	elif [ "$(SERVICE)" = "mongodb" ] || [ "$(SERVICE)" = "mongo" ]; then \
	    $(MAKE) logs-f-mongo ; \
    elif [ -d "$(SUPPORT_DIR)/$(SERVICE)" ] ; then \
	    $(CONTAINER_CMD) logs -f $(CONTAINER_NAME) ; \
	else \
	    echo "ERROR: Unsupported service '$(SERVICE)'"; \
	    $(MAKE) help; \
	    exit 1; \
	fi

attach: ## Attach to CLI for MongoDB or Postgres
	@if [ "$(SERVICE)" = "mongodb" ] || [ "$(SERVICE)" = "mongo" ]; then \
	    $(MAKE) attach-mongodb ; \
    elif [ "$(SERVICE)" = "postgres" ] || [ "$(SERVICE)" = "psql" ]; then \
	    $(MAKE) attach-postgres ; \
    elif

exec: ## Attach to shell for a specific service (SERVICE=<name> required)
	@if [ "$(SERVICE)" = "remote-gui" ] || [ "$(SERVICE)" = "gui" ]; then \
	    $(MAKE) exec-gui ; \
	elif [ "$(SERVICE)" = "grafana" ]; then \
	    $(MAKE) exec-dashboard ; \
	elif [ "$(SERVICE)" = "postgres" ] || [ "$(SERVICE)" = "psql" ]; then \
	    $(MAKE) exec-psql ; \
	elif [ "$(SERVICE)" = "mongodb" ] || [ "$(SERVICE)" = "mongo" ]; then \
	    $(MAKE) exec-mongo ; \
    elif [ -d "$(SUPPORT_DIR)/$(SERVICE)" ] ; then \
	    $(CONTAINER_CMD) exec -it $(CONTAINER_NAME) /bin/bash
	else \
	    echo "ERROR: Unsupported service '$(SERVICE)'"; \
	    $(MAKE) help; \
	    exit 1; \
	fi

#----------------------------------------------------------------------
# Remote-GUI
#----------------------------------------------------------------------
up-gui:
	@echo "Deploying Service: Remote-GUI"
	$(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)remote-gui/docker-compose.yml up -d
down-gui:
	@echo "Stopping Service: Remote-GUI"
	$(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)remote-gui/docker-compose.yml down
clean-gui:
	@echo "Removing Service + Volumes: Remote-GUI"
	$(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)remote-gui/docker-compose.yml down -v
clean-all-gui:
	@echo "Removing Service + Volumes + Image: Remote-GUI"
	$(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)remote-gui/docker-compose.yml down -v --rmi all
logs-gui:
	@echo "Logs: Remote-GUI"
	$(CONTAINER_CMD) logs $(CONTAINER_NAME)
logs-f-gui:
	@echo "Logs (follow): Remote-GUI"
	$(CONTAINER_CMD) logs -f $(CONTAINER_NAME)
exec-gui:
	@echo "Exec into: Remote-GUI"
	$(CONTAINER_CMD) exec -it $(CONTAINER_NAME) /bin/bash

#----------------------------------------------------------------------
# Grafana (dashboard)
#----------------------------------------------------------------------
up-dashboard:
	@echo "Deploying Service: Grafana"
	$(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)grafana/docker-compose.yml up -d
down-dashboard:
	@echo "Stopping Service: Grafana"
	$(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)grafana/docker-compose.yml down
clean-dashboard:
	@echo "Removing Service + Volumes: Grafana"
	$(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)grafana/docker-compose.yml down -v
clean-all-dashboard:
	@echo "Removing Service + Volumes + Image: Grafana"
	$(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)grafana/docker-compose.yml down -v --rmi all
logs-dashboard:
	@echo "Logs: Grafana"
	$(CONTAINER_CMD) logs $(CONTAINER_NAME)
logs-f-dashboard:
	@echo "Logs (follow): Grafana"
	$(CONTAINER_CMD) logs -f $(CONTAINER_NAME)
exec-dashboard:
	@echo "Exec into: Grafana"
	$(CONTAINER_CMD) exec -it $(CONTAINER_NAME) /bin/bash

#----------------------------------------------------------------------
# Postgres
#----------------------------------------------------------------------
up-psql:
	@echo "Deploying Service: Postgres"
	$(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)postgres/docker-compose.yml up -d
down-psql:
	@echo "Stopping Service: Postgres"
	$(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)postgres/docker-compose.yml down
clean-psql:
	@echo "Removing Service + Volumes: Postgres"
	$(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)postgres/docker-compose.yml down -v
clean-all-psql:
	@echo "Removing Service + Volumes + Image: Postgres"
	$(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)postgres/docker-compose.yml down -v --rmi all
logs-psql:
	@echo "Logs: Postgres"
	$(CONTAINER_CMD) logs $(CONTAINER_NAME)
logs-f-psql:
	@echo "Logs (follow): Postgres"
	$(CONTAINER_CMD) logs -f $(CONTAINER_NAME)
attach-psql: ## attach to postgres CLI with your user (requires password)
	@echo "Attach to psql CLI"
    PSQL_USER=$$(grep -m1 'POSTGRES_USER:' "$(SUPPORT_DIR)/$(SERVICE)/docker-compose.yml" | awk '{print $$2}' | tr -d '"\r') ; \
    $(CONTAINER_CMD) exec -it $(CONTAINER_NAME) psql -U $(PSQL_USER)
exec-psql:
	@echo "Exec into: Postgres"
	$(CONTAINER_CMD) exec -it $(CONTAINER_NAME) /bin/bash

#----------------------------------------------------------------------
# MongoDB
#----------------------------------------------------------------------
up-mongo:
	@echo "Deploying Service: MongoDB"
	$(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)mongodb/docker-compose.yml up -d
down-mongo:
	@echo "Stopping Service: MongoDB"
	$(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)mongodb/docker-compose.yml down
clean-mongo:
	@echo "Removing Service + Volumes: MongoDB"
	$(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)mongodb/docker-compose.yml down -v
clean-all-mongo:
	@echo "Removing Service + Volumes + Image: MongoDB"
	$(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)mongodb/docker-compose.yml down -v --rmi all
logs-mongo:
	@echo "Logs: MongoDB"
	$(CONTAINER_CMD) logs $(CONTAINER_NAME)
logs-f-mongo:
	@echo "Logs (follow): MongoDB"
	$(CONTAINER_CMD) logs -f $(CONTAINER_NAME)
exec-mongo:
	@echo "Exec into: MongoDB"
	$(CONTAINER_CMD) exec -it $(CONTAINER_NAME) mongosh

attach-mongo: ## attach to MongoDB CLI with your user (requires password)
	@echo "Attach to psql CLI"
    $(CONTAINER_CMD) exec -it $(CONTAINER_NAME) mongosh
exec-psql:
	@echo "Exec into: Postgres"
	$(CONTAINER_CMD) exec -it $(CONTAINER_NAME) /bin/bash


#----------------------------------------------------------------------
# Help
#----------------------------------------------------------------------
help: ## Show this help message
	@echo ""
	@echo "Usage: make <target> [SERVICE=<service>]"
	@echo ""
	@echo "Services: remote-gui (gui) | grafana | postgres (psql) | mongodb (mongo)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) \
	    | awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

.PHONY: all dry-run \
        up down clean clean-all logs logs-f exec \
        up-gui down-gui clean-gui clean-all-gui logs-gui logs-f-gui exec-gui \
        up-dashboard down-dashboard clean-dashboard clean-all-dashboard logs-dashboard logs-f-dashboard exec-dashboard \
        up-psql down-psql clean-psql clean-all-psql logs-psql logs-f-psql exec-psql \
        up-mongo down-mongo clean-mongo clean-all-mongo logs-mongo logs-f-mongo exec-mongo \
        help