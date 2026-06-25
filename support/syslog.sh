#!/usr/bin/env bash
# syslog.sh — AnyLog syslog forwarding manager
#
# Configures the host syslog daemon to forward all log traffic to the AnyLog
# broker port.  Reads SYSLOG_MONITORING and ANYLOG_BROKER_PORT from the node
# config file so this script stays in sync with the rest of the deployment
# without extra arguments.
#
# Usage:
#   bash syslog.sh setup  [NODE_CONFIGS]
#   bash syslog.sh remove [NODE_CONFIGS]
#   bash syslog.sh help
#
# Arguments:
#   NODE_CONFIGS   Path to node_configs.env  (default: docker-makefiles/anylog-generic/node_configs.env)
#
# Platform behaviour:
#   Linux  — rsyslog drop-in  /etc/rsyslog.d/60-custom-forwarding.conf  (TCP)
#   macOS  — /etc/syslog.conf append                                     (UDP)
#            macOS syslogd only supports UDP; ensure ANYLOG_BROKER_PORT
#            is open for UDP on the AnyLog node.
#
# Both commands are no-ops when SYSLOG_MONITORING != "true" in NODE_CONFIGS.
# setup is idempotent — safe to call repeatedly.

set -euo pipefail

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
die() { echo "ERROR: $1" >&2; exit "${2:-1}"; }

# ──────────────────────────────────────────────
# Args
# ──────────────────────────────────────────────
COMMAND="${1:-help}"
NODE_CONFIGS="${2:-docker-makefiles/anylog-generic/node_configs.env}"

# ──────────────────────────────────────────────
# Read variables from node config
# ──────────────────────────────────────────────
_load_syslog_vars() {
  SYSLOG_MON=$(grep -E '^SYSLOG_MONITORING=' "${NODE_CONFIGS}" 2>/dev/null \
    | head -1 | sed 's/^[^=]*=//;s/[[:space:]]*$//' | tr -d '"'"'" )
  BROKER_PORT=$(grep -E '^ANYLOG_BROKER_PORT=' "${NODE_CONFIGS}" 2>/dev/null \
    | head -1 | sed 's/^[^=]*=//;s/[[:space:]]*$//' | tr -d '"'"'" )
}

# ──────────────────────────────────────────────
# setup
# ──────────────────────────────────────────────
cmd_setup() {
  _load_syslog_vars

  if [[ "${SYSLOG_MON}" != "true" ]]; then
    echo "syslog setup: SYSLOG_MONITORING is not 'true' in ${NODE_CONFIGS} — skipping."
    exit 0
  fi

  [[ -n "${BROKER_PORT}" ]] || die "ANYLOG_BROKER_PORT is not set in ${NODE_CONFIGS}."

  local os marker
  os=$(uname -s)
  marker="# anylog-forwarding port=${BROKER_PORT}"

  case "${os}" in

    Linux)
      command -v rsyslogd >/dev/null 2>&1 \
        || die "rsyslogd not found. Install with: sudo apt-get install rsyslog"

      local conf="/etc/rsyslog.d/60-custom-forwarding.conf"

      if [[ -f "${conf}" ]] && grep -qF "${marker}" "${conf}" 2>/dev/null; then
        echo "syslog setup: rule already present in ${conf} — nothing to do."
        exit 0
      fi

      echo "Installing AnyLog rsyslog rule → ${conf} (TCP port ${BROKER_PORT})"
      printf '%s\n' \
        "${marker}" \
        "\$template remote-incoming-logs, \"/var/log/remote/%HOSTNAME%.log\"" \
        "*.* ?remote-incoming-logs" \
        "*.* action(type=\"omfwd\" target=\"127.0.0.1\" port=\"${BROKER_PORT}\" protocol=\"tcp\")" \
        | sudo tee "${conf}" > /dev/null

      sudo systemctl restart rsyslog \
        && echo "rsyslog restarted." \
        || echo "WARNING: could not restart rsyslog — run: sudo systemctl restart rsyslog"
      ;;

    Darwin)
      local conf="/etc/syslog.conf"

      [[ -f "${conf}" ]] \
        || die "${conf} not found — is this macOS 10.12 or later?\n       On macOS 12+ you may need to re-enable syslogd via launchctl."

      if grep -qF "${marker}" "${conf}" 2>/dev/null; then
        echo "syslog setup: rule already present in ${conf} — nothing to do."
        exit 0
      fi

      echo "Installing AnyLog syslog rule → ${conf} (UDP port ${BROKER_PORT})"
      printf '\n%s\n%s\n' \
        "${marker}" \
        "*.* @127.0.0.1:${BROKER_PORT}" \
        | sudo tee -a "${conf}" > /dev/null

      sudo launchctl kickstart -k system/com.apple.syslogd \
        && echo "syslogd restarted." \
        || echo "WARNING: could not restart syslogd — run: sudo launchctl kickstart -k system/com.apple.syslogd"
      ;;

    *)
      die "Unsupported OS '${os}'. Only Linux and macOS are supported."
      ;;
  esac

  echo "syslog setup: done."
}

