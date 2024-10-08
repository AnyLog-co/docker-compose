# Deploying AnyLog

The following provides direction to deploy AnyLog using [_makefile_](Makefile) for Docker-based deployment.

**Requirements**
* _Docker_
* _docker-compose_
* _Makefile_
```shell
sudo snap install docker
sudo apt-get -y install docker-compose 
sudo apt-get -y install make
 
# Grant non-root user permissions to use docker
USER=`whoami` 
sudo groupadd docker 
sudo usermod -aG docker ${USER} 
newgrp docker
```

## Prepare for Deployment
1. Clone _docker-compose_ from AnyLog repository
```shell
git clone https://github.com/AnyLog-co/docker-compose
cd docker-compose
```

2. Request 3-month License & access to AnyLog Docker Hub [here](https://anylog.co/download-anylog/)

3. Install Database and Grafana - Docker containers found here [here](docker-compose)   

## Deploy AnyLog via Docker 
1. Update configuration for node  
   * [master-configs/base_configs.env](docker-makefile/master-configs/base_configs.env) | [master-configs/advance_configs.env](docker-makefile/master-configs/advance_configs.env)
   * [operator-configs/base_configs.env](docker-makefile/operator-configs/base_configs.env) | [operator-configs/advance_configs.env](docker-makefile/operator-configs/advance_configs.env)
   * [query-configs/base_configs.env](docker-makefile/query-configs/base_configs.env) | [query-configs/advance_configs.env](docker-makefile/query-configs/advance_configs.env)
   * [publisher-configs/base_configs.env](docker-makefile/publisher-configs/base_configs.env) | [publisher-configs/advance_configs.env](docker-makefile/publisher-configs/advance_configs.env)

**base_configs.env**
```dotenv
#--- General ---
# AnyLog License Key
LICENSE_KEY=""
# Information regarding which AnyLog node configurations to enable. By default, even if everything is disabled, AnyLog starts TCP and REST connection protocols
NODE_TYPE=generic
# Name of the AnyLog instance
NODE_NAME=edgelake-node
# Owner of the AnyLog instance
COMPANY_NAME=New Company

#--- Networking ---
# Port address used by AnyLog's TCP protocol to communicate with other nodes in the network
ANYLOG_SERVER_PORT=32548
# Port address used by AnyLog's REST protocol
ANYLOG_REST_PORT=32549
# Port value to be used as an MQTT broker, or some other third-party broker
ANYLOG_BROKER_PORT=""
# A bool value that determines if to bind to a specific IP and Port (a false value binds to all IPs)
TCP_BIND=false
# A bool value that determines if to bind to a specific IP and Port (a false value binds to all IPs)
REST_BIND=false
# A bool value that determines if to bind to a specific IP and Port (a false value binds to all IPs)
BROKER_BIND=false

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

#--- Blockchain ---
# TCP connection information for Master Node
LEDGER_CONN=127.0.0.1:32048

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
MSG_TABLE=bring [sourceName]
# Timestamp column name
MSG_TIMESTAMP_COLUMN=now
# Value column name
MSG_VALUE_COLUMN=bring [readings][][value]
# Column value type
MSG_VALUE_COLUMN_TYPE=float

#--- Advanced Settings ---
# Whether to automatically run a local (or personalized) script at the end of the process
DEPLOY_LOCAL_SCRIPT=false
```

**advance_configs.env**:
```dotenv
#--- Directories ---
# AnyLog Root Path
ANYLOG_PATH=/app
# !local_scripts: ${ANYLOG_HOME}/deployment-scripts/scripts
LOCAL_SCRIPTS=/app/deployment-scripts/scripts
# !test_dir: ${ANYLOG_HOME}/deployment-scripts/tests
TEST_DIR=/app/deployment-scripts/tests

#--- Networking ---
# Declare Policy name
CONFIG_NAME=""
# Overlay IP address - if set, will replace local IP address when connecting to network
OVERLAY_IP=""
# Configurable (local) IP address that can be used when behind a proxy, or using Kubernetes for static IP
PROXY_IP=""
# The number of concurrent threads supporting HTTP requests.
TCP_THREADS=6
# Timeout in seconds to determine a time interval such that if no response is being returned during the time interval, the system returns timeout error.
REST_TIMEOUT=30
# The number of concurrent threads supporting HTTP requests.
REST_THREADS=6
# The number of concurrent threads supporting broker requests.
BROKER_THREADS=6

#--- Database ---
# Whether to start to start system_query logical database
SYSTEM_QUERY=false
# Run system_query using in-memory SQLite. If set to false, will use pre-set database type
MEMORY=false
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

#--- Blockchain ---
# How often to sync from blockchain
SYNC_TIME=30 second
# Source of where the data is coming from
BLOCKCHAIN_SOURCE=master
# Where will the copy of the blockchain be stored
BLOCKCHAIN_DESTINATION=file

#--- Operator ---
# Operator ID
MEMBER=""
# How many days back to sync between nodes
START_DATE=30
# Which tables to partition
TABLE_NAME=*
# Which timestamp column to partition by
PARTITION_COLUMN=insert_timestamp
# Time period to partition by
PARTITION_INTERVAL=1 day
# How many partitions to keep
PARTITION_KEEP=3
# How often to check if an old partition should be removed
PARTITION_SYNC=1 day

#--- Monitoring ---
# Which node type to send monitoring information to
MONITOR_NODE=query

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
THRESHOLD_VOLUME=10KB

#--- Nebula ---
# whether to enable Lighthouse
ENABLE_NEBULA=true
# whether node is type lighthouse
IS_LIGHTHOUSE=false
# Nebula IP address for Lighthouse node
LIGHTHOUSE_IP=""
# External physical IP of the node associated with Nebula lighthouse
LIGHTHOUSE_NODE_IP=""
```

2. Login to AnyLog's Docker hub 
```shell
make login ANYLOG_TYPE=[DOCKER-PASSWORD]
```

3. (Optional) To include Remote-CLI as part of the Query node deployment, uncomment Remote-CLI as part of Remote-CLI service in
docker compose file. Otherwise, an independent Remote-CLI can be found in [docker-compose](docker-compose/Remote-CLI)

4. Start Node using _makefile_
```shell
make up ANYLOG_TYPE=[NODE_TYPE]
```

### Makefile Commands for Docker
* help
```shell
Usage: make [target] ANYLOG_TYPE=[anylog-type]
Targets:
  login       Log into AnyLog's Dockerhub - use ANYLOG_TYPE to set password value
  build       Pull the docker image
  up          Start the containers
  attach      Attach to AnyLog instance
  exec        Attach to shell interface for container
  down        Stop and remove the containers
  logs        View logs of the containers
  clean       Clean up volumes and network
  help        Show this help message
         supported AnyLog types: master, operator, query and publisher
Sample calls: make up ANYLOG_TYPE=master | make attach ANYLOG_TYPE=master | make clean ANYLOG_TYPE=master
```

* Login to AnyLog's Docker Hub 
```shell
make login ANYLOG_TYPE=YOUR_DOCKER_PASSWORD
```

* Bring up a _query_ node
```shell
make up ANYLOG_TYPE=query
```

* Attach to _query_ node
```shell
# to detach: ctrl-d
make attach ANYLOG_TYPE=query  
```

* Bring down _query_ node
```shell
make down ANYLOG_TYPE=query
```
If a _node-type_ is not set, then a generic node would automatically be used    



## Makefile Commands 
* `login` - Log into AnyLog's Dockerhub - use ANYLOG_TYPE to set password valuue
* `build` - pull docker image 
* `up` - Using _docker-compose_, start a container of AnyLog based on node type
* `attach` - Attach to an AnyLog docker container based on node type
* `exec` - Attach to the shell interface of an AnyLog docker container, based on the node type 
* `log` - check docker container logs based on container type
* `down` - Stop container based on node type 
* `clean` - remove everything associated with container (including volume and image) based on node type
 


