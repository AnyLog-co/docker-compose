# Deploying AnyLog 

The following provides information on how to deploy AnyLog using either as _docker-compose_ or _kubernetes_. 

## Requirements  
* docker / docker-compose 
* kompose
* kubectl
* minikube 
* helm

## Directory Structure
**Docker Compose** 
* [docker-compose](docker-compose/docker_install.sh) - installation of docker & docker-compose
* [AnyLog Node](docker-compose/anylog-node) - docker-compose file to install AnyLog-Node & Postgres (v.14.0-alpine) instance 
* [AnyLog Tools](docker-compose/anylog-tools) - docker-compose file to install AnyLog-GUI and our Remote-CLI
* [Postgres](docker-compose/postgres.sh) - shell script to install [PostgreSQL](https://www.postgresql.org/)
* [Grafana](docker-compose/grafana.sh) - shell script to [installing Grafana](https://grafana.com/docs/grafana/latest/installation/) 
via docker

**Kubernetes Deployment**
* [install.sh](helm/install.sh) - script to install _kompose_, _kubectl_, _minikube_ and _helm_
* [credentials.sh](helm/credentials.sh) - configure credentials for Kubernetes in order to download AnyLog 


## Deployments
* [Docker Compose](docker-compose/README.md)
* [Helm](helm/README.md)
* [Demo](demo.md)


## Support 
* [AnyLog Documentation](https://github.com/AnyLog-co/documentation) - documentation for AnyLog  
* [AnyLog API](https://github.com/AnyLog-co/AnyLog-API) - A python package to easily communicate with AnyLog via REST 