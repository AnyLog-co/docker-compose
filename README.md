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

## Basic Deployment
AnyLog deployment contains predefined configurations for each node type, enabling users to deploy a network with a 
simple `docker run` command. This approach allows for quick deployment with minimal configuration but is limited to one 
node type per machine. To overcome this limitation, additional environment configurations can be provided.

### Default Deployment and Networking Configuration
When deploying using the basic command, the container utilizes the default parameters based on `NODE_TYPE`, with the 
following networking configurations:

#### Important Notes:
- **Port Configuration: When deploying on the same machine, no two containers can have the same ports. Be sure to 
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
      <th>Run command</th>
   </tr>
   <tr>
      <td>Master</td>
      <td>32048</td>
      <td>32049</td>
      <td><code>docker run -it -d \ 
<br/>-p 32048:32048 \
<br/>-p 32049:32049 \
<br/>-e NODE_TYPE=master \
<br/>-e LICENSE_KEY=[YOUR_LICENSE_KEY] \
<br/>--name anylog-master --rm anylogco/anylog-network:latest</code></td>
   </tr>
   <tr>
      <td>Operator</td>
      <td>32148</td>
      <td>32149</td>
      <td><code>docker run -it -d \ 
<br/>-p 32148:32148 \
<br/>-p 32149:32149 \
<br/>-e NODE_TYPE=operator \
<br/>-e LEDGER_CONN=[MASTER_NODE IP:Port] \
<br/>-e LICENSE_KEY=[YOUR_LICENSE_KEY] \
<br/>--name anylog-operator --rm anylogco/anylog-network:latest</code></td>
   </tr>
   <tr>
      <td>Query</td>
      <td>32348</td>
      <td>32349</td>
      <td><code>docker run -it -d \ 
<br/>-p 32348:32348 \
<br/>-p 32349:32349 \
<br/>-e NODE_TYPE=query \
<br/>-e LEDGER_CONN=[MASTER_NODE IP:Port] \
<br/>-e LICENSE_KEY=[YOUR_LICENSE_KEY] \
<br/>--name anylog-query --rm anylogco/anylog-network:latest</code></td>
   </tr>
   <tr>
      <td>Generic</td>
      <td>32548</td>
      <td>32549</td>
      <td><code>docker run -it -d \ 
<br/>-p 32548:32548 \
<br/>-p 32549:32549 \
<br/>-e NODE_TYPE=generic \
<br/>-e LICENSE_KEY=[YOUR_LICENSE_KEY] \
<br/>--name anylog-node --rm anylogco/anylog-network:latest</code></td>
   </tr>
</table>
</html>

### Custom Deployment with Multiple Nodes
When deploying multiple nodes (e.g., operators or queries) on the same machine, ensure you configure unique ports for each container by modifying the `ANYLOG_SERVER_PORT` and `ANYLOG_REST_PORT` environment variables. Similarly, ensure each node has a distinct `NODE_NAME` and `CLUSTER_NAME`. Here’s an example of running multiple operators or queries:

```bash
docker run -it -d \
  -p [UNIQUE_SERVER_PORT]:[UNIQUE_SERVER_PORT] \
  -p [UNIQUE_REST_PORT]:[UNIQUE_REST_PORT] \
  -e NODE_TYPE=operator \
  -e LEDGER_CONN=[MASTER_NODE IP:Port] \
  -e LICENSE_KEY=[YOUR_LICENSE_KEY] \
  -e NODE_NAME=[UNIQUE_NODE_NAME] \
  -e CLUSTER_NAME=[UNIQUE_CLUSTER_NAME] \
  --name anylog-operator-1 --rm anylogco/anylog-network:latest
```
`
## Deploy AnyLog via Docker
1. Update `.env` configurations for the node(s) being deployed -- Edit `LEDGER_CONN` in _query_ and _operator_ using  the 
IP address of master node
   * [Master Node](docker-makefiles/master-configs)
   * [Operator Node](docker-makefiles/operator-configs)
   * [Query Node](docker-makefiles/query-configs)

2. Start Node using _makefile_
```shell
make up ANYLOG_TYPE=[NODE_TYPE]
```

### Makefile Commands for Docker
```shell
Targets:
  login         Log into AnyLog's Dockerhub - use ANYLOG_TYPE to set password value
  build         Pull the docker image
  up            Start the containers
  attach        Attach to AnyLog instance
  test-node     Validate node status
  test-network  Validate node can communicate with other nodes in the network
  exec          Attach to shell interface for container
  down          Stop and remove the containers
  logs          View logs of the containers
  clean-vols    stop & clean volumes
  clean         stop & clean up volumes and image
  help                  show this help message
  supported AnyLog types: generic, master, operator, publisher and query
Sample calls: make up ANYLOG_TYPE=master | make attach ANYLOG_TYPE=master | make clean ANYLOG_TYPE=master
```