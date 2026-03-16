#!/usr/bin/env bash
set -euo pipefail

#-------- Helpers --------
die() {
  echo "Error: $1" >&2
  exit "${2:-1}"
}

#-------- Args --------
NODE_CONFIGS=${1:-anylog-generic}
TAG=${2:-latest}
DEPLOYMENT_TYPE=${3:-docker}

if [[ "${DEPLOYMENT_TYPE}" == "k8s" ]]; then
  # if kubernetes then go to k8s script
  # bash build_k8s_compose.sh # <- not written
  die "k8s deployment not yet supported"
fi

#-------- Extract Configs --------
MULTI_FILE=false
if [[ -f "docker-makefiles/${NODE_CONFIGS}/.env" ]] && \
   [[ -f "docker-makefiles/${NODE_CONFIGS}/base_configs.env" ]] && \
   [[ -f "docker-makefiles/${NODE_CONFIGS}/advance_configs.env" ]]; then
  MULTI_FILE=true
  ENV_FILE="docker-makefiles/${NODE_CONFIGS}/.env"
  BASE_ENV="docker-makefiles/${NODE_CONFIGS}/base_configs.env"
  ADVANCE_ENV="docker-makefiles/${NODE_CONFIGS}/advance_configs.env"
elif [[ -f "docker-makefiles/${NODE_CONFIGS}/node_configs.env" ]]; then
  ENV_FILE="docker-makefiles/${NODE_CONFIGS}/node_configs.env"
  BASE_ENV="docker-makefiles/${NODE_CONFIGS}/node_configs.env"
  ADVANCE_ENV="docker-makefiles/${NODE_CONFIGS}/node_configs.env"
else
  die "Missing configuration file(s), cannot continue with deployment"
fi

#-------- Load Configs --------
export IMAGE=$(grep -m1 '^IMAGE=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')
export ENABLE_REMOTE_GUI=$(grep -m1 '^ENABLE_REMOTE_GUI=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')

export NODE_NAME=$(grep -m1 '^NODE_NAME=' "$BASE_ENV" | cut -d= -f2- | tr -d '"\r')
export ANYLOG_SERVER_PORT=$(grep -m1 '^ANYLOG_SERVER_PORT=' "$BASE_ENV" | cut -d= -f2- | tr -d '"\r')
export ANYLOG_REST_PORT=$(grep -m1 '^ANYLOG_REST_PORT=' "$BASE_ENV" | cut -d= -f2- | tr -d '"\r')
export ANYLOG_BROKER_PORT=$(grep -m1 '^ANYLOG_BROKER_PORT=' "$BASE_ENV" | cut -d= -f2- | tr -d '"\r')

#-------- Select Template --------
COMPOSE_FILE="docker-makefiles/docker-compose-template.yaml"
TEMPLATE_COMPOSE_FILE="docker-makefiles/docker-compose-template-base.yaml"

if [[ "$(uname -s)" != "Linux" ]]; then
  TEMPLATE_COMPOSE_FILE="docker-makefiles/docker-compose-template-ports-base.yaml"
fi

if [[ ! -f "$TEMPLATE_COMPOSE_FILE" ]]; then
  die "$TEMPLATE_COMPOSE_FILE not found"
fi
cp "$TEMPLATE_COMPOSE_FILE" "$COMPOSE_FILE"

#-------- Inject env_file --------
if [[ "$MULTI_FILE" == "true" ]]; then
  awk -v env="../../docker-makefiles/${NODE_CONFIGS}/.env" \
      -v base="../../docker-makefiles/${NODE_CONFIGS}/base_configs.env" \
      -v adv="../../docker-makefiles/${NODE_CONFIGS}/advance_configs.env" \
      '/    env_file:/ {print; print "      - " env; print "      - " base; print "      - " adv; next}1' \
      "$COMPOSE_FILE" > temp.yaml && mv temp.yaml "$COMPOSE_FILE"
else
  awk -v cfg="../../docker-makefiles/${NODE_CONFIGS}/node_configs.env" \
      '/    env_file:/ {print; print "      - " cfg; next}1' \
      "$COMPOSE_FILE" > temp.yaml && mv temp.yaml "$COMPOSE_FILE"
