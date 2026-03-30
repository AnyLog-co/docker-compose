# Deploying AnyLog

AnyLog enables real-time visibility and management of distributed edge data across IoT environments — manufacturing,
utilities, oil & gas, smart cities, and more.

- [Documentation](https://github.com/AnyLog-co/documentation/)
- [Configuration Reference](configs.md)
- [Surrounding tools install](support-tools/README.md)


---

## Prerequisites

**1. Install Docker and Make**
```shell
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

# Allow non-root Docker access
sudo usermod -aG docker $(whoami) && newgrp docker
```

**2. Clone this repo**
```shell
git clone https://github.com/AnyLog-co/docker-compose
cd docker-compose
```

**3. Log in to Docker Hub**

AnyLog is a private image — [request credentials and a license key](https://www.anylog.network/download).
```shell
docker login -u anyloguser -p <docker-passkey>
```


---

## Node Types

All AnyLog nodes run the same image — the `NODE_TYPE` config determines what services are enabled.

| Node Type          | Description                                             | Server Port | REST Port |
|--------------------|---------------------------------------------------------|-------------|-----------|
| `generic`          | Sandbox with only network configured                    | 32548       | 32549     |
| `master`           | Blockchain emulator                                     | 32048       | 32049     |
| `operator`         | Stores data from edge devices                           | 32148       | 32149     |
| `query`            | Dedicated query node (`system_query` database enabled)  | 32348       | 32349     |
| `publisher`        | Distributes data among operator nodes                   | 32248       | 32249     |
| `master-operator`  | Master + operator on a single agent                     | 32148       | 32149     |
| `master-publisher` | Master + publisher on a single agent                    | 32248       | 32249     |


---

## Quick Start — Manual Mode

Manual mode uses built-in defaults with a small number of overrides. The database is always SQLite.
Good for local testing; use [config-based deployment](#config-based-deployment) for production.

```shell
# Generic — empty node, network only
make up IS_MANUAL=true ANYLOG_TYPE=generic LICENSE_KEY=<key>

# Master — blockchain emulator
make up IS_MANUAL=true ANYLOG_TYPE=master LICENSE_KEY=<key> \
  ANYLOG_SERVER_PORT=32048 ANYLOG_REST_PORT=32049

# Operator — stores data from devices
make up IS_MANUAL=true ANYLOG_TYPE=operator LICENSE_KEY=<key> \
  ANYLOG_SERVER_PORT=32148 ANYLOG_REST_PORT=32149 \
  LEDGER_CONN=127.0.0.1:32048 CLUSTER_NAME=my-cluster1

# Query — dedicated query node
make up IS_MANUAL=true ANYLOG_TYPE=query LICENSE_KEY=<key> \
  ANYLOG_SERVER_PORT=32348 ANYLOG_REST_PORT=32349 LEDGER_CONN=127.0.0.1:32048

# Publisher — distributes data to operators
make up IS_MANUAL=true ANYLOG_TYPE=publisher LICENSE_KEY=<key> \
  ANYLOG_SERVER_PORT=32248 ANYLOG_REST_PORT=32249 LEDGER_CONN=127.0.0.1:32048
```

> **Each node on the same machine must have unique `ANYLOG_SERVER_PORT`, `ANYLOG_REST_PORT`, and `NODE_NAME`.**


---

## Config-Based Deployment

For full control over node behavior — database type, MQTT, OPC-UA, HA, monitoring, and more.
See [configs.md](configs.md) for all parameters.

**1. Copy a config template**
```shell
cp -r docker-makefiles/anylog-generic docker-makefiles/my-operator
```

**2. Edit `docker-makefiles/my-operator/node_configs.env`**

At minimum, set these in the `basic` section:

```dotenv
NODE_TYPE=operator        # node type
NODE_NAME=my-operator     # must be unique per node
COMPANY_NAME=Acme Inc.

ANYLOG_SERVER_PORT=32148  # must be unique per machine
ANYLOG_REST_PORT=32149

LEDGER_CONN=<master-ip>:32048   # IP:port of the master node
CLUSTER_NAME=my-cluster1        # unique per operator unless HA is enabled
```

And in the `secrets` section:
```dotenv
LICENSE_KEY=<your-license-key>
DB_USER=admin
DB_PASSWD=passwd
```

**3. Deploy**
```shell
make up ANYLOG_TYPE=my-operator
```

**Deploying a second node of the same type**
```shell
cp -r docker-makefiles/my-operator docker-makefiles/my-operator2
# Edit node_configs.env — update NODE_NAME, ports, and CLUSTER_NAME
make up ANYLOG_TYPE=my-operator2
```


---

## Managing Nodes

```shell
make logs ANYLOG_TYPE=my-operator       # view logs
make logs-f ANYLOG_TYPE=my-operator     # follow logs
make attach ANYLOG_TYPE=my-operator     # attach to node (press Enter twice; ctrl-d to detach)
make exec ANYLOG_TYPE=my-operator       # open bash shell in container
make down ANYLOG_TYPE=my-operator       # stop node
make clean ANYLOG_TYPE=my-operator      # stop and remove volumes
make clean-all ANYLOG_TYPE=my-operator  # stop, remove volumes and image
```

Run `make help` to see all available targets and variables.


---

## Notes

### Windows & Mac

Docker Desktop uses port-based networking instead of `network_mode: host`, which can cause containers to advertise
the Docker internal IP rather than the host machine IP. To fix this:

1. Enable host networking in Docker Desktop preferences.
2. Find your machine's local IP (`ifconfig en0 | grep "inet "` on Mac, `ipconfig` on Windows).
3. Set `OVERLAY_IP` in the `advanced` section of `node_configs.env`:
```dotenv
OVERLAY_IP=192.168.86.28
```
4. Optionally set `TCP_BIND=true` under advanced networking for stricter port binding.


### Persisting Config Changes After Reboot

Docker restarts containers from in-memory state — updated `.env` files are not re-read on reboot.
To apply config changes on restart, rebuild the container:

```shell
make up ANYLOG_TYPE=my-operator
```

To automate this at boot with `systemd`:

```ini
# /etc/systemd/system/anylog-my-operator.service
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
sudo systemctl enable anylog-my-operator.service
```

> Each node needs its own systemd service file.