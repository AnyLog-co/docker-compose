# Deploy AnyLog using Kubernetes 

The following provides details in regard to deploying AnyLog Node, and it's corresponding tools, via Kubernetes 
(helm-charts).

## Steps to Deploy AnyLog  
0. [Contact Us](mailto:info@anylog.co) to request credentials for downloading AnyLog 
1. Configure credentials 
```bash
bash $HOME/deployments/helm/credentials.sh ${YOUR_ANYLOG_DOCKER_PASSWORD}
```
2. On all Kubernetes clusters that contain an AnyLog instance that uses Postgres deploy a postgres\
```bash
helm install --generate-name $HOME/deployments/helm/postgres
```
3. 