#!/usr/bin/env bash

# -------- Helpers --------
die() {
  echo "Error: $1" >&2
  exit "${2:-1}"
}

sedi() {
  local expr="$1"
  shift

  if [ "$#" -eq 0 ]; then
    echo "sedi: no files provided" >&2
    return 1
  fi

  if sed --version >/dev/null 2>&1; then
    sed -i "$expr" "$@"
  else
    sed -i '' "$expr" "$@"
  fi
}

# -------- Args --------
NODE_CONFIGS=${1:-anylog-generic}

# -------- Locate Config Files --------
if [[ -f "docker-makefiles/${NODE_CONFIGS}/.env" ]] && \
   [[ -f "docker-makefiles/${NODE_CONFIGS}/base_configs.env" ]] && \
   [[ -f "docker-makefiles/${NODE_CONFIGS}/advance_configs.env" ]]; then
  CONFIG_FILES=(
    "docker-makefiles/${NODE_CONFIGS}/.env"
    "docker-makefiles/${NODE_CONFIGS}/base_configs.env"
    "docker-makefiles/${NODE_CONFIGS}/advance_configs.env"
  )
elif [[ -f "docker-makefiles/${NODE_CONFIGS}/node_configs.env" ]]; then
  CONFIG_FILES=("docker-makefiles/${NODE_CONFIGS}/node_configs.env")
else
  die "Missing configuration file(s) for '${NODE_CONFIGS}', cannot continue"
fi

# -------- Generate Read-Only Snapshot Copy --------
# Filename: {formatted_node_name}.env  (hyphens -> underscores, lowercased)
# Empty-value vars ( VAR="" ) are commented out in the copy.
FORMATTED_NODE_NAME=$(echo "${NODE_CONFIGS}" | tr '[:upper:]' '[:lower:]' | tr '-' '_')
SNAPSHOT_DIR="docker-makefiles/${NODE_CONFIGS}"
SNAPSHOT_FILE="${SNAPSHOT_DIR}/formatted_node_configs.env"

# -------- Generate Docker Compose File --------
DOCKER_DIR="docker-makefiles/docker-compose-files"
DOCKER_FILE="${DOCKER_DIR}/${NODE_CONFIGS}-docker-compose.yaml"
NODE_NAME_FILE="$(dirname "${SNAPSHOT_FILE}")/NODE_NAME.txt"

# -------- Remove files --------

printf "Warning: this will fully reset this node's deployment configuration.\nThe node will be treated as new on next startup and assigned a new identity.\nProceed? [y/N]: "
read -r CONFIRM_DELETE

if [[ "${CONFIRM_DELETE}" == "y" || "${CONFIRM_DELETE}" == "Y" ]]; then
  rm -rf "${DOCKER_FILE}" "${SNAPSHOT_FILE}" "${NODE_NAME_FILE}"
  if [[ -d "${DOCKER_DIR}" && -z "$(ls -A "${DOCKER_DIR}")" ]]; then
    rm -rf "${DOCKER_DIR}"
  fi
else echo "Deletion cancelled." ; fi