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

  export REACT_APP_API_IP=$(grep -m1 '^REACT_APP_API_IP=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')
  export REMOTE_GUI_FE=$(grep -m1 '^REMOTE_GUI_FE=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')
  export REMOTE_GUI_BE=$(grep -m1 '^REMOTE_GUI_BE=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')
  export GRAFANA_URL=$(grep -m1 '^GRAFANA_URL=' "$ENV_FILE" | cut -d= -f2- | tr -d '"\r')
else
  export IMAGE="anylogco/anylog-network"
fi

#-------- Base Configs -------
export NODE_NAME=$(grep -m1 '^NODE_NAME=' "$BASE_ENV" | cut -d= -f2- | tr -d '"\r')
export NIC_TYPE=$(grep -m1 '^NIC_TYPE=' "$BASE_ENV" | cut -d= -f2- | tr -d '"\r')
export ANYLOG_SERVER_PORT=$(grep -m1 '^ANYLOG_SERVER_PORT=' "$BASE_ENV" | cut -d= -f2- | tr -d '"\r')
export ANYLOG_REST_PORT=$(grep -m1 '^ANYLOG_REST_PORT=' "$BASE_ENV" | cut -d= -f2- | tr -d '"\r')
export ANYLOG_BROKER_PORT=$(grep -m1 '^ANYLOG_BROKER_PORT=' "$BASE_ENV" | cut -d= -f2- | tr -d '"\r')

#-------- Advance Configs -------
export REMOTE_GUI=$(grep -m1 '^REMOTE_GUI=' "$ADVANCE_ENV" | cut -d= -f2- | tr -d '"\r')

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
if [[ "${REMOTE_GUI}" == "true" ]]; then
  #-------- Determine REMOTE_GUI_IP -------
  # Priority: REACT_APP_API_IP > NIC_TYPE > fallback
  if [[ -n "$REACT_APP_API_IP" ]]; then
    REMOTE_GUI_IP="$REACT_APP_API_IP"
  elif [[ -n "$NIC_TYPE" ]]; then
    if command -v ip >/dev/null 2>&1; then
      REMOTE_GUI_IP=$(ip -4 addr show dev "$NIC_TYPE" | awk '/inet /{print $2}' | cut -d/ -f1)
    elif command -v ifconfig >/dev/null 2>&1; then
      REMOTE_GUI_IP=$(ifconfig "$NIC_TYPE" | awk '/inet /{print $2}')
    fi
  fi

  # Fallback if still empty
  REMOTE_GUI_IP="${REMOTE_GUI_IP:-$(curl -s https://checkip.amazonaws.com || echo "127.0.0.1")}"
  export REMOTE_GUI_IP

  # Set default ports if not defined
  REMOTE_GUI_FE="${REMOTE_GUI_FE:-31800}"
  REMOTE_GUI_BE="${REMOTE_GUI_BE:-8080}"

   #-------- Add volumes to docker-compose -------
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

  #-------- Add remote-gui service -------
  awk -v remote_ip="$REMOTE_GUI_IP" -v grafana="$GRAFANA_URL" -v fe_port="$REMOTE_GUI_FE" -v be_port="$REMOTE_GUI_BE" '/services:/ {
  print;
  print "  remote-gui:";
  print "    image: anylogco/remote-gui:beta";
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
