# Deploying AnyLog 

The following provides information on how to deploy AnyLog using either as _docker-compose_ or _kubernetes_. 

## Requirements 
* [docker-compose](docker-compose/docker_install.sh) - installment of docker & docker-compose  
* [kompose](https://kompose.io/installation/) - A conversion tool for Docker Compose to container orchestrators such as Kubernetes (or OpenShift).
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) - Kubernetes command line tool
* [minikube](https://minikube.sigs.k8s.io/docs/start/) - local Kubernetes, focusing on making it easy to learn and develop for Kubernetes.
* [helm](https://helm.sh/docs/intro/install/) - Helm is the package manager for Kubernetes

## Directory Structure
**Shell Scripts**   
* [install.sh](shell/install.sh) - code to install _docker_, _docker-compose_, _kompose_, _kubectl_ and _helm_
* [credentials.sh](shell/credentials.sh) - configure credentials for Kubernetes in order to download AnyLog 

**Docker Compose** 
* [AnyLog Node](docker-compose/anylog-node) - docker-compose file to install AnyLog-Node & Postgres (v.14.0-alpine) instance 
* [AnyLog Tools](docker-compose/anylog-tools) - docker-compose file to install AnyLog-GUI and our Remote-CLI
* [Grafana](docker-compose/grafana.sh) - shell script to [installing Grafana](https://grafana.com/docs/grafana/latest/installation/) 
via docker


## Deployments
* [Docker Compose](docker-compose/README.md)
* [Helm]()
* [Demo](demo.md)


## Support 
* [AnyLog Documentation](https://github.com/AnyLog-co/documentation) - documentation for AnyLog  
* [AnyLog API](https://github.com/AnyLog-co/AnyLog-API) - A python package to easily communicate with AnyLog via REST 