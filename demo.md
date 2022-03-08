# Deploying AnyLog 
This branch is intended for the deployment of [Aarna Network](https://www.aarnanetworks.com/) demo with AnyLog. 
The demo will include: 1 _Master_, 3 _Operator_ nodes and a _Query_ node against their [Multi-Cluster Orchestrator](https://www.aarnanetworks.com/amcop).

Please review the [original README](https://github.com/AnyLog-co/deployments/tree/master/REAME.md) for _docker_ deployment 


## Requirements
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) - Kubernetes command line tool
* [helm charts](https://jaya-maduka.medium.com/install-helm-on-ubuntu-20-04-bd5f490c895)
* [Sample Data Generator](https://github.com/AnyLog-co/Sample-Data-Generator) - AnyLog's sample data generator 
* [AnyLog API](https://github.com/AnyLog-co/AnyLog-API) - AnyLog API tool to update 

## Deploy AnyLog Nodes
### General Requirement - on all machines
1. Clone deployments directory & checkout _aarana_ branch  
```bash
cd $HOME
git clone https://github.com/AnyLog-co/deployments
cd $HOME/deployments
git checkout aarana 
```

2. Clone AnyLog-API directory - The AnyLog API has a set of 
[requirements](https://github.com/AnyLog-co/Sample-Data-Generator/blob/master/requirements.txt%20) that should be met 
for the run to succeed. 
```bash
cd $HOME
git clone https://github.com/AnyLog-co/AnyLog-API
```

3. Login into AnyLog for downloading repos - [contact us](mailto:info@anylog.co) for _DOCKER_PASSWORD_ 
```bash
bash $HOME/deployments//credentials.sh ${DOCKER_PASSWORD}
```

4. Deploy Postgres Database - if not deployed AnyLog will use [SQLite](https://sqlite.com/index.html) (no need to make any changes)
```bash
helm install --generate-name $HOME/deployments/helm/postgres
```


### Deploy Nodes
[Master Node](helm/anylog-master) is a "notary" system between other nodes in the network via either a public or private blockchain.
The process will deploy a postgres database as well as an AnyLog node which will create a new database (called _blockchain_), 
which will contain information about the nodes and tables in the network. All other nodes in the network will sync against it. 


[Operator Node](helm/anylog-operator) contain the data that's coming from the sensors; thus when executing a query 
the results are generated based on the information provided by the operator(s). For our demo, this section should be 
repeated 3 times on 3 different machines.  

[Publisher Node](helm/anylog-publisher) is used to distribute the data against the different operators. i.e. instead of 
sending the data into different operator nodes, the user can send all the data into a single point, and AnyLog will 
distribute the data across the different operators, based on the policies in the blockchain.   

[Query Node](helm/anylog-query) is a node dedicated to querying operator nodes, as well as generating reports using BI tools
1. In the [helm file](helm/anylog-query/templates/anylog-query.yaml) update the `MASTER_NODE` value in section _Data_
   * if master node is on the same kubernetes cluster then the value should be `MASTER_NODE=anylog-master-node:32048`
   * if master node is on a different kubernetes cluster then the value should be `MASTER_NODE=192.168.49.2:31900` (based on the example below)   
   ```bash
   # command is run on the physical machine hosting the master node kubernetes service
   minikube service --url anylog-master-node
   
   << COMMENT
   http://192.168.49.2:31900 # TCP 
   http://192.168.49.2:31864 # REST 
   http://192.168.49.2:30260 # Broker 
   COMMENT
   ```
2. Start AnyLog Query node
```bash
helm install --generate-name $HOME/deployments/helm/anylog-query/
```

3a. Deploy [AnyLog GUI](https://github.com/AnyLog-co/AnyLog-GUI) and our proprietary [Remote-CLI](https://github.com/AnyLog-co/Remote-CLI)
```bash
helm install --generate-name $HOME/deployments/helm/anylog-tools
```

3b. Since both the GUI and the CLI are accessible via browser, user should generate an external IP/port for both  
```commandline
minikube service --url anylog-gui
minikube service --url remote-cli
```

4. On the same machine, or a machine that's accessible by the ndoe, install [Grafana](https://grafana.com/docs/grafana/latest/installation/) 
or other BI tool in order to [generate reports](https://github.com/AnyLog-co/documentation/tree/os-dev/northbound%20connectors) 
of the data. Docker deployment of Grafana can be found [here](docker-compose/grafana.sh)
```bash
helm install --generate-name $HOME/deployments/helm/grafana
```

[Standalone Node](helm/anylog-standalone) deploy _master_ and _operator_ as a single AnyLog instance. For the official 
deployment we wil not be using this option. However, it is available for testing and small scale projects.  
1. Deploy [Standalone Helm Chart](helm/anylog-standalone)
```bash
helm install --generate-name $HOME/deployments/helm/anylog-standalone/
```

2. Configure Remote Access to AnyLog Node
```bash 
minikube service --url anylog-standalone-node


<< COMMENT
http://192.168.49.2:31900 # TCP 
http://192.168.49.2:31864 # REST 
http://192.168.49.2:30260 # Broker 
COMMENT 
```

3. A user can install our [AnyLog Toolset](helm/anylog-tools) against the same kubernetes cluster in order to have our
_Remote-CLI_ and _AnyLog-GUI_. Note, all nodes can be used for querying the data; there isnt' a requirement a dedicate 
AnyLog instance.
```bash
helm install --generate-name $HOME/deployments/helm/anylog-tools

minikube service --url anylog-gui
minikube service --url remote-cli
```

### Generate Data & Publisher Node

3. Start Data Generator(s) - AnyLog uses message clients to digest the data coming in. Since the processes are 
preconfigured, you cannot confuse between the two.
```bash
# REST 
python3 ~/Sample-Data-Generator/data_generator.py 192.168.49.2:31864 power post aarna_demo -e --topic power1

# Broker  
python3 ~/Sample-Data-Generator/data_generator.py 192.168.49.2:30260 synchrophasor mqtt aarna_demo -e --topic power2
```
