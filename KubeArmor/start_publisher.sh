#!/bin/bash
minikube start

kubectl create secret docker-registry imagepullsecret \
  --docker-server=docker.io \
  --docker-username=oshadmon \
  --docker-password=docker4AnyLog! \
  --docker-email=ori@anylog.co

