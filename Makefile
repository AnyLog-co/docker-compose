#!/bin/Makefile
$(info LOADING MAKEFILE)

# Default values
export IS_MANUAL ?= false
export ANYLOG_TYPE ?=
export TAG ?= pre-develop
export IMAGE ?= anylogco/anylog-network

# Detect OS type
export OS := $(shell uname -s)
export UNAME_M := $(shell uname -m)
export ANYLOG_UID := $(shell id -u)
export ANYLOG_GID := $(shell id -g)

ifeq ($(UNAME_M),x86_64)
	export DOCKER_PLATFORM := linux/amd64
else ifneq (,$(filter $(UNAME_M),aarch64 arm64))
	export DOCKER_PLATFORM := linux/arm64
else
	$(error Unsupported architecture: $(UNAME_M))
endif

# -------------------
# Defaults in Make
# -------------------
ifeq ($(IS_MANUAL),false)
  ifneq ($(strip $(ANYLOG_TYPE)),)
    # Determine config file paths based on multi vs single file layout
    _ENV_FILE   := docker-makefiles/$(ANYLOG_TYPE)/.env
    _SINGLE_FILE := docker-makefiles/$(ANYLOG_TYPE)/node_configs.env

    ifneq ($(wildcard $(_ENV_FILE)),)
      # Multi-file layout
      export IMAGE     ?= $(shell grep -m1 '^IMAGE='     "$(_ENV_FILE)"  | cut -d= -f2- | tr -d '"\r')
      export NODE_NAME := $(shell grep -m1 '^NODE_NAME=' "$(_BASE_FILE)" | cut -d= -f2- | tr -d '"\r')
    else ifneq ($(wildcard $(_SINGLE_FILE)),)
      # Single-file layout
      export IMAGE     ?= $(shell grep -m1 '^IMAGE='     "$(_SINGLE_FILE)" | cut -d= -f2- | tr -d '"\r')
      export NODE_NAME := $(shell grep -m1 '^NODE_NAME=' "$(_SINGLE_FILE)" | cut -d= -f2- | tr -d '"\r')
    else
      $(error Missing configuration file(s) for $(ANYLOG_TYPE))
    endif
  endif
endif

export CONTAINER_CMD := $(shell if command -v podman >/dev/null 2>&1; then echo "podman"; else echo "docker"; fi)
export DOCKER_COMPOSE_CMD := $(shell if command -v podman-compose >/dev/null 2>&1; then echo "podman-compose"; \
	    elif command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; else echo "docker compose"; fi)
export DOCKER_COMPOSE_FILE := docker-makefiles/docker-compose-files/$(ANYLOG_TYPE)-docker-compose.yaml 

all: help

check-configs:
	@if [ "$(IS_MANUAL)" != "true" ] && [ -z "$(ANYLOG_TYPE)" ]; then \
		echo "ERROR: Missing AnyLog type"; \
		exit 1; \
	elif [ "$(IS_MANUAL)" != "true" ] && [ ! -d docker-makefiles/$(ANYLOG_TYPE) ]; then \
		echo "ERROR: Missing directory for ANYLOG_TYPE=$(ANYLOG_TYPE)"; \
		$(MAKE) help; \
		exit 1; \
	fi
	@echo $(IMAGE)
login: ## log into docker hub for AnyLog
	$(CONTAINER_CMD) login docker.io -u anyloguser --password $(ANYLOG_TYPE)
pull: check-configs ## pull image from docker hub
	$(CONTAINER_CMD) pull docker.io/$(IMAGE):$(TAG)

dry-run: check-configs ## generate docker-compose.yaml
	@echo "Dry Run ${ANYLOG_TYPE} - ${NODE_NAME}"
	bash docker-makefiles/build_docker_compose.sh $(ANYLOG_TYPE) $(TAG)

up: dry-run ## start AnyLog instance
	@echo "Deploy AnyLog $(ANYLOG_TYPE)"
	$(DOCKER_COMPOSE_CMD) -f $(DOCKER_COMPOSE_FILE) up -d

down: dry-run ## stop docker container
	@echo "Stop AnyLog Agent - $(ANYLOG_TYPE)"
	$(DOCKER_COMPOSE_CMD) -f $(DOCKER_COMPOSE_FILE) down

clean: dry-run ## stop container and remove volumes
	@echo "Stop AnyLog Agent - $(ANYLOG_TYPE)"
	$(DOCKER_COMPOSE_CMD) -f $(DOCKER_COMPOSE_FILE) down -v

clean-all: dry-run ## stop container, remove volumes and image
	@echo "Stop AnyLog Agent - $(ANYLOG_TYPE)"
	$(DOCKER_COMPOSE_CMD) -f $(DOCKER_COMPOSE_FILE) down -v --rmi all

logs: check-configs ## view logs
	@echo "View logs"
	$(CONTAINER_CMD) logs $(NODE_NAME)

logs-f: check-configs ## view logs continuously
	$(CONTAINER_CMD) logs -f $(NODE_NAME)

attach: check-configs ## attach to container
	$(CONTAINER_CMD) attach --detach-keys=ctrl-d $(NODE_NAME)

exec: check-configs ## attach to bash shell
	$(CONTAINER_CMD) exec -it $(NODE_NAME) /bin/bash

check-vars: ## Show all environment variables
	@echo "IS_MANUAL             Default: false              Value: $(IS_MANUAL)"
	@echo "ANYLOG_TYPE           Default: generic            Value: $(ANYLOG_TYPE)"
	@echo "IMAGE                 Default: anylogco/anylog-network Value: $(IMAGE)"
	@echo "NODE_NAME             Default: anylog-node        Value: $(NODE_NAME)"
	@echo "CLUSTER_NAME          Default: new-cluster        Value: $(CLUSTER_NAME)"
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
	@echo "  IS_MANUAL           Use manual deployment (true/false)"
	@echo "  ANYLOG_TYPE         Type of node to deploy (e.g., master, operator)"
	@echo "  IMAGE               Docker image repo"
	@echo "  TAG                 Docker image tag"
	@echo "  NODE_NAME           Custom name for the container"
	@echo "  CLUSTER_NAME        Cluster operator node is associated with"
	@echo "  ANYLOG_SERVER_PORT  Port for server communication"
	@echo "  ANYLOG_REST_PORT    Port for REST API"
	@echo "  ANYLOG_BROKER_PORT  Optional broker port"
	@echo "  LEDGER_CONN         Master node IP and port"
	@echo "  LICENSE_KEY         AnyLog License Key"
