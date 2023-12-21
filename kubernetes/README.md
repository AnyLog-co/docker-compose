# README

## Install Kubearmor 
Based on [Kuberarmor Documentation](https://docs.kubearmor.io/kubearmor/) for Helm/Kubernetes 

1. Declare repo in _Helm_
```shell
helm repo add kubearmor https://kubearmor.github.io/charts

helm repo update kubearmor

helm upgrade --install kubearmor-operator kubearmor/kubearmor-operator -n kubearmor --create-namespace
```

2. Install _karmor_ CLI
```shell
curl -sfL http://get.kubearmor.io/ | sudo sh -s -- -b /usr/local/bin
```

3. Build nignx / kubearmor helm package 
* **Note 1**:  [KubeArmorConfig.yml](nginx-kubearmor%2Ftemplates%2FKubeArmorConfig.yml) is the default [sample configurations](https://raw.githubusercontent.com/kubearmor/KubeArmor/main/pkg/KubeArmorOperator/config/samples/sample-config.yml). 
```shell
helm package nginx-kubearmor
```

4. Deploy nginx / kubearmor helm pacakge 
```shell
helm install ./[nginx-kubearmor-0.1.0.tgz](nginx-kubearmor-0.1.0.tgz) --generate-name
```

5. set nginx port-forwarding 
```shell
nohup kubectl port-forward service/nginx 30800:80 > port-forward.log 2>&1 &
```

6. Start karmor gRPC client 
```shell
karmor logs -n default --json
```

**Sample Output**: 
```shell
POD=$(kubectl get pod -l app=nginx -o name)
kubectl exec -it $POD -- bash -c "apt-get -y update && apt-get -y upgrade"

```