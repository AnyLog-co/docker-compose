1. create dir config.sh and include the following: 
```bash
DOCKER_REGISTRY_SERVER=docker.io
DOCKER_USER=oshadmon
DOCKER_EMAIL=ori@anylog.co
DOCKER_PASSWORD=**********
kubectl create secret docker-registry myregistrykey \
  --docker-server=$DOCKER_REGISTRY_SERVER \
  --docker-username=$DOCKER_USER \
  --docker-password=$DOCKER_PASSWORD \
  --docker-email=$DOCKER_EMAIL
```

2. Deploy config.sh 

3. convert docker-compose for k8 

4. in anylog-node-deployment.yml add `imagePullSecrets` as shown: 
```
    spec:
      imagePullSecrets:
        - name: myregistrykey
      containers:
        - env:
...
```

5. deploy k8 

6. [kube_port_access.sh](kube_port_access.sh) 

