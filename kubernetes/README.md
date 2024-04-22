# AnyLog Deployment using Kubernetes 

## Overview
This doc deploys AnyLog instance using Minikube, and Helm. 
The deployment includes a configuration file, copied to a persistent volume, that can be modified in the same Pod to determine the services enabled.    
For a customer deployment, it is recommended to predefine the services for each Pod.

## Table of Content

* [Requirements](#requirements)
* [Deploying AnyLog](#deploy-anylog)
    * [Validate Connectivity](#using-node)
* [Network & Volume Configuration](#networking-and-volume-management)

## Requirements
* [Kubernetes Cluster manager](https://kubernetes.io/docs/tasks/tools/) - deploy Minikube with [Docker](https://minikube.sigs.k8s.io/docs/drivers/docker/) 
* [helm](https://helm.sh/)
* [kubectl](https://kubernetes.io/docs/reference/kubectl/)
* Hardware Requirements - based on [official documentation](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#before-you-begin)

|   Requirements   | 
|:----------------:| 
| 2 GB or more RAM | 
| 2 or more CPUs  |
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

* [Start AnyLog](deploy_node.sh) based on configuration file - this will also start the volumes and enable port-forwarding against the node  
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

### Networking 

AnyLog uses [dynamic ClusterIP](https://kubernetes.io/docs/concepts/services-networking/cluster-ip-allocation/) as it's 
preferred setup. This means a unique IP address is automatically assigned to the services as they are created and ensures 
load balancing across the pods in the service.

#### Configuring the network services on the AnyLog node

Since dynamic ClusterIP generates a new IP whenever a pod is deployed, this causes a issue with AnyLog's metadata 
(hosted in a blockchain or a master node) as each new IP will generate a new policy.  
To resolve this issue, and avoid policy updates, specify the host's internal IP as the `OVERLAY_IP` value. 

The following chart summarizes the setup:

|   Connection Type    | External IP | Internal IP |    Config Command    | 
|:--------------------:| :---: | :---: |:--------------------:| 
|         TCP          | External IP | Overlay IP |   `run tcp server`   | 
|         REST         | External IP | Overlay IP |   `run REST server`  |
| Message Broker (TCP) | External IP | Overlay IP | `run message broker` |

Additional information on the network configuration are in the [networking section](https://github.com/AnyLog-co/documentation/blob/master/network%20configuration.md).

#### Enable P2P messaging between the AnyLog Nodes 

The second part is in AnyLog's networking configuration is the need for nodes to communicate between one another; to 
accomplish this recommend using [port-forwarding](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_port-forward/).

The process fpr port-forwarding is configured to run automatically as part of [deploy_node.sh](deploy_node.sh). 

**Note**: When using Kubernetes, makes sure ports are open and accessible across your network.   

### Volume

The base deployment has the same general volumes as a docker deployment, and uses [PersistentVolumeClaim](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) - _data_, _blockchain_, _anylog_ and _local-scripts (deployments)_.

While _data_, _blockchain_ and _anylog_ are autogenerated and populated, _local-scripts_ gets downloaded as part of the 
container image. Therefore, we utilize an `if/else` process to make this data persistent. 

Note: we copy the scripts to a persitsnt volume that is created after the initialization of the Pod.

```shell
if [[ -d $ANYLOG_PATH/deployment-scripts ]] && [[ -z $(ls -A $ANYLOG_PATH/deployment-scripts) ]]; then # if directory exists but empty
  git clone -b os-dev https://github.com/AnyLog-co/deployment-scripts deployment-scripts-tmp
  mv deployment-scripts-tmp/* deployment-scripts
  rm -rf deployment-scripts-tmp
elif [[ ! -d $ANYLOG_PATH/deployment-scripts ]] ; then  # if directory DNE
  git clone -b os-dev https://github.com/AnyLog-co/deployment-scripts
fi
```

Once a node is up and running, users can change content in _local-scripts_ using `kubectl exec ${POD_NAME} -- /bin/bash`.

Volumes are deployed automatically as part of [deploy_node.sh](deploy_node.sh), and remain persistent as long as PersistentVolumeClaims
are not removed. 




