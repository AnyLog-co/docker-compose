#!/bin/Makefile

SHELL := /bin/bash

# Check if ANYLOG_PATH is passed; if not, display an error
ifneq ($(filter-out $@,$(MAKECMDGOALS)), )
   ANYLOG_PATH := $(filter-out $@,$(MAKECMDGOALS))
else
   $(error "Missing ANYLOG_PATH, cannot continue...")
endif

# Determine NODE_TYPE based on ANYLOG_PATH content
ifneq (,$(findstring operator,$(ANYLOG_PATH)))
   NODE_TYPE := operator
else ifneq (,$(findstring master,$(ANYLOG_PATH)))
   NODE_TYPE := master
else ifneq (,$(findstring query,$(ANYLOG_PATH)))
   NODE_TYPE := query
else
   $(error "Unknown ANYLOG_PATH; cannot determine NODE_TYPE")
endif

export TAG := 1.3.2410-beta9
ifeq ($(shell uname -m), aarch64)
    TAG := latest-arm64
endif

# Only execute shell commands if NOT called with test-node or test-network
ifneq ($(filter test-node test-network,$(MAKECMDGOALS)),test-node test-network)
	export NODE_NAME := $($(shell cat docker-makefile/${ANYLOG_PATH}/base_configs.env | grep NODE_NAME | awk -F "=" '{print $$2}'))
	export ANYLOG_SERVER_PORT := $(shell cat docker-makefile/${ANYLOG_PATH}/base_configs.env | grep ANYLOG_SERVER_PORT | awk -F "=" '{print $$2}')
    export ANYLOG_REST_PORT := $(shell cat docker-makefile/${ANYLOG_PATH}/base_configs.env | grep ANYLOG_REST_PORT | awk -F "=" '{print $$2}')
	export ANYLOG_BROKER_PORT := $(shell cat docker-makefile/${ANYLOG_PATH}/base_configs.env | grep ANYLOG_BROKER_PORT | awk -F "=" '{print $$2}' | grep -v '^$$')
    export REMOTE_CLI := $(shell cat docker-makefile/${ANYLOG_PATH}/advance_configs.env | grep REMOTE_CLI | awk -F "=" '{print $$2}')
    export ENABLE_NEBULA := $(shell cat docker-makefile/${ANYLOG_PATH}/advance_configs.env | grep ENABLE_NEBULA | awk -F "=" '{print $$2}')
    export DOCKER_COMPOSE_CMD := $(shell if command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; else echo "docker compose"; fi)
    export IMAGE := $(shell cat docker-makefile/.env | grep IMAGE | awk -F "=" '{print $$2}')
endif

all: help
login:
	@docker login docker.io -u anyloguser --password $(ANYLOG_TYPE)
generate-docker-compose:
	@if [ "$(REMOTE_CLI)" = "true" ] ; then \
		NODE_TYPE=$(NODE_TYPE) ANYLOG_PATH=$(ANYLOG_PATH) NODE_NAME=$(NODE_NAME) ANYLOG_SERVER_PORT=$(ANYLOG_SERVER_PORT) ANYLOG_REST_PORT=$(ANYLOG_REST_PORT) envsubst < docker-makefile/docker-compose-template-remote-cli.yaml > docker-makefile/docker-compose.yaml; \
	else \
  		NODE_TYPE=$(NODE_TYPE) ANYLOG_PATH=$(ANYLOG_PATH) NODE_NAME=$(NODE_NAME) ANYLOG_SERVER_PORT=$(ANYLOG_SERVER_PORT) ANYLOG_REST_PORT=$(ANYLOG_REST_PORT) envsubst < docker-makefile/docker-compose-template.yaml > docker-makefile/docker-compose.yaml; \
  	fi
test-conn:
	@echo "REST Connection Info for testing (Example: 127.0.0.1:32149):"
	@read CONN; \
	echo $$CONN > conn.tmp
build:
	docker pull docker.io/anylogco/anylog-network:$(TAG)
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
	docker attach --detach-keys=ctrl-d anylog-$(NODE_NAME)
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
	docker exec -it $(NODE_NAME) /bin/sh
logs:
	docker logs anylog-$(NODE_NAME)
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
