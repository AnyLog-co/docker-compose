#!/bin/Makefile
$(info LOADING MAKEFILE)

# Default values
export IS_MANUAL ?= false
export ANYLOG_TYPE ?= ""
export TAG ?= 1.4.2512

# Detect OS type
export OS := $(shell uname -s)
export UNAME_M := $(shell uname -m)
export ANYLOG_UID=$(id -u)
export ANYLOG_GID=$(id -g)
ifeq ($(UNAME_M),x86_64)
  export DOCKER_PLATFORM := linux/amd64
else ifneq (,$(filter $(UNAME_M),aarch64 arm64))
  export DOCKER_PLATFORM := linux/arm64
else
  $(error Unsupported architecture: $(UNAME_M))
endif

export CONTAINER_CMD := $(shell if command -v podman >/dev/null 2>&1; then echo "podman"; else echo "docker"; fi)
export DOCKER_COMPOSE_CMD := $(shell if command -v podman-compose >/dev/null 2>&1; then echo "podman-compose"; \
	    elif command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; else echo "docker compose"; fi)

all: help
check-configs: # check whether ANYLOG_TYPE (used for paths) is configured
	@if [ -z "$(ANYLOG_TYPE)" ]; then \
		echo "ERROR: Missing ANYLOG_TYPE param"; \
		$(MAKE) help; \
		exit 1; \
	fi
set-configs: check-configs # extract params
	@if [ "$(IS_MANUAL)" = "true" ]; then \
		echo "Manual mode: setting default configs"; \
		export ANYLOG_TYPE=generic; \
		export NODE_NAME=anylog-node; \
		export CLUSTER_NAME=new-cluster; \
		export COMPANY_NAME="New Company"; \
		export ANYLOG_SERVER_PORT=32548; \
		export ANYLOG_REST_PORT=32549; \
		export ANYLOG_BROKER_PORT=; \
		export LEDGER_CONN=127.0.0.1:32049; \
		export REMOTE_CLI=; \
		export LICENSE_KEY=; \
		export TEST_CONN=; \
		export NIC_TYPE=; \
	else \
		echo "Reading configs from docker-makefiles/$(ANYLOG_TYPE)"; \
		[ -f docker-makefiles/$(ANYLOG_TYPE)/base_configs.env ] || { \
			echo "ERROR: Config file not found for ANYLOG_TYPE=$(ANYLOG_TYPE)"; \
			exit 1; \
		}; \
		export NODE_NAME=$$(grep -m1 '^NODE_NAME=' docker-makefiles/$(ANYLOG_TYPE)/base_configs.env | cut -d= -f2); \
		export ANYLOG_SERVER_PORT=$$(grep -m1 '^ANYLOG_SERVER_PORT=' docker-makefiles/$(ANYLOG_TYPE)/base_configs.env | cut -d= -f2); \
		export ANYLOG_REST_PORT=$$(grep -m1 '^ANYLOG_REST_PORT=' docker-makefiles/$(ANYLOG_TYPE)/base_configs.env | cut -d= -f2); \
	fi; \
	export DOCKER_FILE_NAME=$$(echo "$$NODE_NAME" | tr ' _' '--')-docker-compose.yaml
login: ## log into the docker hub for AnyLog - use `ANYLOG_TYPE` as the placeholder for password
	$(CONTAINER_CMD) login docker.io -u anyloguser --password $(ANYLOG_TYPE)
pull: ## pull image from the docker hub repository
	$(CONTAINER_CMD) pull docker.io/anylogco/anylog-network:$(TAG)
dry-run: set-configs ## create docker-compose.yaml file based on the .env configuration file(s)
	@echo "Dry Run $(ANYLOG_TYPE) - $(NODE_NAME)"
	@mkdir -p docker-makefiles/docker-compose-files
	@if [ ! -f docker-makefiles/docker-compose-files/${DOCKER_FILE_NAME} ]; then \
        echo "Generating new docker-compose.yaml..."; \
		bash docker-makefiles/update_docker_compose.sh; \
		ANYLOG_UID="$(ANYLOG_UID)" ANYLOG_GID="$(ANYLOG_GID)" DOCKER_PLATFORM="$(DOCKER_PLATFORM)" NODE_NAME="$(NODE_NAME)" ANYLOG_SERVER_PORT=${ANYLOG_SERVER_PORT} ANYLOG_REST_PORT=${ANYLOG_REST_PORT} ANYLOG_BROKER_PORT=${ANYLOG_BROKER_PORT} \
		REMOTE_CLI=$(REMOTE_CLI) ENABLE_NEBULA=$(ENABLE_NEBULA) \
		envsubst < docker-makefiles/docker-compose-template.yaml > docker-makefiles/docker-compose.yaml; \
		mv docker-makefiles/docker-compose.yaml docker-makefiles/docker-compose-files/${DOCKER_FILE_NAME}; \
		rm -rf docker-makefiles/docker-compose-template.yaml; \
	fi
