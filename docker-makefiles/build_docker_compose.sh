#!/usr/bin/env bash
#set -euo pipefail

# -------- Helpers --------
die() {
  echo "Error: $1" >&2
  exit "${2:-1}"
}

OS_TYPE=$(uname)
if [[ "$OS_TYPE" == "Darwin" ]]; then
  SED_INPLACE="sed -i .bak"
else
  SED_INPLACE="sed -i.bak"
fi

# -------- Args --------
NODE_CONFIGS=${1:-anylog-generic}
TAG=${2:-latest}
DEPLOYMENT_TYPE=${3:-docker}
export TAG

if [[ "${DEPLOYMENT_TYPE}" == "k8s" ]]; then
  die "k8s deployment not yet supported"
fi

# -------- Locate Config Files --------
MULTI_FILE=false
if [[ -f "docker-makefiles/${NODE_CONFIGS}/.env" ]] && \
   [[ -f "docker-makefiles/${NODE_CONFIGS}/base_configs.env" ]] && \
   [[ -f "docker-makefiles/${NODE_CONFIGS}/advance_configs.env" ]]; then
  MULTI_FILE=true
  ENV_FILE="docker-makefiles/${NODE_CONFIGS}/.env"
  BASE_ENV="docker-makefiles/${NODE_CONFIGS}/base_configs.env"
elif [[ -f "docker-makefiles/${NODE_CONFIGS}/node_configs.env" ]]; then
  ENV_FILE="docker-makefiles/${NODE_CONFIGS}/formatted_node_configs.env"
  BASE_ENV="docker-makefiles/${NODE_CONFIGS}/formatted_node_configs.env"
else
  die "Missing configuration file(s) for '${NODE_CONFIGS}', cannot continue"
fi

# -------- Generate Read-Only Snapshot Copy --------
bash docker-makefiles/prep_configs.sh "${ANYLOG_TYPE}"


# -------- Load Configs --------
export IMAGE=$(grep -m1 '^IMAGE=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')
export ENABLE_REMOTE_GUI=$(grep -m1 '^ENABLE_REMOTE_GUI=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')

export NODE_NAME=$(grep -m1 '^NODE_NAME=' "$BASE_ENV" | cut -d= -f2- | tr -d '"\r')
export ANYLOG_SERVER_PORT=$(grep -m1 '^ANYLOG_SERVER_PORT=' "$BASE_ENV" | cut -d= -f2- | tr -d '"\r')
export ANYLOG_REST_PORT=$(grep -m1 '^ANYLOG_REST_PORT=' "$BASE_ENV" | cut -d= -f2- | tr -d '"\r')
export ANYLOG_BROKER_PORT=$(grep -m1 '^ANYLOG_BROKER_PORT=' "$BASE_ENV" | cut -d= -f2- | tr -d '"\r')
export DOCKER_SOCKET=$(grep -m1 '^DOCKER_SOCKET=' "$BASE_ENV" | cut -d= -f2- | tr -d '"\r')
export DEPLOYMENTS_REPO=$(grep -m1 '^DEPLOYMENTS_REPO=' "$BASE_ENV" | cut -d= -f2- | tr -d '"\r')
export USER_VOLUMES=$(grep -m1 '^USER_VOLUMES=' ${BASE_ENV} | cut -d= -f2- | tr -d '"\r')


# -------- LICENSE_KEY: prefer env var (set by Makefile), fall back to config file --------
if [[ -z "${LICENSE_KEY:-}" ]]; then
  export LICENSE_KEY=$(grep -m1 '^LICENSE_KEY=' "$BASE_ENV" | cut -d= -f2- | tr -d '"\r')
fi

# -------- Select Template --------
COMPOSE_FILE="docker-makefiles/docker-compose-template.yaml"
TEMPLATE_COMPOSE_FILE="docker-makefiles/docker-compose-template-base.yaml"

if [[ "$(uname -s)" != "Linux" ]]; then
  TEMPLATE_COMPOSE_FILE="docker-makefiles/docker-compose-template-base.yaml"
fi

[[ -f "$TEMPLATE_COMPOSE_FILE" ]] || die "$TEMPLATE_COMPOSE_FILE not found"
cp "$TEMPLATE_COMPOSE_FILE" "${COMPOSE_FILE}"

# -------- Inject env_file --------
if [[ "$MULTI_FILE" == "true" ]]; then
  awk -v env="../../docker-makefiles/${NODE_CONFIGS}/.env" \
      -v base="../../docker-makefiles/${NODE_CONFIGS}/base_configs.env" \
      -v adv="../../docker-makefiles/${NODE_CONFIGS}/advance_configs.env" \
      '/    env_file:/ {print; print "      - " env; print "      - " base; print "      - " adv; next}1' \
      "${COMPOSE_FILE}" > temp.yaml && mv temp.yaml "${COMPOSE_FILE}"
else
  awk -v cfg="../../docker-makefiles/${NODE_CONFIGS}/formatted_node_configs.env" \
      '/    env_file:/ {print; print "      - " cfg; next}1' \
      "${COMPOSE_FILE}" > temp.yaml && mv temp.yaml "${COMPOSE_FILE}"
