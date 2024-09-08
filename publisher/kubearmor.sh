#!/bin/bash

# Add KubeArmor Helm repository
helm repo add kubearmor https://kubearmor.github.io/charts
helm repo update kubearmor

# Install or upgrade KubeArmor operator
helm upgrade --install kubearmor-operator kubearmor/kubearmor-operator -n kubearmor --create-namespace

# Apply sample configuration
kubectl apply -f https://raw.githubusercontent.com/kubearmor/KubeArmor/main/pkg/KubeArmorOperator/config/samples/sample-config.yml

kubearmor policy apply -f kubearamor.yml



