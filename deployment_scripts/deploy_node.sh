#!/bin/bash

# The following script is used to help configure & deploy a node

read -p "Node Type [default: rest | options: rest, master, operator, publisher, query]: " NODE_TYPE
while [[ ! ${NODE_TYPE}  == rest ]] && [[ ! ${NODE_TYPE}  == master ]] && [[ ! ${NODE_TYPE}  == operator ]] && [[ ! ${NODE_TYPE}  == publisher ]] && [[ ! ${NODE_TYPE}  == query ]] && [[ ! -z ${NODE_TYPE} ]] ;
do
  printf "Invalid node type '${NODE_TYPE}'. Node Type [default: rest | options: rest, master, operator, publisher, query]: " NODE_TYPE
done
if [[ -z ${NODE_TYPE} ]] ;
then
  NODE_TYPE=rest
fi

read -p "Deployment Type [options: docker, kubernetes]: " DEPLOYMENT_TYPE
while [[ ! ${DEPLOYMENT_TYPE} == docker ]] && [[ ! ${DEPLOYMENT_TYPE} == kubernetes ]] ;
do
  read -p "Invalid Option '${DEPLOYMENT_TYPE}'. Deployment Type [options: docker, kubernetes]: " DEPLOYMENT_TYPE
done

python3 questions.py ${NODE_TYPE} ${DEPLOYMENT_TYPE}