# AnyLog Support Services

Tooling to configure, generate, and manage the Docker/Podman containers that run alongside AnyLog:
* **[Remote-GUI](https://github.com/AnyLog-co/Remote-GUI)**
* **[Grafana](https://grafana.com/docs/grafana/latest/setup-grafana/installation/docker/)**
* **[PostgreSQL](https://hub.docker.com/_/postgres/)**
* **[MongoDB](https://hub.docker.com/_/mongo/)**
* **[Ollama](Ollama.md)** — local LLM runtime for MCP function calling
* **[Video Inference Models](https://github.com/AnyLog-co/AnyLog-Video-Inference-Models)** — CV/ML inference on edge video streams
* **[Nebula Overlay Network](https://github.com/oshadmon/nebula-anylog)** — encrypted peer-to-peer overlay so AnyLog nodes on separate physical networks communicate as a single unified network

## Requirements

- Docker ≥ 20.10 **or** Podman ≥ 4.0
- `docker compose` plugin **or** `docker-compose` / `podman-compose`
- Bash ≥ 4.0 (for `docker_compose_builder.sh`)
- `make`

---

## Table of Contents

- [Directory Structure](#directory-structure)
- [Quick Start](#quick-start)
- [Config File Format](#config-file-format)
- [Service Configs](#service-configs)
  - [Remote-GUI](#remote-gui)
  - [Grafana](#grafana)
  - [PostgreSQL](#postgresql)
  - [MongoDB](#mongodb)
  - [Ollama](#ollama)
  - [Video Inference Models](#video-inference-models)
  - [Nebula Overlay](#nebula-overlay-network)
- [docker_compose_builder.sh](#docker_compose_buildersh)
- [Makefile Reference](#makefile-reference)
  - [Targets](#targets)
  - [Service Aliases](#service-aliases)
  - [Custom Instances](#custom-instances)
  - [Example Commands](#example-commands)

---

## Directory Structure

```
support/
├── Makefile                      # All lifecycle commands
├── README.md                     # This file
├── Ollama.md                     # Ollama setup guide
├── Video-Inferences.md           # Video inference models guide
├── Nebula.md                     # Nebula overlay network setup guide
├── docker_compose_builder.sh     # Generates docker-compose.yml from configs.yaml
├── grafana/
│   ├── configs.yaml
│   └── docker-compose.yml        # generated — do not edit by hand
├── mongodb/
│   ├── configs.yaml
│   └── docker-compose.yml
├── ollama/
│   ├── configs.yaml
│   ├── docker-compose.yaml
│   ├── docker-compose-gpu.yaml
│   └── ollama-configs.png
├── postgres/
│   ├── configs.yaml
│   └── docker-compose.yml
└── remote-gui/
    ├── configs.yaml
    └── docker-compose.yml
```

Each `docker-compose.yml` is auto-generated from its sibling `configs.yaml` — either explicitly via `make dry-run` or automatically on the first `make up` for that service.

> **Note:** Ollama, Nebula and Video Inference Models are standalone services and are **not** managed by the `Makefile`.
> See [Ollama.md](Ollama.md), [Nebula.md](Nebula.md) and [Video-Inferences.md](Video-Inferences.md) for their dedicated setup guides.

---

## Quick Start

```bash
# 1. (Optional) Pre-generate all docker-compose files
make dry-run

# 2. Start all default services (generates compose files on-demand if missing)
make up

# 3. Start a specific service
make up SERVICE=grafana

# 4. List all services the Makefile can see
make list
```

---

## Config File Format

Each service directory contains a `configs.yaml` that drives `docker_compose_builder.sh`. The file has four sections:

```yaml
GENERAL:
  IMAGE: <registry/image>
  TAG:   <tag>
  NAME:  <container name>          # also becomes the compose service key

NETWORK_CONFIGS:
  NETWORK_MODE: host | ports       # host → network_mode: host; ports → publishes listed ports
  PORTS:
    - <port>

ENV_VARS:
  KEY: value                       # passed as environment variables
  # comment lines are stripped

VOLUMES:
  volume-name: /container/path     # named volumes — declared at top level automatically
```

> **`REMOTE_GUI_NIC`** (remote-gui only): when this key is present in `ENV_VARS`, the builder resolves its value as a network interface name at generation time and injects `VITE_API_URL=http://<resolved-ip>:<REMOTE_GUI_BE>`. Leave the key absent to skip `VITE_API_URL` entirely.

---

## Service Configs

### Remote-GUI

| Field | Value                                                             |
|---|-------------------------------------------------------------------|
| Image | `anylogco/remote-gui:1.0.0`                                       |
| Ports | `8080` (backend), `31800` (frontend)                              |
| Key env vars | `REMOTE_GUI_FE`, `REMOTE_GUI_BE`, `GRAFANA_URL`, `REMOTE_GUI_NIC` |
| Volumes | `image-vol`, `usr-mgm-vol`, `report-configs`                      |

### Grafana

| Field | Value |
|---|---|
| Image | `grafana/grafana:latest` |
| Port | `3000` |
| Key env vars | `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_INITDB_ARGS` |
| Volumes | `grafana-data`, `grafana-log`, `grafana-config` |

### PostgreSQL

| Field | Value |
|---|---|
| Image | `postgres:16.0-alpine` |
| Port | `5432` |
| Key env vars | `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_INITDB_ARGS` |
| Volumes | `pgdata` |

### MongoDB

| Field | Value |
|---|---|
| Image | `mongo:latest` |
| Port | `27017` |
| Key env vars | `MONGO_USER`, `MONGO_PASSWORD` |
| Volumes | `mongo-data`, `mongo-configs` |

### Ollama

Ollama is a lightweight open-source framework for running LLMs locally. AnyLog/EdgeLake use it as the tested model framework for MCP function calling in the Remote-GUI.

| Field | Value |
|---|---|
| Image | `ollama/ollama:latest` |
| Port | `11434` |
| GPU variant | `ollama/docker-compose-gpu.yaml` (requires NVIDIA Container Toolkit) |
| Default model | `qwen2.5:7b-instruct` |

→ Full setup guide: [Ollama.md](Ollama.md)

### Video Inference Models

CV/ML inference on edge video streams, feeding results into AnyLog/EdgeLake nodes.

→ Full setup guide: [Video-Inferences.md](Video-Inferences.md)  
→ Source repository: [AnyLog-co/AnyLog-Video-Inference-Models](https://github.com/AnyLog-co/AnyLog-Video-Inference-Models)

### Nebula Overlay Network

Nebula creates an encrypted peer-to-peer mesh across physically separated machines, giving distributed AnyLog/EdgeLake nodes a shared overlay IP space without requiring them to be on the same LAN or VPN.

| Field | Value |
|---|---|
| Deployed via | `docker compose` on each node |
| Min. nodes | 1 lighthouse + 1 host |
| Overlay port | UDP `4242` |
| Auth | Mutual certificate-based (CA you control) |

→ Full setup guide: [Nebula.md](Nebula.md)  
→ Source repository: [oshadmon/nebula-anylog](https://github.com/oshadmon/nebula-anylog)

---

## `docker_compose_builder.sh`

Reads a `configs.yaml` and writes a `docker-compose.yml` next to it.

```bash
# Usage
./docker_compose_builder.sh [config_file] [output_file]

# Defaults
./docker_compose_builder.sh                                           # configs.yaml → docker-compose.yml
./docker_compose_builder.sh remote-gui/configs.yaml                  # custom input
./docker_compose_builder.sh remote-gui/configs.yaml out-compose.yml  # custom input + output
```

All generated compose files include:
```yaml
restart: always
stdin_open: true
tty: true
```

### Port Conflict Detection

Before writing the compose file, the builder checks whether any port in `NETWORK_CONFIGS.PORTS` is already in use, adapting the check to the network mode:

| `NETWORK_MODE` | How ports are bound | Check method |
|---|---|---|
| `ports` | Docker proxy | `docker ps --format '{{.Ports}}'` |
| `host` | Host OS directly | `ss -tlnp` (falls back to `lsof`) |

If a conflict is found, the builder prints which container or process holds the port and exits non-zero — the compose file is not written.

---

## Makefile Reference

The Makefile auto-detects `docker`/`podman` and `docker-compose`/`podman-compose`.

Any subdirectory containing a `configs.yaml` is automatically recognised as a service — no edits to the Makefile are needed to add new instances.

### Targets

| Target | Description |
|---|---|
| `dry-run` | Generate `docker-compose.yml` for all discovered services (or `SERVICE=one`) |
| `up` | Start service(s); generates compose file on-demand if missing |
| `down` | Stop service(s) |
| `clean` | Stop and remove volumes |
| `clean-all` | Stop, remove volumes and image |
| `logs` | Print container logs (`SERVICE=` required) |
| `logs-f` | Follow container logs (`SERVICE=` required) |
| `exec` | Attach to container shell/client (`SERVICE=` required) |
| `list` | Print default and all auto-discovered services |

Omit `SERVICE` to act on all four default services (`remote-gui`, `grafana`, `postgres`, `mongodb`).

### Service Aliases

| Service | Accepted values for `SERVICE=` |
|---|---|
| Remote-GUI | `remote-gui`, `gui` |
| Grafana | `grafana` |
| PostgreSQL | `postgres`, `psql` |
| MongoDB | `mongodb`, `mongo` |

### Custom Instances

To run a second PostgreSQL or MongoDB instance (e.g. for a different AnyLog node), create a new directory with a `configs.yaml` — no Makefile changes required:

```bash
cp -r postgres/ postgres-prod/
# edit postgres-prod/configs.yaml (change NAME, port, volumes as needed)

make up   SERVICE=postgres-prod
make logs SERVICE=postgres-prod
make exec SERVICE=postgres-prod    # drops into psql automatically
```

`make list` shows every directory the Makefile has discovered.

### Example Commands

```bash
# Generate compose files
make dry-run                           # all discovered services
make dry-run SERVICE=remote-gui        # one service

# Lifecycle
make up                                # start all 4 defaults
make up        SERVICE=gui
make up        SERVICE=postgres-prod   # custom instance
make down      SERVICE=grafana
make clean     SERVICE=mongo
make clean-all SERVICE=psql

# Logs
make logs   SERVICE=gui                # print and exit
make logs-f SERVICE=mongo              # follow

# Shell / client access
make exec SERVICE=gui                  # /bin/bash
make exec SERVICE=psql                 # psql -U postgres
make exec SERVICE=mongo                # mongosh
make exec SERVICE=postgres-prod        # psql -U postgres (matches postgres* pattern)

# Discovery
make list                              # show default + all discovered services
```