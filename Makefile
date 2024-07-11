#!/bin/Makefile

export ANYLOG_TYPE := generic
ifneq ($(filter-out $@,$(MAKECMDGOALS)), )
   export ANYLOG_TYPE = $(filter-out $@,$(MAKECMDGOALS))
endif


export TAG := 1.3.2405-beta5
ifeq ($(shell uname -m), arm64)
    TAG := 1.3.2405-arm64
endif

#export ANYLOG_SERVER_PORT := $(shell grep ANYLOG_SERVER_PORT docker-makefile/$(ANYLOG_TYPE)-configs/base_configs.env | grep -v '""' | grep -v \# | cut -d '=' -f 2)
#export ANYLOG_REST_PORT := $(shell grep ANYLOG_REST_PORT docker-makefile/$(ANYLOG_TYPE)-configs/base_configs.env | grep -v '""' | grep -v \# | cut -d '=' -f 2)
#export ANYLOG_BROKER_PORT := $(shell grep ANYLOG_BROKER_PORT docker-makefile/$(ANYLOG_TYPE)-configs/base_configs.env | grep -v '""' | grep -v \# | cut -d '=' -f 2)



all: help

login:
	@docker login docker.io -u anyloguser --password $(ANYLOG_TYPE)

build:
	docker pull docker.io/anylogco/anylog-network:$(TAG)

dry-run:
	@echo "Dry Run $(ANYLOG_TYPE)"
#	@if [ -n "$(ANYLOG_BROKER_PORT)" ]; then \
#		ANYLOG_TYPE=$(ANYLOG_TYPE) ANYLOG_SERVER_PORT=$(ANYLOG_SERVER_PORT) ANYLOG_REST_PORT=$(ANYLOG_REST_PORT) ANYLOG_BROKER_PORT=$(ANYLOG_BROKER_PORT) envsubst < docker-makefile/docker-compose-template-broker.yaml > docker-makefile/docker-compose.yaml
#	else \
#		ANYLOG_TYPE=$(ANYLOG_TYPE) ANYLOG_SERVER_PORT=$(ANYLOG_SERVER_PORT) ANYLOG_REST_PORT=$(ANYLOG_REST_PORT) envsubst < docker-makefile/docker-compose-template.yaml > docker-makefile/docker-compose.yaml
#	fi
	ANYLOG_TYPE=$(ANYLOG_TYPE) envsubst < docker-makefile/docker-compose-template.yaml > docker-makefile/docker-compose.yaml

up:
	@echo "Deploy AnyLog $(ANYLOG_TYPE)"
#	@if [ -n "$(ANYLOG_BROKER_PORT)" ]; then \
#		ANYLOG_TYPE=$(ANYLOG_TYPE) ANYLOG_SERVER_PORT=$(ANYLOG_SERVER_PORT) ANYLOG_REST_PORT=$(ANYLOG_REST_PORT) ANYLOG_BROKER_PORT=$(ANYLOG_BROKER_PORT) envsubst < docker-makefile/docker-compose-template-broker.yaml > docker-makefile/docker-compose.yaml
#	else \
#		ANYLOG_TYPE=$(ANYLOG_TYPE) ANYLOG_SERVER_PORT=$(ANYLOG_SERVER_PORT) ANYLOG_REST_PORT=$(ANYLOG_REST_PORT) envsubst < docker-makefile/docker-compose-template.yaml > docker-makefile/docker-compose.yaml
#	fi
	ANYLOG_TYPE=$(ANYLOG_TYPE) envsubst < docker-makefile/docker-compose-template.yaml > docker-makefile/docker-compose.yaml
	@docker compose -f docker-makefile/docker-compose.yaml up -d
	@rm -rf docker-makefile/docker-compose.yaml

down:
#	@if [ -n "$(ANYLOG_BROKER_PORT)" ]; then \
#		ANYLOG_TYPE=$(ANYLOG_TYPE) ANYLOG_SERVER_PORT=$(ANYLOG_SERVER_PORT) ANYLOG_REST_PORT=$(ANYLOG_REST_PORT) ANYLOG_BROKER_PORT=$(ANYLOG_BROKER_PORT) envsubst < docker-makefile/docker-compose-template-broker.yaml > docker-makefile/docker-compose.yaml
#	else \
#		ANYLOG_TYPE=$(ANYLOG_TYPE) ANYLOG_SERVER_PORT=$(ANYLOG_SERVER_PORT) ANYLOG_REST_PORT=$(ANYLOG_REST_PORT) envsubst < docker-makefile/docker-compose-template.yaml > docker-makefile/docker-compose.yaml
#	fi
	ANYLOG_TYPE=$(ANYLOG_TYPE) envsubst < docker-makefile/docker-compose-template.yaml > docker-makefile/docker-compose.yaml
	@docker compose -f docker-makefile/docker-compose.yaml down
	@rm -rf docker-makefile/docker-compose.yaml

