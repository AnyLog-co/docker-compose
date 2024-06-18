# Podman

## Podman vs Docker
| Feature                          | Podman                                  | Docker                                  |
|----------------------------------|-----------------------------------------|-----------------------------------------|
| **Architecture**                 | Daemonless, uses a fork-exec model      | Daemon-based                            |
| **Rootless Mode**                | Yes, fully supports rootless containers | Limited support                         |
| **Compatibility**                | Compatible with Docker CLI and API      | Docker CLI and API                      |
| **Container Images**             | Supports OCI and Docker image formats   | Supports OCI and Docker image formats   |
| **Kubernetes Integration**       | Supports Kubernetes YAML directly       | Requires additional tools (e.g., Kompose)|
| **Security**                     | Runs as non-root by default             | Requires root for some operations       |
| **Networking**                   | Uses CNI for network management         | Uses built-in Docker network driver     |
| **Installation**                 | Separate binaries for each component    | Monolithic installation package         |
| **Compose Files**                | Supports Docker Compose with `podman-compose` | Native support with Docker Compose      |
| **Community and Support**        | Growing community, Red Hat supported    | Large community, Docker Inc. supported  |
| **System Requirements**          | Lightweight, fewer dependencies         | More dependencies, larger footprint     |
| **Usage in CI/CD**               | Suitable for CI/CD with rootless mode   | Widely used in CI/CD environments       |



## Install Podman
1. Install _podman_ and _podman-compose_
```shell
# Ubuntu 24.04 
sudo apt-get -y install podman podman-compose

# Ubuntu 22.04 
sudo apt-get -y install podman
sudo apt-get -y install python3-pip 
python3 -m pip install --uprade pip
python3 -m pip install --uprade wheel
python3 -m pip install --uprade setuptools 
python3 -m pip install --uprade podman-compose 
```

2. Update registry information in `/etc/containers/registries.conf`
```editorconfig
unqualified-search-registries = ["docker.io"]
```

3. Restart podman
```shell
sudo service podman restart
```

4. Login to docker and deploy AnyLog -- make sure to comment-out empty unused (ex. `OVERLAY_IP=""`) configurations
```shell
make login -f Makefile.podman ANYLOG_TYPE=${PASWORD}
make up -f Makefile.podman ANYLOG_TYPE=master
... 
```


