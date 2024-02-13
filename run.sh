#!/bin/bash

# Start / Stop Docker such that AnyLog connects to specific ports, as opposed to using a generic bridge connection
# Sample Calls:
#  - help: bash run.sh help
#  - Start: bash run.sh helm NODETYPE up || bash run.sh docker NODETYPE up [--training]
#  - Stop: bash run.sh helm {NODETYPE} down [--volume] || bash run.sh docker {NODETYPE} down [--training] [--volume] [--rmi]

DEPLOYMENT_TYPE=$1
NODETYPE=$2
DOCKERCMD=$3
VOLUME=false
IMAGE=false
TRAINING=false


if [[ ${DEPLOYMENT_TYPE} == help ]] ; then
  printf """Start / Stop Docker such that AnyLog connects to specific ports, as opposed to using a generic bridge connection
  Sample Calls:
  \t- Start: bash run.sh NODETYPE up [--training]
  \t- Stop:  bash run.sh NODETYPE down [--training] [--volume] [--rmi]
  """
  exit 0
fi
ROOT_PATH=$(dirname $(readlink -f "$0"))

if [[ ${DOCKERCMD} == down ]] ; then
  while [[ $# -gt 0 ]] ; do
    case $1 in
      "--volume")
        VOLUME=true
        ;;
      "--rmi")
        IMAGE=true
        ;;
      "--training")
        TRAINING=true
        ;;
      *)
        ;;
    esac
    shift
  done
fi


if [[ ${DEPLOYMENT_TYPE} == docker ]] ; then
  if [[ ${TRAINING} == true ]] ; then
    if [[ ${NODETYPE} == master ]] || [[ ${NODETYPE} == operator ]] || [[ ${NODETYPE} == query ]] ; then
      cd ${ROOT_PATH}/training/anylog-${NODETYPE} || (echo "Failed to cd into anylog-${NODETYPE} dir" && exit 1)
    else
      echo "Invalid deployment type: ${NODETYPE}"
      exit 1
    fi
  elif [[ ${NODETYPE} == master ]] || [[ ${NODETYPE} == operator ]] || [[ ${NODETYPE} == query ]]  || [[ ${NODETYPE} == publisher ]] || [[ ${NODETYPE} == query-remote-cli ]] ; then
    cd ${ROOT_PATH}/docker-compose/anylog-${NODETYPE} || (echo "Failed to cd into anylog-${NODETYPE} dir" && exit 1)
  else
    echo "Invalid deployment type: ${NODETYPE}"
    exit 1
  fi

  export ANYLOG_PATH=$(cat advance_configs.env | grep ANYLOG_PATH | awk -F "=" '{print $2}')
  export NEBULA_CONFIG_FILE=$(cat advance_configs.env | grep NEBULA_CONFIG_FILE | awk -F "=" '{print $2}')
  export ANYLOG_SERVER_PORT=$(cat anylog_configs.env | grep "ANYLOG_SERVER_PORT" | awk -F "=" '{print $2}')
  export ANYLOG_REST_PORT=$(cat anylog_configs.env | grep "ANYLOG_REST_PORT" |  awk -F "=" '{print $2}')
  export ANYLOG_BROKER_PORT=""

  if [[ ${TRAINING} == false ]] && [[ ! $(grep "ANYLOG_BROKER_PORT" advance_configs.env |  awk -F "=" '{print $2}')   = '""' ]] ; then # if ANYLOG_BROKER_PORT exists
    export ANYLOG_BROKER_PORT=$(cat anylog_configs.env | grep "ANYLOG_BROKER_PORT" | awk -F "=" '{print $2}')
  fi

  if [[ ${DOCKERCMD} == up ]] ; then
    if [[ ! -z ${ANYLOG_BROKER_PORT} ]] ; then # if ANYLOG_BROKER_PORT exists
      docker-compose -f docker-compose-broker.yml up -d
    else
      docker-compose up -d
    fi
  elif [[ ${DOCKERCMD} == down ]] ; then
    if [[ ${VOLUME} == true ]] && [[ ${IMAGE} == true ]] ; then
      if [[ ! -z ${ANYLOG_BROKER_PORT} ]] ; then # if ANYLOG_BROKER_PORT exists
      docker-compose -f docker-compose-broker.yml down -v --rmi all
      else
        docker-compose down -v --rmi all
      fi
    elif [[ ${VOLUME} == true ]] && [[ ${IMAGE} == false ]] ; then
      if [[ ! -z ${ANYLOG_BROKER_PORT} ]] ; then # if ANYLOG_BROKER_PORT exists
      docker-compose -f docker-compose-broker.yml down -v
      else
        docker-compose down -v
      fi
    elif [[ ${VOLUME} == false ]] && [[ ${IMAGE} == true ]] ; then
      if [[ ! -z ${ANYLOG_BROKER_PORT} ]] ; then # if ANYLOG_BROKER_PORT exists
      docker-compose -f docker-compose-broker.yml down --rmi all
      else
        docker-compose down --rmi all
      fi
    else
      if [[ ! -z ${ANYLOG_BROKER_PORT} ]] ; then # if ANYLOG_BROKER_PORT exists
        docker-compose -f docker-compose-broker.yml down
      else
        docker-compose down
      fi
    fi
  else
    echo Invalid Userinput ${DOCKERCMD}
    exit 1
  fi
