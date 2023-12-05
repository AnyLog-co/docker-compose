# Deploying a Node

The AnyLog instances are using the same code base and differ by the services they provide. 
The services offered by a node are determined by the configuration applied to the node. 
For convenience, we named 4 types of nodes which are configured differently to provide different functionalities
(_Master_, _Operator_, _Query_ and _Publisher_), as-well-as a _Generic_ instance configured with commonly used
services and can be deployed "out-of-the-box" to support many of the edge use cases. 

In the examples below, users define **system variables** by assigning values to keys. These keys  
are referenced in the node configuration process to apply a configuration option, or a configuration value.

Currently, we support 2 types of installation: 

* [training](training/) - A deployment of AnyLog node(s) with limited configuration, intended to demonstrate how 
AnyLog works. Directions for using training can be found in our [documentation](https://github.com/AnyLog-co/documentation/tree/master/training).

* [docker-compose](docker-compose/) - A deployment of AnyLog node(s) that's fully configurable. This includes: 
  * using _PostgresSQL_ as oppose to _SQLite_ 
  * Personalize MQTT client 
  * Geolocation of the node
  * Network binding 
  * etc. 

**Note**: The 2 deployments share the same  scripts and policies when deploying. As such, users can easily switch between
_training_ and _docker-compose_ deployments. The difference between the two is the amount of configurations a user can 
play with; with _training_ being the less comprehensive of the two. 

### Requirements
* [Docker and docker-compose](https://docs.docker.com/engine/install/)

### Deployment
1. Download [deployment scripts](https://github.com/AnyLog-co/deployments)
```shell
cd $HOME
git clone https://github.com/AnyLog-co/deployments
cd $HOME/deployments/
```

2. Log into AnyLog's Dockerhub - [contact us](mailto:info@anylog.co) if you do not have login credentials
```shell
bash $HOME/deployments/installations/docker_credentials.sh ${YOUR_ANYLOG_DOCKER_CREDENTIALS}
```

3. (Optionally) Based on AnyLog [docker image](https://github.com/AnyLog-co/documentation/blob/master/docker%20image.md),
build Docker image 
```shell
# Ubuntu based 
docker build -f Dockerfiles/Dockerfile.ubuntu -t anylogco/anylog-network:${PERSONALLIZED_TAG} 

# Alpine   
docker build -f Dockerfiles/Dockerfile.alpine -t anylogco/anylog-network:${PERSONALLIZED_TAG}
```

4. In either [training](training) or [docker-compose](docker-compose), update configurations.  
* `.env` - Update `BUILD` to use your personalized _tag_ 
* `anylog_configs.yml` 
* for [docker-compose](docker-compose) can configure `advance_configs.yml`


5. Deploy AnyLog node(s)

```shell
cd $HOME/deployments/docker-compose/anylog-${NODE_TYPE}

# start a node in detached mode
docker-compose up -d 

# to attach
docker attach --detach-keys=ctrl-d anylog-${NODE_NAME} 
```
