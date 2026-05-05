#!/usr/bin/env make
#----------------------------------------------------------------------
# Support-services Makefile
#
# Hardcoded defaults: grafana | remote-gui | postgres | mongodb
# Custom instances  : add any subdirectory with a configs.yaml —
#                     no Makefile edits needed.
#
# Aliases: gui -> remote-gui | psql -> postgres | mongo -> mongodb
#
# Examples:
#   make up                           # start all 4 default services
#   make up   SERVICE=grafana         # start one service by dir name
#   make up   SERVICE=psql            # alias for postgres
#   make up   SERVICE=postgres-prod   # start a custom extra instance
#   make down SERVICE=mongo
#   make logs SERVICE=grafana
#   make exec SERVICE=postgres-prod
#   make list                         # show every discovered service
#----------------------------------------------------------------------
$(info LOADING MAKEFILE)

export CONTAINER_CMD := \
    $(shell if command -v podman >/dev/null 2>&1; then echo "podman"; else echo "docker"; fi)
export DOCKER_COMPOSE_CMD := \
    $(shell if   command -v podman-compose  >/dev/null 2>&1; then echo "podman-compose"; \
            elif command -v docker-compose  >/dev/null 2>&1; then echo "docker-compose"; \
            else echo "docker compose"; fi)

SUPPORT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

# ── Default set — started / stopped when SERVICE is not specified ──────
DEFAULT_SERVICES := remote-gui grafana postgres mongodb

# ── Auto-discover every subdir that contains a configs.yaml ───────────
DISCOVERED_SERVICES := $(patsubst $(SUPPORT_DIR)%/configs.yaml,%,\
                           $(wildcard $(SUPPORT_DIR)*/configs.yaml))

# ── Resolve common aliases → canonical directory name ─────────────────
_SVC := $(SERVICE)
ifeq ($(_SVC),gui)
  override _SVC := remote-gui
endif
ifeq ($(_SVC),psql)
  override _SVC := postgres
endif
ifeq ($(_SVC),mongo)
  override _SVC := mongodb
endif

all: help

# ======================================================================
# dry-run — (re)generate docker-compose.yml from configs.yaml
# ======================================================================
dry-run: ## Generate docker-compose.yml for all discovered services (or SERVICE=one)
	@if [ "$(_SVC)" = "" ]; then \
	    for svc in $(DISCOVERED_SERVICES); do \
	        echo "-> Building compose for $$svc"; \
	        bash $(SUPPORT_DIR)docker_compose_builder.sh \
	            $(SUPPORT_DIR)$$svc/configs.yaml \
	            $(SUPPORT_DIR)$$svc/docker-compose.yml; \
	    done; \
	elif [ -f "$(SUPPORT_DIR)$(_SVC)/configs.yaml" ]; then \
	    echo "-> Building compose for $(_SVC)"; \
	    bash $(SUPPORT_DIR)docker_compose_builder.sh \
	        $(SUPPORT_DIR)$(_SVC)/configs.yaml \
	        $(SUPPORT_DIR)$(_SVC)/docker-compose.yml; \
	else \
	    echo "ERROR: '$(SUPPORT_DIR)$(_SVC)/configs.yaml' not found"; exit 1; \
	fi

# ======================================================================
# Internal targets — always called with SVC=<dirname>
# ======================================================================

# Abort early if the service directory does not exist
_validate:
	@if [ ! -d "$(SUPPORT_DIR)$(SVC)" ]; then \
	    echo ""; \
	    echo "ERROR: No directory '$(SUPPORT_DIR)$(SVC)'"; \
	    echo "       To add a service, create the directory and place a configs.yaml inside."; \
	    echo "       To list known services, run:  make list"; \
	    echo ""; \
	    exit 1; \
	fi

# Generate docker-compose.yml on-demand when it is missing
_ensure-compose: _validate
	@if [ ! -f "$(SUPPORT_DIR)$(SVC)/docker-compose.yml" ]; then \
	    if [ ! -f "$(SUPPORT_DIR)$(SVC)/configs.yaml" ]; then \
	        echo "ERROR: No configs.yaml in '$(SUPPORT_DIR)$(SVC)/'"; exit 1; \
	    fi; \
	    echo "  -> Generating docker-compose.yml for $(SVC) ..."; \
	    bash $(SUPPORT_DIR)docker_compose_builder.sh \
	        $(SUPPORT_DIR)$(SVC)/configs.yaml \
	        $(SUPPORT_DIR)$(SVC)/docker-compose.yml; \
	fi

_up: _ensure-compose
	@echo "Deploying: $(SVC)"
	$(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)$(SVC)/docker-compose.yml up -d

_down: _validate
	@echo "Stopping: $(SVC)"
	$(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)$(SVC)/docker-compose.yml down

_clean: _validate
	@echo "Removing (+ volumes): $(SVC)"
	$(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)$(SVC)/docker-compose.yml down -v

_clean-all: _validate
	@echo "Removing (+ volumes + image): $(SVC)"
	$(DOCKER_COMPOSE_CMD) -f $(SUPPORT_DIR)$(SVC)/docker-compose.yml down -v --rmi all

