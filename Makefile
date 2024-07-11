# Makefile

ANYLOG_PATH := generic
ifneq ($(filter-out $@,$(MAKECMDGOALS)), )
	ANYLOG_PATH = $(filter-out $@,$(MAKECMDGOALS))
endif

export TAG := 1.3.2407
ifeq ($(shell uname -m), arm64)
	export TAG := 1.3.2405-arm64
endif

#export ANYLOG_PATH := $(shell cat docker-makefile/$(ANYLOG_PATH)/advance_configs.env | grep ANYLOG_PATH | awk -F "=" '{print $2}')
export ANYLOG_TYPE := $(shell grep NODE_TYPE docker-makefile/$(ANYLOG_PATH)/base_configs.env | cut -d '=' -f 2)

all: help
login:
	@docker login -u anyloguser --password $(ANYLOG_PATH)
build:
	docker pull anylogco/anylog-network:$(TAG)
up:
	@echo "Deploy AnyLog $(ANYLOG_TYPE)"
	ANYLOG_PATH=$(ANYLOG_PATH)  ANYLOG_TYPE=$(ANYLOG_TYPE)  envsubst < docker-makefile/docker-compose-template.yaml > docker-makefile/docker-compose.yaml
	@docker-compose -f docker-makefile/docker-compose.yaml up -d
	@rm -rf docker-makefile/docker-compose.yaml
down:
	ANYLOG_PATH=$(ANYLOG_PATH)  ANYLOG_TYPE=$(ANYLOG_TYPE) envsubst < docker-makefile/docker-compose-template.yaml > docker-makefile/docker-compose.yaml
	@docker-compose -f docker-makefile/docker-compose.yaml down
	@rm -rf docker-makefile/docker-compose.yaml
clean:
	ANYLOG_PATH=$(ANYLOG_PATH)  ANYLOG_TYPE=$(ANYLOG_TYPE) envsubst < docker-makefile/docker-compose-template.yaml > docker-makefile/docker-compose.yaml
	@docker-compose -f docker-makefile/docker-compose.yaml down
	@docker-compose -f docker-makefile/docker-compose.yaml down -v --rmi all
	@rm -rf docker-makefile/docker-compose.yaml
attach:
	docker attach --detach-keys=ctrl-d anylog-$(ANYLOG_TYPE)
node-status:
	@if [ "$(ANYLOG_PATH)" = "master" ]; then \
		curl -X GET 127.0.0.1:32049 -H "command: get status" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(ANYLOG_PATH)" = "operator" ]; then \
		curl -X GET 127.0.0.1:32149 -H "command: get status" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(ANYLOG_PATH)" = "query" ]; then \
		curl -X GET 127.0.0.1:32349 -H "command: get status" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(NODE_TYPE)" == "publisher" ]; then \
		curl -X GET 127.0.0.1:32249 -H "command: get status" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(NODE_TYPE)" == "generic" ]; then \
		curl -X GET 127.0.0.1:32549 -H "command: get status" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	fi
test-node:
	@if [ "$(ANYLOG_PATH)" = "master" ]; then \
		curl -X GET 127.0.0.1:32049 -H "command: test node" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(ANYLOG_PATH)" = "operator" ]; then \
		curl -X GET 127.0.0.1:32149 -H "command: test node" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(ANYLOG_PATH)" = "query" ]; then \
		curl -X GET 127.0.0.1:32349 -H "command: test node" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(ANYLOG_PATH)" = "publisher" ]; then \
		curl -X GET 127.0.0.1:32249 -H "command: test node" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(NODE_TYPE)" == "generic" ]; then \
		curl -X GET 127.0.0.1:32549 -H "command: test node" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	fi
test-network:
	@if [ "$(ANYLOG_PATH)" = "master" ]; then \
		curl -X GET 127.0.0.1:32049 -H "command: test network" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(ANYLOG_PATH)" = "operator" ]; then \
		curl -X GET 127.0.0.1:32149 -H "command: test network" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(ANYLOG_PATH)" = "query" ]; then \
		curl -X GET 127.0.0.1:32349 -H "command: test network" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(ANYLOG_PATH)" = "publisher" ]; then \
		curl -X GET 127.0.0.1:32249 -H "command: test network" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(NODE_TYPE)" == "generic" ]; then \
		curl -X GET 127.0.0.1:32549 -H "command: test network" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	fi
exec:
	docker exec -it anylog-$(ANYLOG_TYPE) bash
logs:
	docker logs anylog-$(ANYLOG_TYPE)
help:
	@echo "Usage: make [target] [anylog-type]"
	@echo "Targets:"
	@echo "  login       Log into AnyLog's Dockerhub - use ANYLOG_PATH to set password value"
	@echo "  build       Pull the docker image"
	@echo "  up          Start the containers"
	@echo "  attach      Attach to AnyLog instance"
	@echo "  test		 Using cURL validate node is running"
	@echo "  exec        Attach to shell interface for container"
	@echo "  down        Stop and remove the containers"
	@echo "  logs        View logs of the containers"
	@echo "  clean       Clean up volumes and network"
	@echo "  help        Show this help message"
	@echo "  supported AnyLog types: generic, master, operator, and query"
	@echo "Sample calls: make up master | make attach master | make clean master"
