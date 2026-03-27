# Deploying AnyLog

AnyLog enables real-time visibility and management of distributed edge data, applications, and infrastructure. It
transforms edge environments into scalable data tiers optimized for IoT, allowing organizations to extract insights
across industries like manufacturing, utilities, oil & gas, smart cities, retail, robotics, and more.

* [Documentation](https://github.com/AnyLog-co/documentation/)
* [Surrounding components install](support-tools/README.md)


## Prepare Machine

* [Docker & Docker-Compose](https://docs.docker.com/engine/install/)
* _Makefile_
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

| Node Type         | Description                                             | Server Port | REST Port |
|-------------------|---------------------------------------------------------|-------------|-----------|
| `generic`         | Sandbox with only network configured                    | 32548       | 32549     |
| `master`          | Blockchain emulator ("Oracle" alternative)              | 32048       | 32049     |
| `operator`        | Stores data from edge devices                           | 32148       | 32149     |
| `query`           | Dedicated query node (enables `system_query` database)  | 32348       | 32349     |
| `publisher`       | Distributes data among operator nodes                   | 32248       | 32249     |
| `master-operator` | Combined master and operator on a single agent          | 32148       | 32149     |
| `master-publisher`| Combined master and publisher on a single agent         | 32248       | 32249     |


## Deployment via Makefile

The [Makefile](Makefile) supports both _Podman_ and _Docker_, using either manual variable overrides or a
[configuration file](CONFIG.md) in `docker-makefiles/`.

```
Usage: make [target] [VARIABLE=value]

Available targets:
  login        Log into Docker Hub for AnyLog
  pull         Pull image from Docker Hub
  dry-run      Generate docker-compose.yaml from config file(s)
  up           Start AnyLog instance
  down         Stop AnyLog instance
  clean        Stop container and remove volumes
  clean-all    Stop container, remove volumes and image
  attach       Attach to container (ctrl-d to detach)
  exec         Attach to container bash shell
  logs         View container logs
  logs-f       Follow container logs
  check-vars   Show all environment variable values

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

For full control over node behavior, use a `node_configs.env` file. See [CONFIG.md](CONFIG.md) for all parameters.

1. **Copy the config template**
```shell
cp -r docker-makefiles/anylog-generic docker-makefiles/my-operator
```

2. **Edit `docker-makefiles/my-operator/node_configs.env`** — at minimum, update these in the `basic` section:
   - `NODE_TYPE` — set to your desired node type
   - `NODE_NAME` — must be unique per node
   - `COMPANY_NAME`
   - `ANYLOG_SERVER_PORT`, `ANYLOG_REST_PORT` — must be unique per machine
   - `LEDGER_CONN` — IP:port of the master node
   - `CLUSTER_NAME` — unique per operator unless HA is enabled

3. **Set credentials** in the `secrets` section:
   - `LICENSE_KEY`
   - `DB_USER` / `DB_PASSWD` (if using PostgreSQL)

4. **Deploy**
```shell
make up ANYLOG_TYPE=my-operator
```

5. **Check status**
```shell
make logs ANYLOG_TYPE=my-operator
```

6. **Attach to the node** — press Enter twice once attached, `ctrl-d` to detach
```shell
make attach ANYLOG_TYPE=my-operator
```

#### Deploying a Second Node of the Same Type

```shell
cp -r docker-makefiles/my-operator docker-makefiles/my-operator2
# Edit node_configs.env — update NODE_NAME, ports, CLUSTER_NAME
make up ANYLOG_TYPE=my-operator2
```


## Using Windows & Mac

Docker Desktop uses port-based networking instead of `network_mode: host`, which may cause containers to advertise the
Docker internal IP rather than the machine IP.

1. Validate Docker network settings — enable host networking in Docker Desktop preferences.

2. Find your machine's local IP:
```shell
# Mac
ifconfig en0 | grep "inet "

# Windows
ipconfig
```

3. In `node_configs.env`, set `OVERLAY_IP` under the `advanced` section:
```dotenv
OVERLAY_IP=192.168.86.28
```

4. Optionally set `TCP_BIND=true` under advanced networking for stricter port binding.

5. Deploy:
```shell
make up ANYLOG_TYPE=my-operator
```


## Persisting Configs After Reboot

Docker restarts containers using in-memory state, not updated env files. To apply config changes on reboot:

**Option 1** — Rebuild the container after updating configs:
```shell
make up ANYLOG_TYPE=my-operator
```

**Option 2** — Use `systemd` to rebuild on boot:
```service
# /etc/systemd/system/anylog-operator-redeploy.service
[Unit]
Description=Redeploy AnyLog Node After Reboot
After=network.target docker.service
Requires=docker.service

[Service]
WorkingDirectory=%h/docker-compose
ExecStart=/usr/bin/make up ANYLOG_TYPE=my-operator
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