fi

# -------- Inject Broker Port --------
if [[ "${TEMPLATE_COMPOSE_FILE}" == *"ports"* ]] && [[ -n "${ANYLOG_BROKER_PORT:-}" ]]; then
  awk -v port="${ANYLOG_BROKER_PORT}:${ANYLOG_BROKER_PORT}" \
      '/    ports:/ {print; print "      - " port; next}1' \
      "${COMPOSE_FILE}" > temp.yaml && mv temp.yaml "${COMPOSE_FILE}"
fi

# -------- Deployment Scripts Volume --------
if [[ -n "${DEPLOYMENTS_REPO}" && -d "${DEPLOYMENTS_REPO}" ]]; then
  # Use a local deployment-scripts checkout when one is explicitly configured.
  ${SED_INPLACE} "s#- \${NODE_NAME}-local-scripts:/app/deployment-scripts#- ${DEPLOYMENTS_REPO}:/app/deployment-scripts#g" "${COMPOSE_FILE}"
  ${SED_INPLACE} "/^  \${NODE_NAME}-local-scripts:$/d" "${COMPOSE_FILE}"
else
  # URL-based repos are cloned by the AnyLog container at startup. Do not mount
  # a named volume over /app/deployment-scripts, or it hides the cloned scripts.
  ${SED_INPLACE} "/\/app\/deployment-scripts$/d" "${COMPOSE_FILE}"
  ${SED_INPLACE} "/^  \${NODE_NAME}-local-scripts:$/d" "${COMPOSE_FILE}"
fi

# -------- Docker Socket --------
if [[ -z "${DOCKER_SOCKET}" ]] || [[ ! -S "${DOCKER_SOCKET}" ]]; then
  ${SED_INPLACE} "s/- \${DOCKER_GID}/#- \${MISSING-DOCKER_GID}/g" "${COMPOSE_FILE}"
  ${SED_INPLACE} "0,/- \${DOCKER_SOCKET}/s#- \${DOCKER_SOCKET}#\# - \${MISSING-DOCKER_SOCKET}#" "${COMPOSE_FILE}"
else
  if stat -c '%g' "${DOCKER_SOCKET}" >/dev/null 2>&1; then
    export DOCKER_GID=$(stat -c '%g' "${DOCKER_SOCKET}")   # GNU stat (Linux)
  else
    export DOCKER_GID=$(stat -f '%g' "${DOCKER_SOCKET}")   # BSD stat (macOS)
  fi
fi

# -------- macOS: comment out Linux-only directives --------
if [[ "$(uname)" == "Darwin" ]]; then
  ${SED_INPLACE} 's|pid: "host"|# pid: "host"|g'                   "${COMPOSE_FILE}"
  ${SED_INPLACE} 's|- /proc:/host_proc:ro|# - /proc:/host_proc:ro|g' "${COMPOSE_FILE}"
  ${SED_INPLACE} 's|- /:/host:ro|# - /:/host:ro|g'                 "${COMPOSE_FILE}"
  ${SED_INPLACE} 's|- /sys:/host_sys:ro|# - /sys:/host_sys:ro|g'   "${COMPOSE_FILE}"
fi

# -------- Remote-GUI --------
if [[ "${ENABLE_REMOTE_GUI}" == "true" ]]; then
  export REMOTE_GUI_NIC=$(grep -m1 '^REMOTE_GUI_NIC=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')
  export REMOTE_GUI_FE=$(grep -m1 '^REMOTE_GUI_FE=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')
  export REMOTE_GUI_BE=$(grep -m1 '^REMOTE_GUI_BE=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')
  export REMOTE_GUI_TAG=$(grep -m1 '^REMOTE_GUI_TAG=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')
  export GRAFANA_URL=$(grep -m1 '^GRAFANA_URL=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')
  export REMOTE_CONN=$(grep -m1 '^REMOTE_CONN=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')
  export OVERLAY_IP=$(grep -m1 '^OVERLAY_IP=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')

  REMOTE_GUI_FE="${REMOTE_GUI_FE:-31800}"
  REMOTE_GUI_BE="${REMOTE_GUI_BE:-8080}"
  REMOTE_GUI_TAG="${REMOTE_GUI_TAG:-latest}"

  # Resolve NIC -> IP
  REMOTE_GUI_IP="127.0.0.1"
  if [[ -n "${REMOTE_GUI_NIC:-}" ]]; then
    if command -v ip >/dev/null 2>&1; then
      REMOTE_GUI_IP=$(ip -4 addr show dev "${REMOTE_GUI_NIC}" | awk '/inet /{print $2}' | cut -d/ -f1)
    elif command -v ifconfig >/dev/null 2>&1; then
      REMOTE_GUI_IP=$(ifconfig "${REMOTE_GUI_NIC}" | awk '/inet /{print $2}')
    fi
  fi

  if [[ ! -n "${REMOTE_CONN:-}" ]] && [[ -n "${OVERLAY_IP}" ]]; then
    export REMOTE_CONN="${OVERLAY_IP}:${ANYLOG_REST_PORT}"
  elif [[ ! -n "${REMOTE_CONN:-}" ]]; then
    export REMOTE_CONN="${REMOTE_GUI_IP}:${ANYLOG_REST_PORT}"
  fi

  # Add named volumes
  awk -v vol1="image-vol:/app/CLI/local-cli-backend/static/" \
      -v vol2="usr-mgm-vol:/app/CLI/local-cli/backend/usr-mgm/" '
