#!/bin/Makefile

# Default values
export ANYLOG_TYPE ?= generic
export NODE_NAME ?= anylog-node
export COMPANY_NAME ?= New Company
export TAG ?= 1.3.2507-beta14
export ANYLOG_SERVER_PORT ?= 32548
export ANYLOG_REST_PORT ?= 32549
export ANYLOG_BROKER_PORT ?=
export IS_MANUAL ?= false
export TEST_CONN ?=

# Detect OS type
export OS := $(shell uname -s)

# Conditional port override based on ANYLOG_TYPE
ifeq ($(IS_MANUAL), true)

  ifeq ($(ANYLOG_SERVER_PORT),32548)
    ifeq ($(ANYLOG_TYPE), master)
      ANYLOG_SERVER_PORT := 32048
    endif
    ifeq ($(ANYLOG_TYPE), operator)
      ANYLOG_SERVER_PORT := 32148
    endif
    ifeq ($(ANYLOG_TYPE), publisher)
      ANYLOG_SERVER_PORT := 32248
    endif
    ifeq ($(ANYLOG_TYPE), query)
      ANYLOG_SERVER_PORT := 32348
    endif
  endif

  ifeq ($(ANYLOG_REST_PORT),32549)
    ifeq ($(ANYLOG_TYPE), master)
      ANYLOG_REST_PORT := 32049
    endif
    ifeq ($(ANYLOG_TYPE), operator)
      ANYLOG_REST_PORT := 32149
    endif
    ifeq ($(ANYLOG_TYPE), publisher)
      ANYLOG_REST_PORT := 32249
    endif
    ifeq ($(ANYLOG_TYPE), query)
      ANYLOG_REST_PORT := 32349
    endif
  endif

  ifeq ($(NODE_NAME), anylog-node)
    ifeq ($(ANYLOG_TYPE), master)
      NODE_NAME := anylog-master
    endif
    ifeq ($(ANYLOG_TYPE), operator)
      NODE_NAME := anylog-operator
    endif
    ifeq ($(ANYLOG_TYPE), query)
      NODE_NAME := anylog-query
    endif
    ifeq ($(ANYLOG_TYPE), publisher)
      NODE_NAME := anylog-publisher
    endif
  endif
endif

ifeq ($(IS_MANUAL), false)
  ARCH := $(shell uname -m)
  ifeq ($(ARCH),aarch64 arm64)
    TAG := 1.3.2503-arm64
  endif
  ifneq ($(filter test-node test-network,$(MAKECMDGOALS)),test-node test-network)
    export NODE_NAME := $(shell cat docker-makefiles/${ANYLOG_TYPE}-configs/base_configs.env | grep NODE_NAME | awk -F "=" '{print $$2}'| sed 's/ /-/g' | tr '[:upper:]' '[:lower:]')
    export ANYLOG_SERVER_PORT := $(shell cat docker-makefiles/${ANYLOG_TYPE}-configs/base_configs.env | grep ANYLOG_SERVER_PORT | awk -F "=" '{print $$2}')
    export ANYLOG_REST_PORT := $(shell cat docker-makefiles/${ANYLOG_TYPE}-configs/base_configs.env | grep ANYLOG_REST_PORT | awk -F "=" '{print $$2}')
    export ANYLOG_BROKER_PORT := $(shell cat docker-makefiles/${ANYLOG_TYPE}-configs/base_configs.env | grep ANYLOG_BROKER_PORT | awk -F "=" '{print $$2}' | grep -v '^$$')
    export REMOTE_CLI := $(shell cat docker-makefiles/${ANYLOG_TYPE}-configs/advance_configs.env | grep REMOTE_CLI | awk -F "=" '{print $$2}')
    export ENABLE_NEBULA := $(shell cat docker-makefiles/${ANYLOG_TYPE}-configs/advance_configs.env | grep ENABLE_NEBULA | awk -F "=" '{print $$2}')
    export IMAGE := $(shell cat docker-makefiles/.env | grep IMAGE | awk -F "=" '{print $$2}')
  endif

  ifeq ($(OS),Linux)
    export DOCKER_COMPOSE_TEMPLATE := docker-makefiles/docker-compose-template-base.yaml
  else
    export DOCKER_COMPOSE_TEMPLATE := docker-makefiles/docker-compose-template-ports-base.yaml
  endif
endif

