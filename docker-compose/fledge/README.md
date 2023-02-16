# FLEDGE
Docker containers for _FLEDGE_ and _FLEDGE-GUI_ created by [Rob Raesemann](https://hub.docker.com/r/robraesemann)

* [AnyLog Fledge Plugin](https://github.com/AnyLog-co/lfedge-code/tree/main/fledge)
* [Docker Hub](https://hub.docker.com/r/robraesemann/fledge)
* [Documentation](https://fledge-iot.readthedocs.io/en/latest/quick_start/index.html)


## Deployment

1. Clone [repository](https://github.com/AnyLog-co/deployments)
```shell
cd $HOME
git clone https://github.com/AnyLog-co/deployments
```

2. Deploy Containers
```shell
cd $HOME/deployments/docker-compose/fledge/
docker-compose up -d 
```

3. Accessing GUI - [http://${YOUR_IP}/]()

## Connect AnyLog Plugin
1. Attach to `fledge` container
```shell
docker exec -it --detach-keys=ctrl-d fledge bash
```

2. Clone lfedge code into the container  
```shell
git clone https://github.com/AnyLog-co/lfedge-code 
```

3. Copy anylog_plugin into _FLEDGE_
```shell
cp -r /app/lfedge-code/fledge/anylog_rest_conn/ /usr/local/fledge/python/fledge/plugins/north/
```

Under Northbound instances you'll be able to see the `anylog_rest_conn`, an HTTP North plugin. 



