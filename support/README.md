# AnyLog Support Services

Tooling to configure, generate, and manage the Docker/Podman containers that run alongside AnyLog:
* **[Remote-GUI](https://github.com/AnyLog-co/Remote-GUI)**
* **[Grafana](https://grafana.com/docs/grafana/latest/setup-grafana/installation/docker/)**
* **[PostgreSQL](https://hub.docker.com/_/postgres/)**
* **[MongoDB](https://hub.docker.com/_/mongo/)**
* **[Ollama](ollama/README.md)** — local LLM runtime for MCP function calling
* **[Video Inference Models](https://github.com/AnyLog-co/AnyLog-Video-Inference-Models)** — CV/ML inference on edge video streams

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
- [docker_compose_builder.sh](#docker_compose_buildersh)
- [Makefile Reference](#makefile-reference)
  - [Targets](#targets)
  - [Service Aliases](#service-aliases)
  - [Example Commands](#example-commands)
- [Requirements](#requirements)

---

## Directory Structure

```
support/
├── Makefile                      # All lifecycle commands
├── README.md                     # This file
├── Ollama.md                     # Ollama setup guide
├── Video-Inferences.md           # Video inference models guide
├── docker_compose_builder.sh     # Generates docker-compose.yml from configs.yaml
├── grafana/
│   └── configs.yaml
├── mongodb/
│   └── configs.yaml
├── ollama/
│   ├── configs.yaml
│   ├── docker-compose.yaml
│   ├── docker-compose-gpu.yaml
│   └── ollama-configs.png
├── postgres/
│   └── configs.yaml
└── remote-gui/
    └── configs.yaml
```

> **Note:** Ollama and Video Inference Models are standalone services and are **not** managed by the `Makefile`.
> See [Ollama.md](Ollama.md) and [Video-Inferences.md](Video-Inferences.md) for their dedicated setup guides.

---

## Quick Start

```bash
# 1. Generate all docker-compose files from configs
make docker-builder

# 2. Start all services
make up

# 3. Start a specific service
make up SERVICE=gui
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

| Field | Value |
|---|---|
| Image | `anylogco/remote-gui:beta2` |
| Ports | `8080` (backend), `31800` (frontend) |
| Key env vars | `REMOTE_GUI_FE`, `REMOTE_GUI_BE`, `GRAFANA_URL`, `REMOTE_GUI_NIC` |
| Volumes | `image-vol`, `usr-mgm-vol`, `report-configs` |

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

---

## Makefile Reference

The Makefile auto-detects `docker`/`podman` and `docker-compose`/`podman-compose`.

### Targets

| Target | Description |
|---|---|
| `docker-builder` | Generate `docker-compose.yml` for all (or one) service |
| `up` | Start service(s) |
| `down` | Stop service(s) |
| `clean` | Stop and remove volumes |
| `clean-all` | Stop, remove volumes and image |
| `logs` | Print container logs |
| `logs-f` | Follow container logs |
| `exec` | Attach to container shell |

Pass `SERVICE=<alias>` to target a single service. Omit it to act on all four.

### Service Aliases

| Service | Accepted aliases |
|---|---|
| Remote-GUI | `remote-gui`, `gui` |
| Grafana | `grafana` |
| PostgreSQL | `postgres`, `psql` |
| MongoDB | `mongodb`, `mongo` |

### Example Commands

```bash
# Generate
make docker-builder                        # all services
make docker-builder SERVICE=remote-gui     # one service

# Lifecycle
make up                                    # start all
make up        SERVICE=gui
make down      SERVICE=grafana
make clean     SERVICE=mongo
make clean-all SERVICE=psql

# Logs
make logs   SERVICE=gui                    # print and exit
make logs-f SERVICE=mongo                  # follow

# Shell access
make exec SERVICE=gui                      # /bin/bash
make exec SERVICE=psql                     # psql -U postgres
make exec SERVICE=mongo                    # mongosh
```

---

## Requirements

- Docker ≥ 20.10 **or** Podman ≥ 4.0
- `docker compose` plugin **or** `docker-compose` / `podman-compose`
- Bash ≥ 4.0 (for `docker_compose_builder.sh`)
- `make`