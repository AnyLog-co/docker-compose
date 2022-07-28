#!/bin/bash

# The following provides support for installing prerequisites for AnyLog
# --> Docker or Kubernetes (using minikube & helm)
# --> Docker login registrations

read -p "AnyLog Docker Credentials: " DOCKER_PASSWORD
if [[ ! ${DOCKER_PASSWORD} ]] ;
then
  printf "Please emails us at info@anylog.co for your Docker credentials\n"
  exit 1
fi

read -p "Deployment Type [options: docker, kubernetes]: " DEPLOYMENT_TYPE
while [[ ! ${DEPLOYMENT_TYPE} == docker ]] && [[ ! ${DEPLOYMENT_TYPE} == kubernetes ]] ;
do
  read -p "Invalid Option '${DEPLOYMENT_TYPE}'. Deployment Type [options: docker, kubernetes]: " DEPLOYMENT_TYPE
done

if [[ ${DEPLOYMENT_TYPE} == docker ]] ;
then
  bash installations/docker_install.sh
  bash installations/docker_credentials.sh ${DOCKER_PASSWORD}
elif [[ ${DEPLOYMENT_TYPE} == kubernetes ]] ;
then
  bash installations/kube_install.sh
  bash installations/kube_credentials.sh ${DOCKER_PASSWORD}
fi