elif [[ ${DEPLOYMENT_TYPE} == helm ]] ; then
  export NODE_NAME=$(grep "pod_name" ${ROOT_PATH}/kubernetes/configs/anylog_${NODETYPE}.yaml | awk -F ":" '{print $2}')
  export ANYLOG_SERVER_PORT=$(cat ${ROOT_PATH}/kubernetes/configs/anylog_${NODETYPE}.yaml | grep "ANYLOG_SERVER_PORT" | awk -F ":" '{print $2}')
  export ANYLOG_REST_PORT=$(cat ${ROOT_PATH}/kubernetes/configs/anylog_${NODETYPE}.yaml | grep "ANYLOG_REST_PORT" |  awk -F ":" '{print $2}')

  export PROXY_IP=$(cat ${ROOT_PATH}/kubernetes/configs/anylog_${NODETYPE}.yaml | grep "PROXY_IP" |  awk -F ":" '{print $2}')
  export SERVICE_NAME=$(cat ${ROOT_PATH}/kubernetes/configs/anylog_${NODETYPE}.yaml | grep "service_name" |  awk -F ":" '{print $2}')

  export ANYLOG_BROKER_PORT=""
  if [[ ! $(grep "ANYLOG_BROKER_PORT" ${ROOT_PATH}/kubernetes/configs/anylog_${NODETYPE}.yaml |  awk -F ":" '{print $2}')   = '""' ]] ; then
    export ANYLOG_BROKER_PORT=$(cat ${ROOT_PATH}/kubernetes/configs/anylog_${NODETYPE}.yaml | grep "ANYLOG_BROKER_PORT" |  awk -F ":" '{print $2}')
  fi

  if [[ ${DOCKERCMD} == up ]] ; then
    helm install ${ROOT_PATH}/kubernetes/anylog-node-volume-1.22.3.tgz -f ${ROOT_PATH}/kubernetes/configs/anylog_${NODETYPE}.yaml --name-template ${NODE_NAME}-volume
    helm install ${ROOT_PATH}/kubernetes/anylog-node-1.22.3.tgz -f ${ROOT_PATH}/kubernetes/configs/anylog_${NODETYPE}.yaml --name-template ${NODE_NAME}
  elif [[ ${DOCKERCMD} == down ]] ; then
    helm uninstall ${NODE_NAME}
    if [[ ${VOLUME} == true ]] ; then
      helm uninstall ${NODE_NAME}-volume
    fi
  fi
fi