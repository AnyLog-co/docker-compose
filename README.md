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
# If docker, docker-compose and make are already installed via APT or another method, you can skip this step.
sudo snap install docker
sudo apt-get -y install docker-compose 
sudo apt-get -y install make
 
# Grant non-root user permissions to use docker
USER=`whoami`
sudo groupadd docker 
sudo usermod -aG docker ${USER} 
newgrp docker
```

* Clone _docker-compose_ from AnyLog repository
```shell
git clone https://github.com/AnyLog-co/docker-compose
cd docker-compose
```

* AnyLog is a private repository, requiring docker login. Please [reach out](https://www.anylog.network/download) in order to get credentials for both  our Docker login and AnyLog license key.
```shell 
docker login -u anyloguser -p [Docker Login Passkey]
```

## Deployment Configurations
AnyLog deployment contains predefined configurations for each node type, enabling users to deploy a network with a 
simple `docker run` command. This approach allows for quick deployment with minimal configuration but is limited to one 
node type per machine. To overcome this limitation, additional environment configurations can be provided.

### Default Deployment and Networking Configuration
When deploying using the basic command, the container utilizes the default parameters based on `NODE_TYPE`, with the 
following networking configurations:

#### Important Notes:
- **Port Configuration**: When deploying on the same machine, no two containers can have the same ports. Be sure to 
configure unique values for the `ANYLOG_SERVER_PORT` and `ANYLOG_REST_PORT` environment variables for each container.

  
**Unique Node Names and Clusters**: 
- Each node must have a **unique name**. 
- If you deploy multiple operators or queries in the network, each must have a distinct `NODE_NAME`. 
- Clusters are logical object that informs members of the network which operator(s) have a given data set, and when using 
high-availability, managing the sharing of data across operators (on the same cluster). As such, `CLUSTER_NAME` should be unique 
**unless** HA is configured. 

- **License Key**: A valid `LICENSE_KEY` must be provided to deploy AnyLog. [Request License Key](https://anylog.co/download-anylog/)

| Node Type | Server Port | REST Port |
|-----------|-------------|-----------|
| Master    | 32048       | 32049     |
| Operator  | 32148       | 32149     |
| Query     | 32348       | 32349     |
| Generic   | 32548       | 32549     |


**Generic Docker Run Command**: The following command will deploy an AnyLog container with the default configurations   
```shell
docker run -it --network host \
  -e INIT_TYPE=prod \
  -e ANYLOG_TYPE=[AnyLog Type - generic, master, operator, query or publisher] \
  -e LICENSE_KEY=[User specific license key] \
--name anylog-node --rm anylogco/anylog-network:latest
```

## Deployment via Makefile
The [Makefile](Makefile) supports both _Podman_ and _Docker_ based deployment. The deployment process can be run via 
manual specification (subset of the configs)  or using the dotenv [configuration file(s)](docker-makefiles). 

```Makefile 
Usage: make [target] [VARIABLE=value]

Available targets:
  login                 log into the docker hub for AnyLog - use `ANYLOG_TYPE` as the placeholder for password
  build                 pull image from the docker hub repository
  dry-run               create docker-compose.yaml file based on the .env configuration file(s)
  up                    start AnyLog instance
  down                  Stop AnyLog instance
  clean-vols            Stop AnyLog instance and remove associated volumes
  clean                 Stop AnyLog instance and remove associated volumes & image
  attach                Attach to docker / podman container (use ctrl-d to detach)
  exec                  Attach to the shell executable for the container
  logs                  View container logs
  test-node             Test a node via REST interface
  test-network          Test the network via REST interface
  check-vars            Show all environment variable values

Common variables you can override:
  IS_MANUAL           Use manual deployment (true/false) - required to overwrite
  ANYLOG_TYPE         Type of node to deploy (e.g., master, operator)
  TAG                 Docker image tag to use
  NODE_NAME           Custom name for the container
  CLUSTER_NAME           Cluster Operator node is associted with
  ANYLOG_SERVER_PORT  Port for server communication
  ANYLOG_REST_PORT    Port for REST API
  ANYLOG_BROKER_PORT  Optional broker port
  LEDGER_CONN         Master node IP and port
  LICENSE_KEY         AnyLog License Key
  TEST_CONN           REST connection information for testing network connectivity
