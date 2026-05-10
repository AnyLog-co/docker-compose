#!/bin/Makefile
$(info LOADING MAKEFILE)

# ──────────────────────────────────────────────
# Default values
# ──────────────────────────────────────────────
export IS_MANUAL    ?= false
export ANYLOG_TYPE  ?= anylog-generic
export TAG          ?= 1.4.2604-a300f9
export IMAGE        ?= anylogco/anylog-network
export TEST_CONN    ?=

# Resolve short-form aliases (operator → anylog-operator)
ifeq ($(ANYLOG_TYPE),$(filter $(ANYLOG_TYPE),generic master operator query publisher standalone-operator standalone-publisher))
    ANYLOG_TYPE := anylog-$(ANYLOG_TYPE)
    export ANYLOG_TYPE
endif

# ──────────────────────────────────────────────
# Internal — build the flag string passed to deploy.sh
# ──────────────────────────────────────────────
_FLAGS := --type $(ANYLOG_TYPE) --tag $(TAG)
ifneq ($(IMAGE),anylogco/anylog-network)
    _FLAGS += --image $(IMAGE)
endif
ifeq ($(IS_MANUAL),true)
    _FLAGS += --manual
endif
ifneq ($(TEST_CONN),)
    _FLAGS += --test-conn $(TEST_CONN)
endif

ANYLOG_SH := bash deploy.sh

# ──────────────────────────────────────────────
all: help

# ──────────────────────────────────────────────
# Docker Hub
# ──────────────────────────────────────────────
login: ## log into Docker Hub for AnyLog
	$(ANYLOG_SH) login $(_FLAGS)

pull: ## pull image from Docker Hub
	$(ANYLOG_SH) pull $(_FLAGS)

# ──────────────────────────────────────────────
# Lifecycle
# ──────────────────────────────────────────────
dry-run: ## generate docker-compose.yaml (skipped in manual mode)
	$(ANYLOG_SH) dry-run $(_FLAGS)

up: ## start AnyLog instance
	$(ANYLOG_SH) up $(_FLAGS)

down: ## stop AnyLog instance
	$(ANYLOG_SH) down $(_FLAGS)

clean: ## stop container and remove volumes
	$(ANYLOG_SH) clean $(_FLAGS)

clean-all: ## stop container, remove volumes and image
	$(ANYLOG_SH) clean-all $(_FLAGS)

# ──────────────────────────────────────────────
# Observation
# ──────────────────────────────────────────────
logs: ## view container logs
	$(ANYLOG_SH) logs $(_FLAGS)

logs-f: ## follow container logs
	$(ANYLOG_SH) logs-f $(_FLAGS)

attach: ## attach to container (ctrl-d to detach)
	$(ANYLOG_SH) attach $(_FLAGS)

exec: ## attach to bash shell (anylog user)
	$(ANYLOG_SH) exec $(_FLAGS)

exec-root: ## attach to bash shell as root
	$(ANYLOG_SH) exec-root $(_FLAGS)

# ──────────────────────────────────────────────
# Testing
# ──────────────────────────────────────────────
full-test: ## run test-status + test-node + test-network
	$(ANYLOG_SH) full-test $(_FLAGS)

test-status: ## execute `get status` against AnyLog node
	$(ANYLOG_SH) test-status $(_FLAGS)

test-node: ## execute `test node` against AnyLog node
	$(ANYLOG_SH) test-node $(_FLAGS)

test-network: ## execute `test network` against AnyLog node
	$(ANYLOG_SH) test-network $(_FLAGS)

check-processes: ## execute `get processes` against AnyLog node
	$(ANYLOG_SH) check-processes $(_FLAGS)

# ──────────────────────────────────────────────
# Info
# ──────────────────────────────────────────────
check-vars: ## show resolved variable values
	$(ANYLOG_SH) check-vars $(_FLAGS)

help: ## show this help message
	@echo ""
	@echo "Usage: make <target> [VARIABLE=value]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk -F':|##' '{ printf "  \033[36m%-20s\033[0m %s\n", $$1, $$3 }'
	@echo ""
	@echo "Variables:"
	@echo "  IS_MANUAL       Use docker run instead of docker compose (default: false)"
	@echo "  ANYLOG_TYPE     Node type: generic master operator query publisher"
	@echo "                            standalone-operator standalone-publisher"
	@echo "  TAG             Image tag                    (default: pre-develop)"
	@echo "  IMAGE           Image repository             (default: anylogco/anylog-network)"
	@echo "  TEST_CONN       ip:port for test commands    (default: auto-resolved)"
	@echo ""
	@echo "Without make:"
	@echo "  bash deploy.sh help"
	@echo ""

.PHONY: login pull dry-run up down clean clean-all \
        logs logs-f attach exec exec-root \
        full-test test-status test-node test-network check-processes \
        check-vars help