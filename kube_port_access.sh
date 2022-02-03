#!/usr/bin/env bash
if [[ $# -eq 1 ]]
then
  IPADDR=$1
else
  echo "Missing IP Address"
  exit 1
fi

kubectl port-forward --address=${IPADDR} service/grafana 3000:3000
kubectl port-forward --address=${IPADDR} service/database 5432:5432
kubectl port-forward --address=${IPADDR} service/remote-cli 8000:8000
kubectl port-forward --address=${IPADDR} service/anylog-gui 5000:5000
