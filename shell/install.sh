# Update env
cd /tmp/
for CMD in update upgrade update ;
do
  sudo apt-get -y ${CMD}
done

# prerequisites
sudo apt-get -y install curl apt-transport-https ca-certificates

# Install / Download requirements
## docker
sudo apt-get -y install docker.io docker-compose

## docker permissions
USER=`whoami`
sudo groupadd docker
sudo usermod -aG docker ${USER}
newgrp docker

# kompose
curl -L https://github.com/kubernetes/kompose/releases/download/v1.26.1/kompose-linux-amd64 -o kompose
chmod +x kompose
sudo install ./kompose /usr/local/bin/kompose

# kubectl
curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubectl

# minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# install helm - https://helm.sh/docs/intro/install/
curl https://baltocdn.com/helm/signing.asc | sudo apt-key add -
sudo apt-get install apt-transport-https --yes
echo "deb https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm

# Update env
for CMD in update upgrade update ;
do
  sudo apt-get -y ${CMD}
done

cd $HOME
rm -rf /tmp/*




