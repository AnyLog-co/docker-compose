# Set docker credentials for Kubernetes & Helm
if [[ $# -eq 1 ]]
then
  DOCKER_PASSWORD=$1
else
  echo "Missing Docker password for downloading AnyLog code"
  exit 1
fi

docker login -u oshadmon -p ${DOCKER_PASSWORD}