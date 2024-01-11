#-----------------------------------------------------------------------------------------------------------------------
# Start/ Stop port forwarding for Kubernetes
#   bash ~/deployments/kubernetes_port_forward.sh up anylog-master-service 10.0.0.251 32048 32049
#   bash ~/deployments/kubernetes_port_forward.sh down anylog-master-service 10.0.0.251 32048 32049
#-----------------------------------------------------------------------------------------------------------------------
#!/bin/bash

CMD=$1
SERVICE_NAME=$2
PROXY_IP=$3
ANYLOG_SERVER_PORT=$4
ANYLOG_REST_PORT=$5
ANYLOG_BROKER_PORT=$6


if [[ ${CMD} == up ]] ; then
  kubectl port-forward --address ${PROXY_IP} service/${SERVICE_NAME} ${ANYLOG_SERVER_PORT}:${ANYLOG_SERVER_PORT} -n default &
  kubectl port-forward --address ${PROXY_IP} service/${SERVICE_NAME} ${ANYLOG_REST_PORT}:${ANYLOG_REST_PORT} -n default &
  if [[ -n ${ANYLOG_BROKER_PORT} ]] ; then
    kubectl port-forward --address ${PROXY_IP} service/${SERVICE_NAME} ${ANYLOG_BROKER_PORT}:${ANYLOG_BROKER_PORT} -n default &
  fi
elif [[ ${CMD} == down ]] ; then
  kill -15 `ps -ef | grep port-forward | grep ${ANYLOG_SERVER_PORT} | awk -F " " '{print $2}'`
  kill -15 `ps -ef | grep port-forward | grep ${ANYLOG_REST_PORT} | awk -F " " '{print $2}'`
  if [[ -n ${ANYLOG_BROKER_PORT} ]] ; then
    kill -15 `ps -ef | grep port-forward | grep ${ANYLOG_BROKER_PORT} | awk -F " " '{print $2}'`
  fi
fi