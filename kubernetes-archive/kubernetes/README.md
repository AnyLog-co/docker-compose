# Kubernetes 

Directions for deploying Kubearmor can be found [here](Kubearmor/README.md)

## Deploying AnyLog on Kubernetes 
1. Declare secret - [contact us](mailto:info@anylog.co) for your personalized Docker key 
```shell
kubectl create secret docker-registry imagepullsecret \
  --docker-server=docker.io \
  --docker-username=anyloguser \
  --docker-password=[Your Docker API key] \
  --docker-email=anyloguser@anylog.co
```

2. Create Package 
```shell
# packages AnyLog Node 
helm package deployments/kubernetes/anylog-node

# package AnyLog Volume
helm package anylog-node-volume 
```

3. Update `node_configs`

The configuration file for each node consists of configurations for both the deployment and  associated volumes (optional). 
They consist of the minimal amount of configurations needed to deploy an AnyLog node; similar  to the _training_ modules 
in our Docker deployment. A full list of configuration options can be found in the [values.yaml](../../kubernetes/anylog-node/values.yaml).

* [Master Node](../../kubernetes/configurations/anylog_master.yaml)
* [Operator Node](../../kubernetes/configurations/anylog_master.yaml)
* [Query Node](../../kubernetes/configurations/anylog_master.yaml)
* [Publisher Node](../../kubernetes/configurations/anylog_master.yaml)
 

4. Deploy Node 
```shell
# Deploy AnyLog instance & volume
bash deployments/run.sh helm master up

# Set port-forwarding for TCP, REST and Broker is configured
# -- TCP
kubectl port-forward --address 10.0.0.251 service/anylog-master-service 32048:32048 -n default &
# -- REST 
kubectl port-forward --address 10.0.0.251 service/anylog-master-service 32049:32049 -n default &
# -- Broker (used 
kubectl port-forward --address 10.0.0.251 service/anylog-master-service 32150:32150 -n default & 
```

5. Attach / Detach from Pod 
```shell
# Attach to Pod - replace `master` with desired node type 
POD=$(kubectl get pod -l app=anylog-node -o name | grep master)
kubectl attach -it ${POD}

# to detach: Ctrl+p followed by Ctrl+q
```


## Nginx
Validate Nginx works - https://github.com/AnyLog-co/documentation/blob/master/deployments/Networking%20%26%20Security/nginx.md