/    volumes:/ && !vol_found {
  print; print "      - " vol1; print "      - " vol2; vol_found=1; next
}1
END {
  print "  image-vol:"; print "  usr-mgm-vol:"; print "  report-configs:";
}' "${COMPOSE_FILE}" > temp.yaml && mv temp.yaml "${COMPOSE_FILE}"

  # Add remote-gui service
  awk -v remote_ip="$REMOTE_GUI_IP" \
      -v grafana="${GRAFANA_URL:-}" \
      -v fe_port="$REMOTE_GUI_FE" \
      -v be_port="$REMOTE_GUI_BE" \
      -v tag="$REMOTE_GUI_TAG" \
      -v remote_conn="${REMOTE_CONN}" '
/services:/ {
  print;
  print "  remote-gui:";
  print "    image: anylogco/remote-gui:" tag;
  print "    container_name: remote-gui";
  print "    hostname: remote-gui";
  print "    restart: always";
  print "    stdin_open: true";
  print "    tty: true";
  print "    ports:";
  print "      - " fe_port ":" fe_port;
  print "      - " be_port ":" be_port;
  print "    environment:";
  print "      - VITE_API_URL=http://" remote_ip ":" be_port;
  print "      - REMOTE_GUI_FE=" fe_port;
  print "      - REMOTE_GUI_BE=" be_port;
  print "      - REMOTE_CONN=" remote_conn;
  if (grafana != "") print "      - GRAFANA_URL=" grafana;
  print "    volumes:";
  print "      - image-vol:/app/CLI/local-cli-backend/static/";
  print "      - usr-mgm-vol:/app/CLI/local-cli/backend/usr-mgm/";
  print "      - report-configs:/app/CLI/local-cli-backend/plugins/reportgenerator/templates";
  next
}1' "${COMPOSE_FILE}" > temp.yaml && mv temp.yaml "${COMPOSE_FILE}"
fi

# -------- USER VOLUMES --------
if [[ -n "${USER_VOLUMES}" ]]; then
  for VOLUME in ${USER_VOLUMES}; do

    if [[ "${VOLUME}" == *"/"* ]]; then
      MOUNT_NAME=$(basename "${VOLUME}")
    elif [[ "${VOLUME}" == *"\\"* ]]; then
      MOUNT_NAME=$(echo "${VOLUME}" | awk -F "\\" '{print $NF}')
    else
      MOUNT_NAME="${VOLUME}"
    fi

    INJECT="      - ${VOLUME:+${VOLUME}:}/app/${MOUNT_NAME}"

    # Insert BEFORE the root-level volumes:
    ${SED_INPLACE} "/^volumes:/i\\
${INJECT}
" "${COMPOSE_FILE}"

  done
fi

# -------- Envsubst & Write Output --------
echo "Generating final docker-compose.yaml..."
mkdir -p docker-makefiles/docker-compose-files
OUTPUT_FILE="docker-makefiles/docker-compose-files/${NODE_CONFIGS}-docker-compose.yaml"
envsubst < "${COMPOSE_FILE}" > "$OUTPUT_FILE"
rm -rf ${COMPOSE_FILE} ${COMPOSE_FILE}.bak docker-makefiles/${NODE_CONFIGS}/*.bak
echo "Saved: ${OUTPUT_FILE}"



## Filename: {formatted_node_name}.env  (hyphens -> underscores, lowercased)
## Empty-value vars ( VAR="" ) are commented out in the copy.
##FORMATTED_NODE_NAME=$(echo "${NODE_CONFIGS}" | tr '[:upper:]' '[:lower:]' | tr '-' '_')
#SNAPSHOT_DIR="docker-makefiles/${NODE_CONFIGS}"
#SNAPSHOT_FILE="${SNAPSHOT_DIR}/formatted_node_configs.env"
#
#echo "Generating read-only snapshot: ${SNAPSHOT_FILE}"
#
## Collect config files that were used
#if [[ "$MULTI_FILE" == "true" ]]; then
#  SNAPSHOT_SOURCES=("${ENV_FILE}" "${BASE_ENV}" "docker-makefiles/${NODE_CONFIGS}/advance_configs.env")
#else
#  SNAPSHOT_SOURCES=("${ENV_FILE}")
#fi
#
#{
#  for src in "${SNAPSHOT_SOURCES[@]}"; do
#    echo "# ---- $(basename "${src}") ----"
#    sed -E 's/^([A-Za-z_][A-Za-z0-9_]*)=""(\s*(#.*)?)$/#\1=""\2/' "${src}"
#    echo ""
#  done
#} > "${SNAPSHOT_FILE}"
#
#chmod 444 "${SNAPSHOT_FILE}"
#echo "Snapshot saved (read-only): ${SNAPSHOT_FILE}"