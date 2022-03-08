# Deployment via Docker Compose 

The following provides details in regard to deploying AnyLog Node, and it's corresponding tools, via _docker-compose_.


## Requirement
* [contact us](mailto:info@anylog.co) for access to AnyLog Docker Hub repository
* [docker-compose](docker_install.sh)
```commandline
sudo apt-get -y install update
sudo apt-get -y install curl apt-transport-https ca-certificates
sudo apt-get -y install docker.io docker-compose

USER=`whoami`
sudo groupadd docker
sudo usermod -aG docker ${USER}
newgrp docker 
``` 

## Deployment 
**[AnyLog Node](anylog-node)** - deploys AnyLog as a standalone receiving data via MQTT with Postgres v.14.0-alpine. 
Configuration for both containers can be found in [envs directory](anylog-node/envs). Note, AnyLog has a health-check 
process when deploying via docker-compose. If you'd like to use your own Postgres (or SQLite) please make sure to 
comment-out both the database section in [docker-compose](anylog-node/docker-compose.yml) and the _depends_on_ section
under _anylog-node_. 
```shell
cd $HOME/deployments/docker-compose/anylog-node/
docker-compose up -d 
```

**[AnyLog Tools](anylog-tools)** - deploy [AnyLog GUI](https://github.com/AnyLog-co/AnyLog-GUI) and 
[Remote CLI](https://github.com/AnyLog-co/Remote-CLI). The default ports being used for these are 5000 and 8000, these
can be changed in [tools env file](anylog-tools/envs/anylog_tools.env).
```shell
cd $HOME/deployments/docker-compose/anylog-tools/
docker-compose up -d 
```
 