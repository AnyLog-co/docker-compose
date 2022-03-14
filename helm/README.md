# Deploy AnyLog using Kubernetes 

The following provides details in regard to deploying AnyLog Node, and it's corresponding tools, via Kubernetes 
(helm-charts).

## Requirement
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) - Kubernetes command line tool
* [minikube](https://minikube.sigs.k8s.io/docs/start/) - local Kubernetes, focusing on making it easy to learn and develop for Kubernetes.
* [helm-charts](https://helm.sh/docs/intro/quickstart/)


## Steps to Deploy AnyLog  
0. [Contact Us](mailto:info@anylog.co) to request credentials for downloading AnyLog

1. Configure credentials 
```bash
bash $HOME/deployments/helm/credentials.sh ${YOUR_ANYLOG_DOCKER_PASSWORD}
```

2. On all Kubernetes clusters that contain an AnyLog instance that uses Postgres deploy postgres -- alternatively you 
can use your own Postgres instance 
```bash
helm install --generate-name $HOME/deployments/helm/postgres
```

3. Update configuration for the AnyLog Node(s) to be deployed  
    * Node Ports - no two nodes (within the same kubernetes cluster) should have the same port values
      * `ANYLOG_SERVER_PORT`
      * `ANYLOG_REST_PORT`
      * `ANYLOG_BROKER_PORT` (optional)
    * If two operators share a cluster name (`NEW_CLUSTER`), then they'll have the same data 
    

4. Deploy AnyLog Node(s) - example with node of type _Standalone_
```bash
helm install --generate-name $HOME/deployments/helm/anylog-standalone
```

5. (**optional**) Deploy [Remote CLI](https://github.com/AnyLog-co/Remote-CLI) & [AnyLog GUI](https://github.com/AnyLog-co/AnyLog-GUI) - 
These are accesed via browser on ports 5000 (AnyLog GUI) and 8000 (Remote CLI) respectively 
```bash
helm install --generate-name $HOME/deployments/helm/anylog-tools/
```

6. (**optional**) Deploy [Grafana](https://grafana.com/docs/grafana/latest/installation/)
```bash
helm install --generate-name $HOME/deployments/helm/grafana
```

**Notes**: 
* For Kuberenetes instance(s) that are not configured to `NodePort`, users can gain access using the following command: 
```commandline
kubectl port-forward --address ${IP_ADDRESS} service/${SERVICE_NAME} 5432:5432 &> /dev/null &
```
