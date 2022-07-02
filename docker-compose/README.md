# Deployment via Docker Compose 

The following provides details in regard to deploying AnyLog Node via Docker & docker-compose.

## Requirement
* [docker-compose](docker_install.sh)

## Steps to Deploy AnyLog 
0. <a href="mailto:info@anylog.co?subject=docker login credentials">Contact us</a> for docker login credentials


1. If you'd like to use the postgres image we provide please:
    1. Update [Postgres configuration](postgres/postgres.env) if you'd like to utilize our Postgres instance
    2. Deploy Postgres 
```commandline
cd postgres 
docker-compose up -d 
```

2. In [anylog-node/envs](anylog-node/envs) update the configuration in the desired deployment type. Specific things to look at: 
    * `MASTER_NODE` credentials
    * Database Information
    * MQTT configuration - if desired 
   

3. Update [.env](anylog-node/.env) file based on the changes made in the previous version. Specific things to look at: 
    * `CONTAINER_NAME`
    * `VERSION`
    * `ENV_FILE`


4. Deploy the AnyLog instance
```commandline
cd anylog-node 
docker-compose up -d
```

5. Validate node is running
```commandline
curl -X GET ${LOCAL_IP}:${ANYLOG_REST_PORT} -H "command: get status" -H "User-Agent: AnyLog/1.23" 
```
**Disclaimer** - If you'd like to use a single physical machine to run multiple AnyLog instances, you need to change 
the [docker-compose.yml](anylog-node/docker-compose.yml) such that the naming for _service_ and _volumes_ are different.  

### Configuring `DEPLOY_LOCAL_SCRIPT`
The `DEPLOY_LOCAL_SCRIPT` is an extension to the deployment process that the user can create and allow the system to 
automatically run when ever the node is deployed. The script is automatically deployed only from the second deploymnet. 

0. The AnyLog instance needs to be running 


1. Find the file path for the volume location for `local-scripts`
```commandline
docker volume inspect anylog-node_anylog-node-local-scripts
[
    {
        "CreatedAt": "2022-05-04T02:10:56Z",
        "Driver": "local",
        "Labels": {
            "com.docker.compose.project": "anylog-node",
            "com.docker.compose.version": "1.29.2",
            "com.docker.compose.volume": "anylog-node-local-scripts"
        },
        "Mountpoint": "/var/lib/docker/volumes/anylog-node_anylog-node-local-scripts/_data", #<-- path 
        "Name": "anylog-node_anylog-node-local-scripts",
        "Options": null,
        "Scope": "local"
    }
]
```

2. Update the local file: `/var/lib/docker/volumes/anylog-node_anylog-node-local-scripts/_data/local/local_script.al`


3. Execute `local_scirpt.al` file using the REST POST command
```bash
curl -X POST ${LOCAL_IP}:${ANYLOG_REST_PORT} -H "command: process !local_scripts/local_script.al" -H "User-Agent: AnyLog/1.23"
```

## Deploy Grafana & Remote CLI
The Remote CLI & Grafana are optional tools and can be deployed on the same machine of one of the nodes or on a different machine
that's able to communicate with the network. 

### Deploying Grafana
```commandline
cd grafana 
docker-compose up -d 
```

### Deploy Remote CLI
1. Update .env if you'd like to use a port other than `31800` or an IP other than `0.0.0.0`

2. Deploy Remote CLI 
```commandline
cd remote_cli 
docker-compose up -d
```
