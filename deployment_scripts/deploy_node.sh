#!/bin/bash

# The following script is used to help configure & deploy a node
read -p "Node Type [default: rest | options: rest, master, operator, publisher, query, info]: " NODE_TYPE
while [[ ! ${NODE_TYPE}  == rest ]] && [[ ! ${NODE_TYPE}  == master ]] && [[ ! ${NODE_TYPE}  == operator ]] && [[ ! ${NODE_TYPE}  == publisher ]] && [[ ! ${NODE_TYPE}  == query ]] && [[ ! -z ${NODE_TYPE} ]] ;
do
  if [[ ${NODE_TYPE}  == info ]] ;
  then
    printf 'Node type options to deploy: '
    printf '\n\trest - sandbox for understanding AnyLog as only TCP & REST are configured'
    printf '\n\tmaster - a database node replacing an actual blockchain'
    printf '\n\toperator - node where data will be stored'
    printf '\n\tpublisher - node to distribute data among operators'
    printf '\n\tquery - node dedicated to master node\n'
    read -p "Node Type [default: rest | options: rest, master, operator, publisher, query, info]: " NODE_TYPE
  else
    read -p "Invalid node type '${NODE_TYPE}'. Node Type [default: rest | options: rest, master, operator, publisher, query, info]: " NODE_TYPE
  fi
done
if [[ -z ${NODE_TYPE} ]] ;
then
  NODE_TYPE=rest
fi

python3 $HOME/deployments/deployment_scripts/configuration/docker_deployment.py ${NODE_TYPE}