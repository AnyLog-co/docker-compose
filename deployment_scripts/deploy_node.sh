#!/bin/bash

# The following script is used to help configure & deploy a node

read -p "Single Node Docker Install [y/N]: " SINGLE_NODE
while [[ ! `echo ${SINGLE_NODE} | tr '[:upper:]' '[:lower:]'` == y ]] && [[ ! `echo ${SINGLE_NODE} | tr '[:upper:]' '[:lower:]'` == n ]] ;
do
  read -p "Invalid Input '${SINGLE_NODE}'. Single Node Docker Install [y/N]: " SINGLE_NODE
done


if [[ `echo ${SINGLE_NODE} | tr '[:upper:]' '[:lower:]'` == y ]] ;
then
  read -p "Node Type [default: rest | options: rest, master, operator, publisher, query]: " NODE_TYPE
  while [[ ! ${NODE_TYPE}  == rest ]] && [[ ! ${NODE_TYPE}  == master ]] && [[ ! ${NODE_TYPE}  == operator ]] && [[ ! ${NODE_TYPE}  == publisher ]] && [[ ! ${NODE_TYPE}  == query ]] && [[ ! -z ${NODE_TYPE} ]] ;
  do
    read -p "Invalid node type '${NODE_TYPE}'. Node Type [default: rest | options: rest, master, operator, publisher, query]: " NODE_TYPE
  done
  if [[ -z ${NODE_TYPE} ]] ;
  then
    NODE_TYPE=rest
  fi

  read -p "Deployment Type [options: docker, kubernetes, standalone]: " DEPLOYMENT_TYPE
  while [[ ! ${DEPLOYMENT_TYPE} == docker ]] && [[ ! ${DEPLOYMENT_TYPE} == kubernetes ]]  && [[ ! ${DEPLOYMENT_TYPE} == standalone ]];
  do
    read -p "Invalid Option '${DEPLOYMENT_TYPE}'. Deployment Type [options: docker, kubernetes]: " DEPLOYMENT_TYPE
  done
else
  DEPLOYMENT_TYPE=docker
  NODE_TYPE=demo
fi

python3 questions.py ${NODE_TYPE} --deployment-type ${DEPLOYMENT_TYPE}