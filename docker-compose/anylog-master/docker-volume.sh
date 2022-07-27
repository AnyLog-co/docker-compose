# Create volumes for docker compose
source .env
for vol in anylog blockchain data local-scripts
do
  docker volume create --name ${CONTAINER_NAME}-${vol}
done