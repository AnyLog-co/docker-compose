# Deploy AnyLog using Kubernetes 

The following provides details in regard to deploying AnyLog Node, and it's corresponding tools, via Kubernetes 
(helm-charts).

## Requirement
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) - Kubernetes command line tool
* [minikube](https://minikube.sigs.k8s.io/docs/start/) - local Kubernetes, focusing on making it easy to learn and develop for 
  Kubernetes. Alternativly a user can use something else; such as: _kubeadm_, _MicroK8s_, _K3s_    
* [helm-charts](https://helm.sh/docs/intro/quickstart/) - Kubernetes package manager 
* [nginx](https://nginx.org/en/) - web server used as a reverse proxy

## Deploying an AnyLog Instance 
1. [Install Kubernetes](kube_install.sh)
   * _kubectl_
   * _minikube_
   * _helm-charts_ 
   

2. Clone & configure helm packages 
```bash
git clone https://github.com/AnyLog-co/deployments 
```


3. Package and deploy helm packages
```bash
# packages 
helm package $HOME/deployments/helm/anylog-master/
helm install anylog-master-1.0220301.tgz
```

## Configuring Nginx 
1. Install Nginx
```bash 
sudo apt-get -y install nginx 
```


2. Remove _default_ files 
```bash
sudo rm -rf /etc/nginx/sites-enabled/default 
sudo rm -rf /etc/nginx/sites-available/default 
```

3. Get IP of Kubernetes cluster   
```bash 
minikube ip
```

4. Create `/etc/nginx/sites-enabled/anylog.conf` file
```bash
sudo vim /etc/nginx/sites-enabled/anylog.conf
```


5. Update `/etc/nginx/sites-enabled/anylog.conf` file to support REST communication
```editorconfig
# nginx default webpage 
server {
  listen 80;
  server_name _;
}

# Grafana
server {
  listen 3000;
  server_name _;
  location / {
    proxy_set_header Host            $host;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_pass http://192.168.49.2:31000;
  }
}

# AnyLog Master REST 
server {
  listen 32049;
  server_name _;
  location / {
    proxy_set_header Host            $host;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_pass http://192.168.49.2:32049;
  }
}

# AnyLog Query REST 
server {
  listen 32349;
  server_name _;
  location / {
    proxy_set_header Host            $host;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_pass http://192.168.49.2:32349;
  }
}
...
```

6. Update `/etc/nginx/nginx.conf` to support TCP communication with AnyLog nodes 
```editorconfig
stream {
    # AnyLog Master TCP 
    upstream anylog_master {
        server 192.168.49.2:32048;
    }
    server {
        listen 32048 so_keepalive=on;
        proxy_pass anylog_master;
    }
    
    # AnyLog Query TCP 
    upstream anylog_query {
        server 192.168.49.2:32348;
    }
    server {
        listen 32348 so_keepalive=on;
        proxy_pass anylog_query;
    }
}
```

7. Restart _Nginx_ service 
```bash
sudo service nginx stop
sudo service nginx starts 
```

Once Nginx is configured the user can utilize the public IP to communicate with the K8s cluster outside the physical machine  