```

### Manual Deployment
The manual configuration-based deployment uses the default configurations, but allows the user to manipulate a subset of 
said configurations. When using the manual deployment the database layer will be _SQLite_. 

* Generic - An empty AnyLog instance consisting of **only** network configuration services 
```shell
make up IS_MANUAL=true ANYLOG_TYPE=generic LICENSE_KEY=[User specific license key]
```

* Master - An AnyLog instance that replaces a real blockchain, acting as an "Oracle" alternative for the network. 
```shell
make up IS_MANUAL=true ANYLOG_TYPE=master LICENSE_KEY=[User specific license key] ANYLOG_SERVER_PORT=32048 ANYLOG_REST_PORT=32049
```

* Operator - An AnyLog instance dedicated to storing data from devices 
```shell
make up IS_MANUAL=true ANYLOG_TYPE=operator LICENSE_KEY=[User specific license key] ANYLOG_SERVER_PORT=32148 ANYLOG_REST_PORT=32149 LEDGER_CONN=104.237.138.113:32048 CLUSTER_NAME=my-cluster1
```

* Query - An AnyLog instance dedicated for running queries. Any node can act as a query node as long as they have `system_query` logical database
```shell
make up IS_MANUAL=true ANYLOG_TYPE=query LICENSE_KEY=[User specific license key] ANYLOG_SERVER_PORT=32348 ANYLOG_REST_PORT=32349 LEDGER_CONN=104.237.138.113:32048
```

* Publisher - An AnyLog instance that's intended for distributing data among operator nodes.  
```shell
make up IS_MANUAL=true ANYLOG_TYPE=publisher LICENSE_KEY=[User specific license key] ANYLOG_SERVER_PORT=32248 ANYLOG_REST_PORT=32249 LEDGER_CONN=104.237.138.113:32048
```

All AnyLog containers run the same source code / image. It is the configurations that define which services to enable. 


### Configuration-based Deployment
The following will describe deploying an Operator node. But the logic can be applied to any node type.  
1. **Customize Configuration**
Key values to set in the *[*basic config](docker-makefiles/operator-configs/base_configs.env)**:
* `NODE_NAME` – must be unique per node type 
* `COMPANY_NAME`
* `ANYLOG_SERVER_PORT`, `ANYLOG_REST_PORT`, `ANYLOG_BROKER_PORT` (optional) – must be unique per container / machine 
* `CLUSTER_NAME` – each Operator should have its own cluster if HA is disabled 
* `LEDGER_CONN` – IP and port of the master node 
* Database credentials

[Advanced configurations](docker-makefiles/operator-configs/advance_configs.env) covers optional settings like thread usage, geolocation overrides, and Nebula overlay support.


2. **Deploy Node** - the [Makefile](Makefile) can be used with either _Podman_ or _Docker_. 
```shell
cd docker-compose
make up ANYLOG_TYPE=operator
```

3. **Check Status**  
```shell
cd docker-compose
make logs ANYLOG_TYPE=operator

<<COMMENT 
# Expected output for Operator Node 

AL nov-operator2 > 
    Process         Status       Details                                                                      
    ---------------|------------|----------------------------------------------------------------------------|
    TCP            |Running     |Listening on: 170.187.157.30:32158, Threads Pool: 6                         |
    REST           |Running     |Listening on: 170.187.157.30:32159, Threads Pool: 5, Timeout: 20, SSL: False|
    Operator       |Running     |Cluster Member: True, Using Master: 104.237.138.113:32048, Threads Pool: 10 |
    Blockchain Sync|Running     |Sync every 30 seconds with master using: 104.237.138.113:32048              |
    Scheduler      |Running     |Schedulers IDs in use: [0 (system)] [1 (user)]                              |
    Blobs Archiver |Running     |                                                                            |
    MQTT           |Not declared|                                                                            |
    Message Broker |Not declared|No active connection                                                        |
    SMTP           |Not declared|                                                                            |
    Streamer       |Running     |Default streaming thresholds are 5 seconds and 102,400 bytes                |
    Query Pool     |Running     |Threads Pool: 3                                                             |
    Kafka Consumer |Not declared|                                                                            |
    gRPC           |Not declared|                                                                            |
    OPC-UA Client  |Not declared|                                                                            |
    Publisher      |Not declared|                                                                            |
    Distributor    |Not declared|                                                                            |
    Consumer       |Not declared|                                                                            |
