#!/bin/bash

kubectl create deployment nginx --image=nginx
POD=$(kubectl get pod -l app=nginx -o name)

# Add KubeArmor Helm repository
helm repo add kubearmor https://kubearmor.github.io/charts
helm repo update kubearmor

# Install or upgrade KubeArmor operator
helm upgrade --install kubearmor-operator kubearmor/kubearmor-operator -n kubearmor --create-namespace

# Apply sample configuration
kubectl apply -f https://raw.githubusercontent.com/kubearmor/KubeArmor/main/pkg/KubeArmorOperator/config/samples/sample-config.yml

# Define KubeArmor policy to monitor all pods in the default namespace
cat <<EOF | kubectl apply -f -
apiVersion: security.kubearmor.com/v1
kind: KubeArmorPolicy
metadata:
  name: monitor-default-namespace
  namespace: default
spec:
  selector:
    matchLabels:
      app: '*'
  process:
    matchPaths:
      - path: "/"
        fromSource:
          - path: "/bin/bash"
          - path: "/bin/sh"
  file:
    matchDirectories:
      - dir: "/etc"
        recursive: true
      - dir: "/var/log"
        recursive: true
  network:
    matchProtocols:
      - protocol: TCP
        fromSource:
          - path: "/bin/bash"
          - path: "/bin/sh"
  action:
    log: true
EOF

# Retrieve logs and alerts from KubeArmor pods
#kubectl logs -n kubearmor -l app=kubearmor-operator
#kubectl get alerts -n default
#kubectl get logs -n default



