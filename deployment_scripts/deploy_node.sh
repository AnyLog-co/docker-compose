#!/bin/bash
<<COMMENT
The following code initiates a Python3 script that helps setup configurations for an AnyLog instance.
COMMENT

# Function to display node type options
function display_node_type_options() {
  printf 'Node type options to deploy:'
  printf '\n\tgeneric - sandbox for understanding AnyLog as only TCP & REST are configured'
  printf '\n\tmaster - a database node replacing an actual blockchain'
  printf '\n\toperator - node where data will be stored'
  printf '\n\tpublisher - node to distribute data among operators'
  printf '\n\tquery - node dedicated to master node (installed with Remote-CLI)'
  printf '\n\tinfo - display node type options\n'
}

# Function to validate yes/no options
function validate_yes_no_option() {
  local input
  read -p "$1: " input
  while [[ ! ${input} =~ ^(y|n)$ ]]; do
    read -p "Invalid option: ${input}. $1: " input
  done
  echo "${input}"
}

read -p "Node Type [default: generic | options: generic, master, operator, publisher, query, info]: " NODE_TYPE
if [[ -z ${NODE_TYPE} ]] ; then NODE_TYPE=generic ; fi
while [[ ! ${NODE_TYPE} =~ ^(generic|master|operator|publisher|query)$ ]] && [[ ! -z ${NODE_TYPE} ]]; do
  if [[ ${NODE_TYPE} == info ]]; then
    display_node_type_options
    NODE_TYPE=""
    read -p "Node Type [default: generic | options: generic, master, operator, publisher, query, info]: " NODE_TYPE
  elif [[ -z ${NODE_TYPE} ]]
  then
    NODE_TYPE=generic
  else
    read -p "Invalid node type '${NODE_TYPE}'. Node Type [default: generic | options: generic, master, operator, publisher, query, info]: " NODE_TYPE
  fi
done

read -p "Deployment Type [default: docker | options: docker, kubernetes]: " DEPLOYMENT_TYPE

while [[ ! ${DEPLOYMENT_TYPE} =~ ^(docker|kubernetes)$ ]] || [[ -z ${DEPLOYMENT_TYPE} ]]; do
  if [[ -z ${DEPLOYMENT_TYPE} ]]; then
    DEPLOYMENT_TYPE=docker
  else
    read -p "Invalid deployment type '${DEPLOYMENT_TYPE}'. Deployment Type [default: docker | options: docker, kubernetes]: " DEPLOYMENT_TYPE
  fi
done

EXISTING_CONFIGS=$(validate_yes_no_option "Deploy Existing Configs [y/n]")

read -p "AnyLog Build Version [default: latest | options: latest, predevelop, test]: " BUILD_TYPE
# Loop until a valid build type is provided
while [[ ! ${BUILD_TYPE} =~ ^(latest|predevelop|test)$ ]] || [[ -z ${BUILD_TYPE} ]]; do
  # Set a default value if input is empty
  if [[ -z ${BUILD_TYPE} ]]; then
    BUILD_TYPE=latest
  else
    read -p "Invalid build type: ${BUILD_TYPE}. AnyLog Build Version [default: latest | options: latest, predevelop, test]: " BUILD_TYPE
  fi
done

DEMO_BUILD=$(validate_yes_no_option "Demo Deployment [y/n]")

printf "\n"
# If user decides not to use existing configs, then ask questions to help fill out the configurations.
if [[ ${EXISTING_CONFIGS} == n ]] && [[ ${DEMO_BUILD} == y ]]; then
  python3 $HOME/deployments/deployment_scripts/main.py ${NODE_TYPE} \
    --build ${BUILD_TYPE} \
    --deployment-type ${DEPLOYMENT_TYPE} \
    --demo-build
elif [[ ${EXISTING_CONFIGS} == n ]] && [[ ${DEMO_BUILD} == n ]]; then
  python3 $HOME/deployments/deployment_scripts/main.py ${NODE_TYPE} \
    --build ${BUILD_TYPE} \
    --deployment-type ${DEPLOYMENT_TYPE}
elif [[ ${DEPLOYMENT_TYPE} == docker ]] && [[ ${DEMO_BUILD} == y ]]; then
  python3 $HOME/deployments/deployment_scripts/main.py ${NODE_TYPE} \
    --build ${BUILD_TYPE} \
    --deployment-type ${DEPLOYMENT_TYPE} \
    --config-file $HOME/deployments/docker-compose/anylog-${NODE_TYPE}/anylog_configs.env \
    --demo-build
