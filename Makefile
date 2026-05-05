#!/bin/Makefile
$(info LOADING MAKEFILE)

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

ANYLOG_SH := bash deploy.sh

# ──────────────────────────────────────────────
# License acceptance endpoint
# ──────────────────────────────────────────────
LICENSE_URL ?= http://127.0.0.1:8001/api/license-accept

# ──────────────────────────────────────────────
all: help

# ──────────────────────────────────────────────
# License acceptance
# ──────────────────────────────────────────────
license-check: .license_accepted ## accept license agreement (auto-runs before up/pull)

.license_accepted:
	@cat LICENSE.txt
	@echo ""
	@echo "========================================"
	@echo "  License Agreement Acceptance Required"
	@echo "========================================"
	@echo ""
	@while true; do \
		printf "Full Name:    "; read NAME; \
		echo "$$NAME" | grep -qE '^[A-Za-z]{2,}( [A-Za-z]+)+$$' && break; \
		echo "  ERROR: Please enter a valid full name (first and last name, letters only)."; \
	done; \
	while true; do \
		printf "Company:      "; read COMPANY; \
		[ $$(echo "$$COMPANY" | tr -d '[:space:]' | wc -c) -ge 2 ] && break; \
		echo "  ERROR: Company name must be at least 2 characters."; \
	done; \
	while true; do \
		printf "Email:        "; read EMAIL; \
		echo "$$EMAIL" | grep -qE '^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$$' && break; \
		echo "  ERROR: Please enter a valid email address (e.g. user@example.com)."; \
	done; \
	while true; do \
		printf "Project:      "; read PROJECT; \
		[ $$(echo "$$PROJECT" | tr -d '[:space:]' | wc -c) -ge 2 ] && break; \
		echo "  ERROR: Project name must be at least 2 characters."; \
	done; \
	while true; do \
		printf "License Key:  "; read LICENSE_KEY; \
		_LQ=$$(printf '\342\200\234'); \
		_RQ=$$(printf '\342\200\235'); \
		_RESULT=$$(echo "$$LICENSE_KEY" | awk -v lq="$$_LQ" -v rq="$$_RQ" '{ \
			brace = index($$0, "{"); \
			if (brace == 0) { print "INVALID|no brace in key"; exit } \
			hex  = substr($$0, 1, brace - 1); \
			json = substr($$0, brace); \
			gsub(/\\"/, "\"", json); \
			gsub(lq, "\"", json); \
			gsub(rq, "\"", json); \
			hex_ok = (length(hex) == 256 && hex ~ /^[0-9a-f]/); \
			co_ok  = (json ~ /"company":"[^"]+"/); \
			ex_ok  = (json ~ /"expiration":"[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]"/); \
			ty_ok  = (json ~ /"type":"[^"]+"/); \
			if (hex_ok && co_ok && ex_ok && ty_ok) { print "VALID"; exit } \
			msg = "INVALID|"; \
			if (!hex_ok) msg = msg "hex must be 256 lowercase hex chars (got " length(hex) "); "; \
			if (!co_ok)  msg = msg "missing/invalid company; "; \
			if (!ex_ok)  msg = msg "missing/invalid expiration YYYY-MM-DD; "; \
			if (!ty_ok)  msg = msg "missing/invalid type; "; \
			print msg; exit \
		}'); \
		if [ "$$_RESULT" = "VALID" ]; then break; fi; \
		echo "  ERROR: Invalid license key - $$(echo "$$_RESULT" | cut -d'|' -f2)"; \
	done; \
	echo ""; \
	while true; do \
		printf "Do you accept the license agreement? [yes/no]: "; read ANSWER; \
		case "$$ANSWER" in \
			yes|no) break ;; \
			*) echo "  ERROR: Please type 'yes' or 'no'." ;; \
		esac; \
	done; \
	echo ""; \
	if [ "$$ANSWER" != "yes" ]; then \
		echo "License not accepted. Aborting."; \
		exit 1; \
	fi; \
	echo "Registering license acceptance..."; \
	python3 -c " \
import json, sys; \
print(json.dumps({ \
    'name':        sys.argv[1], \
    'company':     sys.argv[2], \
    'email':       sys.argv[3], \
    'project':     sys.argv[4], \
    'license_key': sys.argv[5], \
    'timestamp':   sys.argv[6]  \
}))" "$$NAME" "$$COMPANY" "$$EMAIL" "$$PROJECT" "$$LICENSE_KEY" \
	"$$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /tmp/license_payload.json; \
	HTTP_CODE=$$(curl -sk -o /tmp/license_response.txt -w "%{http_code}" \
		-X POST "$(LICENSE_URL)" \
		-H "Content-Type: application/json" \
		-d @/tmp/license_payload.json); \
	if [ "$$HTTP_CODE" = "200" ] || [ "$$HTTP_CODE" = "201" ]; then \
		echo "Registration successful."; \
		echo "$$NAME|$$COMPANY|$$EMAIL|$$PROJECT|$$LICENSE_KEY|$$(date -u +%Y-%m-%dT%H:%M:%SZ)" > .license_accepted; \
	else \
		echo "Warning: Registration server returned HTTP $$HTTP_CODE."; \
		echo "Response: $$(cat /tmp/license_response.txt)"; \
		printf "Continue anyway? [yes/no]: "; read CONT; \
		if [ "$$CONT" != "yes" ]; then \
			echo "Aborting."; exit 1; \
		fi; \
		echo "$$NAME|$$COMPANY|$$EMAIL|$$PROJECT|$$LICENSE_KEY|$$(date -u +%Y-%m-%dT%H:%M:%SZ)|unregistered" > .license_accepted; \
	fi

