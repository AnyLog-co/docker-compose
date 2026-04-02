# Deploying AnyLog

AnyLog enables real-time visibility and management of distributed edge data across IoT environments — manufacturing,
utilities, oil & gas, smart cities, and more.

- [Documentation](https://github.com/AnyLog-co/documentation/)
- [Surrounding tools install](support/README.md)
- [deployment-scripts](https://github.com/AnyLog-co/deployment-scripts) — scripts executed at startup for AnyLog


## Node Types

All AnyLog nodes run the same image — the `NODE_TYPE` config determines what services are enabled.

| Node Type                     | Description                                              | Server Port | REST Port | Broker Port (optional) | Config File                                                                       |
|-------------------------------|----------------------------------------------------------|-------------|-----------|------------------------|-----------------------------------------------------------------------------------|
| `generic`                     | Sandbox with only network configured                     | 32548       | 32549     | 32550                  | [node_configs.env](docker-makefiles/anylog-generic/node_configs.env)              |
| `master`                      | Blockchain emulator                                      | 32048       | 32049     | —                      | [node_configs.env](docker-makefiles/anylog-master/node_configs.env)               |
| `operator`                    | Stores data from edge devices                            | 32148       | 32149     | 32150                  | [node_configs.env](docker-makefiles/anylog-operator/node_configs.env)             |
| `query`                       | Dedicated query node (`system_query` database enabled)   | 32348       | 32349     | —                      | [node_configs.env](docker-makefiles/anylog-query/node_configs.env)                |
| `publisher`                   | Distributes data among operator nodes                    | 32248       | 32249     | 32250                  | [node_configs.env](docker-makefiles/anylog-publisher/node_configs.env)            |
| `master-standalone-operator`  | Master + operator with `system_query` on a single agent  | 32148       | 32149     | 32150                  | [node_configs.env](docker-makefiles/anylog-standalone-operator/node_configs.env)  |
| `master-standalone-publisher` | Master + publisher with `system_query` on a single agent | 32248       | 32249     | 32250                  | [node_configs.env](docker-makefiles/anylog-standalone-publisher/node_configs.env) |


## Other Deployment Types

- [OVA installation](https://github.com/AnyLog-co/anylog-demo-ova-scripts) — pre-defined virtual machine image with AnyLog pre-configured
- [OpenHorizon deployment](https://github.com/AnyLog-co/service-anylog) — deploying AnyLog via OpenHorizon

---

## Requirements

1. An AnyLog license key and access to the Docker repository — available on our <a href="https://anylog.network/downloads" target="_blank">website</a>.
2. Docker installed on each machine. Full directions in the <a href="https://docs.docker.com/engine/install/" target="_blank">Docker documentation</a>.

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


## Preparing Your Machines

Unless stated otherwise, the following steps should be done on all machines:

1. Make sure nodes and users have satisfied the [requirements](#requirements) above.

2. Clone the docker-compose repository:
```shell
git clone https://github.com/AnyLog-co/docker-compose
cd docker-compose
```

3. Log in to Docker Hub — AnyLog is a private image. [Request credentials and a license key](https://www.anylog.network/download).
```shell
make login ANYLOG_TYPE=<docker-passkey>
```

---

## Configuration & Deployment

### Configuration File Organization

For consistency across deployment types, configurations are defined in a single dotenv file broken down into sections.

| Section      | Sub-section     | Content                                                                             |
|--------------|-----------------|--------------------------------------------------------------------------------------|
| `.env`       | —               | Docker-level settings: image, init type, deployment repo/branch, Docker socket       |
| `basic`      | General         | Node type, node name, company name                                                   |
|              | Networking      | TCP, REST, and broker ports                                                          |
|              | Database        | DB type (SQLite/PostgreSQL), IP, port, autocommit                                    |
|              | NoSQL           | Blob storage toggle, backend type, endpoint, port                                    |
|              | System Query    | `system_query` database toggle and type                                              |
|              | Blockchain      | Master node connection, sync interval, source, local storage                         |
|              | Operator        | Cluster name, default logical database                                               |
|              | Monitoring      | Node, storage, and syslog monitoring toggles                                         |
| `southbound` | MQTT            | Broker connection, topic, column mappings, logging                                   |
|              | OPC-UA          | Endpoint URL, root node, pull frequency                                              |
|              | Video Streaming | Source URL, port, stream name, YOLO detection toggle                                 |
| `advanced`   | Directories     | Paths for AnyLog root, deployment scripts, test scripts                              |
|              | General         | Policy visibility, local script execution, geo-location fields                       |
|              | Networking      | DNS, NIC, overlay IP, bind settings, thread counts, REST timeout                     |
|              | NoSQL           | Blob dedup, compression, local folder                                                |
|              | Object Store    | Bucket group, ID, cloud region                                                       |
|              | Operator (HA)   | Member ID, HA toggle, sync start date, thread count                                  |
|              | Sub Processes   | File compression, write mode, buffer flush thresholds, query threads                 |
| `secrets`    | —               | License key, DB credentials, NoSQL credentials, MQTT credentials, object store keys  |
| `remote-gui` | —               | Enable toggle, image tag, NIC, frontend/backend ports, Grafana URL                   |


### Configuration

Since AnyLog is service-based, users can define almost any combination of services and databases on the same instance
(except starting an operator and publisher service together).

When deploying a node, make sure the following parameters are set correctly:

- `NODE_TYPE` — defines the services enabled at startup based on the configuration file
- `NODE_NAME` — nodes on the same physical machine must have unique names
- `COMPANY_NAME` — owner of the AnyLog node / agent
- `ANYLOG_SERVER_PORT`, `ANYLOG_REST_PORT`, and (optional) `ANYLOG_BROKER_PORT`
- `LEDGER_CONN` — which blockchain network the node is associated with
- `CLUSTER_NAME` — required for operator nodes unless HA is enabled; if HA is wanted, set `ENABLE_HA=true`
- `LICENSE_KEY` — if the license key is already registered on the blockchain, it does not need to be restated in configs

For the `generic` node type, only the networking configurations matter — it acts as a sandbox with no other services
or databases deployed automatically at startup.


### Deployment

1. Complete the steps in [Requirements](#requirements).

2. Bring up a node:
```shell
make up ANYLOG_TYPE=<config-dir-in-docker-makefiles>
```

3. Manage the running node:
```shell
# Attach to node
make attach ANYLOG_TYPE=<config-dir-in-docker-makefiles>

# Open a shell inside the container
make exec ANYLOG_TYPE=<config-dir-in-docker-makefiles>

# View logs
make logs ANYLOG_TYPE=<config-dir-in-docker-makefiles>

# Follow logs continuously
make logs-f ANYLOG_TYPE=<config-dir-in-docker-makefiles>
```


#### Recommended Deployment Order

1. Set [configs for master](docker-makefiles/anylog-master/node_configs.env).

2. Deploy master:
```shell
make up ANYLOG_TYPE=anylog-master
```

3. Validate master is running — the process table at the bottom of the log confirms all services:
```shell
make logs-f ANYLOG_TYPE=anylog-master
```
```
    Process         Status       Details
    ---------------|------------|-------------------------------------------------------------------------|
    TCP            |Running     |Listening on: 45.79.74.39:32048, Threads Pool: 6                         |
    REST           |Running     |Listening on: 45.79.74.39:32049, Threads Pool: 6, Timeout: 20, SSL: False|
    Blockchain Sync|Running     |Sync every 60 seconds with master using: 45.79.74.39:32048               |
    Scheduler      |Running     |Schedulers IDs in use: [0 (system)] [1 (user)]                           |
    Query Pool     |Running     |Threads Pool: 3                                                          |
```

4. Bring up the remaining nodes, ensuring `LEDGER_CONN` in each config is set to the master node's TCP address
(in the example above: `45.79.74.39:32048`).