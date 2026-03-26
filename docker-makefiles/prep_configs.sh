#!/usr/bin/env bash
set -euo pipefail

# -------- Helpers --------
die() {
  echo "Error: $1" >&2
  exit "${2:-1}"
}

sedi() {
  if sed --version >/dev/null 2>&1; then
    sed -i "$@"
  else
    sed -i '' "$@"
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

# -------- Step 1: Normalize Single-Quoted Values to Double-Quoted --------
# Transforms:  MY_VAR='XXX'  ->  MY_VAR="XXX"
# Leaves already-double-quoted, unquoted, and comment lines untouched.
normalize_quotes() {
  local file="$1"
  echo "Normalizing quotes in: ${file}"
  sedi "s/=''/=\"\"/g" "${file}"
  sedi -E "s/^([A-Za-z_][A-Za-z0-9_]*)='(.*)'/\1=\"\2\"/" "${file}"
}

for cfg in "${CONFIG_FILES[@]}"; do
  normalize_quotes "${cfg}"
done

# -------- Step 2: Update LICENSE_KEY --------
# Multi-file layout: LICENSE_KEY lives in base_configs.env (index 1).
# Single-file layout: LICENSE_KEY lives in node_configs.env (index 0).
if [[ ${#CONFIG_FILES[@]} -gt 1 ]]; then
  BASE_ENV="${CONFIG_FILES[1]}"
else
  BASE_ENV="${CONFIG_FILES[0]}"
fi

if [[ ! -f "${BASE_ENV}" ]]; then
  echo "Failed to locate file: ${BASE_ENV} — skipping LICENSE_KEY update"
else
  # Extract raw value (everything after LICENSE_KEY=)
  CURRENT_LICENSE_KEY=$(sed -n 's/^LICENSE_KEY=//p' "${BASE_ENV}")

  # Strip trailing carriage return and any surrounding quotes
  CURRENT_LICENSE_KEY="${CURRENT_LICENSE_KEY%$'\r'}"
  CURRENT_LICENSE_KEY="${CURRENT_LICENSE_KEY#\"}" ; CURRENT_LICENSE_KEY="${CURRENT_LICENSE_KEY%\"}"
  CURRENT_LICENSE_KEY="${CURRENT_LICENSE_KEY#\'}" ; CURRENT_LICENSE_KEY="${CURRENT_LICENSE_KEY%\'}"

  if [[ -z "${CURRENT_LICENSE_KEY}" ]]; then
    echo "No LICENSE_KEY found in ${BASE_ENV} — skipping"
  else
    # Replace any internal single quotes with double quotes
    UPDATED_LICENSE_KEY="${CURRENT_LICENSE_KEY//\'/\"}"
    sedi "s|^LICENSE_KEY=.*|LICENSE_KEY=${UPDATED_LICENSE_KEY}|" "${BASE_ENV}"
    echo "LICENSE_KEY updated in ${BASE_ENV}"
  fi
fi

echo "Config update complete."
