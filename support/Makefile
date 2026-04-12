#----------------------------------------------------------------------
# The following provides make commands for support functions
# - Remote-GUI
# - Grafana
# - Postgres
# - Mongodb
#----------------------------------------------------------------------
#!/bin/Makefile
$(info LOADING MAKEFILE)

export SERVICE ?= ""

export CONTAINER_CMD := $(shell if command -v podman >/dev/null 2>&1; then echo "podman"; else echo "docker"; fi)
export DOCKER_COMPOSE_CMD := $(shell if command -v podman-compose >/dev/null 2>&1; then echo "podman-compose"; \
	    elif command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; else echo "docker compose"; fi)

