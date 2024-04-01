# directions to install docker & docker-compose on Ubuntu

# update / upgrade env
for CMD in update upgrade update
do
    sudo apt-get -y ${CMD}
done

# install docker & docker-compose
sudo snap install docker

# Grant user permission to docker
USER=`whoami`
sudo groupadd docker
sudo usermod -aG docker ${USER}
newgrp docker

# Install make and docker-compose
sudo apt-get -y install docker-compose make

# update / upgrade env
for CMD in update upgrade update
do
    sudo apt-get -y ${CMD}
done