clean-license: ## reset license acceptance (re-prompts on next up/pull)
	@rm -f .license_accepted
	@echo "License acceptance cleared."

debug-key: ## diagnose license key input (run this to troubleshoot key validation)
	@printf "Paste license key: "; read K; \
	echo "--- od (raw bytes around brace) ---"; \
	echo "$$K" | od -c | grep -A2 '{'; \
	echo "--- smart quote check ---"; \
	echo "$$K" | od -c | grep -q '342 200 234' && echo "WARNING: left smart-quotes detected" || echo "no left smart-quotes"; \
	echo "$$K" | od -c | grep -q '342 200 235' && echo "WARNING: right smart-quotes detected" || echo "no right smart-quotes"; \
	echo "--- awk parse ---"; \
	_LQ=$$(printf '\342\200\234'); \
	_RQ=$$(printf '\342\200\235'); \
	echo "$$K" | awk -v lq="$$_LQ" -v rq="$$_RQ" '{ \
		brace = index($$0, "{"); \
		print "brace_pos=" brace; \
		print "hex_len=" (brace > 1 ? brace-1 : 0); \
		json = substr($$0, brace); \
		print "json_raw=[" json "]"; \
		gsub(/\\"/, "\"", json); \
		gsub(lq, "\"", json); \
		gsub(rq, "\"", json); \
		print "json_clean=[" json "]"; \
		print "co_ok=" (json ~ /"company":"[^"]+"/); \
		print "ex_ok=" (json ~ /"expiration":"[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]"/); \
		print "ty_ok=" (json ~ /"type":"[^"]+"/); \
	}'

debug-post: ## test POST to license server and show exact request/response
	@echo "--- testing POST to $(LICENSE_URL) ---"; \
	BODY="{\"name\":\"Test User\",\"company\":\"Test Co\",\"email\":\"test@test.com\",\"project\":\"test\",\"license_key\":\"testkey\",\"timestamp\":\"$$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"; \
	echo "Request body:"; \
	echo "$$BODY"; \
	echo ""; \
	echo "Response:"; \
	curl -sk -v -X POST "$(LICENSE_URL)" \
		-H "Content-Type: application/json" \
		-d "$$BODY" 2>&1

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
up: .license_accepted ## start AnyLog instance
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
	@echo ""
	@echo "Without make:"
	@echo "  bash deploy.sh help"
	@echo ""

.PHONY: license-check clean-license debug-key debug-post \
        login pull dry-run up down clean clean-all \
        logs logs-f attach exec exec-root \
        full-test test-status test-node test-network check-processes \
        check-vars help
