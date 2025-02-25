#!/bin/Makefile

SHELL := /bin/bash
ifneq ($(filter-out $@,$(MAKECMDGOALS)), )
   export ANYLOG_TYPE = $(filter-out $@,$(MAKECMDGOALS))
else
	export ANYLOG_TYPE := generic
endif

ARCH := $(shell uname -m)
export TAG := latest

# Check if the architecture matches aarch64 or arm64
ifeq ($(ARCH),aarch64)
    TAG := latest-arm64
else ifeq ($(ARCH),arm64)
    TAG := latest-arm64
else
    TAG := latest
endif
#ifeq ($(shell uname -m), aarch64)
#    TAG := latest-arm64
#endif

export DOCKER_COMPOSE_CMD := $(shell if command -v podman-compose >/dev/null 2>&1; then echo "podman-compose"; \
	elif command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; else echo "docker compose"; fi)

export CONTAINER_CMD := $(shell if command -v podman >/dev/null 2>&1; then echo "podman"; else echo "docker"; fi)

# Only execute shell commands if NOT called with test-node or test-network
ifneq ($(filter test-node test-network,$(MAKECMDGOALS)),test-node test-network)
	export ANYLOG_SERVER_PORT := $(shell cat docker-makefile/${ANYLOG_TYPE}-configs/base_configs.env | grep ANYLOG_SERVER_PORT | awk -F "=" '{print $$2}')
    export ANYLOG_REST_PORT := $(shell cat docker-makefile/${ANYLOG_TYPE}-configs/base_configs.env | grep ANYLOG_REST_PORT | awk -F "=" '{print $$2}')
	export ANYLOG_BROKER_PORT := $(shell cat docker-makefile/${ANYLOG_TYPE}-configs/base_configs.env | grep ANYLOG_BROKER_PORT | awk -F "=" '{print $$2}' | grep -v '^$$')
    export REMOTE_CLI := $(shell cat docker-makefile/${ANYLOG_TYPE}-configs/advance_configs.env | grep REMOTE_CLI | awk -F "=" '{print $$2}')
    export ENABLE_NEBULA := $(shell cat docker-makefile/${ANYLOG_TYPE}-configs/advance_configs.env | grep ENABLE_NEBULA | awk -F "=" '{print $$2}')
    export IMAGE := $(shell cat docker-makefile/.env | grep IMAGE | awk -F "=" '{print $$2}')
endif


all: help
login:
	$(CONTAINER_CMD) login docker.io -u anyloguser --password $(ANYLOG_TYPE)
generate-docker-compose:
	@if [ "$(REMOTE_CLI)" == "true" ] && [ "$(ENABLE_NEBULA)" == "true" ] && [ ! -z "$(ANYLOG_BROKER_PORT)" ]; then \
  		ANYLOG_TYPE="$(ANYLOG_TYPE)" ANYLOG_SERVER_PORT=${ANYLOG_SERVER_PORT} ANYLOG_REST_PORT=${ANYLOG_REST_PORT} ANYLOG_BROKER_PORT=${ANYLOG_BROKER_PORT} envsubst < docker-makefile/docker-compose-template-nebula-remote-cli-broker.yaml > docker-makefile/docker-compose.yaml; \
  	elif [ "$(REMOTE_CLI)" == "false" ] && [ "$(ENABLE_NEBULA)" == "true" ] && [ ! -z "$(ANYLOG_BROKER_PORT)" ]; then \
  		ANYLOG_TYPE="$(ANYLOG_TYPE)" ANYLOG_SERVER_PORT=${ANYLOG_SERVER_PORT} ANYLOG_REST_PORT=${ANYLOG_REST_PORT} ANYLOG_BROKER_PORT=${ANYLOG_BROKER_PORT} envsubst < docker-makefile/docker-compose-template-nebula-broker.yaml > docker-makefile/docker-compose.yaml; \
	elif [ "$(REMOTE_CLI)" == "true" ] && [ "$(ENABLE_NEBULA)" == "false" ] && [ ! -z "$(ANYLOG_BROKER_PORT)" ]; then \
  		ANYLOG_TYPE="$(ANYLOG_TYPE)" ANYLOG_SERVER_PORT=${ANYLOG_SERVER_PORT} ANYLOG_REST_PORT=${ANYLOG_REST_PORT} ANYLOG_BROKER_PORT=${ANYLOG_BROKER_PORT} envsubst < docker-makefile/docker-compose-template-remote-cli-broker.yaml > docker-makefile/docker-compose.yaml; \
	elif [ "$(REMOTE_CLI)" == "true" ] && [ "$(ENABLE_NEBULA)" == "true" ] && [ -z "$(ANYLOG_BROKER_PORT)" ]; then \
  		ANYLOG_TYPE="$(ANYLOG_TYPE)" ANYLOG_SERVER_PORT=${ANYLOG_SERVER_PORT} ANYLOG_REST_PORT=${ANYLOG_REST_PORT} envsubst < docker-makefile/docker-compose-template-nebula-remote-cli.yaml > docker-makefile/docker-compose.yaml; \
	elif [ "$(REMOTE_CLI)" == "true" ] && [ "$(ENABLE_NEBULA)" == "false" ] && [ -z "$(ANYLOG_BROKER_PORT)" ]; then \
  		ANYLOG_TYPE="$(ANYLOG_TYPE)" ANYLOG_SERVER_PORT=${ANYLOG_SERVER_PORT} ANYLOG_REST_PORT=${ANYLOG_REST_PORT} envsubst < docker-makefile/docker-compose-template-remote-cli.yaml > docker-makefile/docker-compose.yaml; \
	elif [ "$(REMOTE_CLI)" == "false" ] && [ "$(ENABLE_NEBULA)" == "true" ] && [ -z "$(ANYLOG_BROKER_PORT)" ]; then \
  		ANYLOG_TYPE="$(ANYLOG_TYPE)" ANYLOG_SERVER_PORT=${ANYLOG_SERVER_PORT} ANYLOG_REST_PORT=${ANYLOG_REST_PORT} envsubst < docker-makefile/docker-compose-template-nebula.yaml > docker-makefile/docker-compose.yaml; \
	elif [ "$(REMOTE_CLI)" == "false" ] && [ "$(ENABLE_NEBULA)" == "false" ] && [ ! -z "$(ANYLOG_BROKER_PORT)" ]; then \
  		ANYLOG_TYPE="$(ANYLOG_TYPE)" ANYLOG_SERVER_PORT=${ANYLOG_SERVER_PORT} ANYLOG_REST_PORT=${ANYLOG_REST_PORT} ANYLOG_BROKER_PORT=${ANYLOG_BROKER_PORT} envsubst < docker-makefile/docker-compose-template-broker.yaml > docker-makefile/docker-compose.yaml; \
  	else \
  	  ANYLOG_TYPE="$(ANYLOG_TYPE)" ANYLOG_SERVER_PORT=${ANYLOG_SERVER_PORT} ANYLOG_REST_PORT=${ANYLOG_REST_PORT} envsubst < docker-makefile/docker-compose-template.yaml > docker-makefile/docker-compose.yaml; \
  	fi
