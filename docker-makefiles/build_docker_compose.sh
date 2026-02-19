#!/usr/bin/env bash
set -euo pipefail

NODE_CONFIGS=${1-anylog-generic}
TAG=${2-latest}

#-------- Extract Configs -------
ENV_FILE="docker-makefiles/${NODE_CONFIGS}/.env"
BASE_ENV="docker-makefiles/${NODE_CONFIGS}/base_configs.env"
ADVANCE_ENV="docker-makefiles/${NODE_CONFIGS}/advance_configs.env"

# Load main .env
if [[ -f "$ENV_FILE" ]]; then
  export IMAGE=$(grep -m1 '^IMAGE=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')
  export REMOTE_GUI_IP=$(grep -m1 '^REMOTE_GUI_IP=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')
  export REMOTE_GUI_NIC=$(grep -m1 '^REMOTE_GUI_NIC=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')
  export GRAFANA_URL=$(grep -m1 '^GRAFANA_URL=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')
else
  export IMAGE="anylogco/anylog-network"
  export REMOTE_GUI_IP=$(curl -s https://checkip.amazonaws.com || echo "127.0.0.1")
fi

# Determine REMOTE_GUI_IP if empty
if [[ -z "${REMOTE_GUI_IP}" ]]; then
  if [[ -n "${REMOTE_GUI_NIC}" ]]; then
    REMOTE_GUI_IP=$(ip -4 addr show dev "$REMOTE_GUI_NIC" | awk '/inet /{print $2}' | cut -d/ -f1)
  else
    REMOTE_GUI_IP=$(curl -s https://checkip.amazonaws.com || echo "127.0.0.1")
  fi
fi
export REMOTE_GUI_IP

#-------- Advance Configs -------
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
  echo "Error: $TEMPLATE_COMPOSE_FILE not found."
  exit 1
fi
cp "$TEMPLATE_COMPOSE_FILE" "$COMPOSE_FILE"

# Inject ANYLOG_BROKER_PORT if needed
if [[ "${TEMPLATE_COMPOSE_FILE}" == *"ports"* ]] && [[ -n "$ANYLOG_BROKER_PORT" ]]; then
  awk -v port="${ANYLOG_BROKER_PORT}:${ANYLOG_BROKER_PORT}" '/    ports:/ {print; print "      - " port; next}1' "$COMPOSE_FILE" > temp.yaml && mv temp.yaml "$COMPOSE_FILE"
fi

#-------- Remote-GUI --------
# Only if REMOTE_GUI_IP is set
if [[ -n "$REMOTE_GUI_IP" ]]; then
  # Volumes
  awk -v vol1="image-vol:/app/CLI/local-cli-backend/static/" -v vol2="usr-mgm-vol:/app/CLI/local-cli/backend/usr-mgm/" '
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

  # Add remote-gui service
  awk -v remote_ip="$REMOTE_GUI_IP" -v grafana="$GRAFANA_URL" '/services:/ {
    print;
    print "  remote-gui:";
    print "    image: anylogco/remote-gui:beta";
    print "    container_name: remote-gui";
    print "    restart: always";
    print "    stdin_open: true";
    print "    tty: true";
    print "    ports:";
    print "      - 3001:3001";
    print "      - 8000:8000";
    print "    environment:";
    print "      - REACT_APP_API_URL=http://" remote_ip ":8000";
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
