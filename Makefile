#!/bin/Makefile

export ANYLOG_TYPE := generic
ifneq ($(filter-out $@,$(MAKECMDGOALS)), )
   export ANYLOG_TYPE = $(filter-out $@,$(MAKECMDGOALS))
endif

export TAG := 1.3.2410-beta2
ifeq ($(shell uname -m), aarch64)
    TAG := latest-arm64
endif

export NODE_TYPE ?= 127.0.0.1
export REST_PORT := $(shell cat docker-makefile/${ANYLOG_TYPE}-configs/base_configs.env | grep ANYLOG_REST_PORT | awk -F "=" '{print $$2}')
export REMOTE_CLI := $(shell cat docker-makefile/${ANYLOG_TYPE}-configs/advance_configs.env | grep REMOTE_CLI | awk -F "=" '{print $$2}')
export IS_NEBULA := $(shell cat docker-makefile/${ANYLOG_TYPE}-configs/advance_configs.env | grep ENABLE_NEBULA | awk -F "=" '{print $$2}')
export DOCKER_COMPOSE_CMD := $(shell if command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; else echo "docker compose"; fi)

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
node-status:
	@if [ "$(ANYLOG_TYPE)" = "master" ]; then \
		curl -X GET 127.0.0.1:32049 -H "command: get status" -H "User-Agent: AnyLog/1.23" -w "\n"
	elif [ "$(ANYLOG_TYPE)" = "operator" ]; then \
		curl -X GET 127.0.0.1:32149 -H "command: get status" -H "User-Agent: AnyLog/1.23" -w "\n"
	elif [ "$(ANYLOG_TYPE)" = "query" ]; then \
		curl -X GET 127.0.0.1:32349 -H "command: get status" -H "User-Agent: AnyLog/1.23" -w "\n"
	elif [ "$(NODE_TYPE)" == "publisher" ]; then \
		curl -X GET 127.0.0.1:32249 -H "command: get status" -H "User-Agent: AnyLog/1.23" -w "\n"
	elif [ "$(NODE_TYPE)" == "generic" ]; then \
		curl -X GET 127.0.0.1:32549 -H "command: get status" -H "User-Agent: AnyLog/1.23" -w "\n"
	fi
test-node:
	@echo "Test Node Against: $(NODE_IP):$(REST_PORT)"
	@curl -X GET $(NODE_IP):$(REST_PORT)
	@curl -X GET $(NODE_IP):$(REST_PORT) -H "command: test node"
test-network:
	@echo "Test Network Against: $(NODE_IP):$(REST_PORT)"
	@curl -X GET $(NODE_IP):$(REST_PORT) -H "command: test network"
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
	@echo "  test		 	Using cURL validate node is running"
	@echo "  exec			Attach to shell interface for container"
	@echo "  down			Stop and remove the containers"
	@echo "  logs			View logs of the containers"
	@echo "  clean-vols 	stop & clean volumes"
	@echo "  clean       	stop & clean up volumes and image"
	@echo "  help			show this help message"
	@echo "supported AnyLog types: generic, master, operator, and query"
	@echo "Sample calls: make up master | make attach master | make clean master"
