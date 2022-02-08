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
docker-compose up -d 
```
* How to GET IP address of AnyLog Node
```bash
# Find container ID
docker ps -a | grep anylog-node | awk -F " " '{print $1}' 
684270a55359

# Based on the container ID locate the IP address 
docker network inspect docker-compose_frontend -v  Containers 
[
    {
        "Name": "docker-compose_frontend",
        "Id": "0376489eac2b7f86d98054a303d457e0dbe269fa5b193184f32e935cf852c72b",
        "Created": "2022-02-08T22:46:36.52179439Z",
        "Scope": "local",
        "Driver": "bridge",
        "EnableIPv6": false,
        "IPAM": {
            "Driver": "default",
            "Options": null,
            "Config": [
                {
                    "Subnet": "192.168.96.0/20",
                    "Gateway": "192.168.96.1"
                }
            ]
        },
        "Internal": false,
        "Attachable": true,
        "Ingress": false,
        "ConfigFrom": {
            "Network": ""
        },
        "ConfigOnly": false,
        "Containers": {
            "25a6bef11ffc65afff78b5d98d06099c74a5223cc502a8f8f063e0c96963233a": {
                "Name": "postgres",
                "EndpointID": "bc8764a2cf709e04dc0e4ff935bf65bf0367651c7091eedb6b5defd3293a513b",
                "MacAddress": "02:42:c0:a8:60:02",
                "IPv4Address": "192.168.96.2/20",
                "IPv6Address": ""
            },
            "558a94e7b3fab64d542646eaa7ef8ac4b2ab308fc15d759d9508cce0fce07c52": {
                "Name": "grafana",
                "EndpointID": "ca52cd5668748dfdf808ccd9132914b8b16a787a9e9a319603fc94bedb82b18b",
                "MacAddress": "02:42:c0:a8:60:04",
                "IPv4Address": "192.168.96.4/20",
                "IPv6Address": ""
            },
            "684270a5535936a6bc39d53aac3d4cc8e50e449571060290a6e73c0f0fdc4098": { 
                "Name": "anylog-node",
                "EndpointID": "ecd91cfb5d998417540953558d9f6995bc9961549e2bb659cd335e0405511977",
                "MacAddress": "02:42:c0:a8:60:03",
                "IPv4Address": "192.168.96.3/20", # <-- This is your IP
                "IPv6Address": ""
            },
            "7ca6b9ad16fc6140b4b11b701ae24756f26027ba0a61e17f866c87889598dfd8": {
                "Name": "remote-cli",
                "EndpointID": "5e47bb83e403eaf7bd5756ff32831f000126a7c5f1b9789d01f738c25259d05c",
                "MacAddress": "02:42:c0:a8:60:05",
                "IPv4Address": "192.168.96.5/20",
                "IPv6Address": ""
            }
        },
        "Options": {},
        "Labels": {
            "com.docker.compose.network": "frontend",
            "com.docker.compose.project": "docker-compose",
            "com.docker.compose.version": "1.25.0"
        }
    }
]

# Execute cURL 
curl -X GET 192.168.96.3:3481 -H "command: get status"  -H "User-Agent: AnyLog/1.23"
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
