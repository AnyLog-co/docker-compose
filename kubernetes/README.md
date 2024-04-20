# Kubernetes 

## Requirements 
* [Kubernetes Cluster manager](https://kubernetes.io/docs/tasks/tools/) - we use Minikube with [HyperKit](https://minikube.sigs.k8s.io/docs/drivers/hyperkit/) / [HyperV](https://minikube.sigs.k8s.io/docs/drivers/hyperv/) driver 
* [helm](https://helm.sh/)
* [kubectl](https://kubernetes.io/docs/reference/kubectl/)
* Hardware Requirements - based on [official documentation](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#before-you-begin)

|   Requirements   | 
|:----------------:| 
| 2 GB or more RAM | 
|  2 or more CPUs  |
| Network connectivity between machines in cluster | 
| Unique hostname / MAC address for every physical node | 
| Disable swap on machine |  

## Deploying Kubernetes and Configuring Nginx   


## Deploy AnyLog 
1. Select preferred [configurations](configurations/) and update values in `node_configs`
```yaml
...
node_configs:
  general:
    # AnyLog License Key
    LICENSE_KEY: ad5722d6a5694693ff3fa12301208358e05145280702c747a8c8c827d8054675314a68eb07908acf083473e2a183b93a74a3cd88829a092ea4e5b0504ac056b7374211c27ab5d42421028950c00750a5795996e996c2939f725e885b7a2f807d616d32cd2b6a906d740002a11c353f5ddcbd78d4fc3c90ef40d45e8f44b3932f{'company':'Customer','expiration':'2024-07-04','type':'beta'}
    # Information regarding which AnyLog node configurations to enable. By default, even if everything is disabled, AnyLog starts TCP and REST connection protocols
    NODE_TYPE: master
    # Name of the AnyLog instance
    NODE_NAME: anylog-master
    # Owner of the Anylog instance
    COMPANY_NAME: New Company

  networking:
    # Port address used by AnyLog's TCP protocol to communicate with other nodes in the network
    ANYLOG_SERVER_PORT: 32048
    # Port address used by AnyLog's REST protocol
    ANYLOG_REST_PORT: 32049
    # Internal IP address of the machine the container is running on - if not set, then a unique IP will be used each time 
    OVERLAY_IP: 10.0.0.251 

  blockchain:
    # TCP connection information for Master Node
    LEDGER_CONN: 127.0.0.1:32048
```

2. Package AnyLog 
```shell 
helm package anylog-node
```

3. Deploy AnyLog 
```shell
helm install ./anylog-node-1.03.24.tgz -f configurations/anylog_master.yaml --name-template anylog-master 
```

4. Validate node is running 
```shell
AnyLog-Mac-mini ~ % kubectl get all 
NAME                                            READY   STATUS    RESTARTS   AGE
pod/anylog-master-deployment-7b4ff75fb7-mnsxf   1/1     Running   0          5m10s

NAME                            TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                           AGE
service/anylog-master-service   NodePort    10.108.209.76   <none>        32048:32048/TCP,32049:32049/TCP   5m10s
service/kubernetes              ClusterIP   10.96.0.1       <none>        443/TCP                           18h

NAME                                       READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/anylog-master-deployment   1/1     1            1           5m10s

NAME                                                  DESIRED   CURRENT   READY   AGE
replicaset.apps/anylog-master-deployment-7b4ff75fb7   1         1         1       5m10s
```

5. For each port  in service - set port-forwarding 
```shell
kubectl port-forward pod/anylog-master-deployment-7b4ff75fb7-hsd7n [SERVICE_PORT]:[SERVICE_PORT] --address [INTERNAL_MACHINE_IP]

# examples 
kubectl port-forward pod/anylog-master-deployment-7b4ff75fb7-hsd7n 32048:32048 --address 10.0.0.251
kubectl port-forward pod/anylog-master-deployment-7b4ff75fb7-hsd7n 32049:32049 --address 10.0.0.251
```

### Using Node
* Attach to AnyLog CLI   
```shell
# to detach ctrl-p-q
kubectl attach -it pod/anylog-master-deployment-7b4ff75fb7-mnsxf 
```

* Attach to exec of pod 
```shell
# to detach ctrl-p-q
kubectl exec -it pod/anylog-master-deployment-7b4ff75fb7-mnsxf -- /bin/bash  
```


