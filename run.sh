#!/bin/bash

# Start / Stop Docker such that AnyLog connects to specific ports, as opposed to using a generic bridge connection
# Sample Calls:
#  - help: bash run.sh help
#  - Start: bash run.sh NODETYPE up [--training]
#  - Stop: bash run.sh {NODETYPE} down [--training] [--volume] [--rmi]

NODETYPE=$1
DOCKERCMD=$2
VOLUME=false
IMAGE=false
TRAINING=false

if [[ ${NODETYPE} == help ]] ; then
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

if [[ ${TRAINING} == true ]] ; then
  if [[ ${NODETYPE} == master ]] ; then
    cd ${ROOT_PATH}/training/anylog-master || echo "Failed to cd into anylog-master dir" && exit 1
  elif [[ ${NODETYPE} == operator ]] ; then
    cd ${ROOT_PATH}/training/anylog-operator || echo "Failed to cd into anylog-operator dir" && exit 1
  elif [[ ${NODETYPE} == query ]] ; then
    cd ${ROOT_PATH}/training/anylog-query || echo "Failed to cd into anylog-query dir" && exit 1
  else
    echo "Invalid deployment type: ${NODETYPE}"
    exit 1
  fi
elif [[ ${NODETYPE} == master ]] ; then
  cd ${ROOT_PATH}/docker-compose/anylog-master || echo "Failed to cd into anylog-master dir" && exit 1
elif [[ ${NODETYPE} == operator ]] ; then
  cd ${ROOT_PATH}/docker-compose/anylog-operator || echo "Failed to cd into anylog-operator dir" && exit 1
elif [[ ${NODETYPE} == query ]] ; then
  cd ${ROOT_PATH}/docker-compose/anylog-query || echo "Failed to cd into anylog-query dir" && exit 1
elif [[ ${NODETYPE} == query-remote-cli ]] ; then # AnyLog Query with Remote-CLI
  cd ${ROOT_PATH}/docker-compose/anylog-query-remote-cli || echo "Failed to cd into anylog-query-remote-cli dir" && exit 1
elif [[ ${NODETYPE} == publisher ]] ; then
  cd ${ROOT_PATH}/docker-compose/anylog-publisher || echo "Failed to cd into anylog-publisher dir" && exit 1
else
  echo "Invalid deployment type: ${NODETYPE}"
  exit 1
fi


export ANYLOG_SERVER_PORT=`cat anylog_configs.env | grep "ANYLOG_REST_PORT" | awk -F "=" '{print $2}'`
export ANYLOG_REST_PORT=`cat anylog_configs.env | grep "ANYLOG_SERVER_PORT" |  awk -F "=" '{print $2}'`
export ANYLOG_BROKER_PORT=""
if [[ ${TRAINING} == false ]] && [[ ! $(grep "ANYLOG_BROKER_PORT" advance_configs.env |  awk -F "=" '{print $2}')   = '""' ]] ; then # if ANYLOG_BROKER_PORT exists
    export ANYLOG_BROKER_PORT=`grep "ANYLOG_BROKER_PORT" advance_configs.env |  awk -F "=" '{print $2}'`
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