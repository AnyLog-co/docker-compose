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
MULTI_FILE=false
if [[ -f "docker-makefiles/${NODE_CONFIGS}/.env" ]] && \
   [[ -f "docker-makefiles/${NODE_CONFIGS}/base_configs.env" ]] && \
   [[ -f "docker-makefiles/${NODE_CONFIGS}/advance_configs.env" ]]; then
  MULTI_FILE=true
  CONFIG_FILES=(
    "docker-makefiles/${NODE_CONFIGS}/.env"
    "docker-makefiles/${NODE_CONFIGS}/base_configs.env"
    "docker-makefiles/${NODE_CONFIGS}/advance_configs.env"
  )
  BASE_ENV="docker-makefiles/${NODE_CONFIGS}/base_configs.env"
elif [[ -f "docker-makefiles/${NODE_CONFIGS}/node_configs.env" ]]; then
  CONFIG_FILES=("docker-makefiles/${NODE_CONFIGS}/node_configs.env")
  BASE_ENV="docker-makefiles/${NODE_CONFIGS}/node_configs.env"
else
  die "Missing configuration file(s) for '${NODE_CONFIGS}', cannot continue"
fi

SNAPSHOT_DIR="docker-makefiles/${NODE_CONFIGS}"
SNAPSHOT_FILE="${SNAPSHOT_DIR}/formatted_node_configs.env"

# -------- Step 1: Copy source -> formatted_node_configs.env --------
# node_configs.env is never modified — all transformations happen on the snapshot only.
[[ -f "${SNAPSHOT_FILE}" ]] && rm -f "${SNAPSHOT_FILE}"
echo "Generating snapshot: ${SNAPSHOT_FILE}"

if [[ "${MULTI_FILE}" == "true" ]]; then
  {
    for cfg in "${CONFIG_FILES[@]}"; do
      echo "# ---- $(basename "${cfg}") ----"
      cat "${cfg}"
      echo ""
    done
  } > "${SNAPSHOT_FILE}"
else
  cp "${BASE_ENV}" "${SNAPSHOT_FILE}"
fi

# -------- Step 2: Fix quotation issues in snapshot --------
# Transforms:  MY_VAR='XXX'  ->  MY_VAR="XXX"
# Leaves already-double-quoted, unquoted, and comment lines untouched.
sedi "s/=''/=\"\"/g" "${SNAPSHOT_FILE}"
sedi -E "s/^([A-Za-z_][A-Za-z0-9_]*)='(.*)'/\1=\"\2\"/" "${SNAPSHOT_FILE}"

# -------- Step 3: Normalize LICENSE_KEY in snapshot --------
# Strip surrounding quotes, replace internal single quotes with double quotes.
CURRENT_LICENSE_KEY=$(sed -n 's/^LICENSE_KEY=//p' "${BASE_ENV}")
CURRENT_LICENSE_KEY="${CURRENT_LICENSE_KEY%$'\r'}"
CURRENT_LICENSE_KEY="${CURRENT_LICENSE_KEY#\"}" ; CURRENT_LICENSE_KEY="${CURRENT_LICENSE_KEY%\"}"
CURRENT_LICENSE_KEY="${CURRENT_LICENSE_KEY#\'}" ; CURRENT_LICENSE_KEY="${CURRENT_LICENSE_KEY%\'}"

if [[ -z "${CURRENT_LICENSE_KEY}" ]]; then
  echo "No LICENSE_KEY found in ${BASE_ENV} — skipping"
else
  UPDATED_LICENSE_KEY="${CURRENT_LICENSE_KEY//\'/\"}"
  sedi "s|^LICENSE_KEY=.*|LICENSE_KEY=${UPDATED_LICENSE_KEY}|" "${SNAPSHOT_FILE}"
  echo "LICENSE_KEY updated in snapshot"
fi

# -------- Step 4: Set permissions --------
# 644: owner-writable so build_docker_compose.sh can resolve and write vars (e.g. CONTAINER_NAME);
# group/other read-only so it's not accidentally hand-edited.
chmod 644 "${SNAPSHOT_FILE}"

echo "Config update complete."