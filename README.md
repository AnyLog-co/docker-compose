# Deploying AnyLog

AnyLog enables real-time visibility and management of distributed edge data across IoT environments — manufacturing,
utilities, oil & gas, smart cities, and more.

- [Documentation](https://github.com/AnyLog-co/documentation/)
- [Surrounding tools install](support/README.md)
- [deployment-scripts](https://github.com/AnyLog-co/deployment-scripts) - scripts being executed at start up for AnyLog

### Node Types

All AnyLog nodes run the same image — the `NODE_TYPE` config determines what services are enabled.

| Node Type                     | Description                                              | Server Port | REST Port | Config File                                                                       | 
|-------------------------------|----------------------------------------------------------|-------------|-----------|-----------------------------------------------------------------------------------| 
| `generic`                     | Sandbox with only network configured                     | 32548       | 32549     | [node_configs.env](docker-makefiles/anylog-generic/node_configs.env)              |
| `master`                      | Blockchain emulator                                      | 32048       | 32049     | [node_configs.env](docker-makefiles/anylog-master/node_configs.env)               | 
| `operator`                    | Stores data from edge devices                            | 32148       | 32149     | [node_configs.env](docker-makefiles/anylog-operator/node_configs.env)             |
| `query`                       | Dedicated query node (`system_query` database enabled)   | 32348       | 32349     | [node_configs.env](docker-makefiles/anylog-query/node_configs.env)                |
| `publisher`                   | Distributes data among operator nodes                    | 32248       | 32249     | [node_configs.env](docker-makefiles/anylog-publisher/node_configs.env)            |
| `master-standalone-operator`  | Master + operator with `system_query` on a single agent  | 32148       | 32149     | [node_configs.env](docker-makefiles/anylog-standalone-operator/node_configs.env)  |
| `master-standalone-publisher` | Master + publisher with `system_query` on a single agent | 32248       | 32249     | [node_configs.env](docker-makefiles/anylog-standalone-publisher/node_configs.env) |


### Other deployment types
- [OVA installation](https://github.com/AnyLog-co/anylog-demo-ova-scripts) - pre-defined virtualmachine image that has AnyLog pre-configured
- [open-horizon deployment](https://github.com/AnyLog-co/service-anylog) - 

--- 

## Requirements

1. An AnyLog License key and access to our docker repository can be found on our <a href="https://anylog.network/downloads" target="_blank">website</a>
2. The deployment can occur on separate machines or on one machine and is done via docker. Directions can be found in <a href="https://docs.docker.com/engine/install/" target="_blank">Docker documentation</a>
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

### Peppering the machine(s) to deploy AnyLog

Unless stated otherwise, the following steps are to be done on all machines:  

1. Make sure node(s) and user have satisfied the [requirements](#requirements) above

2. Clone docker-compose repository
```shell
git clone https://github.com/AnyLog-co/docker-compose
cd docker-compose
```

3. Log in to Docker Hub AnyLog is a private image — [request credentials and a license key](https://www.anylog.network/download).
```shell
make login ANYLOG_TYPE=[license key]
```
--- 

## Configuration & Deployment

### Configuration file organization: 

For consistency across different deployment types, the configurations are defined in a single dotenv file and broken 
down into sections. 

|    Section    |   Sub-section    |                                       Content                                        |
|:-------------:|:----------------:|:------------------------------------------------------------------------------------:|
|    `.env`     |        —         |    Docker-level settings: image, init type, deployment repo/branch, Docker socket    |
|    `basic`    |     General      |                          Node type, node name, company name                          |
|               |    Networking    |                             TCP, REST, and broker ports                              |
|               |     Database     |                  DB type (SQLite/PostgreSQL), IP, port, autocommit                   |
|               |      NoSQL       |                  Blob storage toggle, backend type, endpoint, port                   |
|               |   System Query   |                       `system_query` database toggle and type                        |
|               |    Blockchain    |             Master node connection, sync interval, source, local storage             |
|               |     Operator     |                        Cluster name, default logical database                        |
|               |    Monitoring    |                     Node, storage, and syslog monitoring toggles                     |
| `southbound`  |       MQTT       |                  Broker connection, topic, column mappings, logging                  |
|               |      OPC-UA      |                       Endpoint URL, root node, pull frequency                        |
|               | Video Streaming  |                 Source URL, port, stream name, YOLO detection toggle                 |
|  `advanced`   |   Directories    |               Paths for AnyLog root, deployment scripts, test scripts                |
|               |     General      |            Policy visibility, local script execution, geo-location fields            |
|               |    Networking    |           DNS, NIC, overlay IP, bind settings, thread counts, REST timeout           |
|               |      NoSQL       |                        Blob dedup, compression, local folder                         |
|               |   Object Store   |                            Bucket group, ID, cloud region                            |
|               |  Operator (HA)   |                 Member ID, HA toggle, sync start date, thread count                  |
|               |  Sub Processes   |         File compression, write mode, buffer flush thresholds, query threads         |
|   `secrets`   |        —         | License key, DB credentials, NoSQL credentials, MQTT credentials, object store keys  |
| `remote-gui`  |        —         |          Enable toggle, image tag, NIC, frontend/backend ports, Grafana URL          |

### Configuration
Since AnyLog is service based, except starting an operator and publisher service together users can define have just 
about any combination of services (and database) on the samee instance.

As such, when deploying a node it's important to make sure the following params are set correctly

* `NODE_TYPE` - defines the services being enabled (by default) based on the configuration file
* `NODE_NAME` - nodes that reside on the same physical machine must have unique names, if they are of the same type
* `COMPANY_NAME` - owner of the AnyLog node / agent
* `ANYLOG_SERVER_PORT`, `ANYLOG_REST_PORT` and (optional) `ANYLOG_BROKER_PORT`
* `LEDGER_CONN` - which (blockchain) network the node is associated with
* `CLUSTER_NAME` - for Operator nodes this is a must if the user does not want HA. If they do want HA, then make sure
`ENABLE_HA` is set to **true**
* `LICENSE_KEY` - if the license key is already defined on the blockchain, there's no need to restate it in the configs

For node type `generiric`, only the networking configurations are important as it acts as a sandbox with no other servies
or database being automatically deployed at startup. 


### Deployment 

1. Please make sure you've completed the steps in [requirements](#Requirements)

2. Bring up a node
```shell
make up ANYLOG_TYPE=[config file in docker-makefiles]
```

3. Attach / exec / logs etc.
```shell
# attach to node 
make attach ANYLOG_TYPE=[config file in docker-makefiles]

# attach to shell of container 
make exec ANYLOG_TYPE=[config file in docker-makefiles]

# view logs 
make logs ANYLOG_TYPE=[config file in docker-makefiles]

# view logs continues 
make logs-f ANYLOG_TYPE=[config file in docker-makefiles]
```

#### Recommended deployment
1. Set [configs for master](docker-makefiles/anylog-master/node_configs.env)


2. Deploy master 
```shell
make up ANYLOG_TYPE=anylog-master
```

3. Validate Master is running
```shell
root@anylog-master:~# make logs-f ANYLOG_TYPE=anylog-master

AnyLog Version: 1.4.2603 [4b350e] [2026-03-04 15:18:28] (Release)

* (c) 2021-2023 AnyLog Inc.
*
* This software is licensed under the terms and conditions of the AnyLog SOFTWARE EVALUATION AGREEMENT
* available at https://github.com/AnyLog-co/documentation/blob/master/License/Evaluation%20License.md 

AL > 

AL > process /app/deployment-scripts/node-deployment/main.al 
AL > Messages in Echo Queue! ...
AL anylog-master >  

|=================================================================|
|Configure TCP Server from policy 827b621e48f1023db284d52968d33179|
|=================================================================|

AL anylog-master > 

|==================================================================|
|Configure REST Server from policy 827b621e48f1023db284d52968d33179|
|==================================================================|

AL anylog-master > Database blockchain using psql connected!
AL anylog-master > The usage of this software is subject to an active an license agreement with AnyLog.
company    : Guest
expiration : 2026-08-01
type       : beta

AL anylog-master > 

|=============================================================|
|Script from policy 827b621e48f1023db284d52968d33179 processed|
|=============================================================|

AL anylog-master > 
    Process         Status       Details                                                                   
    ---------------|------------|-------------------------------------------------------------------------|
    TCP            |Running     |Listening on: 45.79.74.39:32048, Threads Pool: 6                         |
    REST           |Running     |Listening on: 45.79.74.39:32049, Threads Pool: 6, Timeout: 20, SSL: False|
    MCP            |Not declared|                                                                         |
    Operator       |Not declared|                                                                         |
    Blockchain Sync|Running     |Sync every 60 seconds with master using: 45.79.74.39:32048               |
    Scheduler      |Running     |Schedulers IDs in use: [0 (system)] [1 (user)]                           |
    Blobs Archiver |Not declared|                                                                         |
    MQTT           |Not declared|                                                                         |
    MSG Client Pool|Not declared|                                                                         |
    MSG Broker     |Not declared|No active connection                                                     |
    SMTP           |Not declared|                                                                         |
    Streamer       |Not declared|                                                                         |
    UNS Streamer   |Not declared|                                                                         |
    Query Pool     |Running     |Threads Pool: 3                                                          |
    Kafka Consumer |Not declared|                                                                         |
    gRPC           |Not declared|                                                                         |
    PLC Client     |Not declared|                                                                         |
    Pull Processes |Not declared|                                                                         |
    Video Processes|Not declared|                                                                         |
    Publisher      |Not declared|                                                                         |
    Distributor    |Not declared|                                                                         |
    Consumer       |Not declared|                                                                         |
```

4. Bring up the other nodes in the network - make usre the `LEDGER_CONN` is properly associated with the IP:port of the TCP for `master_node` (in the example: 45.79.74.39:32048)