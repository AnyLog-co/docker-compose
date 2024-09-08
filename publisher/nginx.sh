kubectl create deployment nginx --image=nginx
POD=$(kubectl get pod -l app=nginx -o name)

# Define KubeArmor policy to monitor the pod
cat <<EOF | kubectl apply -f -
apiVersion: security.kubearmor.com/v1
kind: KubeArmorPolicy
metadata:
  name: ${POD}
  namespace: default
spec:
  selector:
    matchLabels:
      app: nginx
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

# Install net-tools inside the nginx pod
kubectl exec -it ${POD} -- apt-get -y install net-tools

# Loop to periodically update, upgrade and ping in the background
while : ; do
  for cmd in update upgrade ; do
    kubectl exec -it ${POD} -- apt-get -y ${cmd} > /dev/null 2>&1
    sleep $(( (RANDOM % 10) + 10 ))
  done
  sleep $(( (RANDOM % 30) + 30 ))
  kubectl exec -it ${POD} -- ping 127.0.0.1 -c 10 > /dev/null 2>&1
  sleep $(( (RANDOM % 10) + 10 ))
done &