fi

#-------- Inject Broker Port --------
if [[ "${TEMPLATE_COMPOSE_FILE}" == *"ports"* ]] && [[ -n "$ANYLOG_BROKER_PORT" ]]; then
  awk -v port="${ANYLOG_BROKER_PORT}:${ANYLOG_BROKER_PORT}" \
      '/    ports:/ {print; print "      - " port; next}1' \
      "$COMPOSE_FILE" > temp.yaml && mv temp.yaml "$COMPOSE_FILE"
fi

#-------- Remote-GUI --------
if [[ "${ENABLE_REMOTE_GUI}" == "true" ]]; then
  export REMOTE_GUI_NIC=$(grep -m1 '^REMOTE_GUI_NIC=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')
  export REMOTE_GUI_FE=$(grep -m1 '^REMOTE_GUI_FE=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')
  export REMOTE_GUI_BE=$(grep -m1 '^REMOTE_GUI_BE=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')
  export REMOTE_GUI_TAG=$(grep -m1 '^REMOTE_GUI_TAG=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')
  export GRAFANA_URL=$(grep -m1 '^GRAFANA_URL=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')

  # Set default ports if not defined
  REMOTE_GUI_FE="${REMOTE_GUI_FE:-31800}"
  REMOTE_GUI_BE="${REMOTE_GUI_BE:-8080}"
  REMOTE_GUI_TAG="${REMOTE_GUI_TAG:-latest}"

  #-------- Determine REMOTE_GUI_IP --------
  REMOTE_GUI_IP="127.0.0.1"
  if [[ -n "${REMOTE_GUI_NIC}" ]]; then
    if command -v ip >/dev/null 2>&1; then
      REMOTE_GUI_IP=$(ip -4 addr show dev "${REMOTE_GUI_NIC}" | awk '/inet /{print $2}' | cut -d/ -f1)
    elif command -v ifconfig >/dev/null 2>&1; then
      REMOTE_GUI_IP=$(ifconfig "${REMOTE_GUI_NIC}" | awk '/inet /{print $2}')
    fi
  fi

  #-------- Add volumes to docker-compose --------
  awk -v vol1="image-vol:/app/CLI/local-cli-backend/static/" \
      -v vol2="usr-mgm-vol:/app/CLI/local-cli/backend/usr-mgm/" '
/    volumes:/ && !vol_found {
  print;
  print "      - " vol1;
  print "      - " vol2;
  vol_found=1;
  next
}1
END {
  print "  image-vol:";
  print "  usr-mgm-vol:";
  print "  report-configs:";
}' "$COMPOSE_FILE" > temp.yaml && mv temp.yaml "$COMPOSE_FILE"

  #-------- Add remote-gui service --------
  awk -v remote_ip="$REMOTE_GUI_IP" \
      -v grafana="$GRAFANA_URL" \
      -v fe_port="$REMOTE_GUI_FE" \
      -v be_port="$REMOTE_GUI_BE" \
      -v tag="$REMOTE_GUI_TAG" '
/services:/ {
  print;
  print "  remote-gui:";
  print "    image: anylogco/remote-gui:" tag;
  print "    container_name: remote-gui";
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
  if (grafana != "") print "      - GRAFANA_URL=" grafana;
  print "    volumes:";
  print "      - image-vol:/app/CLI/local-cli-backend/static/";
  print "      - usr-mgm-vol:/app/CLI/local-cli/backend/usr-mgm/";
  print "      - report-configs:/app/CLI/local-cli-backend/plugins/reportgenerator/templates";
  next
}1' "$COMPOSE_FILE" > temp.yaml && mv temp.yaml "$COMPOSE_FILE"
fi

#-------- Envsubst substitution --------
echo "Generating final docker-compose.yaml..."
mkdir -p docker-makefiles/docker-compose-files
OUTPUT_FILE="docker-makefiles/docker-compose-files/${NODE_CONFIGS}-docker-compose.yaml"
envsubst < "$COMPOSE_FILE" > "$OUTPUT_FILE"
echo "Saved as $OUTPUT_FILE"
rm -f "$COMPOSE_FILE"