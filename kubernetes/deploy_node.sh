#!/bin/bash

CMD=$1
CONFIG_FILE=$2
INTERNAL_IP=$3

APP_NAME=`cat ${CONFIG_FILE} | grep app_name | awk -F ":" '{print $2}' | awk '{gsub(" ", ""); print}'`
ANYLOG_SERVER_PORT=`cat ${CONFIG_FILE} | grep SERVER_PORT  | awk -F ":" '{print $2}' | awk '{gsub(" ", ""); print}'`
ANYLOG_REST_PORT=`cat ${CONFIG_FILE} | grep REST_PORT  | awk -F ":" '{print $2}' | awk '{gsub(" ", ""); print}'`
SERVICE_NAME=`cat ${CONFIG_FILE} | grep service_name  | awk -F ":" '{print $2}' | awk '{gsub(" ", ""); print}'`
NAMESPACE=`cat ${CONFIG_FILE} | grep namespace  | awk -F ":" '{print $2}' | awk '{gsub(" ", ""); print}'`


if [[ ${CMD} == start ]] ; then
# pacakge AnyLog
helm install anylog-node-1.03.24.tgz -f ${CONFIG_FILE} --name-template ${APP_NAME}
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

kubectl port-forward -n ${NAMESPACE} service/${SERVICE_NAME} ${ANYLOG_SERVER_PORT}:${ANYLOG_SERVER_PORT} --address=${INTERNAL_IP} > "$HOME/port_${HOSTNAME}_${ANYLOG_SERVER_PORT}.log" 2>&1 &
kubectl port-forward -n ${NAMESPACE} service/${SERVICE_NAME} ${ANYLOG_REST_PORT}:${ANYLOG_REST_PORT} --address=${INTERNAL_IP} > "$HOME/port_${HOSTNAME}_${ANYLOG_REST_PORT}.log" 2>&1 &

elif [[ ${CMD} == stop ]] ; then
helm delete ${APP_NAME}
kill -15 `ps -ef | grep port-forward | grep ${ANYLOG_SERVER_PORT} | awk -F " " '{print $2}'`
kill -15 `ps -ef | grep port-forward | grep ${ANYLOG_REST_PORT} | awk -F " " '{print $2}'`
fi