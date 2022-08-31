# Based on -- https://www.linuxbuzz.com/how-to-install-minikube-on-ubuntu/#:~:text=Login%20to%20your%20Ubuntu%2022.04%20%2F%20Ubuntu%2020.04,case%20it%20is%20not%20installed%20the%20refer%20below%3A

# update / upgrade env
for CMD in update upgrade update
do
    sudo apt-get -y ${CMD}
done
# install docker
sudo apt-get -y install docker.io docker-compose

# Grant user permission to docker
USER=`whoami`
sudo groupadd docker
sudo usermod -aG docker ${USER}
newgrp docker

# requirements for kubectl
sudo apt-get install -y apt-transport-https ca-certificates curl
# Download the Google Cloud public signing key
sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg

# Add the Kubernetes apt repository
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

# Update apt package index with the new repository and install kubectl
sudo apt-get update
sudo apt-get install -y kubectl

# download minikube - replace amd64 with arm64 for RPI4
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64

# Install minikube
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# install helm
sudo snap instal helm --clasic

# update / upgrade env
for CMD in update upgrade update
do
    sudo apt-get -y ${CMD}
done

# start minikube
minikube start
# update / upgrade env
for CMD in update upgrade update
do
    sudo apt-get -y ${CMD}
done
# install docker
sudo apt-get -y install docker.io docker-compose

# Grant user permission to docker
USER=`whoami`
sudo groupadd docker
sudo usermod -aG docker ${USER}
newgrp docker

# requirements for kubectl
sudo apt-get install -y apt-transport-https ca-certificates curl
# Download the Google Cloud public signing key
sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg

# Add the Kubernetes apt repository
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

# Update apt package index with the new repository and install kubectl
sudo apt-get update
sudo apt-get install -y kubectl

# download minikube - replace amd64 with arm64 for RPI4
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64

# Install minikube
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# install helm
sudo snap instal helm --clasic

# update / upgrade env
for CMD in update upgrade update
do
    sudo apt-get -y ${CMD}
done

# start minikube
minikube start
