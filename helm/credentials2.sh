# Set docker credentials for Kubernetes & Helm
DOCKER_PASSWORD=ZHZ1b3EyNWdlcG5kNXJzZHBzbXVoM2Y5ZmI6ZDVmMzQ0MGItMGE2ZS00YTRkLWFmYjEtYTU1NTlmN2FhZDgx
DOCKER_REGISTRY_SERVER=nvcr.io
DOCKER_USER=\$oauthtoken 
kubectl create secret docker-registry anylog-registry-key \
  --docker-server=${DOCKER_REGISTRY_SERVER} \
  --docker-username=${DOCKER_USER} \
  --docker-password=${DOCKER_PASSWORD} \
