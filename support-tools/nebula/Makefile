SHELL := /bin/bash

export NEBULA_TYPE ?= lighthouse
export CERT_FILES ?=

export DOCKER_COMPOSE_CMD := $(shell \
    if command -v podman-compose >/dev/null 2>&1; then \
        echo "podman-compose"; \
    elif command -v docker-compose >/dev/null 2>&1; then \
        echo "docker-compose"; \
    else \
        echo "docker compose"; \
    fi)

all: help

create-dir: ## create directory and copy licensing / certificate files if exists
	@sudo mkdir -p /var/bin/nebula/configs
	@sudo chown -R root:root /var/bin/nebula
	@sudo chmod -R 755 /var/bin/nebula
	@if [ "$(NEBULA_TYPE)" = "lighthouse" ]; then \
	    echo "Lighthouse type — skipping certificate copy"; \
	elif [ -d "$(CERT_FILES)" ]; then \
	    sudo mv "$(CERT_FILES)"/* /var/bin/nebula/configs; \
	else \
	    echo "Missing CERT_FILES cannot continue...."; \
	    exit 1; \
	fi
up: ## bring up nebula
	@$(MAKE) create-dir NEBULA_TYPE=$(NEBULA_TYPE) CERT_FILES=$(CERT_FILES)
	@$(DOCKER_COMPOSE_CMD) -f ./docker-compose.yaml up -d
down: ## bring down nebula
	@$(DOCKER_COMPOSE_CMD) -f ./docker-compose.yaml down
clean: ## remove nebula and clean everything
	@$(DOCKER_COMPOSE_CMD) -f ./docker-compose.yaml down -v --rmi all
	@$(MAKE) remove-dir
remove-dir: ## remove directories with licensing / certificate files
	@sudo rm -rf /var/bin/nebula
help:
	@echo "Usage: make [target] [VARIABLE=value]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk -F':|##' '{ printf "  \033[36m%-20s\033[0m %s\n", $$1, $$3 }'
	@echo ""
