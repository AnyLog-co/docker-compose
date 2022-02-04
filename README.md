# Deploying AnyLog 

## Requirements 
* [docker-compose](https://github.com/AnyLog-co/documentation/blob/master/Docker%20Compose%20&%20Kubernetes.md)
* [kompose](https://kompose.io/installation/) - A conversion tool for Docker Compose to container orchestrators such as Kubernetes (or OpenShift).
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) - Kubernetes command line tool
* [minikube](https://minikube.sigs.k8s.io/docs/start/) - local Kubernetes, focusing on making it easy to learn and develop for Kubernetes.

## Prepare Deployment 
0. Clone & cd into docker-compose dir 
```commandline
cd $HOME
git clone https://github.com/AnyLog-co/docker-compose
cd $HOME/docker-compose 
```

1. Update [.env](.env) with desired configuration. Specific params to look at: 
   * Usernames & Passwords 
   * NODE_TYPE
   * COMPANY_NAME
   * Networking (such as IPs, ports and master_node)
   * DB_USER
   * DEFAULT_DBMS
   * MQTT params 


2. Convert docker-compose 
```commandline
docker-compose config > docker-compose-resolved.yaml
```

## Deploy AnyLog  
Once done, the depoloyment can be done either via _docker-compose_, _kubernetes_ or _helm_

**docker-compose**
```commandline
cp docker-compose-resolved.yaml docker-compose.yaml 

# start
docker-compose up -d

# attach 
docker attach --detach-keys="ctrl-d" ${CONTAINER_NAME}  

# stop 
docker down  
```

**kubernetes**
```commandline
mkdir $HOME/kube  
cd $HOME/kube 

# convert for kubernetes 
kubectl convert -f $HOME/docker-compose/docker-compose-resolved.yaml 

# Deploy 
kubectl apply -f $HOME/kube

# Attach
kubectl exec -it ${POD_NAME} -- bash 

# stop 
kubectl delete -f $HOME/kube
```


