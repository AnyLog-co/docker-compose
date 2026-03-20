#!/usr/bin/env bash
# generate-compose.sh — Generates docker-compose.yml from a .conf/.yaml file
# Usage: ./generate-compose.sh [config_file] [output_file]
#   config_file  defaults to configs.yaml
#   output_file  defaults to docker-compose.yml

set -euo pipefail

CONFIG_FILE="${1:-configs.yaml}"
OUTPUT_FILE="${2:-docker-compose.yml}"

# ── Validate input ────────────────────────────────────────────────────────────
if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "ERROR: Config file '${CONFIG_FILE}' not found." >&2
  exit 1
fi

# ── Helpers ───────────────────────────────────────────────────────────────────

# Extract a top-level scalar:  KEY: value  (strips CRLF)
get_value() {
  local key="$1"
  grep -E "^${key}:[[:space:]]*" "$CONFIG_FILE" | head -1 \
    | sed -E "s/^${key}:[[:space:]]*//" | tr -d '\r' \
    | sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//'
}

# Extract a scalar nested one level under a section:
#   SECTION:
#     KEY: value
get_section_value() {
  local section="$1" key="$2"
  awk -v section="${section}" -v key="${key}" '
    $0 ~ "^"section":"  { inside=1; next }
    inside && /^[^[:space:]]/ { exit }
    inside {
      line = $0; gsub(/\r/, "", line)
      if (line ~ "^[[:space:]]+"key":[[:space:]]*") {
        sub(/^[[:space:]]+[^:]+:[[:space:]]*/, "", line)
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", line)
        print line; exit
      }
    }
  ' "$CONFIG_FILE"
}

# Collect list items under a sub-section:
#   PARENT:
#     CHILD:
#       - item1
#       - item2
get_list_under() {
  local parent="$1" child="$2"
  awk -v parent="${parent}" -v child="${child}" '
    $0 ~ "^"parent":"                             { in_parent=1; next }
    in_parent && /^[^[:space:]]/                  { exit }
    in_parent && $0 ~ "^[[:space:]]+"child":[[:space:]]*$" { in_child=1; next }
    in_child  && /^[[:space:]]+-/ {
      line = $0; gsub(/\r/, "", line)
      sub(/^[[:space:]]+-[[:space:]]*/, "", line)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", line)
      print line; next                            # <-- next prevents fallthrough
    }
    in_child  && /^[[:space:]]/ && !/^[[:space:]]+-/ { in_child=0 }
  ' "$CONFIG_FILE"
}

