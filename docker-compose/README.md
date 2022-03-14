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
**[AnyLog Node](anylog-node)** - Deploy an AnyLog container of type: [master](anylog-node/envs/anylog_master.env),
[operator](anylog-node/envs/anylog_operator.env), [publisher](anylog-node/envs/anylog_publisher.env), 
[query](anylog-node/envs/anylog_query.env), [standalone](anylog-node/envs/anylog_standalone.env), 
[standalone-publisher](anylog-node/envs/anylog_standalone_publisher.env), [rest](anylog-node/envs/anylog_rest.env)
or [empty](anylog-node/envs/anylog_none.env). 
1. Copy the desired AnyLog node type into [anylog-node/envs/anylog_node.env](anylog-node/envs/anylog_node.env) 


2. Update the configuration in [anylog_node.env](anylog-node/envs/anylog_node.env) as you see fit
   * If you'd like to use Postgres on Docker, and updated the database credentials please also update the configuratiion
   in [postgres.sh](postgres.sh)
   * If you'd like to run multiple AnyLog containers on a single physical machine, make sure the AnyLog ports differ - 
   _ANYLOG_SERVER_PORT_, _ANYLOG_REST_PORT_ and optionally _ANYLOG_BROKER_PORT_. 

   
3. Deploy AnyLog - note the [docker-compose](anylog-node/docker-compose.yml) has a health check to validate Postgres is running. 
Please make sure either Postgres is running via Docker or the section is commented out if you'd like to use a different 
Postgres or SQLite
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

**[Postgres](postgres.sh)** - Postgres database for use to deploy using Docker. Alternatively, users can either opt to
use their own _Postgres_ database or _SQLite_ (built-in). 
```shell
bash $HOME/deployments/docker-compose/postgres.sh
```

**[Grafana](grafana.sh)** - One of the more common BI tools used with AnyLog is Grafana, as such we provide a docker 
deployment script, but highly recommend [physically installing it](https://grafana.com/docs/grafana/latest/installation/).
```shell
bash $HOME/deployments/docker-compose/grafana.sh
```