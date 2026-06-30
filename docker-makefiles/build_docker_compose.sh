#!/usr/bin/env bash
#set -euo pipefail

# -------- Helpers --------
die() {
  echo "Error: $1" >&2
  exit "${2:-1}"
}

# WSL reports uname -s as Linux; detect it for compose template auto-selection.
_is_wsl() {
  if [[ -n "${WSL_DISTRO_NAME:-}" ]]; then
    return 0
  fi
  if grep -qiE 'microsoft|wsl' /proc/version 2>/dev/null; then
    return 0
  fi
  return 1
}

# Auto-select ports-based compose on WSL, macOS, and other non-native-Linux hosts.
_auto_use_ports_template() {
  local os
  os=$(uname -s)
  if [[ "${os}" == "Darwin" ]]; then
    return 0
  fi
  if _is_wsl; then
    return 0
  fi
  if [[ "${os}" != "Linux" ]]; then
    return 0
  fi
  return 1
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
  DIR_NAME=$(dirname "$BASE_ENV")
elif [[ -f "docker-makefiles/${NODE_CONFIGS}/node_configs.env" ]]; then
  ENV_FILE="docker-makefiles/${NODE_CONFIGS}/formatted_node_configs.env"
  BASE_ENV="docker-makefiles/${NODE_CONFIGS}/formatted_node_configs.env"
  DIR_NAME=$(dirname "$BASE_ENV")
else
  die "Missing configuration file(s) for '${NODE_CONFIGS}', cannot continue"
fi

# -------- Generate Read-Only Snapshot Copy --------
bash docker-makefiles/prep_configs.sh "${NODE_CONFIGS}"


# -------- Load Configs --------
export NETWORK_TYPE=$(grep -m1 '^NETWORK_TYPE' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')
export IMAGE=$(grep -m1 '^IMAGE=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')
export ENABLE_REMOTE_GUI=$(grep -m1 '^ENABLE_REMOTE_GUI=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')


NODE_NAME=$(grep -m1 '^NODE_NAME=' "$BASE_ENV" | cut -d= -f2- | tr -d '"\r')
CONTAINER_NAME=$(grep -m1 '^CONTAINER_NAME=' "$BASE_ENV" | cut -d= -f2- | tr -d '"\r')
UPDATE_SED="true"

if [[ -n "${CONTAINER_NAME}" ]] ; then
  export CONTAINER_NAME
  UPDATE_SED="false"
elif [[ -n "${NODE_NAME}" ]] ; then
  export CONTAINER_NAME="${NODE_NAME}"
else
  export CONTAINER_NAME="${NODE_CONFIGS}"
fi
if [[ "${UPDATE_SED}" == "true" ]] ; then
  ${SED_INPLACE} "s/^CONTAINER_NAME=\"\"/CONTAINER_NAME=\"${CONTAINER_NAME}\"/g" "${DIR_NAME}/node_configs.env"
fi

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

# -------- Select Template --------
COMPOSE_FILE="docker-makefiles/docker-compose-template.yaml"

if [[ -n "${NETWORK_TYPE}" ]] && [[ "${NETWORK_TYPE}" != "network" ]] && [[ "${NETWORK_TYPE}" != "ports" ]]; then
  TEMPLATE_COMPOSE_FILE="docker-makefiles/docker-compose-template-net-specific-base.yaml"
elif [[ "${NETWORK_TYPE}" == "ports" ]]; then
  TEMPLATE_COMPOSE_FILE="docker-makefiles/docker-compose-template-ports-base.yaml"
elif [[ "${NETWORK_TYPE}" == "network" ]]; then
  TEMPLATE_COMPOSE_FILE="docker-makefiles/docker-compose-template-base.yaml"
elif [[ -z "${NETWORK_TYPE}" ]] && _auto_use_ports_template; then
  TEMPLATE_COMPOSE_FILE="docker-makefiles/docker-compose-template-ports-base.yaml"
else
  TEMPLATE_COMPOSE_FILE="docker-makefiles/docker-compose-template-base.yaml"
fi

[[ -f "$TEMPLATE_COMPOSE_FILE" ]] || die "$TEMPLATE_COMPOSE_FILE not found"
echo "Compose template: ${TEMPLATE_COMPOSE_FILE}"
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
# Ports template already maps server, REST, and broker; no extra injection needed.

# -------- Deployment Scripts Volume --------
SOURCE_ENV="docker-makefiles/${NODE_CONFIGS}/node_configs.env"
if [[ -f "${SOURCE_ENV}" ]]; then
  DEPLOYMENTS_REPO=$(grep -m1 '^DEPLOYMENTS_REPO=' "${SOURCE_ENV}" | cut -d= -f2- | tr -d '"\r')
  DEPLOYMENTS_BRANCH=$(grep -m1 '^DEPLOYMENTS_BRANCH=' "${SOURCE_ENV}" | cut -d= -f2- | tr -d '"\r')
fi

if [[ -z "${DEPLOYMENTS_REPO}" && -z "${DEPLOYMNETS_BRANCH}" ]]  || \
   [[ "${DEPLOYMENTS_REPO}" == "https://github.com/AnyLog-co/deployment-scripts" && "${DEPLOYMENTS_BRANCH}" == "pre-develop" ]] ; then
  # Option 1: default deployment-scripts built into the image
  echo "Use built-in default option"
  ${SED_INPLACE} "s/#      - \${CONTAINER_NAME}-local-scripts:\/app\/deployment-scripts/      - \${CONTAINER_NAME}-local-scripts:\/app\/deployment-scripts/g" "${COMPOSE_FILE}"
  ${SED_INPLACE} "s/#  \${CONTAINER_NAME}-local-scripts:/  \${CONTAINER_NAME}-local-scripts:/g" "${COMPOSE_FILE}"
elif [[ -n "${DEPLOYMENTS_REPO}" && -d "${DEPLOYMENTS_REPO}" ]]; then
  # Option 2: bake deployment-scripts into the init image (COPY at build time).
  # Docker Desktop cannot reliably bind-mount /home/... or tarball files from WSL.
  DEPLOYMENTS_REPO=$(cd "${DEPLOYMENTS_REPO}" && pwd)
  [[ -f "${DEPLOYMENTS_REPO}/node-deployment/main.al" ]] || \
    die "deployment-scripts missing main.al at: ${DEPLOYMENTS_REPO}/node-deployment/main.al"

  SCRIPTS_BUILD_DIR="docker-makefiles/docker-compose-files/${NODE_CONFIGS}-scripts-build"
  rm -rf "${SCRIPTS_BUILD_DIR}"
  mkdir -p "${SCRIPTS_BUILD_DIR}"
  echo "Packaging deployment-scripts from ${DEPLOYMENTS_REPO} -> ${SCRIPTS_BUILD_DIR}"
  tar czf "${SCRIPTS_BUILD_DIR}/deployment-scripts.tar.gz" -C "${DEPLOYMENTS_REPO}" .
  cat > "${SCRIPTS_BUILD_DIR}/Dockerfile" <<'EOF'
FROM busybox
COPY deployment-scripts.tar.gz /deployment-scripts-seed.tar.gz
EOF

  # Init container: extract baked-in tarball into named volume; fail loudly if main.al missing
  awk '
    /^      "chown -R 10001:10001/ {
      print "      \"rm -rf /app/deployment-scripts/* /app/deployment-scripts/.[!.]* 2>/dev/null; tar xzf /deployment-scripts-seed.tar.gz -C /app/deployment-scripts && test -f /app/deployment-scripts/node-deployment/main.al || { echo \\\"init: deployment-scripts seed failed\\\" >&2; exit 1; }; chown -R 10001:10001"
      next
    }
    { print }
  ' "${COMPOSE_FILE}" > temp.yaml && mv temp.yaml "${COMPOSE_FILE}"

  awk '
    /"tar xzf \/deployment-scripts-seed/ { in_cmd=1 }
    in_cmd && /^        \/app\/AnyLog-Network\/data$/ {
      print
      print "        /app/deployment-scripts"
      next
    }
    /^      "\]/ { in_cmd=0 }
    { print }
  ' "${COMPOSE_FILE}" > temp.yaml && mv temp.yaml "${COMPOSE_FILE}"

  awk -v ctx="./${NODE_CONFIGS}-scripts-build" -v tag="${NODE_CONFIGS}-scripts-init" '
    /\$\{CONTAINER_NAME\}-init:/ { in_init=1 }
    in_init && /^    image: busybox/ {
      print "    build:"
      print "      context: " ctx
      print "      dockerfile: Dockerfile"
      print "    image: " tag
      next
    }
    in_init && /-data:\/app\/AnyLog-Network\/data$/ && !scripts_seeded {
      print
      print "      - ${CONTAINER_NAME}-local-scripts:/app/deployment-scripts"
      scripts_seeded=1
      next
    }
    { print }
  ' "${COMPOSE_FILE}" > temp.yaml && mv temp.yaml "${COMPOSE_FILE}"

  # Main service already mounts local-scripts in the template; remove stale host bind-mounts
  ${SED_INPLACE} '\|- /home/[^ ]*:/app/deployment-scripts|d' "${COMPOSE_FILE}"
  ${SED_INPLACE} '\|- //wsl[^ ]*:/app/deployment-scripts|d' "${COMPOSE_FILE}"
  ${SED_INPLACE} '\|- \./[^ ]*-deployment-scripts\.tar\.gz:/deployment-scripts-seed\.tar\.gz:ro|d' "${COMPOSE_FILE}"
  if ! grep -q 'local-scripts:/app/deployment-scripts' "${COMPOSE_FILE}"; then
    ${SED_INPLACE} "s|- \${CONTAINER_NAME}-data:/app/AnyLog-Network/data|- \${CONTAINER_NAME}-data:/app/AnyLog-Network/data\n      - \${CONTAINER_NAME}-local-scripts:/app/deployment-scripts|" "${COMPOSE_FILE}"
  fi
  ${SED_INPLACE} "s/^#  \${CONTAINER_NAME}-local-scripts:$/  \${CONTAINER_NAME}-local-scripts:/" "${COMPOSE_FILE}"

elif [[ "${DEPLOYMENTS_REPO}" == http://* || "${DEPLOYMENTS_REPO}" == https://* ]]; then
  # Option 3: reclone at startup — no volume needed at all
  echo "Using GitHub reclone at startup: ${DEPLOYMENTS_REPO}@${DEPLOYMENTS_BRANCH}"
  ${SED_INPLACE} "/\/app\/deployment-scripts$/d" "${COMPOSE_FILE}"
  ${SED_INPLACE} "/^#  \${CONTAINER_NAME}-local-scripts:$/d" "${COMPOSE_FILE}"
  ${SED_INPLACE} "/^  \${CONTAINER_NAME}-local-scripts:$/d" "${COMPOSE_FILE}"

elif [[ -n "${DEPLOYMENTS_REPO}" ]] ; then
  die "DEPLOYMENTS_REPO path does not exist: '${DEPLOYMENTS_REPO}'. Use a valid host directory or a https:// GitHub URL."
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
# -------- Host Mounts --------
export HOST_PROC=$(grep -m1 '^HOST_PROC=' "$BASE_ENV" | cut -d= -f2- | tr -d '"\r')
export HOST_ROOT=$(grep -m1 '^HOST_ROOT=' "$BASE_ENV" | cut -d= -f2- | tr -d '"\r')
export HOST_SYS=$(grep -m1  '^HOST_SYS='  "$BASE_ENV" | cut -d= -f2- | tr -d '"\r')

for VAR_NAME in HOST_PROC HOST_ROOT HOST_SYS; do
  HOST_PATH="${!VAR_NAME}"
  if [[ -z "${HOST_PATH}" ]] || [[ ! -e "${HOST_PATH}" ]]; then
    ${SED_INPLACE} "s|- \${${VAR_NAME}}:.*|# - \${MISSING-${VAR_NAME}}|g" "${COMPOSE_FILE}"
  fi
done

#if [[ "$(uname)" == "Darwin" ]]; then
#  ${SED_INPLACE} 's|pid: "host"|# pid: "host"|g'                   "${COMPOSE_FILE}"
#  ${SED_INPLACE} 's|- /proc:/host_proc:ro|# - /proc:/host_proc:ro|g' "${COMPOSE_FILE}"
#  ${SED_INPLACE} 's|- /:/host:ro|# - /:/host:ro|g'                 "${COMPOSE_FILE}"
#  ${SED_INPLACE} 's|- /sys:/host_sys:ro|# - /sys:/host_sys:ro|g'   "${COMPOSE_FILE}"
#fi


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
  VOLUME_INJECT=""
  for VOLUME in ${USER_VOLUMES}; do
    if [[ "${VOLUME}" == *"/"* ]]; then
      MOUNT_NAME=$(basename "${VOLUME}")
    elif [[ "${VOLUME}" == *"\\"* ]]; then
      MOUNT_NAME=$(echo "${VOLUME}" | awk -F "\\" '{print $NF}')
    else
      MOUNT_NAME="${VOLUME}"
    fi
    VOLUME_INJECT="${VOLUME_INJECT}\n      - ${VOLUME}:/app/${MOUNT_NAME}"
  done

  # Insert all user volumes after the data volume in the main service
  ${SED_INPLACE} "s#- \${CONTAINER_NAME}-data:/app/AnyLog-Network/data#- \${CONTAINER_NAME}-data:/app/AnyLog-Network/data${VOLUME_INJECT}#g" "${COMPOSE_FILE}"
fi

# -------- Envsubst & Write Output --------
UNAME_M=$(uname -m)
case "$UNAME_M" in
  x86_64)          export DOCKER_PLATFORM="linux/amd64" ;;
  aarch64|arm64)   export DOCKER_PLATFORM="linux/arm64" ;;
  *)               export DOCKER_PLATFORM="linux/amd64" ;;
esac

echo "Generating final docker-compose.yaml..."
mkdir -p docker-makefiles/docker-compose-files
OUTPUT_FILE="docker-makefiles/docker-compose-files/${NODE_CONFIGS}-docker-compose.yaml"
envsubst < "${COMPOSE_FILE}" > "$OUTPUT_FILE"
rm -rf ${COMPOSE_FILE} ${COMPOSE_FILE}.bak docker-makefiles/${NODE_CONFIGS}/*.bak
echo "Saved: ${OUTPUT_FILE}"

