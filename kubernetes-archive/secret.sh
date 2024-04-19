#!/bin/bash

# command: bash secret.sh ${DOCKER_KEY}

PASSWORD=$1
kubectl create secret docker-registry imagepullsecret \
    --docker-server=docker.io \
    --docker-username=anyloguser \
    --docker-password=${PASSWORD} \
    --docker-email=anyloguser@anylog.co
