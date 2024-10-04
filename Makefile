#!/bin/Makefile

SHELL := /bin/bash
ifneq ($(filter-out $@,$(MAKECMDGOALS)), )
   export ANYLOG_TYPE = $(filter-out $@,$(MAKECMDGOALS))
else
	export ANYLOG_TYPE := generic
endif

export TAG := 1.3.2410-beta3
ifeq ($(shell uname -m), aarch64)
    TAG := latest-arm64
endif

ifneq ($(filter test-node test-network,$(MAKECMDGOALS)),test-node test-network)
    export NODE_TYPE ?= 127.0.0.1
    export REST_PORT := $(shell cat docker-makefile/${ANYLOG_TYPE}-configs/base_configs.env | grep ANYLOG_REST_PORT | awk -F "=" '{print $$2}')
    export REMOTE_CLI := $(shell cat docker-makefile/${ANYLOG_TYPE}-configs/advance_configs.env | grep REMOTE_CLI | awk -F "=" '{print $$2}')
    export ENABLE_NEBULA := $(shell cat docker-makefile/${ANYLOG_TYPE}-configs/advance_configs.env | grep ENABLE_NEBULA | awk -F "=" '{print $$2}')
    export DOCKER_COMPOSE_CMD := $(shell if command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; else echo "docker compose"; fi)
    export IMAGE := $(shell cat docker-makefile/.env | grep IMAGE | awk -F "=" '{print $$2}')
endif
v
all: help
login:
	@docker login docker.io -u anyloguser --password $(ANYLOG_TYPE)
generate-docker-compose:
	@if [ "$(REMOTE_CLI)" = "true" ] && [ "$(ENABLE_NEBULA)" = "true" ]; then \
		ANYLOG_TYPE="$(ANYLOG_TYPE)" envsubst < docker-makefile/docker-compose-template-remote-cli-nebula.yaml > docker-makefile/docker-compose.yaml; \
	elif [ "$(ENABLE_NEBULA)" = "true" ] ; then \
		ANYLOG_TYPE="$(ANYLOG_TYPE)" envsubst < docker-makefile/docker-compose-template-nebula.yaml > docker-makefile/docker-compose.yaml; \
	elif [ "$(REMOTE_CLI)" = "true" ]; then \
		ANYLOG_TYPE="$(ANYLOG_TYPE)" envsubst < docker-makefile/docker-compose-template-remote-cli.yaml > docker-makefile/docker-compose.yaml; \
	else \
		ANYLOG_TYPE="$(ANYLOG_TYPE)" envsubst < docker-makefile/docker-compose-template.yaml > docker-makefile/docker-compose.yaml; \
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
	docker attach --detach-keys=ctrl-d anylog-$(ANYLOG_TYPE)
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
	docker exec -it anylog-$(ANYLOG_TYPE) bash
logs:
	docker logs anylog-$(ANYLOG_TYPE)
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
