#!/usr/bin/env bash
set -euo pipefail

ENV_FILE=".env"

# -------- Load ENV --------
if [[ -f "$ENV_FILE" ]]; then
  source "$ENV_FILE"
fi

# -------- Defaults --------
REMOTE_GUI_FE=${REMOTE_GUI_FE:-31800}
REMOTE_GUI_BE=${REMOTE_GUI_BE:-8080}
GRAFANA_URL=${GRAFANA_URL:-""}

# -------- Detect IP --------
if [[ -n "${REACT_APP_API_IP:-}" ]]; then
  REMOTE_GUI_IP="$REACT_APP_API_IP"

elif [[ -n "${NIC_TYPE:-}" ]] && command -v ip >/dev/null 2>&1; then
  REMOTE_GUI_IP=$(ip -4 addr show "$NIC_TYPE" | awk '/inet /{print $2}' | cut -d/ -f1)

else
  REMOTE_GUI_IP=$(curl -s https://checkip.amazonaws.com || echo "127.0.0.1")
fi

echo "Using IP: $REMOTE_GUI_IP"

# -------- Create volumes --------
docker volume create image-vol >/dev/null
docker volume create usr-mgm-vol >/dev/null
docker volume create report-configs >/dev/null

# -------- Remove old container if exists --------
docker rm -f remote-gui >/dev/null 2>&1 || true

# -------- Run Remote GUI --------
docker run -d \
  --name remote-gui \
  --restart always \
  -p ${REMOTE_GUI_FE}:${REMOTE_GUI_FE} \
  -p ${REMOTE_GUI_BE}:${REMOTE_GUI_BE} \
  -e VITE_API_URL=http://${REMOTE_GUI_IP}:${REMOTE_GUI_BE} \
  -e REMOTE_GUI_FE=${REMOTE_GUI_FE} \
  -e REMOTE_GUI_BE=${REMOTE_GUI_BE} \
  -e GRAFANA_URL=${GRAFANA_URL} \
  -v image-vol:/app/CLI/local-cli-backend/static/ \
  -v usr-mgm-vol:/app/CLI/local-cli/backend/usr-mgm/ \
  -v report-configs:/app/CLI/local-cli-backend/plugins/reportgenerator/templates \
  anylogco/remote-gui:beta

echo ""
echo "Remote GUI deployed successfully"
echo "Frontend: http://${REMOTE_GUI_IP}:${REMOTE_GUI_FE}"
echo "Backend:  http://${REMOTE_GUI_IP}:${REMOTE_GUI_BE}"