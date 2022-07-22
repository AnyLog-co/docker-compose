# Deploying AnyLog 

The following provides the tools needed to deploy AnyLog using either a Kubernetes (via Helm) or Docker with docker-compose. 

For any other deployment format please reach out to us at [info@anylog.co](mailto:info@anylog.co).       

Our [deplyoment documentation](https://github.com/AnyLog-co/documentation/tree/master/deployments) provide directions in 
terms of how to deploy the differnet AnyLog nodes. We recommend starting with our basic deployment - as shown in the 
diagram below

<img alt="deployment diagram" src="https://github.com/AnyLog-co/documentation/blob/master/imgs/deployment_diagram.png"/>

### AnyLog Version & Node Types
AnyLog has 3 major versions, each version is built on both _Ubuntu:20.04_ with _python:3.9-alpine_. 
* develop - is a stable release that's been used as part of our Test Network for a number of weeks, and gets updated every 4-6 weeks.
* predevelop - is our beta release, which is being used by our Test Network for testing purposes.
* testing - Any time there's a change in the code we deploy a "testing" image to be used for (internal) testing purposes. Usually the image will be Ubuntu based, unless stated otherwise.

| Build | Base Image | CPU Architecture | Pull Command | Size | 
|---|---|---|---|---|
| develop | Ubuntu:20.04 | amd64,arm/v7,arm64 | `docker pull anylogco/anylog-network:develop` | 664MB | 
| develop-alpine | python:3.9-alpine | amd64,arm/v7,arm64 | `docker pull anylogco/anylog-network:develop-alpine` | 460MB| 
| predevelop | Ubuntu:20.04 | amd64,arm/v7,arm64 | `docker pull anylogco/anylog-network:predevelop` | ~245MB | 
| predevelop-alpine | python:3.9-alpine | amd64,arm/v7,arm64 | `docker pull anylogco/anylog-network:predevelop-alpine` | ~178MB | 
| testing | Ubuntu:20.04 | amd64,arm/v7,arm64 | `docker pull anylogco/anylog-network:testing` |

By default, the AnyLog image is configured to run as a _REST_ node, which means that the TCP and REST options 
are running, but no other process is enabled. This allows for users to play with the system with no other services 
running in the background, but already having the default network configurations. The other major node types are:  

* Master - A node that's dedicated to managing the ledger on the blockchain (database)  
* Operator - Node that contains the data generated by devices and sensors
* Publisher - Node to distribute data coming in from different devices and sensors across the different operator nodes 
* Query - Node dedicated to query the data, usually connected to a BI tool, such as Grafana 

For a basic deployment of an AnyLog REST node, you can execute the following command:   

```shell
docker run --network host -it --detach-keys="ctrl-d" --name anylog-node --rm anylogco/anylog-network:develop
```

## Support 
* [AnyLog Documentation](https://github.com/AnyLog-co/documentation) - documentation for AnyLog  
* [AnyLog API](https://github.com/AnyLog-co/AnyLog-API) - A python package to easily communicate with AnyLog via REST 
* Directions for configuring nginx can be found in the [helm deployment documentation](helm/README.md#configuring-nginx)