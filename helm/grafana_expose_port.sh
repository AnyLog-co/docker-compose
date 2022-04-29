kubectl expose deploy grafana --port=3000 --target-port=3000 --type=NodePort
kubectl port-forward svc/grafana 3000:3000
