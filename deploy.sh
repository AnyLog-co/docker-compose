#!/bin/bash
if [[ $# -eq 2 ]]
then
  DOCKER_PASSWORD=${1}
  DEPLOYMENT_TYPE=${2}
else
  echo "Missing: docker password & deployment type"
  exit 1
fi

if [[ ! ${DEPLOYMENT_TYPE} == docker ]] && [[ ! ${DEPLOYMENT_TYPE} == helm ]] && [[ ! ${DEPLOYMENT_TYPE} == k8s ]] && [[ ! ${DEPLOYMENT_TYPE} == kubernetes ]]
then
  printf "Invalid Option ${DEPLOYMENT_TYPE}. Options: \n\t- docker\n\t- helm\n\t- kubernetes or k8s\n"
  exit 1
elif
fi

#cd $HOME/deployments/
#
## expose AnyLog ports
#export ANYLOG_SERVER_PORT=32048
#export ANYLOG_REST_PORT=32049
#export ANYLOG_BROKER_PORT=32050
#export GUI_PORT=5000
#export CLI_PORT=8000
#
## deploy docker
#if [[ ${DEPLOYMENT_TYPE} == "docker" ]]
#then
#  # login to docker
#  docker login -u oshadmon -p ${DOCKER_PASSWORD}
#  cd docker-compose
#  docker-compse up -d
#  cd ..
#fi
#
#
