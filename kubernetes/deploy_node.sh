#!/bin/bash

#!/bin/bash

CMD=$1
CONFIG_FILE=$2
INTERNAL_IP=$3

commands=("package" "start" "stop")
status=false

if [[ ! " ${commands[@]} " =~ " ${CMD} " ]]; then
  if [[ ! ${CMD} == "" ]]; then
    echo "Invalid command '${CMD}'"
  fi
  status="true"
fi

if [[ ${status} == "true" ]] || [[ $# -lt 1 ]]; then
  printf "Options:\n"
  printf "\tpackage - package AnyLog for Kubernetes\n"
  printf "\tstart - start kubernetes instance (with port-forwarding)\n"
  printf "\tstop - delete kuberentes instance & corresponding port-forwarding\n"
  printf "\nSample Command: bash deploy_node.sh start configurations/anylog_master 10.0.0.215\n\n"
fi


IMAGE_NAME=`cat anylog-node/Chart.yaml | grep "name:" | awk -F ":" '{print $2}' | awk '{gsub(" ", ""); print}'`
IMAGE_VERSION=`cat anylog-node/Chart.yaml | grep "version:" | awk -F ":" '{print $2}' | awk '{gsub(" ", ""); print}'`

if [[ -n ${CONFIG_FILE} ]] && [[ -f ${CONFIG_FILE} ]] ; then
  APP_NAME=`cat ${CONFIG_FILE} | grep app_name | awk -F ":" '{print $2}' | awk '{gsub(" ", ""); print}'`
  ANYLOG_SERVER_PORT=`cat ${CONFIG_FILE} | grep SERVER_PORT  | awk -F ":" '{print $2}' | awk '{gsub(" ", ""); print}'`
  ANYLOG_REST_PORT=`cat ${CONFIG_FILE} | grep REST_PORT  | awk -F ":" '{print $2}' | awk '{gsub(" ", ""); print}'`
  ANYLOG_BROKER_PORT=`cat ${CONFIG_FILE} | grep BROKER_PORT  | awk -F ":" '{print $2}' | awk '{gsub(" ", ""); print}'`
  SERVICE_NAME=`cat ${CONFIG_FILE} | grep service_name  | awk -F ":" '{print $2}' | awk '{gsub(" ", ""); print}'`
  NAMESPACE=`cat ${CONFIG_FILE} | grep namespace  | awk -F ":" '{print $2}' | awk '{gsub(" ", ""); print}'`
elif [[ -n ${CONFIG_FILE} ]] && [[ ! -f ${CONFIG_FILE} ]] ; then
  echo "Error: Configuration file '$CONFIG_FILE' not found."
  exit 1
fi

if [[ ${CMD} == package ]] ; then
  helm package anylog-node/
elif [[ ${CMD} == start ]] ; then
  if [[ ! -f ./${IMAGE_NAME}-${IMAGE_VERSION}.tgz ]] ; then
    echo "Error failed to locate deployment package: ./${IMAGE_NAME}-${IMAGE_VERSION}.tgz"
    exit 1
  fi
  helm install ./anylog-node-volumes-0.0.0.tgz -f ${CONFIG_FILE} --name-template ${APP_NAME}-volume
  helm install ./${IMAGE_NAME}-${IMAGE_VERSION}.tgz -f ${CONFIG_FILE} --name-template ${APP_NAME}
  echo "Waiting for the pod to be in the 'Running' state..."
  while true; do
      POD_STATUS=$(kubectl get pod -l app=${APP_NAME} -o jsonpath="{.items[0].status.phase}" 2>/dev/null)
      echo ${POD_STATUS}
      if [ "$POD_STATUS" == "Running" ]; then
          echo "Pod is now running. Starting port forwarding..."
          break
      fi
      sleep 1
  done
  sleep 1
  if [[ -n ${INTERNAL_IP} ]] ; then
    kubectl port-forward -n ${NAMESPACE} service/${SERVICE_NAME} ${ANYLOG_SERVER_PORT}:${ANYLOG_SERVER_PORT} --address=${INTERNAL_IP} > "$HOME/port_${HOSTNAME}_${ANYLOG_SERVER_PORT}.log" 2>&1 &
    kubectl port-forward -n ${NAMESPACE} service/${SERVICE_NAME} ${ANYLOG_REST_PORT}:${ANYLOG_REST_PORT} --address=${INTERNAL_IP} > "$HOME/port_${HOSTNAME}_${ANYLOG_REST_PORT}.log" 2>&1 &
    if [[ ${ANYLOG_BROKER_PORT} ]] ; then
      kubectl port-forward -n ${NAMESPACE} service/${SERVICE_NAME} ${ANYLOG_BROKER_PORT}:${ANYLOG_BROKER_PORT} --address=${INTERNAL_IP} > "$HOME/port_${HOSTNAME}_${ANYLOG_BROKER_PORT}.log" 2>&1 &
    fi
  else
    kubectl port-forward -n ${NAMESPACE} service/${SERVICE_NAME} ${ANYLOG_SERVER_PORT}:${ANYLOG_SERVER_PORT} > "$HOME/port_${HOSTNAME}_${ANYLOG_SERVER_PORT}.log" 2>&1 &
    kubectl port-forward -n ${NAMESPACE} service/${SERVICE_NAME} ${ANYLOG_REST_PORT}:${ANYLOG_REST_PORT}  > "$HOME/port_${HOSTNAME}_${ANYLOG_REST_PORT}.log" 2>&1 &
    if [[ ${ANYLOG_BROKER_PORT} ]] ; then
      kubectl port-forward -n ${NAMESPACE} service/${SERVICE_NAME} ${ANYLOG_BROKER_PORT}:${ANYLOG_BROKER_PORT} > "$HOME/port_${HOSTNAME}_${ANYLOG_BROKER_PORT}.log" 2>&1 &
    fi
  fi
elif [[ ${CMD} == stop ]] ; then
  helm delete ${APP_NAME}
  kill -15 `ps -ef | grep port-forward | grep ${ANYLOG_SERVER_PORT} | awk -F " " '{print $2}'`
  kill -15 `ps -ef | grep port-forward | grep ${ANYLOG_REST_PORT} | awk -F " " '{print $2}'`
  if [[ ${ANYLOG_BROKER_PORT} ]] ; then
    kill -15 `ps -ef | grep port-forward | grep ${ANYLOG_BROKER_PORT} | awk -F " " '{print $2}'`
  fi
fi