_logs: _validate
	@echo "Logs: $(SVC)"
	$(CONTAINER_CMD) logs $(SVC)

_logs-f: _validate
	@echo "Logs (follow): $(SVC)"
	$(CONTAINER_CMD) logs -f $(SVC)

# Exec into service — uses the right client per service type:
#   postgres* -> psql   |   mongo* -> mongosh   |   everything else -> bash
_attach: _validate
	@if echo "$(SVC)" | grep -q "^postgres"; then \
	    $(CONTAINER_CMD) exec -it $(SVC) psql -U admin -d postgres; \
    elif echo "$(SVC)" | grep -q "^mongo"; then \
	    $(CONTAINER_CMD) exec -it $(SVC) mongosh; \
	else \
	    echo "Unsupported attach option to service $(SERVICE)"; \
    fi

_exec: _validate
	$(CONTAINER_CMD) exec -it $(SVC) /bin/bash

# ======================================================================
# Public targets — iterate defaults or delegate to _<op> SVC=...
# ======================================================================

# Shared shell snippet: loop over DEFAULT_SERVICES and call an internal target
# Usage (inside a recipe): $(call _each, _up)
define _each
	for svc in $(DEFAULT_SERVICES); do \
	    if [ -d "$(SUPPORT_DIR)$$svc" ]; then \
	        $(MAKE) -s $(1) SVC=$$svc || true; \
	    else \
	        echo "  (skipping $$svc — directory not found)"; \
	    fi; \
	done
endef

up: ## Start service(s). Omit SERVICE to start all defaults; SERVICE=<dir> for one
	@if [ "$(_SVC)" = "" ]; then \
	    $(call _each,_up); \
	else \
	    $(MAKE) -s _up SVC=$(_SVC); \
	fi

down: ## Stop service(s). Omit SERVICE to stop all defaults; SERVICE=<dir> for one
	@if [ "$(_SVC)" = "" ]; then \
	    $(call _each,_down); \
	else \
	    $(MAKE) -s _down SVC=$(_SVC); \
	fi

clean: ## Stop + remove volumes. Omit SERVICE for all defaults; SERVICE=<dir> for one
	@if [ "$(_SVC)" = "" ]; then \
	    $(call _each,_clean); \
	else \
	    $(MAKE) -s _clean SVC=$(_SVC); \
	fi

clean-all: ## Stop + remove volumes + images. Omit SERVICE for all defaults; SERVICE=<dir> for one
	@if [ "$(_SVC)" = "" ]; then \
	    $(call _each,_clean-all); \
	else \
	    $(MAKE) -s _clean-all SVC=$(_SVC); \
	fi

logs: ## Print logs — SERVICE=<dir> required  (e.g. SERVICE=grafana)
	@if [ "$(_SVC)" = "" ]; then \
	    echo "ERROR: SERVICE is required.  Example: make logs SERVICE=grafana"; exit 1; \
	fi
	@$(MAKE) -s _logs SVC=$(_SVC)

logs-f: ## Follow logs — SERVICE=<dir> required  (e.g. SERVICE=postgres-prod)
	@if [ "$(_SVC)" = "" ]; then \
	    echo "ERROR: SERVICE is required.  Example: make logs-f SERVICE=postgres"; exit 1; \
	fi
	@$(MAKE) -s _logs-f SVC=$(_SVC)

attach: ## Attach the native client (psql / mongosh) — SERVICE=<dir> required
	@if [ "$(_SVC)" = "" ]; then \
	    echo "ERROR: SERVICE is required.  Example: make attach SERVICE=postgres"; exit 1; \
	fi
	@$(MAKE) -s _attach SVC=$(_SVC)

exec: ## Open a bash shell in the container — SERVICE=<dir> required
	@if [ "$(_SVC)" = "" ]; then \
	    echo "ERROR: SERVICE is required.  Example: make exec SERVICE=mongodb"; exit 1; \
	fi
	@$(MAKE) -s _exec SVC=$(_SVC)

# ======================================================================
# Utility
# ======================================================================
list: ## List default and all auto-discovered services
	@echo ""
	@echo "Default services   : $(DEFAULT_SERVICES)"
	@echo "Discovered services: $(DISCOVERED_SERVICES)"
	@echo ""
	@echo "Tip: add a new subdir with configs.yaml to register a custom instance."
	@echo "     Example: postgres-prod/configs.yaml  =>  make up SERVICE=postgres-prod"
	@echo ""

help: ## Show this help message
	@echo ""
	@echo "Usage: make <target> [SERVICE=<service>]"
	@echo ""
	@echo "  Default services : $(DEFAULT_SERVICES)"
	@echo "  Aliases          : gui -> remote-gui  |  psql -> postgres  |  mongo -> mongodb"
	@echo "  Custom instances : create subdir + configs.yaml, then use SERVICE=<dirname>"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) \
	    | awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'
	@echo ""

.PHONY: all dry-run list help \
        up down clean clean-all logs logs-f attach exec \
        _validate _ensure-compose \
        _up _down _clean _clean-all _logs _logs-f _attach _exec