# Set docker credentials for Kubernetes & Helm
if [[ $# -eq 1 ]]
then
  DOCKER_PASSWORD=$1
else
  echo "Missing Docker password for downloading AnyLog code"
  exit 1
fi

DOCKER_REGISTRY_SERVER=docker.io
DOCKER_USER=oshadmon
DOCKER_EMAIL=ori@anylog.co
kubectl create secret docker-registry myregistrykey \
  --docker-server=${DOCKER_REGISTRY_SERVER} \
  --docker-username=${DOCKER_USER} \
  --docker-password=${DOCKER_PASSWORD} \
  --docker-email=${DOCKER_EMAIL}
