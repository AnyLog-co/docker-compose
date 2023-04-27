#!/bin/bash
<<COMMENT
The following code initiates a Python3 script that helps setup configurations for an AnyLog instance.
COMMENT

read -p "Node Type [default: generic | options: generic, master, operator, publisher, query, info]: " NODE_TYPE
while [[ ! ${NODE_TYPE}  == generic ]] && [[ ! ${NODE_TYPE}  == master ]] && [[ ! ${NODE_TYPE}  == operator ]] && [[ ! ${NODE_TYPE}  == publisher ]] && [[ ! ${NODE_TYPE}  == query ]] && [[ ! -z ${NODE_TYPE} ]] ;
do
  if [[ ${NODE_TYPE}  == info ]] ;
  then
    printf 'Node type options to deploy: '
#    printf '\n\none - an AnyLog instance with literally nothing configured'
    printf '\n\generic - sandbox for understanding AnyLog as only TCP & REST are configured'
    printf '\n\tmaster - a database node replacing an actual blockchain'
    printf '\n\toperator - node where data will be stored'
    printf '\n\tpublisher - node to distribute data among operators'
    printf '\n\tquery - node dedicated to master node (installed with Remote-CLI)\n'
#    printf "\n\tstandalone - node that consists of both master and operator deployment configurations"
#    printf "\n\tstandalone-publisher - node that consists of both master and publisher deployment configurations"
  fi

  read -p "Invalid node type '${NODE_TYPE}'. Node Type [default: generic | options: generic, master, operator, publisher, query, info]: " NODE_TYPE

done
if [[ -z ${NODE_TYPE} ]] ; then NODE_TYPE=generic ; fi


#read -p "Deployment Type [default: docker | options: docker, kubernetes]: " DEPLOYMENT_TYPE
#while [[ ! ${DEPLOYMENT_TYPE} == docker ]] && [[ ! ${DEPLOYMENT_TYPE} == kubernetes ]] && [[ ! -z ${DEPLOYMENT_TYPE} ]] ;
#do
#  read -p "Invalid deployment type '${DEPLOYMENT_TYPE}'. Deployment Type [default: docker | options: docker, kubernetes]: " DEPLOYMENT_TYPE
#done
if [[ -z ${DEPLOYMENT_TYPE} ]] ; then DEPLOYMENT_TYPE=docker ; fi

read -p "Deploy Existing Configs [y / n]: " EXISTING_CONFIGS
while [[ ! ${EXISTING_CONFIGS} == y ]] && [[ ! ${EXISTING_CONFIGS} == n ]] ;
do
  read -p "Invalid option: ${EXISTING_CONFIGS}. Deploy Existing Configs [y / n]: " EXISTING_CONFIGS
done


read -p "AnyLog Build Version [default: predevelop | options: develop, predevelop, test]: " BUILD_TYPE
while [[ ! ${BUILD_TYPE} == develop ]] && [[ ! ${BUILD_TYPE} == predevelop ]] && [[ ! ${BUILD_TYPE} == test ]]  && [[ ! -z ${BUILD_TYPE} ]] ;
do
  read -p "Invalid build type: ${BUILD_TYPE}. AnyLog Build Version [default: develop | options: develop, predevelop, test]: " BUILD_TYPE
done
if [[ -z ${BUILD_TYPE} ]] ; then BUILD_TYPE=predevelop ; fi
printf "\n"

# if user decides not to use existing configs, then ask questions to help fill-out the configurations.
if [[ ${EXISTING_CONFIGS} == n ]] ;
then
  python3 $HOME/deployments/deployment_scripts/main.py ${NODE_TYPE} \
    --build ${BUILD_TYPE} \
    --deployment-type ${DEPLOYMENT_TYPE}
elif [[ ${DEPLOYMENT_TYPE}  == docker ]] ;
then
    python3 $HOME/deployments/deployment_scripts/main.py ${NODE_TYPE} \
    --build ${BUILD_TYPE} \
    --deployment-type ${DEPLOYMENT_TYPE} \
    --config-file $HOME/deployments/docker-compose/anylog-${NODE_TYPE}/anylog_configs.env
elif [[ ${DEPLOYMENT_TYPE}  == kubernetes ]] ;
then
    python3 $HOME/deployments/deployment_scripts/main.py ${NODE_TYPE} \
    --build ${BUILD_TYPE} \
    --deployment-type ${DEPLOYMENT_TYPE} \
    --config-file $HOME/deployments/helm/sample-configurations/anylog_${NODE_TYPE}.yaml
fi

read -p  "Would you like to deploy AnyLog now (y/n)? " DEPLOY_NODE
while [[ ! ${DEPLOY_NODE} == y ]] && [[ ! ${DEPLOY_NODE} == n ]] ;
do
  read -p  "Would you like to deploy AnyLog now (y/n)? " DEPLOY_NODE
done

if [[ ${DEPLOY_NODE} == y ]] && [[ ${DEPLOYMENT_TYPE} == docker ]] && [[ ${NODE_TYPE} == query ]];
then
  read -p "Deploy Remote-CLI with Query Node (y/n)? " REMOTE_CLI
  while [[ ! ${REMOTE_CLI} == y ]] && [[ ! ${REMOTE_CLI} == n ]] ;
  do
    read -p "Deploy Remote-CLI with Query Node (y/n)? " REMOTE_CLI
  done
fi

if [[ ${DEPLOY_NODE} == y ]] && [[ ${DEPLOYMENT_TYPE} == docker ]] ;
then
  if [[ ${NODE_TYPE} == generic ]] ; then
    cd $HOME/deployments/docker-compose/anylog-rest
  elif [[ ${REMOTE_CLI} == y ]] ; then
    cp  $HOME/deployments/docker-compose/anylog-query/anylog_configs.env $HOME/deployments/docker-compose/anylog-query-remote-cli/anylog_configs.env
    cd $HOME/deployments/docker-compose/anylog-query-remote-cli/
  else
    cd $HOME/deployments/docker-compose/anylog-${NODE_TYPE}
  fi
  docker-compose up -d
fi
#elif [[ ${DEPLOY_NODE} == y ]] && [[ ${DEPLOYMENT_TYPE} == kubernetes ]] ;
#then
#   NODE_NAME=`grep "NODE_NAME: " deployments/helm/sample-configurations/anylog_${NODE_TYPE}.yaml | awk -F ": " '{print $2}' | awk '{$1=$1;print}'`
#   NODE_NAME=${NODE_NAME/ /-}
#
#   if [[ ${REMOTE_CLI} == y ]] ;
#   then
#      helm install $HOME/deployments/helm/packages/anylog-node-remote-cli-volume-1.22.3.tgz \
#        --name-template ${NODE_NAME}-cli-vol \
#        --values $HOME/deployments/helm/sample-configurations/anylog_${NODE_TYPE}.yaml
#
#      helm install $HOME/deployments/helm/packages/anylog-node-remote-cli-1.22.3.tgz \
#        --name-template ${NODE_NAME}-cli \
#        --values $HOME/deployments/helm/sample-configurations/anylog_${NODE_TYPE}.yaml
#  else
#      helm install $HOME/deployments/helm/packages/anylog-node-volume-1.22.3.tgz \
#        --name-template ${NODE_NAME}-vol \
#        --values $HOME/deployments/helm/sample-configurations/anylog_${NODE_TYPE}.yaml
#
#      helm install $HOME/deployments/helm/packages/anylog-node-1.22.3.tgz \
#        --name-template ${NODE_NAME} \
#        --values $HOME/deployments/helm/sample-configurations/anylog_${NODE_TYPE}.yaml
#  fi
#fi

