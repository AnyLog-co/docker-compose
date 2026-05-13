# Deploying AnyLog

AnyLog enables real-time visibility and management of distributed edge data, applications, and infrastructure. It
transforms edge environments into scalable data tiers optimized for IoT, allowing organizations to extract insights
across industries like manufacturing, utilities, oil & gas, smart cities, retail, robotics, and more.

* [Documentation](https://github.com/AnyLog-co/documentation/)
* [Support services](support/README.md) — Grafana, PostgreSQL, MongoDB, Remote-GUI


## Repository Layout

```
docker-compose/
├── Makefile                          # Thin wrapper around deploy.sh
├── deploy.sh                         # Node lifecycle manager — works without make
├── README.md                         # This file
├── Deploy_PLC.md                     # PLC deployment guide
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

> **Note:** The `Makefile` is a thin wrapper — every target delegates to `deploy.sh`. If `make` is not available
> on your system (e.g. certain ARM/Qualcomm hardware), use `bash deploy.sh` directly with identical behaviour.


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

Both the short form (`operator`) and the full directory name (`anylog-operator`) are accepted — both tools resolve
the alias automatically.


## Deployment

All commands are available via `make` or `bash deploy.sh` — choose whichever is available on your system.

```
Commands:
  login           Log into Docker Hub
  pull            Pull image from Docker Hub
  dry-run         Generate docker-compose.yaml (prints docker run command in manual mode)
  up              Start AnyLog instance
  down            Stop AnyLog instance
  clean           Stop and remove volumes
  clean-all       Stop, remove volumes and image
  logs            View container logs
  logs-f          Follow container logs
  attach          Attach to container (ctrl-d to detach)
  exec            Shell into container (anylog user)
  exec-root       Shell into container (root)
  full-test       Run test-status + test-node + test-network
  test-status     GET status from node
  test-node       Test node configuration
  test-network    Test network connectivity
  check-processes List active/inactive services
  check-vars      Show resolved variable values

Variables (make) / Options (deploy.sh):
  IS_MANUAL / --manual      Use docker run instead of docker compose (default: false)
  ANYLOG_TYPE / --type      Node type to deploy
  TAG         / --tag       Image tag                    (default: pre-develop)
  IMAGE       / --image     Image repository
  NODE_NAME   / --node-name Override container name
  TEST_CONN   / --test-conn ip:port for test commands    (default: auto-resolved)
  LICENSE_KEY / --license-key License key for deployment  (prompts if missing)
  PROMPT_LICENSE / --prompt-license Force license key and acceptance prompts
```

### Important Notes

- **Unique ports**: No two containers on the same machine can share ports. Set unique `ANYLOG_SERVER_PORT` and `ANYLOG_REST_PORT` per container.
- **Unique node names**: Each node must have a distinct `NODE_NAME`.
- **Clusters**: `CLUSTER_NAME` should be unique per operator unless HA is configured.
- **License key**: A valid `LICENSE_KEY` is required. [Request one here](https://www.anylog.network/download).


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
# via make
make up ANYLOG_TYPE=my-operator

# via deploy.sh (no make required)
bash deploy.sh up --type my-operator
```

4. **Check status**
```shell
make logs ANYLOG_TYPE=my-operator
bash deploy.sh logs --type my-operator
```

5. **Attach to the node** — press Enter twice once attached, `ctrl-d` to detach
```shell
make attach ANYLOG_TYPE=my-operator
bash deploy.sh attach --type my-operator
```

#### Deploying a Second Node of the Same Type

```shell
cp -r docker-makefiles/my-operator docker-makefiles/my-operator2
# Edit node_configs.env — update NODE_NAME, ports, CLUSTER_NAME
make up ANYLOG_TYPE=my-operator2
bash deploy.sh up --type my-operator2
```


### Manual Deployment (docker run)

When `IS_MANUAL=true` / `--manual`, the node is started with `docker run --env-file` rather than docker compose.
This is useful on systems where docker compose is unavailable. The same `node_configs.env` file is used.

Running `dry-run` in manual mode prints the exact `docker run` command that will be executed — useful for
inspection before committing:

```shell
make dry-run IS_MANUAL=true ANYLOG_TYPE=operator
bash deploy.sh dry-run --type operator --manual
```

To start:
```shell
# Generic
make up IS_MANUAL=true ANYLOG_TYPE=generic
bash deploy.sh up --type generic --manual

# Operator
make up IS_MANUAL=true ANYLOG_TYPE=operator
bash deploy.sh up --type operator --manual

# Master
make up IS_MANUAL=true ANYLOG_TYPE=master
bash deploy.sh up --type master --manual
```

> **Note:** In manual mode the init container that pre-sets volume ownership does not run.
> Volume directories will be owned by root until AnyLog corrects permissions internally.


## Debug Mode

Debug mode starts a lightweight sidecar container alongside the AnyLog node. It shares the node's network stack,
PID namespace, and data volumes, making it useful for diagnosing connectivity or inspecting files without touching
the running node. Common network tools (`ping`, `nc`, `curl`, `net-tools`) are pre-installed.

```shell
make up-debug ANYLOG_TYPE=my-operator
bash deploy.sh up --type my-operator  # sidecar activated via --profile debug

# Shell into the sidecar
docker exec -it my-operator-debugger /bin/bash

make down-debug ANYLOG_TYPE=my-operator
```

### Root Access to the Running Node

The AnyLog container runs as the `anylog` user. To install tools or inspect system state without restarting:

```shell
make exec-root ANYLOG_TYPE=my-operator
bash deploy.sh exec-root --type my-operator
# node process keeps running — changes do not persist across restarts
apt-get update && apt-get install -y net-tools iputils-ping netcat-traditional
```


## Testing

Test targets work independently of `ANYLOG_TYPE` — point them at any reachable node via `TEST_CONN`.

```shell
# Default (127.0.0.1 + REST port from config)
make test-status ANYLOG_TYPE=my-operator
bash deploy.sh test-status --type my-operator

# Target any node explicitly
make full-test TEST_CONN=192.168.1.10:32149
bash deploy.sh full-test --test-conn 192.168.1.10:32149
```

| Target / Command     | AnyLog command sent | Description                                          |
|----------------------|---------------------|------------------------------------------------------|
| `full-test`          | —                   | Runs test-status, test-node, test-network in sequence |
| `test-status`        | `get status`        | Confirms the node process is running                 |
| `test-node`          | `test node`         | Validates node configuration and connectivity        |
| `test-network`       | `test network`      | Checks communication with other network members      |
| `check-processes`    | `get processes`     | Lists all active and inactive services on the node   |

Port reference:

| Node type  | REST port |
|------------|-----------|
| generic    | 32549     |
| master     | 32049     |
| operator   | 32149     |
| query      | 32349     |
| publisher  | 32249     |


## Using Windows & Mac

Docker Desktop uses port-based networking instead of `network_mode: host`, which may cause containers to advertise
the Docker internal IP rather than the machine IP.

1. Enable host networking in Docker Desktop preferences.

2. Find your machine's local IP:
```shell
# Mac
ifconfig en0 | grep "inet "

# Windows
ipconfig
```

3. In `node_configs.env`, set `OVERLAY_IP` under the advanced section:
```dotenv
OVERLAY_IP=192.168.86.28
```

4. Optionally set `TCP_BIND=true` under advanced networking for stricter port binding.

5. Deploy:
```shell
make up ANYLOG_TYPE=my-operator
bash deploy.sh up --type my-operator
```


## Persisting Configs After Reboot

Docker restarts containers using in-memory state, not updated env files. To apply config changes on reboot:

**Option 1** — Rebuild the container after updating configs:
```shell
make up ANYLOG_TYPE=my-operator
bash deploy.sh up --type my-operator
```

**Option 2** — Use `systemd` to rebuild on boot:
```
# /etc/systemd/system/anylog-operator-redeploy.service
[Unit]
Description=Redeploy AnyLog Node After Reboot
After=network.target docker.service
Requires=docker.service

[Service]
WorkingDirectory=%h/docker-compose
ExecStart=/usr/bin/bash deploy.sh up --type my-operator
Restart=on-failure
User=%u

[Install]
WantedBy=multi-user.target
```

```shell
sudo systemctl daemon-reload
sudo systemctl enable anylog-operator-redeploy.service
```

Note: Each node requires its own systemd service.


## Support Services

External services that work alongside AnyLog nodes are managed separately under `support/`.

| Service    | Default Port | Notes                        |
|------------|--------------|------------------------------|
| Grafana    | 3000         | Dashboards and visualization |
| PostgreSQL | 5432         | Persistent storage backend   |
| MongoDB    | 27017        | Document store backend       |
| Remote-GUI | 8080, 31800  | AnyLog web interface         |

```shell
cd support/
make up SERVICE=grafana
make list    # show all discovered services
```

See [support/README.md](support/README.md) for full documentation.