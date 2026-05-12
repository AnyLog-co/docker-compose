#!/usr/bin/env bash
# license.sh — LICENSE_KEY resolver
#
# Resolves LICENSE_KEY from (in priority order):
#   1. Environment variable   (set manually or passed via Makefile)
#   2. Config file            (base_configs.env for multi-file layout,
#                              node_configs.env for single-file layout)
#
# Exports LICENSE_KEY into the environment so both deploy.sh and
# docker compose inherit it.
#
# Usage (always sourced, never executed directly):
#   source docker-makefiles/license.sh <NODE_CONFIGS>
#
# Arguments:
#   NODE_CONFIGS   Canonical node type dir name  (e.g. anylog-operator)
#                  The same value passed as ANYLOG_TYPE elsewhere.

# ── Guard: must be sourced, not executed ──────────────────────────────
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "ERROR: license.sh must be sourced, not executed directly." >&2
  echo "       Use: source docker-makefiles/license.sh <NODE_CONFIGS>" >&2
  exit 1
fi

# ── Helpers ───────────────────────────────────────────────────────────
_license_die() { echo "ERROR: $1" >&2; return 1; }

# ── Args ──────────────────────────────────────────────────────────────
_license_resolve() {
  local node_configs="${1:-}"
  local config_file=""

  [[ -n "${node_configs}" ]] \
    || _license_die "license.sh: NODE_CONFIGS argument is required" || return 1

  # ── 1. Already in environment ────────────────────────────────────────
  if [[ -n "${LICENSE_KEY:-}" ]]; then
    echo "LICENSE_KEY: resolved from environment"
    export LICENSE_KEY
    return 0
  fi

  # ── 2. Locate config file ────────────────────────────────────────────
  # Multi-file layout: LICENSE_KEY lives in base_configs.env
  # Single-file layout: LICENSE_KEY lives in node_configs.env
  local base_env="docker-makefiles/${node_configs}/base_configs.env"
  local single_env="docker-makefiles/${node_configs}/node_configs.env"

  if [[ -f "${base_env}" ]]; then
    config_file="${base_env}"
  elif [[ -f "${single_env}" ]]; then
    config_file="${single_env}"
  else
    _license_die "license.sh: no config file found for '${node_configs}'" || return 1
  fi

  # ── 3. Read from config file ─────────────────────────────────────────
  local key
  key=$(grep -m1 '^LICENSE_KEY=' "${config_file}" 2>/dev/null \
        | cut -d= -f2- | tr -d '"'"'"' | tr -d '[:space:]' || true)

  if [[ -n "${key}" ]]; then
    echo "LICENSE_KEY: resolved from ${config_file}"
    export LICENSE_KEY="${key}"
    return 0
  fi

  # ── 4. Not found anywhere ────────────────────────────────────────────
  _license_die "LICENSE_KEY is not set. Provide it via:
       - Environment:  LICENSE_KEY=<key> make up
       - Makefile:     LICENSE_KEY := <key>
       - Config file:  LICENSE_KEY=<key> in ${config_file}" || return 1
}

_license_resolve "$@"