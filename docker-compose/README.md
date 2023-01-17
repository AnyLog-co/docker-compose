# Installing AnyLog using Docker 

The following provides general directions for installing AnyLog through _Docker_ and _docker-compose_. Detailed directions
can be found in our [deployment documentation](https://github.com/AnyLog-co/documentation/tree/os-dev/deployments). 

### Requirements
* Docker
* docker-compose
* Python3 + [dotenv](https://pypi.org/project/python-dotenv/) - for utilizing [deployment scripts](../deplyoment_scripts) 

## Deployment 
### Setting Up Machine
1. Clone [deployments](https://github.com/AnyLog-co/deployments)
```shell
cd $HOME ; git clone https://github.com/AnyLog-co/deployments
```
2. Log into AnyLog docker in order to download the image. If you do not have login credentials for our Docker hub, feel 
free to <a href="mailto:info@anylog.co?subject=Request Docker access">send us a message</a>.
```shell
# log into docker for access to AnyLog
bash $HOME/deployments/installations/docker_credentials.sh ${DOCKER_PASSWORD}
```
3. Manually deploy Postgres and/or MongoDB if planning to use in deployment -- this step is not needed for [Demo Cluster](#demo-cluster)
    * [Postgres Configuration](postgres/postgres.env)
    * [MongoDB Configurations](mongodb/.env)
```shell
# deploy PostgreSQL 
cd $HOME/deployments/docker-compose/postgres/ ; docker-compose up -d 
# Deploy MongoDB 
cd $HOME/deployments/docker-compose/mongodb/ ; docker-compose up -d 
```
### Scripted Process 
1. Initiate the deployment scripts - this will prepare the configurations (based on user input) and deploy an AnyLog 
instance.    
```shell
bash $HOME/deployments/deployment_scripts/deploy_node.sh 
```
2. (Optional) Deploy Remote-CLI -- A _query_ instance will also deploy Remote-CLI by itself; there's no need to redeploy it.
   * Access for Remote-CLI is [http://${LOCAL_IP_ADDRESS}:31800]() 
```shell
cd $HOME/deployments/docker-compose/remote-cli/ ; docker-compose up -d 
```
3. (Optional) Deploy Grafana
   * Access for Grafana is [http://${LOCAL_IP_ADDRESS}:3000]()
```shell
cd $HOME/deployments/docker-compose/grafana/ ; docker-compose up -d 
```

### Manual Process
1. cd into the desired node 
```shell
# master node
cd $HOME/deployments/docker-compose/anylog-master/

# operator node 
cd $HOME/deployments/docker-compose/anylog-operator/

# publisher node 
cd $HOME/deployments/docker-compose/anylog-publisher/

# query with Remote-CLI node 
cd $HOME/deployments/docker-compose/query-remote-cli/
```
2. Update deployment configurations
```shell
vim anylog_configs.env
```
3. Update image information (default is _predevelop_)
```shell
vim .env 
```
**Note** - If you'd like to deploy multiple operator nodes on a single machine, then the service name 
(`anylog-operator-node`) and volume names in [docker-compose.yaml](anylog-operator/docker-compose.yml) needs to be 
updated. 

4. Deploy Node 
```shell
docker-compose up -d 
```
5. (Optional) Deploy Remote-CLI -- A _query_ instance will also deploy Remote-CLI by itself; there's no need to redeploy it.
   * Access for Remote-CLI is [http://${LOCAL_IP_ADDRESS}:31800]() 
```shell
cd $HOME/deployments/docker-compose/remote-cli/ ; docker-compose up -d 
```
6. (Optional) Deploy Grafana
   * Access for Grafana is [http://${LOCAL_IP_ADDRESS}:3000]()
```shell
cd $HOME/deployments/docker-compose/grafana/ ; docker-compose up -d 
```


### Demo Cluster 
The [Demo Cluster Deployment](anylog-demo-network) is a standalone package that deploys the demo network on a single
AnyLog physical machine. This includes:
   * 1 Master 
   * 2 Operators (1 with SQLite and one with Postgres)
   * 1 Query Node 
   * Postgres 
   * Grafana 
   * Remote-CLI

1. cd into [demo-cluster-deployment](anylog-demo-network)
```shell
cd $HOME/deployments/docker-compose/anylog-demo-network/
```
2. (Optional) Update configurations
```shell
# Postgres 
vim envs/postgres.env 

# Master 
vim envs/anylog_master.env 

# Operator 1 
vim envs/anylog_operator1.env 

# Operator 2  
vim envs/anylog_operator2.env

# Query 
vim envs/anylog_query.env
```
3. Update image information (default is _predevelop_)
```shell
vim .env 
```
4. Deploy Node
   * Access for Remote-CLI is [http://${LOCAL_IP_ADDRESS}:31800]()
   * Access for Grafana is [http://${LOCAL_IP_ADDRESS}:3000]()
```shell
docker-compose up -d 
```
5. Deploy EdgeX using the directions in [lfedge-code](https://github.com/AnyLog-co/lfedge-code) to get data into the 
operator running with local broker 