test-conn:
	@echo "REST Connection Info for testing (Example: 127.0.0.1:32149):"
	@read CONN; \
	echo $$CONN > conn.tmp
build:
	$(CONTAINER_CMD) pull docker.io/anylogco/anylog-network:$(TAG)
dry-run:
	@echo "Dry Run $(ANYLOG_TYPE)"
	ANYLOG_TYPE=$(ANYLOG_TYPE) envsubst < docker-makefile/docker-compose-template.yaml > docker-makefile/docker-compose.yaml
up: generate-docker-compose
	@echo "Deploy AnyLog $(ANYLOG_TYPE)"
	@${DOCKER_COMPOSE_CMD} -f docker-makefile/docker-compose.yaml up -d
	@rm -rf docker-makefile/docker-compose.yaml
down: generate-docker-compose
	@echo "Stop AnyLog $(ANYLOG_TYPE)"
	@${DOCKER_COMPOSE_CMD} -f docker-makefile/docker-compose.yaml down
	@rm -rf docker-makefile/docker-compose.yaml
clean-vols: generate-docker-compose
	@${DOCKER_COMPOSE_CMD} -f docker-makefile/docker-compose.yaml down --volumes
	@rm -rf docker-makefile/docker-compose.yaml
clean: generate-docker-compose
	ANYLOG_TYPE=$(ANYLOG_TYPE) envsubst < docker-makefile/docker-compose-template.yaml > docker-makefile/docker-compose.yaml
	@${DOCKER_COMPOSE_CMD} -f docker-makefile/docker-compose.yaml down --volumes --rmi all
	@rm -rf docker-makefile/docker-compose.yaml
attach:
	@$(CONTAINER_CMD) attach --detach-keys=ctrl-d anylog-$(ANYLOG_TYPE)
test-node: test-conn
	@CONN=$$(cat conn.tmp); \
	echo "Node State against $$CONN"; \
	curl -X GET http://$$CONN -H "command: get status"    -H "User-Agent: AnyLog/1.23" -w "\n"; \
	curl -X GET http://$$CONN -H "command: test node"     -H "User-Agent: AnyLog/1.23" -w "\n"; \
	curl -X GET http://$$CONN -H "command: get processes" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	rm -rf conn.tmp

test-network: test-conn
	@CONN=$$(cat conn.tmp); \
	echo "Test Network Against: $$CONN"; \
	curl -X GET http://$$CONN -H "command: test network" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	rm -rf conn.tmp
exec:
	@$(CONTAINER_CMD) exec -it anylog-$(ANYLOG_TYPE) bash
logs:
	@$(CONTAINER_CMD) logs anylog-$(ANYLOG_TYPE)
help:
	@echo "Usage: make [target] [anylog-type]"
	@echo "Targets:"
	@echo "  login       	Log into AnyLog's Dockerhub - use ANYLOG_TYPE to set password value"
	@echo "  build       	Pull the docker image"
	@echo "  up	  		 	Start the containers"
	@echo "  attach      	Attach to AnyLog instance"
	@echo "  test-node		Validate node status"
	@echo "  test-network	Validate node can communicate with other nodes in the network"
	@echo "  exec			Attach to shell interface for container"
	@echo "  down			Stop and remove the containers"
	@echo "  logs			View logs of the containers"
	@echo "  clean-vols 	stop & clean volumes"
	@echo "  clean       	stop & clean up volumes and image"
	@echo "  help			show this help message"
	@echo "supported AnyLog types: generic, master, operator, and query"
	@echo "Sample calls: make up master | make attach master | make clean master"