<<COMMENT
```

4. **Attach** - to detach `ctrl-d`
```shell
make attach ANYLOG_TYPE=operator
[press Enter twice]
```

#### Additional Operator
1. Copy the node configurations into a new configurations directory 
```shell
cp docker-makefiles/operator-configs docker-makefiles/operator2-configs
```

2. Update configuration files

3. Start new operator node 
```shell
make up ANYLOG_TYPE=operator2
```

## Configuration file(s) Breakdown 
**[Basic Configs](docker-makefiles/operator-configs/base_configs.env)**
* General configurations
```dotenv
#--- General ---
# AnyLog License Key
LICENSE_KEY=""
# Information regarding which AnyLog node configurations to enable. By default, even if everything is disabled, AnyLog starts TCP and REST connection protocols
NODE_TYPE=operator
# Name of the AnyLog instance
NODE_NAME=anylog-operator
# Owner of the AnyLog instance
COMPANY_NAME=New Company
```

* Networking
```dotenv
#--- Networking ---
# Port address used by AnyLog's TCP protocol to communicate with other nodes in the network
ANYLOG_SERVER_PORT=32148
# Port address used by AnyLog's REST protocol
ANYLOG_REST_PORT=32149
# Port value to be used as an MQTT broker, or some other third-party broker
ANYLOG_BROKER_PORT=""
# A bool value that determines if to bind to a specific IP and Port (a false value binds to all IPs)
TCP_BIND=false
# A bool value that determines if to bind to a specific IP and Port (a false value binds to all IPs)
REST_BIND=false
# A bool value that determines if to bind to a specific IP and Port (a false value binds to all IPs)
BROKER_BIND=false
```

* Database
```dotenv
#--- Database ---
# Physical database type (sqlite or psql)
DB_TYPE=sqlite
# Username for SQL database connection
DB_USER=""
# Password correlated to database user
DB_PASSWD=""
# Database IP address
DB_IP=127.0.0.1
# Database port number
DB_PORT=5432
# Whether to set autocommit data
AUTOCOMMIT=false
# Whether to enable NoSQL logical database
ENABLE_NOSQL=false
# Whether to start system_query logical database
SYSTEM_QUERY=false
# Run system_query using in-memory SQLite. If set to false, will use pre-set database type
MEMORY=false

# Whether to enable NoSQL logical database
ENABLE_NOSQL=false
# Physical database type
NOSQL_TYPE=mongo
# Username for SQL database connection
NOSQL_USER=""
# Password correlated to database user
NOSQL_PASSWD=""
# Database IP address
NOSQL_IP=127.0.0.1
# Database port number
NOSQL_PORT=27017
# Store blobs in database
BLOBS_DBMS=false
# Whether (re)store a blob if already exists
BLOBS_REUSE=true
```

* Blockchain  
```dotenv
#--- Blockchain ---
# How often to sync from blockchain
BLOCKCHAIN_SYNC=30 second
# Source of where the data is metadata stored/coming from. This can either be master for "local" install or specific
# blockchain network to be used (ex. optimism)
BLOCKCHAIN_SOURCE=master
# TCP connection information for Master Node
LEDGER_CONN=127.0.0.1:32048
```

* Operator specific configs
```dotenv
#--- Operator ---
# Owner of the cluster
CLUSTER_NAME=nc-cluster1
# Logical database name
DEFAULT_DBMS=new_company
# Whether to enable partitioning
ENABLE_PARTITIONS=true
# Which tables to partition
TABLE_NAME=*
# Which timestamp column to partition by
PARTITION_COLUMN=insert_timestamp
# Time period to partition by
PARTITION_INTERVAL=14 days
# How many partitions to keep
PARTITION_KEEP=3
# How often to check if an old partition should be removed
PARTITION_SYNC=1 day
```

* [Data Aggregation](https://github.com/AnyLog-co/documentation/blob/master/aggregations.md) & Other services
```dotenv
#--- Data Aggregation --
# Enable data aggregation based om timestamp / column
ENABLE_AGGREGATIONS=false
# Timestamp column to aggregate against
AGGREGATION_TIME_COLUMN=insert_timestamp
# Value column to aggregate against
AGGREGATION_VALUE_COLUMN=value

#--- MQTT ---
# Whether to enable the default MQTT process
ENABLE_MQTT=false

# IP address of MQTT broker
MQTT_BROKER=139.144.46.246
# Port associated with MQTT broker
MQTT_PORT=1883
# User associated with MQTT broker
MQTT_USER=anyloguser
# Password associated with MQTT user
MQTT_PASSWD=mqtt4AnyLog!
# Whether to enable MQTT logging process
MQTT_LOG=false

