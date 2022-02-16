# Deploying AnyLog 
The following provides information on how to deploy AnyLog using either as _docker-compose_ or _kubernetes_. 

By default, both deployments deploy an AnyLog single-node with data coming in from a remote MQTT broker.

Configuration can be found in the [env](docker-compose/envs) for docker-compose and in the actual YAML files for kubernetes and helm deployments. 

## Requirements 
* [docker-compose](https://github.com/AnyLog-co/documentation/blob/master/Docker%20Compose%20&%20Kubernetes.md)
* [kompose](https://kompose.io/installation/) - A conversion tool for Docker Compose to container orchestrators such as Kubernetes (or OpenShift).
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) - Kubernetes command line tool
* [minikube](https://minikube.sigs.k8s.io/docs/start/) - local Kubernetes, focusing on making it easy to learn and develop for Kubernetes.

## Prepare Deployment
Clone the deployments directory  
```bash
cd $HOME
git clone https://github.com/AnyLog-co/deployments
cd $HOME/deployments 
```

## Docker Compose 
* Where to update deployment configurations [envs](docker-compose/envs/)
  * [AnyLog Network](docker-compose/envs/anylog_node.env) 
  * [AnyLog Tools](docker-compose/envs/anylog_tools.env) - Configuration for _AnyLog GUI_ and _Remote CLI_  
  * [Postgres](docker-compose/envs/postgres.env)
  * [Grafana](docker-compose/envs/grafana.env)
  
* How to start docker-compose
```bash
cd $HOME/deployments/docker-compose/ 
docker-compose up -d 
```

* cURL request against AnyLog-Network -- `anylog-node` service uses the `network_mode: host` rather than the network created by the network. As such, AnyLog uses the same IP(s) as the machine it seats on. 
```bash
curl -X GET ${YOUR_IP}:3481 -H "command: get status" -H "Usr-Agent: AnyLog/1.23"
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

## kubernetes / helm
* Configure Credentials
```bash
bash $HOME/docker-compose/credentials.sh ${YOUR_PASSWDRD}
```

* Deploy Packages
```bash
# To deploy with kubernetes 
kubectl apply -f $HOME/deployments/kube/

# To deploy with helm 
helm install --generate-name helm/anylogchart/
```

* Configure remote access for _Postgres_, _Grafana_, _AnyLog GUI_ and _Remote CLI_
```bash
bash $HOME/deployments/kube_port_access.sh ${LOCAL_IP}

# Verification
anylog@pc-ubuntu2004-k8:~/deployments$ ps fux 
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
anylog     74252  0.0  0.0  14056  5728 ?        S    00:18   0:01 sshd: anylog@pts/1
anylog     74253  0.0  0.0  10136  6992 pts/1    Ss   00:18   0:00  \_ -bash
anylog    104935  0.0  0.0   9260  3628 pts/1    R+   02:06   0:00      \_ ps fux
anylog      1417  0.0  0.0  14060  5716 ?        S    Feb15   0:01 sshd: anylog@pts/0
anylog      1418  0.0  0.0   8636  4532 pts/0    Ss+  Feb15   0:00  \_ -bash
anylog    104020  0.1  0.4 751316 38540 pts/1    Sl   02:01   0:00 kubectl port-forward --address 10.0.0.212 service/anylog-gui 5000:5000
anylog    104019  0.1  0.4 751060 38472 pts/1    Sl   02:01   0:00 kubectl port-forward --address 10.0.0.212 service/remote-cli 8000:8000
anylog    104018  0.1  0.4 751316 39624 pts/1    Sl   02:01   0:00 kubectl port-forward --address 10.0.0.212 service/grafana 3000:3000
anylog    104017  0.1  0.4 751316 39212 pts/1    Sl   02:01   0:00 kubectl port-forward --address 10.0.0.212 service/postgres 5432:5432
anylog      1297  0.0  0.1  18648  9864 ?        Ss   Feb15   0:02 /lib/systemd/systemd --user
anylog      1302  0.0  0.0 168876  3488 ?        S    Feb15   0:00  \_ (sd-pam)
```

* Configure Remote Access to AnyLog Node
  1.  Edit the service anylog-node and change the type from _ClusterIP_ to _NodePort_ save and exit.
```bash
kubectl edit service anylog-node
``` 

```json
# Before
apiVersion: v1
kind: Service
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","kind":"Service","metadata":{"annotations":{},"labels":{"app":"anylog-node"},"name":"anylog-node","namespace":"default"},"spec":{"ports":[{"name":"anylog-node-tcp","port":32048},{"name":"anylog-node-rest","port":32049},{"name":"anylog-node-broker","port":32050}],"selector":{"app":"anylog-node"}}}
  creationTimestamp: "2022-02-16T01:57:30Z"
  labels:
    app: anylog-node
  name: anylog-node
  namespace: default
  resourceVersion: "746"
  uid: 9453d895-7edc-49bb-a350-4568333be0ef
spec:
  clusterIP: 10.97.103.16
  clusterIPs:
  - 10.97.103.16
  internalTrafficPolicy: Cluster
  ipFamilies:
  - IPv4
  ipFamilyPolicy: SingleStack
  ports:
  - name: anylog-node-tcp
    port: 32048
    protocol: TCP
    targetPort: 32048
  - name: anylog-node-rest
    port: 32049
    protocol: TCP
    targetPort: 32049
  - name: anylog-node-broker
    port: 32050
    protocol: TCP
    targetPort: 32050
  selector:
    app: anylog-node
  sessionAffinity: None
  type: ClusterIP
status:
  loadBalancer: {}

# After 
apiVersion: v1
kind: Service
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","kind":"Service","metadata":{"annotations":{},"labels":{"app":"anylog-node"},"name":"anylog-node","namespace":"default"},"spec":{"ports":[{"name":"anylog-node-tcp","port":32048},{"name":"anylog-node-rest","port":32049},{"name":"anylog-node-broker","port":32050}],"selector":{"app":"anylog-node"}}}
  creationTimestamp: "2022-02-16T01:57:30Z"
  labels:
    app: anylog-node
  name: anylog-node
  namespace: default
  resourceVersion: "746"
  uid: 9453d895-7edc-49bb-a350-4568333be0ef
spec:
  clusterIP: 10.97.103.16
  clusterIPs:
  - 10.97.103.16
  internalTrafficPolicy: Cluster
  ipFamilies:
  - IPv4
  ipFamilyPolicy: SingleStack
  ports:
  - name: anylog-node-tcp
    port: 32048
    protocol: TCP
    targetPort: 32048
  - name: anylog-node-rest
    port: 32049
    protocol: TCP
    targetPort: 32049
  - name: anylog-node-broker
    port: 32050
    protocol: TCP
    targetPort: 32050
  selector:
    app: anylog-node
  sessionAffinity: None
  type: NodePort
status:
  loadBalancer: {}
```

  2. Get the external service URL to make a REST Call
```bash
anylog@pc-ubuntu2004-k8:~/deployments$ minikube service --url anylog-node
http://192.168.49.2:31900
http://192.168.49.2:31864
http://192.168.49.2:30260

# check 
curl -X GET 192.168.49.2:31864 -H "command: get status" -H "User-Agent: AnyLog/1.23"  -w "\n"
anylog-node@24.23.250.144:32048 running
```
**Note** - A node outside the kubernetes cluster will use the new IP and Ports

* Attach to bash 
```bash
kubectl exec -it pod/${POD_NAME} -- bash
```

* To Stop
```bash
kubectl delete -f $HOME/deployments/kube/
```