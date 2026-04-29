# Deploying AnyLog

AnyLog enables real-time visibility and management of distributed edge data, applications, and infrastructure. It
transforms edge environments into scalable data tiers optimized for IoT, allowing organizations to extract insights
across industries like manufacturing, utilities, oil & gas, smart cities, retail, robotics, and more.

* [Documentation](https://github.com/AnyLog-co/documentation/)
* [Support services](support/README.md) — Grafana, PostgreSQL, MongoDB, Remote-GUI


## Repository Layout

```
docker-compose/
├── Makefile                          # Main lifecycle commands for AnyLog nodes
├── README.md                         # This file
├── Deploy_PLC.md                     # PLC deployment guide
├── docker_run.sh                     # Standalone docker run helper
├── docker-makefiles/
│   ├── anylog-generic/
│   │   └── node_configs.env          # Config template — copy and customise per node
│   ├── anylog-master/
│   ├── anylog-operator/
│   ├── anylog-publisher/
│   ├── anylog-query/
│   ├── anylog-standalone-operator/
│   ├── anylog-standalone-publisher/
│   ├── build_docker_compose.sh       # Generates docker-compose.yaml from configs
│   ├── prep_configs.sh               # Pre-flight config validation
│   ├── docker-compose-template-base.yaml       # Linux template (host networking)
│   └── docker-compose-template-ports-base.yaml # Mac/Windows template (port mapping)
└── support/                          # External services (Grafana, Postgres, MongoDB, etc.)
    └── README.md
```

Generated compose files land in `docker-makefiles/docker-compose-files/` and are not committed to the repo.


## Prepare Machine

* [Docker & Docker-Compose](https://docs.docker.com/engine/install/)

```shell
# Install Docker on Ubuntu
sudo apt-get -y update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get -y update

sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin make git

# Grant non-root user permissions to use Docker
USER=`whoami`
sudo groupadd docker
sudo usermod -aG docker ${USER}
newgrp docker
```

* Clone the deployment repository
```shell
git clone https://github.com/AnyLog-co/docker-compose
cd docker-compose
```

* AnyLog is a private repository — [request credentials](https://www.anylog.network/download) for Docker login and your license key.
```shell
docker login -u anyloguser -p [Docker Login Passkey]
```


## Node Types

All AnyLog containers run the same image — configurations determine which services are enabled.

| Node Type               | Description                                             | Server Port | REST Port |
|-------------------------|---------------------------------------------------------|-------------|-----------|
| `generic`               | Sandbox with only network configured                    | 32548       | 32549     |
| `master`                | Blockchain emulator ("Oracle" alternative)              | 32048       | 32049     |
| `operator`              | Stores data from edge devices                           | 32148       | 32149     |
| `query`                 | Dedicated query node (enables `system_query` database)  | 32348       | 32349     |
| `publisher`             | Distributes data among operator nodes                   | 32248       | 32249     |
| `standalone-operator`   | Combined master and operator on a single agent          | 32148       | 32149     |
| `standalone-publisher`  | Combined master and publisher on a single agent         | 32248       | 32249     |

You can pass either the short form (`operator`) or the full directory name (`anylog-operator`) — the Makefile resolves both.


## Deployment via Makefile

The [Makefile](Makefile) supports both _Podman_ and _Docker_, using either manual variable overrides or a
configuration file in `docker-makefiles/`.

```
Usage: make [target] [VARIABLE=value]

Available targets:
  login                 Log into Docker Hub for AnyLog
  pull                  Pull image from Docker Hub
  dry-run               Generate docker-compose.yaml from config file(s)
  up                    Start AnyLog instance
  down                  Stop AnyLog instance
  clean                 Stop container and remove volumes
  clean-all             Stop container, remove volumes and image
  attach                Attach to container (ctrl-d to detach)
  exec                  Attach to container bash shell (as anylog user)
  exec-root             Attach to container bash shell as root
  logs                  View container logs
  logs-f                Follow container logs
  check-vars            Show all environment variable values

Common variables:
  IS_MANUAL             Use manual deployment (true/false)
  ANYLOG_TYPE           Node type to deploy (e.g., master, operator)
  IMAGE                 Docker image repository
  TAG                   Docker image tag
  NODE_NAME             Custom container name
  CLUSTER_NAME          Cluster the operator node is associated with
  ANYLOG_SERVER_PORT    Port for TCP communication
  ANYLOG_REST_PORT      Port for REST API
  ANYLOG_BROKER_PORT    Optional broker port
  LEDGER_CONN           Master node IP:port
  LICENSE_KEY           AnyLog license key
```

### Important Notes

- **Unique ports**: No two containers on the same machine can share ports. Set unique `ANYLOG_SERVER_PORT` and `ANYLOG_REST_PORT` per container.
- **Unique node names**: Each node must have a distinct `NODE_NAME`.
- **Clusters**: `CLUSTER_NAME` should be unique per operator unless HA is configured.
- **License key**: A valid `LICENSE_KEY` is required. [Request one here](https://www.anylog.network/download).


### Manual Deployment

Uses built-in defaults with a small set of overrides. Database layer is always SQLite in manual mode.

```shell
# Generic — empty node with only network services
make up IS_MANUAL=true ANYLOG_TYPE=generic LICENSE_KEY=[key]

# Master — blockchain emulator
make up IS_MANUAL=true ANYLOG_TYPE=master LICENSE_KEY=[key] ANYLOG_SERVER_PORT=32048 ANYLOG_REST_PORT=32049

# Operator — stores data from devices
make up IS_MANUAL=true ANYLOG_TYPE=operator LICENSE_KEY=[key] \
  ANYLOG_SERVER_PORT=32148 ANYLOG_REST_PORT=32149 \
  LEDGER_CONN=127.0.0.1:32048 CLUSTER_NAME=my-cluster1

# Query — dedicated query node
make up IS_MANUAL=true ANYLOG_TYPE=query LICENSE_KEY=[key] \
  ANYLOG_SERVER_PORT=32348 ANYLOG_REST_PORT=32349 LEDGER_CONN=127.0.0.1:32048

# Publisher — distributes data to operators
make up IS_MANUAL=true ANYLOG_TYPE=publisher LICENSE_KEY=[key] \
  ANYLOG_SERVER_PORT=32248 ANYLOG_REST_PORT=32249 LEDGER_CONN=127.0.0.1:32048
```


### Configuration-based Deployment

For full control over node behavior, use a `node_configs.env` file.

1. **Copy the config template**
```shell
cp -r docker-makefiles/anylog-generic docker-makefiles/my-operator
```

2. **Edit `docker-makefiles/my-operator/node_configs.env`** — at minimum, update these:
   - `NODE_TYPE` — set to your desired node type
   - `NODE_NAME` — must be unique per node
   - `COMPANY_NAME`
   - `ANYLOG_SERVER_PORT`, `ANYLOG_REST_PORT` — must be unique per machine
   - `LEDGER_CONN` — IP:port of the master node
   - `CLUSTER_NAME` — unique per operator unless HA is enabled
   - `LICENSE_KEY`
   - `DB_USER` / `DB_PASSWD` (if using PostgreSQL)

3. **Deploy**
```shell
make up ANYLOG_TYPE=my-operator
```

4. **Check status**
```shell
make logs ANYLOG_TYPE=my-operator
```

5. **Attach to the node** — press Enter twice once attached, `ctrl-d` to detach
```shell
make attach ANYLOG_TYPE=my-operator
```

#### Deploying a Second Node of the Same Type

```shell
cp -r docker-makefiles/my-operator docker-makefiles/my-operator2
# Edit node_configs.env — update NODE_NAME, ports, CLUSTER_NAME
make up ANYLOG_TYPE=my-operator2
```

## Testing

The Makefile includes a set of targets to validate that an AnyLog node is active and reachable via REST.
These targets work independently of `ANYLOG_TYPE` — you can test any node on the network as long as you know its 
REST address.

```shell
# Default connection (127.0.0.1:32549 — generic node)
make test-status

# Target a specific node
make full-test TEST_CONN=192.168.1.10:32149
```

| Target            | Command sent        | Description                                      |
|-------------------|---------------------|--------------------------------------------------|
| `full-test`       | —                   | Runs `test-status`, `test-node`, `test-network` in sequence |
| `test-status`     | `get status`        | Confirms the node process is running             |
| `test-node`       | `test node`         | Validates node configuration and connectivity    |
| `test-network`    | `test network`      | Checks communication with other network members  |
| `check-processes` | `get processes`     | Lists all active and inactive services on the node |

**Variable:**

| Variable    | Default           | Description                        |
|-------------|-------------------|------------------------------------|
| `TEST_CONN` | `127.0.0.1:32549` | `IP:port` of the node to test against |

Port reference — use the `ANYLOG_REST_PORT` for the node type you are testing:

| Node type  | REST port |
|------------|-----------|
| generic    | 32549     |
| master     | 32049     |
| operator   | 32149     |
| query      | 32349     |
| publisher  | 32249     |