export CONTAINER_CMD := $(shell if command -v podman >/dev/null 2>&1; then echo "podman"; else echo "docker"; fi)

export DOCKER_COMPOSE_CMD := $(shell if command -v podman-compose >/dev/null 2>&1; then echo "podman-compose"; \
	elif command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; else echo "docker compose"; fi)

all: help
login: ## log into the docker hub for AnyLog - use `ANYLOG_TYPE` as the placeholder for password
	$(CONTAINER_CMD) login docker.io -u anyloguser --password $(ANYLOG_TYPE)

generate-docker-compose:
	@bash docker-makefiles/update_docker_compose.sh
	@NODE_NAME="$(NODE_NAME)" ANYLOG_SERVER_PORT=${ANYLOG_SERVER_PORT} ANYLOG_REST_PORT=${ANYLOG_REST_PORT} ANYLOG_BROKER_PORT=${ANYLOG_BROKER_PORT} \
	REMOTE_CLI=$(REMOTE_CLI) ENABLE_NEBULA=$(ENABLE_NEBULA) \
	envsubst < docker-makefiles/docker-compose-template.yaml > docker-makefiles/docker-compose.yaml

build: ## pull image from the docker hub repository
	$(CONTAINER_CMD) pull docker.io/anylogco/anylog-network:$(TAG)

dry-run: generate-docker-compose ## create docker-compose.yaml file based on the .env configuration file(s)
	@echo "Dry Run $(ANYLOG_TYPE)"

up: ## start AnyLog instance
	@echo "Deploy AnyLog $(ANYLOG_TYPE)"
ifeq ($(IS_MANUAL),true)
ifeq ($(OS),Linux)
	@$(CONTAINER_CMD) run -it --rm --network host \
		-e INIT_TYPE=prod \
		-e NODE_TYPE=$(ANYLOG_TYPE) \
		-e ANYLOG_SERVER_PORT=$(ANYLOG_SERVER_PORT) \
		-e ANYLOG_REST_PORT=$(ANYLOG_REST_PORT) \
		-e NODE_NAME=$(NODE_NAME) \
		$(if $(ANYLOG_BROKER_PORT),-e ANYLOG_BROKER_PORT=$(ANYLOG_BROKER_PORT)) \
		-v $(NODE_NAME)-anylog:/app/AnyLog-Network/anylog \
		-v $(NODE_NAME)-blockchain:/app/AnyLog-Network/blockchain \
		-v $(NODE_NAME)-data:/app/AnyLog-Network/data \
		-v $(NODE_NAME)-local-scripts:/app/deployment-scripts \
		--name $(NODE_NAME) \
		anylogco/anylog-network:$(TAG)
else
	@$(CONTAINER_CMD) run -it --rm \
		-p $(ANYLOG_SERVER_PORT):$(ANYLOG_SERVER_PORT) \
		-p $(ANYLOG_REST_PORT):$(ANYLOG_REST_PORT) \
		$(if $(ANYLOG_BROKER_PORT),-p $(ANYLOG_BROKER_PORT):$(ANYLOG_BROKER_PORT)) \
		-e INIT_TYPE=prod \
		-e NODE_TYPE=$(ANYLOG_TYPE) \
		-e ANYLOG_SERVER_PORT=$(ANYLOG_SERVER_PORT) \
		-e ANYLOG_REST_PORT=$(ANYLOG_REST_PORT) \
		-e NODE_NAME=$(NODE_NAME) \
		$(if $(ANYLOG_BROKER_PORT),-e ANYLOG_BROKER_PORT=$(ANYLOG_BROKER_PORT)) \
		-v $(NODE_NAME)-anylog:/app/AnyLog-Network/anylog \
		-v $(NODE_NAME)-blockchain:/app/AnyLog-Network/blockchain \
		-v $(NODE_NAME)-data:/app/AnyLog-Network/data \
		-v $(NODE_NAME)-local-scripts:/app/deployment-scripts \
		--name $(NODE_NAME) \
		anylogco/anylog-network:$(TAG)
endif
else
	@$(MAKE) generate-docker-compose
	@$(DOCKER_COMPOSE_CMD) -f docker-makefiles/docker-compose.yaml up -d
	@rm -f docker-makefiles/docker-compose.yaml docker-makefiles/docker-compose-template.yaml
endif

