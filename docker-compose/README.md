# Installing AnyLog using Docker 

The following provides general directions for installing AnyLog through _Docker_ and _docker-compose_. Detailed directions
can be found in our [deployment documentation](https://github.com/AnyLog-co/documentation/tree/os-dev/deployments). 

### Requirements 
There are 2 [basic requirements](https://github.com/AnyLog-co/documentation/blob/os-dev/deployments/Docker/Prerequisites.md) 
for deploying AnyLog and its corresponding services.
* Docker
* docker-compose 

### Deploying Postgres
```shell
cd deployments/docker-compose/postgres 
docker-compose up -d 
```

### Deploying AnyLog Node
1. Go into docker-compose directory
```shell
cd deployments/docker-compose/anylog-node
```

2. Update the configurations in `.env` file
```dotenv
CONTAINER_NAME=al-node
IMAGE=anylogco/anylog-network
VERSION=predevelop
ENV_FILE=envs/anylog_rest.env
```

3. Deploy AnyLog 
```shell
docker-compose up -d 
```

### Deploying Grafana 
```shell
cd deployments/docker-compose/grafana 
docker-compose up -d
```

### Deploying Remote-CLI
```shell
cd deployments/docker-compose/remote-cli 
docker-compose up -d
```