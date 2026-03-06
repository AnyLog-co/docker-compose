# Support 

The following provides examples to run support processes outside of AnyLog container(s).

## PostgresSQL 

PostgresSQL is a SQL based database, that's used as an alternative to SQLite, allowing to keep data persistent without 
the need to AnyLog containers persistent. 

Directions for installing locally on machine
* [GUI-based Install](https://www.w3schools.com/postgresql/postgresql_install.php)
* [Ubuntu](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-22-04)
* [Centos](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-centos-8)

```shell
docker run -it -d \
  -p 5432:5432 \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=passwd \
  -e POSTGRES_INITDB_ARGS="--auth=md5" \
  -v pgdata:/var/lib/postgresql/data \
--name postgres postgres:14.0-alpine  
```

## MongoDB 

MongoDB is a NoSQL baased database, that's used to store blobs (images, videos, files, etc.) wihtin AnyLog. It is an 
alternative to storing blobs locally on the file system, removing the need to keep AnyLog containers persistent.  

Directions for installing locally on machine can be found in the [official documentation](https://www.mongodb.com/docs/manual/installation/)

```shell
# Run MongoDB container
docker run -d \
  --name mongo-docker \
  --restart always \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=passwd \
  -v mongo-data:/data/db \
  -v mongo-configs:/data/configdb \
  mongo:latest

# Run Mongo Express container
# Mongo Express URL: http://${YOUR_URL}:28081/
docker run -d \
  --name mongo-express \
  --restart always \
  -p 28081:8081 \
  -e ME_CONFIG_MONGODB_SERVER=mongo-docker \
  -e ME_CONFIG_BASICAUTH_USERNAME=admin \
  -e ME_CONFIG_BASICAUTH_PASSWORD=passwd \
  -e ME_CONFIG_MONGODB_ADMINUSERNAME=admin \
  -e ME_CONFIG_MONGODB_ADMINPASSWORD=passwd \
  -e ME_CONFIG_MONGODB_URL="mongodb://admin:passwd@mongo-docker:27017/" \
  --link mongo-docker:mongo \
  mongo-express:latest
```

## Remote-CLI 

An AnyLog specific alternative to Postman. The [Remote-CLI](https://github.com/AnyLog-co/Remote-CLI) allows to communicate 
with AnyLog via cURL using a web-based interface. 

```shell
CONN_IP=0.0.0.0
CLI_PORT=31800

docker run -p ${CLI_PORT}:${CLI_PORT} --name remote-cli \
   -e CONN_IP=${CONN_IP} \
   -e CLI_PORT=${CLI_PORT} \
   -v remote-cli:/app/Remote-CLI/anylog_query/static/json \
   -v remote-cli-keys:/app/Remote-CLI/anylog_query/static/pem \
   --rm  -it -d anylogco/remote-cli:smart-city-demo
```

## Grafana

Directions for installing locally on machine can be found in the [official documentation](https://grafana.com/docs/grafana/latest/setup-grafana/installation/)

```shell
docker run -d \
  --name grafana \
  --restart always \
  -p 3000:3000 \
  -e GRAFANA_ADMIN_USER=admin \
  -e GRAFANA_ADMIN_PASSWORD=passwd \
  -e GF_AUTH_DISABLE_LOGIN_FORM=false \
  -e GF_AUTH_ANONYMOUS_ENABLED=true \
  -e GF_SECURITY_ALLOW_EMBEDDING=true \
  -e GF_INSTALL_PLUGINS=simpod-json-datasource,grafana-worldmap-panel \
  -v grafana-data:/var/lib/grafana \
  -v grafana-log:/var/log/grafana \
  -v grafana-config:/etc/grafana \
  grafana/grafana:latest

```
