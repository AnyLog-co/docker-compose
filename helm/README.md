# Installing AnyLog using Kubernetes 

The following provides general directions for installing AnyLog through _helm_ and _Kubernetes_. Detailed directions
can be found in our [deployment documentation](https://github.com/AnyLog-co/documentation/tree/os-dev/deployments). 

### Requirements  
for deploying AnyLog and its corresponding services.
* Docker 
* helm
* Kubernetes deployment tools (we use [minikube](https://minikube.sigs.k8s.io/docs/start/)) 
* Python3 + [dotenv](https://pypi.org/project/python-dotenv/) - for utilizing [deployment scripts](../deplyoment_scripts)

### Prerequisites
* [NGINX](https://github.com/AnyLog-co/documentation/blob/os-dev/deployments/Networking/nginx.md) used for consistent IP address    
* [Nebula Overlay Network](https://github.com/AnyLog-co/documentation/blob/os-dev/deployments/Networking/nebula.md)

## Deployment 
### Scripted Process 
0. Manually deploy Postgres and/or MongoDB if planning to use in deployment
    * [Postgres Volume](sample-configurations/postgres_volume.yaml) & [Postgres Configuration](sample-configurations/postgres.yaml)
    * [MongoDB Volume](sample-configurations/mongodb_volume.yaml) & [MongoDB Configurations](mongodb/.env)
```shell
# deploy PostgreSQL 
helm install $HOME/deployments/helm/packages/postgres-volume-14.0-alpine.tgz --name-template psql-volume --values $HOME/deployments/helm/sample-configurations/postgres_volume.yaml
helm install $HOME/deployments/helm/packages/postgres-14.0-alpine.tgz --name-template psql --values $HOME/deployments/helm/sample-configurations/postgres.yaml

# Deploy MongoDB 
helm install $HOME/deployments/helm/packages/mongodb-volume-4.tgz --name-template mongo-volume --values $HOME/deployments/helm/sample-configurations/mongodb_volume.yaml
helm install $HOME/deployments/helm/packages/mongodb-4.tgz --name-template mongo --values $HOME/deployments/helm/sample-configurations/mongodb.yaml
```
1. Initiate the deployment scripts - this will prepare the configurations (based on user input) and deploy an AnyLog 
instance.    
```shell
bash $HOME/deployments/deployment_scripts/deploy_node.sh 
```
2. (Optional) Deploy Remote-CLI
   * Access for Remote-CLI is [http://${LOCAL_IP_ADDRESS}:31800]() 
```shell
helm install $HOME/deployments/helm/packages/remote-cli-volume-1.0.0.tgz --name-template remote-cli-volume --values $HOME/deployments/helm/sample-configurations/remote_cli_volume.yaml
helm install $HOME/deployments/helm/packages/remote-cli-1.0.0.tgz --name-template remote-cli --values $HOME/deployments/helm/sample-configurations/remote_cli.yaml  
```
3. (Optional) Deploy Grafana
   * Access for Grafana is [http://${LOCAL_IP_ADDRESS}:3000]()
```shell
helm install $HOME/deployments/helm/packages/grafana-volume-7.5.7.tgz --name-template grafana-volume --values $HOME/deployments/helm/sample-configurations/grafana_volume.yaml
helm install $HOME/deployments/helm/packages/grafana-7.5.7.tgz --name-template grafana --values $HOME/deployments/helm/sample-configurations/grafana.yaml
```

### Manual Process
0. Manually deploy Postgres and/or MongoDB if planning to use in deployment
    * [Postgres Volume](sample-configurations/postgres_volume.yaml) & [Postgres Configuration](sample-configurations/postgres.yaml)
    * [MongoDB Volume](sample-configurations/mongodb_volume.yaml) & [MongoDB Configurations](mongodb/.env)
```shell
# deploy PostgreSQL 
helm install $HOME/deployments/helm/packages/postgres-volume-14.0-alpine.tgz --name-template psql-volume --values $HOME/deployments/helm/sample-configurations/postgres_volume.yaml
helm install $HOME/deployments/helm/packages/postgres-14.0-alpine.tgz --name-template psql --values $HOME/deployments/helm/sample-configurations/postgres.yaml

# Deploy MongoDB 
helm install $HOME/deployments/helm/packages/mongodb-volume-4.tgz --name-template mongo-volume --values $HOME/deployments/helm/sample-configurations/mongodb_volume.yaml
helm install $HOME/deployments/helm/packages/mongodb-4.tgz --name-template mongo --values $HOME/deployments/helm/sample-configurations/mongodb.yaml
```
1. Update deployment configurations
```shell
# master node
vim $HOME/deployments/helm/sample-configurations/anylog_master.yaml

# operator node
vim $HOME/deployments/helm/sample-configurations/anylog_operator.yaml

# publisher node
vim $HOME/deployments/helm/sample-configurations/anylog_publisher.yaml

# query node
vim $HOME/deployments/helm/sample-configurations/anylog_query.yaml
```

2. Deploy Volume
```shell
# master node
helm install $HOME/deployments/helm/packages/anylog-node-volume-1.22.3.tgz --name-template master-vol --values $HOME/deployments/helm/sample-configurations/anylog_master.yaml

# operator node
helm install $HOME/deployments/helm/packages/anylog-node-volume-1.22.3.tgz --name-template operator-vol --values $HOME/deployments/helm/sample-configurations/anylog_operator.yaml

# publisher node
helm install $HOME/deployments/helm/packages/anylog-node-volume-1.22.3.tgz --name-template publisher-vol --values $HOME/deployments/helm/sample-configurations/anylog_publisher.yaml

# query node
helm install $HOME/deployments/helm/packages/anylog-node-volume-1.22.3.tgz --name-template query-vol --values $HOME/deployments/helm/sample-configurations/anylog_query.yaml
```

3. Deploy Node 
```shell
# master node
helm install $HOME/deployments/helm/packages/anylog-node-1.22.3.tgz --name-template master --values $HOME/deployments/helm/sample-configurations/anylog_master.yaml

# operator node
helm install $HOME/deployments/helm/packages/anylog-node-1.22.3.tgz --name-template operator --values $HOME/deployments/helm/sample-configurations/anylog_operator.yaml

# publisher node
helm install $HOME/deployments/helm/packages/anylog-node-1.22.3.tgz --name-template publisher --values $HOME/deployments/helm/sample-configurations/anylog_publisher.yaml

# query node
helm install $HOME/deployments/helm/packages/anylog-node-1.22.3.tgz --name-template query --values $HOME/deployments/helm/sample-configurations/anylog_query.yaml
```

4. (Optional) Deploy Remote-CLI
   * Access for Remote-CLI is [http://${LOCAL_IP_ADDRESS}:31800]() 
```shell
helm install $HOME/deployments/helm/packages/remote-cli-volume-1.0.0.tgz --name-template remote-cli-volume --values $HOME/deployments/helm/sample-configurations/remote_cli_volume.yaml
helm install $HOME/deployments/helm/packages/remote-cli-1.0.0.tgz --name-template remote-cli --values $HOME/deployments/helm/sample-configurations/remote_cli.yaml  
```
5. (Optional) Deploy Grafana
   * Access for Grafana is [http://${LOCAL_IP_ADDRESS}:3000]()
```shell
helm install $HOME/deployments/helm/packages/grafana-volume-7.5.7.tgz --name-template grafana-volume --values $HOME/deployments/helm/sample-configurations/grafana_volume.yaml
helm install $HOME/deployments/helm/packages/grafana-7.5.7.tgz --name-template grafana --values $HOME/deployments/helm/sample-configurations/grafana.yaml
```


### Attaching to a node
* Attach into bash instance of node 
```shell
kubectl exec -it ${POD_NAME} bash
```
* Attach into AnyLog CLI 
```shell
kubectl attach -it ${POD_NAME}
```

To detach from either `crtl-p` + `ctrl-q` 
