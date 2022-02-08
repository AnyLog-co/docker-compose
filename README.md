# Deploying AnyLog 

## Requirements 
* [docker-compose](https://github.com/AnyLog-co/documentation/blob/master/Docker%20Compose%20&%20Kubernetes.md)
* [kompose](https://kompose.io/installation/) - A conversion tool for Docker Compose to container orchestrators such as Kubernetes (or OpenShift).
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) - Kubernetes command line tool
* [minikube](https://minikube.sigs.k8s.io/docs/start/) - local Kubernetes, focusing on making it easy to learn and develop for Kubernetes.

## Prepare Deployment 
1. Clone & cd into docker-compose dir 
```commandline
cd $HOME
git clone https://github.com/AnyLog-co/docker-compose
cd $HOME/docker-compose 
```
2. Update environment variables in [envs](envs/) directory -- specifically [postgres](envs/postgres.env) and [anylog-network](envs/anylog_node.env) configs 


## Docker Compose 
* How to start docker-compose
```commandline
docker-compose up -d 
```
* How to attach to AnyLog
```commandline
docker attach --detach-keys="ctrl-d" anylog-node
```
* How to access Volume(s)

* How to stop docker-compose - when adding `-v` the the end of the command, user will also delete the volume(s)
```commandline
docker-compose down
```


## kubernetes
1. In docker-compose dir generate `docker-compose-updated.yml` which contains actual environment variables rather than names
```commandline
# convert docker with env to variables
cd $HOME/docker-compose
docker-compose config > docker-compose-updated.yml
```

2. Convert docker-compose-updated
```commandline
mkdir $HOME/kube  
cd $HOME/kube 

# convert for kubernetes 
kompose convert -f $HOME/docker-compose/docker-compose-updated.yaml 
```

3. Deploy kubernetes
```commandline
kubectl apply -f $HOME/kube
```

4. Open networking for access 

