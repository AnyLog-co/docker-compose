# Based on -- https://www.linuxbuzz.com/how-to-install-minikube-on-ubuntu/#:~:text=Login%20to%20your%20Ubuntu%2022.04%20%2F%20Ubuntu%2020.04,case%20it%20is%20not%20installed%20the%20refer%20below%3A

# update / upgrade env
for CMD in update upgrade update
do
    sudo apt-get -y ${CMD}
done

sudo snap install microk8s --classic
sudo microk8s.start

sudo snap alias microk8s.kubectl kubectl
sudo snap alias microk8s.helm helm

# Grant user permission to docker
USER=`whoami`
sudo usermod -a -G microk8s ${USER}
newgrp microk8s

