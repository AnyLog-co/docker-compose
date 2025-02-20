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
AnyLog deployment contains  predefined configurations for each node type, enabling users to deploy a network with a 
simple `docker run` command. This approach allows for quick deployment with minimal configuration but is limited to one 
node type per machine. To overcome this limitation, additional environment configurations can be provided.

### Default Deployment and Networking Configuration
When deploying using the basic command, the container utilizes the default parameters based on `NODE_TYPE`, with the 
following networking configurations:

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
<br/>-p 320498:32049 \
<br/>-e NODE_TYPE=master \
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
<br/>--name anylog-query --rm anylogco/anylog-network:latest</code></td>
   </tr>
   <tr>
      <td>Generic</td>
      <td>3548</td>
      <td>32549</td>
      <td><code>docker run -it -d \ 
<br/>-p 32548:32548 \
<br/>-p 32549:32549 \
<br/>-e NODE_TYPE=generic \
<br/>--name anylog-node --rm anylogco/anylog-network:latest</code></td>
   </tr>
</table>
</html>


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
  supported EdgeLake types: generic, master, operator, publisher and query
Sample calls: make up ANYLOG_TYPE=master | make attach ANYLOG_TYPE=master | make clean ANYLOG_TYPE=master
```