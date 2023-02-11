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

# update / upgrade env
for CMD in update upgrade update
do
    sudo apt-get -y ${CMD}
done