# Collect ENV_VARS entries (YAML "KEY: value" style) → outputs "KEY=value" lines
get_env_vars() {
  awk '
    /^ENV_VARS:/                    { inside=1; next }
    inside && /^[^[:space:]]/       { exit }
    inside {
      line = $0; gsub(/\r/, "", line)
      if (line ~ /^[[:space:]]*#/ || line ~ /^[[:space:]]*$/) next
      if (line ~ /^[[:space:]]+[A-Za-z_][A-Za-z0-9_]*:[[:space:]]*/) {
        sub(/^[[:space:]]+/, "", line)
        sub(/:[[:space:]]*/, "=", line)
        sub(/[[:space:]]*#.*$/, "", line)
        sub(/[[:space:]]+$/, "", line)
        if (length(line)) print line
      }
    }
  ' "$CONFIG_FILE"
}

# Collect VOLUMES entries → outputs "volname /container/path" per line
get_volumes() {
  awk '
    /^VOLUMES:/                     { inside=1; next }
    inside && /^[^[:space:]]/       { exit }
    inside {
      line = $0; gsub(/\r/, "", line)
      if (line ~ /^[[:space:]]*#/ || line ~ /^[[:space:]]*$/) next
      if (line ~ /^[[:space:]]+[A-Za-z0-9_-]+:/) {
        sub(/^[[:space:]]+/, "", line)
        n = index(line, ":")
        volname = substr(line, 1, n-1)
        path    = substr(line, n+1)
        sub(/^[[:space:]]+/, "", path)
        sub(/[[:space:]]+$/, "", path)
        if (length(path)) print volname " " path
      }
    }
  ' "$CONFIG_FILE"
}

# ── Parse config ──────────────────────────────────────────────────────────────

IMAGE=$(get_section_value "GENERAL" "IMAGE")
TAG=$(get_section_value "GENERAL" "TAG")
NAME=$(get_section_value "GENERAL" "NAME")
NETWORK_MODE=$(get_section_value "NETWORK_CONFIGS" "NETWORK_MODE")

if [[ -z "$IMAGE" || -z "$TAG" ]]; then
  echo "ERROR: GENERAL.IMAGE and GENERAL.TAG are required in '${CONFIG_FILE}'." >&2
  exit 1
fi

# NAME drives both the service key and container_name; fall back to image basename
SERVICE_NAME="${NAME:-$(basename "$IMAGE" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9_-' '-' | sed 's/-*$//')}"

# ── Resolve REMOTE_GUI_NIC → VITE_API_URL ────────────────────────────────────

REMOTE_GUI_NIC=$(get_section_value "ENV_VARS" "REMOTE_GUI_NIC" 2>/dev/null || true)
REMOTE_GUI_NIC="${REMOTE_GUI_NIC//\"/}"; REMOTE_GUI_NIC="${REMOTE_GUI_NIC//\'/}"

REMOTE_GUI_BE=$(get_section_value "ENV_VARS" "REMOTE_GUI_BE" 2>/dev/null || true)

REMOTE_GUI_IP="127.0.0.1"
if [[ -n "${REMOTE_GUI_NIC:-}" ]]; then
  echo "→ Resolving IP for NIC '${REMOTE_GUI_NIC}'..."
  if command -v ip >/dev/null 2>&1; then
    REMOTE_GUI_IP=$(ip -4 addr show dev "${REMOTE_GUI_NIC}" \
                    | awk '/inet /{print $2}' | cut -d/ -f1)
  elif command -v ifconfig >/dev/null 2>&1; then
    REMOTE_GUI_IP=$(ifconfig "${REMOTE_GUI_NIC}" | awk '/inet /{print $2}')
  else
    echo "WARNING: Neither 'ip' nor 'ifconfig' found — falling back to 127.0.0.1" >&2
  fi
  if [[ -z "$REMOTE_GUI_IP" ]]; then
    echo "WARNING: Could not resolve IP for NIC '${REMOTE_GUI_NIC}' — falling back to 127.0.0.1" >&2
    REMOTE_GUI_IP="127.0.0.1"
  else
    echo "  ✔ ${REMOTE_GUI_NIC} → ${REMOTE_GUI_IP}"
  fi
fi

VITE_API_URL="http://${REMOTE_GUI_IP}:${REMOTE_GUI_BE}"

# ── Collect sections ──────────────────────────────────────────────────────────
mapfile -t PORTS     < <(get_list_under "NETWORK_CONFIGS" "PORTS")
mapfile -t ENV_LINES < <(get_env_vars)
mapfile -t VOL_LINES < <(get_volumes)

# ── Write docker-compose.yml ──────────────────────────────────────────────────
{
  echo "# Auto-generated by generate-compose.sh from ${CONFIG_FILE}"
  echo "# $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  echo ""
  echo "services:"
  echo "  ${SERVICE_NAME}:"
  echo "    image: ${IMAGE}:${TAG}"
  [[ -n "$NAME" ]] && echo "    container_name: ${NAME}"

  # Networking
  case "${NETWORK_MODE,,}" in
    host)
      echo "    network_mode: host"
      ;;
    ports)
      if [[ ${#PORTS[@]} -gt 0 ]]; then
        echo "    ports:"
        for port in "${PORTS[@]}"; do
          echo "      - \"${port}:${port}\""
        done
      fi
      ;;
    "")
      echo "    # WARNING: NETWORK_CONFIGS.NETWORK_MODE not set — networking skipped"
      ;;
    *)
      echo "    # WARNING: unknown NETWORK_MODE '${NETWORK_MODE}' — networking skipped"
      ;;
  esac

  # Environment
  if [[ ${#ENV_LINES[@]} -gt 0 ]]; then
    echo "    environment:"
    for line in "${ENV_LINES[@]}"; do
      [[ -z "$line" ]] && continue
      echo "      - ${line}"
    done
    echo "      - VITE_API_URL=${VITE_API_URL}"
  fi

  # Volumes (service mounts)
  if [[ ${#VOL_LINES[@]} -gt 0 ]]; then
    echo "    volumes:"
    for vol in "${VOL_LINES[@]}"; do
      echo "      - ${vol%% *}:${vol#* }"
    done
  fi

  echo "    restart: unless-stopped"

  # Top-level named volume declarations
  if [[ ${#VOL_LINES[@]} -gt 0 ]]; then
    echo ""
    echo "volumes:"
    for vol in "${VOL_LINES[@]}"; do
      echo "  ${vol%% *}:"
    done
  fi

} > "$OUTPUT_FILE"

echo "✔  Generated '${OUTPUT_FILE}' from '${CONFIG_FILE}'"