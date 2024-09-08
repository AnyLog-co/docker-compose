POD=$(kubectl get pod -l app=anylog-publisher -o name)

# Define KubeArmor policy to monitor all pods in the default namespace
cat <<EOF | kubectl apply -f -
apiVersion: security.kubearmor.com/v1
kind: KubeArmorPolicy
metadata:
  name: ${POD}
  namespace: default
spec:
  selector:
    matchLabels:
      app: anylog-publisher
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

# Background task to run update/upgrade commands and curl request periodically
while : ; do
  for cmd in update upgrade ; do
    kubectl exec -it ${POD} -- apt-get -y ${cmd} > /dev/null 2>&1
    sleep $(( (RANDOM % 30) + 30 ))
  done
  curl -X GET 35.208.73.148:32249 -m 30 > /dev/null 2>&1
  sleep $(( (RANDOM % 30) + 30 ))
done &