up: dry-run ## start AnyLog instance
	@echo "Deploy AnyLog $(ANYLOG_TYPE)"
	$(DOCKER_COMPOSE_CMD) -f docker-makefiles/docker-compose-files/${DOCKER_FILE_NAME} up -d
down: dry-run ## stop docker container
	@echo "Stop AnyLog Agent - $(ANYLOG_TYPE)"
	$(DOCKER_COMPOSE_CMD) -f docker-makefiles/docker-compose-files/${DOCKER_FILE_NAME} down
clean: dry-run  ## stop container and remove volumes
	@echo "Stop AnyLog Agent - $(ANYLOG_TYPE)"
	$(DOCKER_COMPOSE_CMD) -f docker-makefiles/docker-compose-files/${DOCKER_FILE_NAME} down -v
clean-all: dry-run ## stop container, remove volume and remove image
	@echo "Stop AnyLog Agent - $(ANYLOG_TYPE)"
	$(DOCKER_COMPOSE_CMD) -f docker-makefiles/docker-compose-files/${DOCKER_FILE_NAME} down -v --rmi all

logs: set-configs ## view logs
	@echo "View logs"
	$(CONTAINER_CMD) log $(NODE_NAME)

logs-f: set-configs ## view logs continuously
	$(CONTAINER_CMD) log -f $(NODE_NAME)

attach: set-configs ## attach to container
	$(CONTAINER_CMD) attach --detach-keys=ctrl-d $(NODE_NAME)

exec: set-configs ## attach to /bin/bash of container
	$(CONTAINER_CMD) exec -it $(NODE_NAME) /bin/bash
check-vars: ## Show all environment variable values
	@echo "IS_MANUAL             Default: false              Value: $(IS_MANUAL)"
	@echo "ANYLOG_TYPE           Default: generic            Value: $(ANYLOG_TYPE)"
	@echo "NODE_NAME             Default: anylog-node        Value: $(NODE_NAME)"
	@echo "CLUSTER_NAME          Default: new-cluster        Value: $(CLUSTER_NAME)"
	@echo "COMPANY_NAME          Default: New Company        Value: $(COMPANY_NAME)"
	@echo "TAG                   Default: latest             Value: $(TAG)"
	@echo "ANYLOG_SERVER_PORT    Default: 32548              Value: $(ANYLOG_SERVER_PORT)"
	@echo "ANYLOG_REST_PORT      Default: 32549              Value: $(ANYLOG_REST_PORT)"
	@echo "ANYLOG_BROKER_PORT    Default:                    Value: $(ANYLOG_BROKER_PORT)"
	@echo "LEDGER_CONN           Default: 127.0.0.1:32049     Value: $(LEDGER_CONN)"
	@echo "LICENSE_KEY           Default:                    Value: $(LICENSE_KEY)"
help:
	@echo "Usage: make [target] [VARIABLE=value]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk -F':|##' '{ printf "  \033[36m%-20s\033[0m %s\n", $$1, $$3 }'
	@echo ""
	@echo "Common variables you can override:"
	@echo "  IS_MANUAL           Use manual deployment (true/false) - required to overwrite"
	@echo "  ANYLOG_TYPE         Type of node to deploy (e.g., master, operator)"
	@echo "  TAG                 Docker image tag to use"
	@echo "  NODE_NAME           Custom name for the container"
	@echo "  CLUSTER_NAME		 Cluster Operator node is associted with"
	@echo "  ANYLOG_SERVER_PORT  Port for server communication"
	@echo "  ANYLOG_REST_PORT    Port for REST API"
	@echo "  ANYLOG_BROKER_PORT  Optional broker port"
	@echo "  LEDGER_CONN         Master node IP and port"
	@echo "  LICENSE_KEY         AnyLog License Key"
	@echo "  TEST_CONN           REST connection information for testing network connectivity"