down: ## Stop AnyLog instance
	@echo "Stop AnyLog $(ANYLOG_TYPE)"
ifeq ($(IS_MANUAL),true)
	@$(CONTAINER_CMD) stop $(NODE_NAME)
else
	@$(MAKE) generate-docker-compose
	@$(DOCKER_COMPOSE_CMD) -f docker-makefiles/docker-compose.yaml down
	@rm -f docker-makefiles/docker-compose.yaml docker-makefiles/docker-compose-template.yaml
endif

clean-vols: ## Stop AnyLog instance and remove associated volumes
	@echo "Stop AnyLog $(ANYLOG_TYPE) & Remove Volumes"
ifeq ($(IS_MANUAL),true)
	@$(CONTAINER_CMD) stop $(NODE_NAME)
	@$(CONTAINER_CMD) volume rm $(NODE_NAME)-anylog $(NODE_NAME)-blockchain $(NODE_NAME)-data $(NODE_NAME)-local-scripts
else
	@$(MAKE) generate-docker-compose
	@$(DOCKER_COMPOSE_CMD) -f docker-makefiles/docker-compose.yaml down --volumes
	@rm -f docker-makefiles/docker-compose.yaml
endif

clean: ## Stop AnyLog instance and remove associated volumes & image
	@echo "Stop AnyLog $(ANYLOG_TYPE) & Remove Volumes and Images"
ifeq ($(IS_MANUAL),true)
	@$(CONTAINER_CMD) stop $(NODE_NAME)
	@$(CONTAINER_CMD) volume rm $(NODE_NAME)-anylog $(NODE_NAME)-blockchain $(NODE_NAME)-data $(NODE_NAME)-local-scripts
	@$(CONTAINER_CMD) rmi anylogco/anylog-network:$(TAG)
else
	@$(MAKE) generate-docker-compose
	@$(DOCKER_COMPOSE_CMD) -f docker-makefiles/docker-compose.yaml down --volumes --rmi all
	@rm -f docker-makefiles/docker-compose.yaml docker-makefiles/docker-compose-template.yaml
endif

attach: ## Attach to docker / podman container (use ctrl-d to detach)
	@$(CONTAINER_CMD) attach --detach-keys=ctrl-d $(NODE_NAME)

exec: ## Attach to the shell executable for the container
	@$(CONTAINER_CMD) exec -it $(NODE_NAME) /bin/bash

logs: ## View container logs
	@$(CONTAINER_CMD) logs $(NODE_NAME)

test-node: ## Test a node via REST interface
ifeq ($(TEST_CONN), )
	@echo "Missing Connection information (Param Name: TEST_CONN)"
	exit 1
endif
	@echo "Test Node against $(TEST_CONN)"
	@curl -X GET http://$(TEST_CONN) -H "command: test node" -H "User-Agent: AnyLog/1.23" -w "\n"

test-network: ## Test the network via REST interface
ifeq ($(TEST_CONN), )
	@echo "Missing Connection information (Param Name: TEST_CONN)"
	exit 1
endif
	@echo "Test Network against $(TEST_CONN)"
	@curl -X GET http://$(TEST_CONN) -H "command: test network" -H "User-Agent: AnyLog/1.23" -w "\n"
check-vars: ## Show all environment variable values
	@echo "IS_MANUAL    Default: false          Value: $(IS_MANUAL)"
	@echo "ANYLOG_TYPE  Default: generic        Value: $(ANYLOG_TYPE)"
	@echo "NODE_NAME    Default: anylog-node    Value: $(NODE_NAME)"
	@echo "NODE_NAME    Default: New Company    Value: $(COMPANY_NAME)"
	@echo "TAG          Default: latest         Value: $(TAG)"
	@echo "ANYLOG_SERVER_PORT          Default: 32548         Value: $(ANYLOG_SERVER_PORT)"
	@echo "ANYLOG_REST_PORT            Default: 32549         Value: $(ANYLOG_REST_PORT)"
	@echo "ANYLOG_BROKER_PORT          Default:          Value: $(ANYLOG_BROKER_PORT)"
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
	@echo "  ANYLOG_SERVER_PORT  Port for server communication"
	@echo "  ANYLOG_REST_PORT    Port for REST API"
	@echo "  ANYLOG_BROKER_PORT  Optional broker port"
	@echo "  TEST_CONN           REST connection information for testing network connectivity"
