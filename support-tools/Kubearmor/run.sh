#!/bin/bash

# Declare Repo
helm repo add kubearmor https://kubearmor.github.io/charts
helm repo update kubearmor
helm upgrade --install kubearmor-operator kubearmor/kubearmor-operator -n kubearmor --create-namespace

# install KubeArmor CLI
curl -sfL http://get.kubearmor.io/ | sudo sh -s -- -b /usr/local/bin

# Deploy KubeArmor
kubectl apply -f kubearmor.yaml

# view output
karmor logs --json --namespace kubearmor