# ──────────────────────────────────────────────
# remove
# ──────────────────────────────────────────────
cmd_remove() {
  _load_syslog_vars

  if [[ "${SYSLOG_MON}" != "true" ]]; then
    echo "syslog remove: SYSLOG_MONITORING is not 'true' in ${NODE_CONFIGS} — skipping."
    exit 0
  fi

  [[ -n "${BROKER_PORT}" ]] || die "ANYLOG_BROKER_PORT is not set in ${NODE_CONFIGS}."

  local os marker
  os=$(uname -s)
  marker="# anylog-forwarding port=${BROKER_PORT}"

  case "${os}" in

    Linux)
      local conf="/etc/rsyslog.d/60-custom-forwarding.conf"

      if [[ ! -f "${conf}" ]]; then
        echo "syslog remove: ${conf} not found — nothing to remove."
        exit 0
      fi

      sudo rm -f "${conf}"
      echo "Removed ${conf}"

      sudo systemctl restart rsyslog \
        && echo "rsyslog restarted." \
        || echo "WARNING: could not restart rsyslog — run: sudo systemctl restart rsyslog"
      ;;

    Darwin)
      local conf="/etc/syslog.conf"

      if ! grep -qF "${marker}" "${conf}" 2>/dev/null; then
        echo "syslog remove: AnyLog rule not found in ${conf} — nothing to remove."
        exit 0
      fi

      # Two-pass removal: delete the marker line and the forwarding rule that
      # follows it.  Using an address range is safer than { N; d; } which
      # breaks when the marker falls on the last line of the file.
      sudo sed -i '' "/${marker//\//\\/}/,/^\*\.\* @127\.0\.0\.1:${BROKER_PORT}$/d" "${conf}"
      echo "Removed AnyLog forwarding rule from ${conf}"

      sudo launchctl kickstart -k system/com.apple.syslogd \
        && echo "syslogd restarted." \
        || echo "WARNING: could not restart syslogd — run: sudo launchctl kickstart -k system/com.apple.syslogd"
      ;;

    *)
      die "Unsupported OS '${os}'."
      ;;
  esac

  echo "syslog remove: done."
}

# ──────────────────────────────────────────────
# help
# ──────────────────────────────────────────────
cmd_help() {
  cat <<EOF

Usage: bash syslog.sh <command> [NODE_CONFIGS]

Commands:
  setup    Configure host syslog to forward to AnyLog broker port (idempotent)
  remove   Remove the AnyLog syslog forwarding rule
  help     Show this message

Arguments:
  NODE_CONFIGS   Path to node_configs.env
                 (default: docker-makefiles/anylog-generic/node_configs.env)

Config keys read from NODE_CONFIGS:
  SYSLOG_MONITORING    Must be "true" to take any action
  ANYLOG_BROKER_PORT   Port syslog forwards to

Platform behaviour:
  Linux  — rsyslog drop-in /etc/rsyslog.d/60-custom-forwarding.conf  (TCP)
  macOS  — /etc/syslog.conf append                                    (UDP)

Examples:
  bash syslog.sh setup
  bash syslog.sh setup  docker-makefiles/anylog-operator/node_configs.env
  bash syslog.sh remove docker-makefiles/anylog-operator/node_configs.env

EOF
}

# ──────────────────────────────────────────────
# Dispatch
# ──────────────────────────────────────────────
case "${COMMAND}" in
  setup)          cmd_setup  ;;
  remove)         cmd_remove ;;
  help|--help|-h) cmd_help   ;;
  *) die "Unknown command '${COMMAND}' — run 'bash syslog.sh help'" ;;
esac