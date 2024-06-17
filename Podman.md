# Podman

## Install Podman 
1. Install _podman_ and _podman-compose_
```shell
sudo apt-get -y install podman podman-compose
```

2. Update registry information in `/etc/containers/registries.conf`
```editorconfig
unqualified-search-registries = ["docker.io"]
```

3. Restart podman
```shell
sudo service podman restart
```

4. Login to docker and deploy AnyLog

# Podman vs Docker

