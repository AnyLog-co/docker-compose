# Makefile

ANYLOG_TYPE := generic
ifneq ($(filter-out $@,$(MAKECMDGOALS)), )
	ANYLOG_TYPE = $(filter-out $@,$(MAKECMDGOALS))
endif

export TAG := latest
ifeq ($(shell uname -m), arm64)
	export TAG := latest-arm64
endif

all: help
login:
	@bash installations/docker_credentials.sh $(ANYLOG_TYPE)
build:
	docker pull anylogco/anylog-network:$(TAG)
up:
	@echo "Deploy AnyLog with config file: anylog_$(ANYLOG_TYPE).env"
	ANYLOG_TYPE=$(ANYLOG_TYPE) envsubst < docker_makefile/docker-compose-template.yaml > docker_makefile/docker-compose.yaml
	@docker-compose -f docker_makefile/docker-compose.yaml up -d
	@rm -rf docker_makefile/docker-compose.yaml
down:
	ANYLOG_TYPE=$(ANYLOG_TYPE) envsubst < docker_makefile/docker-compose-template.yaml > docker_makefile/docker-compose.yaml
	@docker-compose -f docker_makefile/docker-compose.yaml down
	@rm -rf docker_makefile/docker-compose.yaml
clean:
	ANYLOG_TYPE=$(ANYLOG_TYPE) envsubst < docker_makefile/docker-compose-template.yaml > docker_makefile/docker-compose.yaml
	@docker-compose -f docker_makefile/docker-compose.yaml down -v --rmi all
	@rm -rf docker_makefile/docker-compose.yaml
attach:
	docker attach --detach-keys=ctrl-d edgelake-$(ANYLOG_TYPE)
node-status:
	@if [ "$(ANYLOG_TYPE)" = "master" ]; then \
		curl -X GET 127.0.0.1:32049 -H "command: get status" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(ANYLOG_TYPE)" = "operator" ]; then \
		curl -X GET 127.0.0.1:32149 -H "command: get status" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(ANYLOG_TYPE)" = "query" ]; then \
		curl -X GET 127.0.0.1:32349 -H "command: get status" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(NODE_TYPE)" == "publisher" ]; then \
		curl -X GET 127.0.0.1:32249 -H "command: get status" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(NODE_TYPE)" == "generic" ]; then \
		curl -X GET 127.0.0.1:32549 -H "command: get status" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	fi
test-node:
	@if [ "$(ANYLOG_TYPE)" = "master" ]; then \
		curl -X GET 127.0.0.1:32049 -H "command: test node" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(ANYLOG_TYPE)" = "operator" ]; then \
		curl -X GET 127.0.0.1:32149 -H "command: test node" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(ANYLOG_TYPE)" = "query" ]; then \
		curl -X GET 127.0.0.1:32349 -H "command: test node" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(ANYLOG_TYPE)" = "publisher" ]; then \
		curl -X GET 127.0.0.1:32249 -H "command: test node" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(NODE_TYPE)" == "generic" ]; then \
		curl -X GET 127.0.0.1:32549 -H "command: test node" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	fi
test-network:
	@if [ "$(ANYLOG_TYPE)" = "master" ]; then \
		curl -X GET 127.0.0.1:32049 -H "command: test network" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(ANYLOG_TYPE)" = "operator" ]; then \
		curl -X GET 127.0.0.1:32149 -H "command: test network" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(ANYLOG_TYPE)" = "query" ]; then \
		curl -X GET 127.0.0.1:32349 -H "command: test network" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(ANYLOG_TYPE)" = "publisher" ]; then \
		curl -X GET 127.0.0.1:32249 -H "command: test network" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	elif [ "$(NODE_TYPE)" == "generic" ]; then \
		curl -X GET 127.0.0.1:32549 -H "command: test network" -H "User-Agent: AnyLog/1.23" -w "\n"; \
	fi
exec:
	docker exec -it edgelake-$(ANYLOG_TYPE) bash
logs:
	docker logs edgelake-$(ANYLOG_TYPE)
help:
	@echo "Usage: make [target] [edgelake-type]"
	@echo "Targets:"
	@echo "  login		 Log into AnyLog's Dockerhub - use ANYLOG_TYPE to set password valuue"
	@echo "  build       Pull the docker image"
	@echo "  up          Start the containers"
	@echo "  attach      Attach to EdgeLake instance"
	@echo "  test		 Using cURL validate node is running"
	@echo "  exec        Attach to shell interface for container"
	@echo "  down        Stop and remove the containers"
	@echo "  logs        View logs of the containers"
	@echo "  clean       Clean up volumes and network"
	@echo "  help        Show this help message"
	@echo "  supported EdgeLake types: generic, master, operator, and query"
	@echo "Sample calls: make up master | make attach master | make clean master"
