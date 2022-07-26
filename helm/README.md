# Installing AnyLog using Kubernetes 

The following provides general directions for installing AnyLog through _helm_ and _Kubernetes_. Detailed directions
can be found in our [deployment documentation](https://github.com/AnyLog-co/documentation/tree/os-dev/deployments). 

## Requirements 
There are 3 [basic requirements](https://github.com/AnyLog-co/documentation/blob/os-dev/deployments/Kubernetes/Prerequisites.md) 
for deploying AnyLog and its corresponding services.
* Docker 
* helm
* Kubernetes deployment tools (we use [minikube](https://minikube.sigs.k8s.io/docs/start/)) 

## Setting-up Nginx
Due to [networking configurations](https://github.com/AnyLog-co/documentation/blob/os-dev/deployments/Kubernetes/Networking.md), 
we recommend setting-up _Nginx_ in order to have consistent IPs in policy declarations of the blockchain.    
1. Install Nginx 
```shell 
sudo apt-get -y install nginx
```

2. Remove default files
```shell
sudo rm -rf /etc/nginx/sites-enabled/default 
sudo rm -rf /etc/nginx/sites-available/default
```

3. Update `/etc/nginx/nginx.conf` to support both TCP & Message broker (if set) communication 
```shell
# 1. import ngx_stream_module.so module at the top of the file.
# With Ubuntu 20.04 this step was need. However, with later version of Ubuntu it was not. 
include /usr/lib/nginx/modules/ngx_stream_module.so;

# 2. At the bottom add stream process - each AnyLog node (on the same machine) should have its own upstream & server 
# process(es) within the stream section
stream {
    # AnyLog TCP Connection - repeat the next two steps for each node
    upstream anylog_node {
        server ${KUBE_APISERVER_IP}:32048;
    }
    server {
        listen 32048 so_keepalive=on;
        proxy_pass anylog_node;
    }
    # AnyLog Message Broker Connection - repeat the next two steps for each node 
    upstream anylog_node_broker {
        server ${KUBE_APISERVER_IP}:32050;
    }
    server {
        listen 32050 so_keepalive=on;
        proxy_pass anylog_node_broker;
    }
}
```

4. Create a new file called `/etc/nginx/sites-enabled/anylog.conf` for REST communication
```shell
# sudo vim /etc/nginx/sites-enabled/anylog.conf 
# nginx default webpage - this generates the default nginx homepage 
server {
  listen 80;
  server_name;
}

# Grafana 
server {
  listen 3000;
  server_name _;
  location / {
    proxy_set_header Host            $host;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_pass http://${KUBE_APISERVER_IP}:31000;
  }
}

# Remote-CLI
server {
  listen 31800;
  server_name _;
  location / {
    proxy_set_header Host            $host;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_pass http://${KUBE_APISERVER_IP}:31800;
  }
}


# AnyLog Node - make sure the IP & REST Port are correct. This section needs to repeated for each AnyLog node on the 
# machine. 
server {
  listen 32049;
  server_name _;
  location / {
    proxy_set_header Host            $host;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_pass http://${KUBE_APISERVER_IP}:32049;
  }
}
```

## Deploying Postgres
```shell
# Deploy Volume for PostgreSQL  
helm install ~/deployments/packages/postgres-volume-14.0-alpine.tgz --values ~/deployments/configurations/helm/postgres_volume.yaml --name-template postgres-volume 

# Deploy actual PostgreSQL node 
helm install ~/deployments/packages/postgres-14.0-alpine.tgz --values ~/deployments/configurations/helm/postgres.yaml --name-template postgres
```

## Deploying AnyLog Node
By default, AnyLog _helm_ package is configured to run as a REST node if no `--values` are set.  
```shell
helm install ~/deployments/helm/packages/anylog-node-1.22.3.tgz --values ~/deployments/helm/sample-configurations/${ANYLOG_CONFIG}.yaml --name-template ${DEPLOYMENT_NAME}
```

## Deploying Grafana 

## Deploying Remote-CLI 