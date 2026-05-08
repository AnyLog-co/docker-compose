#!/bin/Makefile
$(info LOADING MAKEFILE)

SHELL := /bin/bash

# ──────────────────────────────────────────────
# Default values
# ──────────────────────────────────────────────
export IS_MANUAL    ?= false
export ANYLOG_TYPE  ?= anylog-generic
export TAG          ?= 1.4.2604
export IMAGE        ?= anylogco/anylog-network
export TEST_CONN    ?=
export LICENSE_KEY  ?=

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

ANYLOG_SH := bash ./docker-makefiles/deploy.sh


# ──────────────────────────────────────────────
# Docker Hub
# ──────────────────────────────────────────────
login: ## log into Docker Hub for AnyLog
	$(ANYLOG_SH) login $(_FLAGS)

pull: .license_accepted ## pull image from Docker Hub
	$(ANYLOG_SH) pull $(_FLAGS)

# ──────────────────────────────────────────────
# Lifecycle
# ──────────────────────────────────────────────
dry-run: ## generate docker-compose.yaml (skipped in manual mode)
	$(ANYLOG_SH) dry-run $(_FLAGS)

# Read LICENSE_KEY from sentinel and export into the environment so deploy.sh
# and docker compose both inherit it — matching the same export pattern used
# by IS_MANUAL, ANYLOG_TYPE, TAG etc. at the top of this file.
up: .license_accepted syslog-setup ## start AnyLog instance (auto-configures rsyslog if SYSLOG_MONITORING=true)
	@export LICENSE_KEY=$$(cut -d'|' -f5 .license_accepted); $(ANYLOG_SH) up $(_FLAGS)

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
# Syslog forwarding
# ──────────────────────────────────────────────
# Reads SYSLOG_MONITORING and ANYLOG_BROKER_PORT from
# docker-makefiles/$(ANYLOG_TYPE)/node_configs.env — the same file deploy.sh
# passes as --env-file to docker run / docker compose.
#
#   Linux (Ubuntu)  — rsyslog drop-in /etc/rsyslog.d/60-custom-forwarding.conf (TCP)
#   macOS (Darwin)  — native syslogd via /etc/syslog.conf append (UDP)
#                     macOS syslogd only supports UDP forwarding; ensure
#                     ANYLOG_BROKER_PORT is open for UDP on the AnyLog node.
#
# Targets:
#   syslog-setup   — install the forwarding rule (idempotent)
#   syslog-remove  — remove the forwarding rule
#
# Both targets are no-ops when SYSLOG_MONITORING != true in node_configs.env.

NODE_CONFIGS = docker-makefiles/$(ANYLOG_TYPE)/node_configs.env

syslog-setup: ## configure syslog to forward to AnyLog msg port (reads node_configs.env)
	@SYSLOG_MON=$$(grep -E '^SYSLOG_MONITORING=' $(NODE_CONFIGS) 2>/dev/null | head -1 | sed 's/^[^=]*=//;s/[[:space:]]*$$//'); \
	BROKER_PORT=$$(grep -E '^ANYLOG_BROKER_PORT=' $(NODE_CONFIGS) 2>/dev/null | head -1 | sed 's/^[^=]*=//;s/[[:space:]]*$$//'); \
	if [ "$$SYSLOG_MON" != "true" ]; then \
		echo "syslog-setup: SYSLOG_MONITORING is not 'true' in $(NODE_CONFIGS) — skipping."; \
		exit 0; \
	fi; \
	if [ -z "$$BROKER_PORT" ]; then \
		echo "ERROR: ANYLOG_BROKER_PORT is not set in $(NODE_CONFIGS)."; \
		exit 1; \
	fi; \
	\
	OS=$$(uname -s); \
	MARKER="# anylog-forwarding port=$$BROKER_PORT"; \
	\
	case "$$OS" in \
	\
	Linux) \
		if ! command -v rsyslogd >/dev/null 2>&1; then \
			echo "ERROR: rsyslogd not found. Install with: sudo apt-get install rsyslog"; \
			exit 1; \
		fi; \
		CONF_FILE="/etc/rsyslog.d/60-custom-forwarding.conf"; \
		if [ -f "$$CONF_FILE" ] && grep -qF "$$MARKER" "$$CONF_FILE" 2>/dev/null; then \
			echo "syslog-setup: rule already present in $$CONF_FILE — nothing to do."; \
			exit 0; \
		fi; \
		echo "Installing AnyLog rsyslog rule → $$CONF_FILE (TCP port $$BROKER_PORT)"; \
		printf '%s\n' \
			"$$MARKER" \
			"\$$template remote-incoming-logs, \"/var/log/remote/%%HOSTNAME%%.log\"" \
			"*.* ?remote-incoming-logs" \
			"*.* action(type=\"omfwd\" target=\"127.0.0.1\" port=\"$$BROKER_PORT\" protocol=\"tcp\")" \
			| sudo tee "$$CONF_FILE" > /dev/null; \
		sudo systemctl restart rsyslog \
			&& echo "rsyslog restarted." \
			|| echo "WARNING: could not restart rsyslog — run: sudo systemctl restart rsyslog"; \
		;; \
	\
	Darwin) \
		CONF_FILE="/etc/syslog.conf"; \
		if [ ! -f "$$CONF_FILE" ]; then \
			echo "ERROR: $$CONF_FILE not found — is this macOS 10.12 or later?"; \
			echo "       On macOS 12+ you may need to re-enable syslogd via launchctl."; \
			exit 1; \
		fi; \
		if grep -qF "$$MARKER" "$$CONF_FILE" 2>/dev/null; then \
			echo "syslog-setup: rule already present in $$CONF_FILE — nothing to do."; \
			exit 0; \
		fi; \
		echo "Installing AnyLog syslog rule → $$CONF_FILE (UDP port $$BROKER_PORT)"; \
		printf '\n%s\n%s\n' \
			"$$MARKER" \
			"*.* @127.0.0.1:$$BROKER_PORT" \
			| sudo tee -a "$$CONF_FILE" > /dev/null; \
		sudo launchctl kickstart -k system/com.apple.syslogd \
			&& echo "syslogd restarted." \
			|| echo "WARNING: could not restart syslogd — run: sudo launchctl kickstart -k system/com.apple.syslogd"; \
		;; \
	\
	*) \
		echo "ERROR: Unsupported OS '$$OS'. Only Linux and macOS are supported."; \
		exit 1; \
		;; \
	esac; \
	echo "syslog-setup: done."