clean:
#	@if [ -n "$(ANYLOG_BROKER_PORT)" ]; then \
#		ANYLOG_TYPE=$(ANYLOG_TYPE) ANYLOG_SERVER_PORT=$(ANYLOG_SERVER_PORT) ANYLOG_REST_PORT=$(ANYLOG_REST_PORT) ANYLOG_BROKER_PORT=$(ANYLOG_BROKER_PORT) envsubst < docker-makefile/docker-compose-template-broker.yaml > docker-makefile/docker-compose.yaml
#	else \
#		ANYLOG_TYPE=$(ANYLOG_TYPE) ANYLOG_SERVER_PORT=$(ANYLOG_SERVER_PORT) ANYLOG_REST_PORT=$(ANYLOG_REST_PORT) envsubst < docker-makefile/docker-compose-template.yaml > docker-makefile/docker-compose.yaml
#	fi
	ANYLOG_TYPE=$(ANYLOG_TYPE) envsubst < docker-makefile/docker-compose-template.yaml > docker-makefile/docker-compose.yaml
	@docker compose -f docker-makefile/docker-compose.yaml down --volumes
	@docker images --format '{{.ID}}' docker.io/anylogco/anylog-network | xargs docker rmi
	@docker images --format '{{.ID}}' docker.io/anylogco/remote-cli | xargs docker rmi
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
	@if [ "$(ANYLOG_TYPE)" = "master" ]; then \
		curl -X GET 127.0.0.1:32049 -H "command: test node" -H "User-Agent: AnyLog/1.23" -w "\n"
	elif [ "$(ANYLOG_TYPE)" = "operator" ]; then \
		curl -X GET 127.0.0.1:32149 -H "command: test node" -H "User-Agent: AnyLog/1.23" -w "\n"
	elif [ "$(ANYLOG_TYPE)" = "query" ]; then \
		curl -X GET 127.0.0.1:32349 -H "command: test node" -H "User-Agent: AnyLog/1.23" -w "\n"
	elif [ "$(ANYLOG_TYPE)" = "publisher" ]; then \
		curl -X GET 127.0.0.1:32249 -H "command: test node" -H "User-Agent: AnyLog/1.23" -w "\n"
	elif [ "$(NODE_TYPE)" == "generic" ]; then \
		curl -X GET 127.0.0.1:32549 -H "command: test node" -H "User-Agent: AnyLog/1.23" -w "\n"
	fi
test-network:
	@if [ "$(ANYLOG_TYPE)" = "master" ]; then \
		curl -X GET 127.0.0.1:32049 -H "command: test network" -H "User-Agent: AnyLog/1.23" -w "\n"
	elif [ "$(ANYLOG_TYPE)" = "operator" ]; then \
		curl -X GET 127.0.0.1:32149 -H "command: test network" -H "User-Agent: AnyLog/1.23" -w "\n"
	elif [ "$(ANYLOG_TYPE)" = "query" ]; then \
		curl -X GET 127.0.0.1:32349 -H "command: test network" -H "User-Agent: AnyLog/1.23" -w "\n"
	elif [ "$(ANYLOG_TYPE)" = "publisher" ]; then \
		curl -X GET 127.0.0.1:32249 -H "command: test network" -H "User-Agent: AnyLog/1.23" -w "\n"
	elif [ "$(NODE_TYPE)" == "generic" ]; then \
		curl -X GET 127.0.0.1:32549 -H "command: test network" -H "User-Agent: AnyLog/1.23" -w "\n"
	fi
exec:
	docker exec -it anylog-$(ANYLOG_TYPE) bash
logs:
	docker logs anylog-$(ANYLOG_TYPE)
help:
	@echo "Usage: make [target] [anylog-type]"
	@echo "Targets:"
	@echo "  login       Log into AnyLog's Dockerhub - use ANYLOG_TYPE to set password value"
	@echo "  build       Pull the docker image"
	@echo "  up	  Start the containers"
	@echo "  attach      Attach to AnyLog instance"
	@echo "  test		 Using cURL validate node is running"
	@echo "  exec	Attach to shell interface for container"
	@echo "  down	Stop and remove the containers"
	@echo "  logs	View logs of the containers"
	@echo "  clean       Clean up volumes and network"
	@echo "  help	Show this help message"
	@echo "  supported AnyLog types: generic, master, operator, and query"
	@echo "Sample calls: make up master | make attach master | make clean master"
