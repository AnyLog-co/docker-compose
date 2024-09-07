#!/bin/bash
minikube start

kubectl create secret docker-registry imagepullsecret \
  --docker-server=docker.io \
  --docker-username=oshadmon \
  --docker-password=docker4AnyLog! \
  --docker-email=ori@anylog.co

bash deploy_node.sh packaage anylog_publisher.yaml  10.128.0.8
bash deploy_node.sh start anylog_publisher.yaml  10.128.0.8
bash kubearmor.sh