syslog-remove: ## remove the AnyLog syslog forwarding rule
	@SYSLOG_MON=$$(grep -E '^SYSLOG_MONITORING=' $(NODE_CONFIGS) 2>/dev/null | head -1 | sed 's/^[^=]*=//;s/[[:space:]]*$$//'); \
	if [ "$$SYSLOG_MON" != "true" ]; then \
		echo "syslog-remove: SYSLOG_MONITORING is not 'true' in $(NODE_CONFIGS) — skipping."; \
		exit 0; \
	fi; \
	BROKER_PORT=$$(grep -E '^ANYLOG_BROKER_PORT=' $(NODE_CONFIGS) 2>/dev/null | head -1 | sed 's/^[^=]*=//;s/[[:space:]]*$$//'); \
	OS=$$(uname -s); \
	MARKER="# anylog-forwarding port=$$BROKER_PORT"; \
	\
	case "$$OS" in \
	\
	Linux) \
		CONF_FILE="/etc/rsyslog.d/60-custom-forwarding.conf"; \
		if [ ! -f "$$CONF_FILE" ]; then \
			echo "syslog-remove: $$CONF_FILE not found — nothing to remove."; \
			exit 0; \
		fi; \
		sudo rm -f "$$CONF_FILE"; \
		echo "Removed $$CONF_FILE"; \
		sudo systemctl restart rsyslog \
			&& echo "rsyslog restarted." \
			|| echo "WARNING: could not restart rsyslog — run: sudo systemctl restart rsyslog"; \
		;; \
	\
	Darwin) \
		CONF_FILE="/etc/syslog.conf"; \
		if ! grep -qF "$$MARKER" "$$CONF_FILE" 2>/dev/null; then \
			echo "syslog-remove: AnyLog rule not found in $$CONF_FILE — nothing to remove."; \
			exit 0; \
		fi; \
		sudo sed -i '' "/^$$MARKER$$/{ N; d; }" "$$CONF_FILE"; \
		echo "Removed AnyLog forwarding rule from $$CONF_FILE"; \
		sudo launchctl kickstart -k system/com.apple.syslogd \
			&& echo "syslogd restarted." \
			|| echo "WARNING: could not restart syslogd — run: sudo launchctl kickstart -k system/com.apple.syslogd"; \
		;; \
	\
	*) \
		echo "ERROR: Unsupported OS '$$OS'."; \
		exit 1; \
		;; \
	esac; \
	echo "syslog-remove: done."

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
	@echo "  TAG             Image tag                    (default: 1.4.2604)"
	@echo "  IMAGE           Image repository             (default: anylogco/anylog-network)"
	@echo "  TEST_CONN       ip:port for test commands    (default: auto-resolved)"
	@echo "  LICENSE_KEY     License key (prompted on first run, stored in .license_accepted)"
	@echo "  LICENSE_URL     License registration endpoint (default: http://127.0.0.1:8001/api/license-accept)"
	@echo "  SYSLOG_MONITORING   Set to 'true' in node_configs.env to enable syslog → AnyLog forwarding"
	@echo "                      Linux: rsyslog drop-in (TCP)  |  macOS: syslogd append (UDP)"
	@echo "  ANYLOG_BROKER_PORT     Port syslog forwards to (read from node_configs.env)"
	@echo ""
	@echo "Without make:"
	@echo "  bash deploy.sh help"
	@echo ""

.PHONY: license-check clean-license debug-key debug-post \
        login pull dry-run up down clean clean-all \
        logs logs-f attach exec exec-root \
        full-test test-status test-node test-network check-processes \
        check-vars help \
        syslog-setup syslog-remove
