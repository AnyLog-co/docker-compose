# Set docker credentials for Kubernetes & Helm
if [[ $# -eq 1 ]]
then
  DOCKER_PASSWORD=$1
else
  echo "Missing Docker password for downloading AnyLog code"
  exit 1
fi

kubectl create secret docker-registry imagepullsecret \
  --docker-server=docker.io \
  --docker-username=anyloguser \
  --docker-password=${DOCKER_PASSWORD} \
  --docker-email=anyloguser@anylog.co
