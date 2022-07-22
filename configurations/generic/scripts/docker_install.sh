# directions to install docker & docker-compose on Ubuntu

# update / upgrade env
for CMD in update upgrade update
do
    sudo apt-get -y ${CMD}
done

# install docker & docker-compose
sudo apt-get -y install docker.io docker-compose

# Grant user permission to docker
USER=`whoami`
sudo groupadd docker
sudo usermod -aG docker ${USER}
newgrp docker