# Topic to get data for
MSG_TOPIC=anylog-demo
# Logical database name
MSG_DBMS=new_company
# Table where to store data
MSG_TABLE=bring [table]
# Timestamp column name
MSG_TIMESTAMP_COLUMN=bring [timestamp]
# Value column name
MSG_VALUE_COLUMN=bring [value]
# Column value type
MSG_VALUE_COLUMN_TYPE=float

#----- OPC-UA ---
# Whether or not to enable to OPC-UA service
ENABLE_OPCUA=false
# OPC-UA URL address (ex. opcua.tcp:;//127.0.0.1:4840)
OPCUA_URL=""
# Node information the root is located in (ex. ns=2;s=DataSet)
OPCUA_NODE=""
# How often to pull data from OPC-UA
OPCUA_FREQUENCY=""
```

* Node Monitoring
```dotenv
#--- Monitoring ---
# Whether to monitor the node or not
MONITOR_NODES=true
# Store monitoring in Operator node(s)
STORE_MONITORING=false
# For operator, accept syslog data from local (Message broker required)
SYSLOG_MONITORING=false
```

* Commonly used advanced configs 
```dotenv
#--- Advanced Settings ---
# Whether to automatically run a local (or personalized) script at the end of the process
DEPLOY_LOCAL_SCRIPT=false
# Run code in debug mode
DEBUG_MODE=false
```

**Advanced Configs**
* AnyLog Directory Paths
```
#--- Directories ---
# AnyLog Root Path - if changed make sure to change volume path in docker-compose-template
ANYLOG_PATH=/app
# !local_scripts: ${ANYLOG_HOME}/deployment-scripts/scripts
LOCAL_SCRIPTS=/app/deployment-scripts/node-deployment
# !test_dir: ${ANYLOG_HOME}/deployment-scripts/test
TEST_DIR=/app/deployment-scripts/tests
```
* General configs & enable "third-party" apps
```dotenv
# --- General ---
# Disable AnyLog's CLI interface
DISABLE_CLI=false
# Enable Remote-CLI
REMOTE_CLI=false
```
* Geolocation
```dotenv
#--- Geolocation ---
# Coordinates of the machine - used by Grafana to map the network
LOCATION=""
# Country where machine is located
COUNTRY=""
# State where machine is located
STATE=""
# City where machine is located
CITY=""
```
* Networking 
```dotenv
#--- Networking ---
# Declare Policy name
CONFIG_NAME=""
# Overlay IP address - if set, will replace local IP address when connecting to network
OVERLAY_IP=""
# The number of concurrent threads supporting HTTP requests.
TCP_THREADS=6
# Timeout in seconds to determine a time interval such that if no response is being returned during the time interval, the system returns timeout error.
REST_TIMEOUT=30
# The number of concurrent threads supporting HTTP requests.	
REST_THREADS=6
# The number of concurrent threads supporting broker requests.
BROKER_THREADS=6
```
* Blockchain
```dotenv
#--- Blockchain ---
# Where will the copy of the blockchain be stored
BLOCKCHAIN_DESTINATION=file
```
* Operator / HA specific configs
```dotenv
#--- Operator ---
# Operator ID
MEMBER=""
# Whether of not to enable HA against the cluster
ENABLE_HA=false
# How many days back to sync between nodes
START_DATE=30
# How many threads to use in the operator process
OPERATOR_THREADS=3
```

* Other configs
```dotenv
#--- Advanced Settings ---
# Compress JSON and SQL file(s) backup
COMPRESS_FILE=true
# Number of parallel queries
QUERY_POOL=6
# When data comes in write to database immediately, as opposed to waiting for a full buffer
WRITE_IMMEDIATE=false
# If buffer is not full, how long to wait until pushing data through
THRESHOLD_TIME=60 seconds
# Buffer size to reach, at which point data is pushed through
THRESHOLD_VOLUME=100KB
```
* Nebula configurations
```
#--- Nebula ---
# whether to enable Lighthouse
ENABLE_NEBULA=false
# create new nebula keys
NEBULA_NEW_KEYS=false
# whether node is type lighthouse
IS_LIGHTHOUSE=false
# Nebula CIDR IP address for itself - the IP component should be the same as the OVERLAY_IP (ex. 10.10.1.15/24)
CIDR_OVERLAY_ADDRESS=""
# Nebula IP address for Lighthouse node (ex. 10.10.1.15)
LIGHTHOUSE_IP=""
# External physical IP of the node associated with Nebula lighthouse
LIGHTHOUSE_NODE_IP=""
```

