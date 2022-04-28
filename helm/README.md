# Deploy AnyLog using Kubernetes 

The following provides details in regard to deploying AnyLog Node, and it's corresponding tools, via Kubernetes 
(helm-charts).

## Requirement
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) - Kubernetes command line tool
* [minikube](https://minikube.sigs.k8s.io/docs/start/) - local Kubernetes, focusing on making it easy to learn and develop for 
  Kubernetes. Alternativly a user ccan use something else; such as: _kubeadm_, _MicroK8s_, _K3s_    
* [helm-charts](https://helm.sh/docs/intro/quickstart/) - Kubernetes package manager 
* [nginx](https://nginx.org/en/) - web server used as a reverse proxy

## Steps
1. [Install Kubernetes](kube_install.sh)
   * _kubectl_
   * _minikube_
   * _helm-charts_ 


2. Install Nginx 
```bash 
sudo apt-get -y install nginx 
```

3. Either Clone 