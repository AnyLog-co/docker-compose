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


## Deploy AnyLog
0. Validate connectivity between machines in the network 

1. Select preferred [configurations](configurations/) and update values in `node_configs`
```yaml
...
node_configs:
  general:
    # AnyLog License Key
    LICENSE_KEY: ""
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
    OVERLAY_IP: "" 

  blockchain:
    # TCP connection information for Master Node
    LEDGER_CONN: 127.0.0.1:32048
```

2. Deploy AnyLog using [deploy_node.sh](deploy_node.sh)
* package AnyLog instance 
```shell
bash deploy_node.sh package
```

* Start AnyLog based on configuration file - this will also start the volumes and enable port-forwarding against the node  
```shell
bash deploy_node. start configurations/${CONFIG_FILE} ${INTERNAL_IP_ADDRESS}
```

* Stop AnyLog instance and corresponding port-forwarding, it will not remove volumes 
```shell
bash deploy_node. stop configurations/${CONFIG_FILE} 
```

### Using Node
* Attach to AnyLog CLI   
```shell
# to detach ctrl-p-q
kubectl attach -it pod/anylog-master-deployment-7b4ff75fb7-mnsxf 
```

* Attach to the shell interface of the node  
```shell
# to detach ctrl-p-q
kubectl exec -it pod/anylog-master-deployment-7b4ff75fb7-mnsxf -- /bin/bash  
```

## Networking and Volume management 


