# Deploying AnyLog

AnyLog provides Real-Time Visibility and Management of Distributed Edge Data, Applications and Infrastructure. AnyLog 
transforms the edge to a scalable data tier that is optimized for IoT data, enabling organizations to extract real-time 
insight for any use case in any industries spanning Manufacturing, Utilities, Oil & Gas, Retail, Robotics, Smart Cities, 
Automotive, and more.

* [Documentation](https://github.com/AnyLog-co/documentation/)
* [Surrounding components install](support-tools/README.md)


## Prepare Machine
* [Docker & Docker-Compose](https://docs.docker.com/engine/install/)
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

  
- **Unique Node Names and Clusters**: Each node must have a unique name. If you deploy multiple operators or queries in 
the network, each must have a distinct `NODE_NAME`. Additionally, no two operators can reside on the same `CLUSTER_NAME`. 
These variables should be set accordingly when deploying multiple nodes.


- **License Key**: A valid `LICENSE_KEY` must be provided to deploy AnyLog. [Request License Key](https://anylog.co/download-anylog/)

<html>
<table>
   <tr>
      <th>Node Type</th>
      <th>Server Port</th>
      <th>Rest Port</th>
   </tr>
   <tr>
      <td>Master</td>
      <td>32048</td>
      <td>32049</td>
   </tr>
   <tr>
      <td>Operator</td>
      <td>32148</td>
      <td>32149</td>
   </tr>
   <tr>
      <td>Query</td>
      <td>32348</td>
      <td>32349</td>
   </tr>
   <tr>
      <td>Generic</td>
      <td>32548</td>
      <td>32549</td>
   </tr>
</table>
</html>

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
1. Update [configuration files](docker-makefiles/operator-configs). The [basic configurations](docker-makefiles/operator-configs/base_configs.env) 
consist of basic information such as port numbers,  node and cluster name, database credentials and key services. While [advanced configurations](docker-makefiles/operator-configs/advance_configs.env)
have things like the utilization of threads, overwrite geolocation, and enabling nebula overlay network. 
When deploying a user is usually interested in the following params (all in [basic configurations](docker-makefiles/operator-configs/base_configs.env)):  
* `NODE_NAME` - no two nodes of the same type may have the same name 
* `COMPANY_NAME` 
* `ANYLOG_SERVER_PORT`, `ANYLOG_REST_PORT`, `ANYLOG_BROKER_PORT` (optional) - no two nodes on the same physical machine amy have the same port value(s)
* `CLUSTER_NAME` - Logical cluster name. When HA is **not** enabled, each operator should reside in its own cluster 
* `LEDGER_CONN` - Connection information to master node
* Database credential information

2. Deploy Node - the [Makefile](Makefile) can be used with either _Podman_ or _Docker_. 
```shell
cd docker-compose
make up ANYLOG_TYPE=operator
```

3. View the state of the node  
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

4. Attach to node - to detach `ctrl-d`
```shell
make attach ANYLOG_TYPE=operator
[press Enter twice]
```

#### Adding an additional Operator
1. Copy the node configurations into a new configurations directory 
```shell
cp docker-makefiles/operator-configs docker-makefiles/operator2-configs
```

2. Update configuration files

3. Start new operator node 
```shell
make up ANYLOG_TYPE=operator2
```