elif [[ ${DEPLOYMENT_TYPE} == docker ]] && [[ ${DEMO_BUILD} == n ]]; then
  python3 $HOME/deployments/deployment_scripts/main.py ${NODE_TYPE} \
    --build ${BUILD_TYPE} \
    --deployment-type ${DEPLOYMENT_TYPE} \
    --config-file $HOME/deployments/docker-compose/anylog-${NODE_TYPE}/anylog_configs.env
elif [[ ${DEPLOYMENT_TYPE} == kubernetes ]] && [[ ${DEMO_BUILD} == y ]]; then
  python3 $HOME/deployments/deployment_scripts/main.py ${NODE_TYPE} \
    --build ${BUILD_TYPE} \
    --deployment-type ${DEPLOYMENT_TYPE} \
    --config-file $HOME/deployments/helm/sample-configurations/anylog_${NODE_TYPE}.yaml \
    --demo-build
elif [[ ${DEPLOYMENT_TYPE} == kubernetes ]] && [[ ${DEMO_BUILD} == n ]]; then
  python3 $HOME/deployments/deployment_scripts/main.py ${NODE_TYPE} \
    --build ${BUILD_TYPE} \
    --deployment-type ${DEPLOYMENT_TYPE} \
    --config-file $HOME/deployments/helm/sample-configurations/anylog_${NODE_TYPE}.yaml
fi

if [[ ${NODE_TYPE} == query ]]; then
  REMOTE_CLI=$(validate_yes_no_option "Deploy Remote-CLI with Query Node (y/n)?")
  if [[ ${REMOTE_CLI} == y ]] && [[ ${DEPLOYMENT_TYPE} == docker ]]; then
    cp $HOME/deployments/docker-compose/anylog-query/anylog_configs.env $HOME/deployments/docker-compose/anylog-query-remote-cli/anylog_configs.env
    sed -i "s/BUILD=.*/BUILD=${BUILD}/g" $HOME/deployments/docker-compose/anylog-query-remote-cli/.env
  elif [[ ${REMOTE_CLI} == y ]] && [[ ${DEPLOYMENT_TYPE} == kubernetes ]]; then
    if [[ $(uname) == "Darwin" ]]; then
      sed -i '' 's/remote_cli false/remote_cli true/' "$HOME/deployments/helm/sample-configurations/anylog_${NODE_TYPE}.yaml"
    elif [[ "$(expr substr $(uname -s) 1 5)" == "Linux" ]]; then
      sed -i 's/remote_cli false/remote_cli true/' "$HOME/deployments/helm/sample-configurations/anylog_${NODE_TYPE}.yaml"
    fi
  fi
fi

DEPLOY_NODE=$(validate_yes_no_option "Would you like to deploy AnyLog now (y/n)?")

if [[ ${DEPLOY_NODE} == y ]]; then
  if [[ ${DEPLOYMENT_TYPE} == docker ]]; then
    cd $HOME/deployments/docker-compose/anylog-${NODE_TYPE}
    if [[ ${REMOTE_CLI} == y ]]; then
      cd $HOME/deployments/docker-compose/anylog-query-remote-cli/
    fi
    docker-compose up -d
  elif [[ ${DEPLOYMENT_TYPE} == kubernetes ]]; then
    if [[ ${REMOTE_CLI} == y ]]; then
      helm install $HOME/deployments/helm/packages/remote-cli-volume-1.0.0.tgz -f $HOME/deployments/helm/sample-configurations/remote_cli.yaml --generate-name
      helm install $HOME/deployments/helm/packages/remote-cli-1.0.0.tgz -f $HOME/deployments/helm/sample-configurations/remote_cli.yaml --generate-name
    fi
    helm install $HOME/deployments/helm/packages/anylog-node-volume-1.22.3.tgz -f $HOME/deployments/helm/sample-configurations/anylog_${NODE_TYPE}.yaml --generate-name
    helm install $HOME/deployments/helm/packages/anylog-node-1.22.3.tgz -f $HOME/deployments/helm/sample-configurations/anylog_${NODE_TYPE}.yaml --generate-name
  fi
fi
