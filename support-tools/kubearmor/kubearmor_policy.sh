#!/bin/bash

POLICY_APP=$1

cat <<EOF | kubectl apply -f -
apiVersion: security.kubearmor.com/v1
kind: KubeArmorPolicy
metadata:
  name: audit-${POLICY_APP}-access
spec:
  selector:
    matchLabels:
      app: ${POLICY_APP}
  process:
    matchPaths:
    - path: /usr/bin/*
    - path: /usr/bin/apt
    - path: /usr/bin/apt-get
  message: Alert! Use of any process detected!
  action:
    Audit
EOF