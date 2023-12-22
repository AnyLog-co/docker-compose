# AnyLog 

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
helm package anylog-node

# package AnyLog Volume
helm package anylog-node-volume 
```

3. Update `node_configs`

The configuration file for each node consists of configurations for both the deployment and  associated volumes (optional). 
They consist of the minimal amount of configurations needed to deploy an AnyLog node; similar  to the _training_ modules 
in our Docker deployment. A full list of configuration options can be found in the [values.yaml](anylog-node/values.yaml).

* [Master Node](configs/anylog_master.yaml)
* [Operator Node](configs/anylog_master.yaml)
* [Query Node](configs/anylog_master.yaml)
* [Publisher Node](configs/anylog_master.yaml)
 

4. Deploy Node 
```shell
# Deploy AnyLog instance

# Deploy associated Volumes  
```

5. Attach / Detach from Pod 
```shell
# Attach to Pod - replace `master` with desired node type 
POD=$(kubectl get pod -l app=nginx -o name | grep master)


# to detach: Ctrl+P followed by Ctrl+Q
```

**Questions**: 
1. on values.yaml - `LEDGER_CONN` should have the same name as service 
2. on values.yaml - For volumes, instead of /app/AnyLog-Network or /app/deployment-scripts /app should be replaced with 
relative { .Values.node_configs.directory.ANYLOG_PATH } 
