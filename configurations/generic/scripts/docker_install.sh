sudo apt-get -y install update
sudo apt-get -y install curl apt-transport-https ca-certificates
sudo apt-get -y install docker.io docker-compose

USER=`whoami`
sudo groupadd docker
sudo usermod -aG docker ${USER}
newgrp docker