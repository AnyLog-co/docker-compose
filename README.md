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
```bash
cp docker-compose-base.yml docker-compose.yml 
docker-compose up -d 
```

* cURL request against AnyLog-Network -- `anylog-node` service uses the `network_mode: host` rather than the network created by the network. As such, AnyLog uses the same IP(s) as the machine it seats on. 
```bash
curl -X GET 10.0.0.212:3481 -H "commnad: get status" -H "Usr-Agent: AnyLog/1.23"
```

* How to attach to AnyLog
```bash
docker attach --detach-keys="ctrl-d" anylog-node
```
* How to access Volume(s)
```bash
# Locate the Mountpoint 
docker volume inspect docker-compose_anylog-node-local-scripts 
[
    {
        "CreatedAt": "2022-02-08T22:46:36Z",
        "Driver": "local",
        "Labels": {
            "com.docker.compose.project": "docker-compose",
            "com.docker.compose.version": "1.25.0",
            "com.docker.compose.volume": "anylog-node-local-scripts"
        },
        "Mountpoint": "/var/lib/docker/volumes/docker-compose_anylog-node-local-scripts/_data",
        "Name": "docker-compose_anylog-node-local-scripts",
        "Options": null,
        "Scope": "local"
    }
]

# Use sudo command to access directory / files  
sudo ls /var/lib/docker/volumes/docker-compose_anylog-node-local-scripts/_data
hidden_node.al  local_script.al  master.al  mqtt.al  operator.al  publisher.al  query.al  rest_init.al  single_node.al  single_node_publisher.al
```

* How to stop docker-compose - when adding `-v` the the end of the command, user will also delete the volume(s)
```commandline
docker-compose down
```


## kubernetes
status volumes: 
* All deployments work 
* able to access everything but AnyLog 
* missing volumes 
```
cd $HOME/docker-compose 

cp docker-compose-k8s.yml docker-compose.yml 

docker-compose config > ~/docker-compose/docker-compose-update.yml 

mkdir ~/kube

cd ~/kube 

kompose convert -f ~/docker-compose/docker-compose-update.yml

kompose app -f . 

bash ~/docker-compose/kube_port_access.sh 10.0.0.212
```
