#!/bin/Makefile

export ANYLOG_TYPE := generic
ifneq ($(filter-out $@,$(MAKECMDGOALS)), )
   export ANYLOG_TYPE = $(filter-out $@,$(MAKECMDGOALS))
endif

export TAG := 1.3.2408-beta10
ifeq ($(shell uname -m), arm64)
    TAG := 1.3.2405-arm64
endif

export NODE_TYPE ?= 127.0.0.1
export REST_PORT := $(shell cat docker-makefile/${ANYLOG_TYPE}-configs/base_configs.env | grep ANYLOG_REST_PORT | awk -F "=" '{print $$2}')

all: help
login:
	@docker login docker.io -u anyloguser --password $(ANYLOG_TYPE)
build:
	docker pull docker.io/anylogco/anylog-network:$(TAG)
dry-run:
	@echo "Dry Run $(ANYLOG_TYPE)"
	ANYLOG_TYPE=$(ANYLOG_TYPE) envsubst < docker-makefile/docker-compose-template.yaml > docker-makefile/docker-compose.yaml
up:
	@echo "Deploy AnyLog $(ANYLOG_TYPE)"
	ANYLOG_TYPE=$(ANYLOG_TYPE) envsubst < docker-makefile/docker-compose-template.yaml > docker-makefile/docker-compose.yaml
	@docker compose -f docker-makefile/docker-compose.yaml up -d
	@rm -rf docker-makefile/docker-compose.yaml
down:
	ANYLOG_TYPE=$(ANYLOG_TYPE) envsubst < docker-makefile/docker-compose-template.yaml > docker-makefile/docker-compose.yaml
	@docker compose -f docker-makefile/docker-compose.yaml down
	@rm -rf docker-makefile/docker-compose.yaml
clean-vols: # clean only volumes
	ANYLOG_TYPE=$(ANYLOG_TYPE) envsubst < docker-makefile/docker-compose-template.yaml > docker-makefile/docker-compose.yaml
	@docker compose -f docker-makefile/docker-compose.yaml down --volume
	@rm -rf docker-makefile/docker-compose.yaml
clean: # clean volumes + image
	ANYLOG_TYPE=$(ANYLOG_TYPE) envsubst < docker-makefile/docker-compose-template.yaml > docker-makefile/docker-compose.yaml
	@docker compose -f docker-makefile/docker-compose.yaml down --volumes --rmi
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
	@echo "Test Node Against: $(HZN_LISTEN_IP):$(REST_PORT)"
	@curl -X GET $(HZN_LISTEN_IP):$(REST_PORT)
	@curl -X GET $(HZN_LISTEN_IP):$(REST_PORT) -H "command: test node"
test-network:
	@echo "Test Network Against: $(HZN_LISTEN_IP):$(REST_PORT)"
	@curl -X GET $(HZN_LISTEN_IP):$(REST_PORT) -H "command: test network"
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
