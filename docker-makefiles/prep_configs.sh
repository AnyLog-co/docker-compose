#!/usr/bin/env bash
#set -euo pipefail

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

_parse_license_field() {
  local field="$1"
  local key="$2"
  echo "${key}" | awk -v field="${field}" '{
    brace = index($0, "{")
    if (brace == 0) { print ""; exit }
    json = substr($0, brace)
    gsub(/\\"/, "\"", json)
    needle = "\"" field "\""
    pos = index(json, needle)
    if (pos == 0) { print ""; exit }
    rest = substr(json, pos + length(needle))
    colon = index(rest, ":")
    if (colon == 0) { print ""; exit }
    rest = substr(rest, colon + 1)
    sub(/^[ \t]*/, "", rest)
    if (substr(rest, 1, 1) != "\"") { print ""; exit }
    rest = substr(rest, 2)
    end_pos = index(rest, "\"")
    if (end_pos == 0) { print ""; exit }
    print substr(rest, 1, end_pos - 1)
  }'
}

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

# -------- Step 2.5: Resolve COMPANY_NAME --------
# Priority: explicit COMPANY_NAME > non-Guest license company > acme
COMPANY_ENV_FILE=""
for cfg in "${CONFIG_FILES[@]}"; do
  if grep -q '^COMPANY_NAME=' "${cfg}" 2>/dev/null; then
    COMPANY_ENV_FILE="${cfg}"
    break
  fi
done

if [[ -n "${COMPANY_ENV_FILE}" ]]; then
  CURRENT_COMPANY_NAME=$(grep -m1 '^COMPANY_NAME=' "${COMPANY_ENV_FILE}" | cut -d= -f2- | tr -d '"\r')

  if [[ -n "${CURRENT_COMPANY_NAME}" ]]; then
    echo "COMPANY_NAME already set: ${CURRENT_COMPANY_NAME}"
  else
    RESOLVED_COMPANY_NAME="acme"
    if [[ -n "${CURRENT_LICENSE_KEY:-}" ]]; then
      LICENSE_COMPANY=$(_parse_license_field "company" "${CURRENT_LICENSE_KEY}")
      if [[ -n "${LICENSE_COMPANY}" && "${LICENSE_COMPANY}" != "Guest" ]]; then
        RESOLVED_COMPANY_NAME="${LICENSE_COMPANY}"
      fi
    fi
    sedi "s|^COMPANY_NAME=.*|COMPANY_NAME=\"${RESOLVED_COMPANY_NAME}\"|" "${COMPANY_ENV_FILE}"
    echo "COMPANY_NAME resolved to: ${RESOLVED_COMPANY_NAME}"
  fi
fi

# -------- Step 3: Generate Read-Only Snapshot Copy --------
# Filename: {formatted_node_name}.env  (hyphens -> underscores, lowercased)
# Empty-value vars ( VAR="" ) are commented out in the copy.
FORMATTED_NODE_NAME=$(echo "${NODE_CONFIGS}" | tr '[:upper:]' '[:lower:]' | tr '-' '_')
SNAPSHOT_DIR="docker-makefiles/${NODE_CONFIGS}"
SNAPSHOT_FILE="${SNAPSHOT_DIR}/formatted_node_configs.env"
if [[ -f "${SNAPSHOT_FILE}" ]] ; then rm -rf ${SNAPSHOT_FILE} ; fi

echo "Generating read-only snapshot: ${SNAPSHOT_FILE}"

# Concatenate all config files, comment out empty-value lines, write snapshot
{
  for cfg in "${CONFIG_FILES[@]}"; do
    echo "# ---- $(basename "${cfg}") ----"
    sed -E 's/^([A-Za-z_][A-Za-z0-9_]*)=""(\s*(#.*)?)$/#\1=""\2/' "${cfg}"
    echo ""
  done
} > "${SNAPSHOT_FILE}"

chmod 444 "${SNAPSHOT_FILE}"
#echo "Snapshot saved (read-only): ${SNAPSHOT_FILE}"

echo "Config update complete."