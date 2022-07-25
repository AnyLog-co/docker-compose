# Based on -- https://www.linuxbuzz.com/how-to-install-minikube-on-ubuntu/#:~:text=Login%20to%20your%20Ubuntu%2022.04%20%2F%20Ubuntu%2020.04,case%20it%20is%20not%20installed%20the%20refer%20below%3A
# Docker should already be installed

sudo apt-get -y update
sudo apt install curl wget apt-transport-https -y
if [[ ${TYPE} == "x86_64" ]] || [[ ${TYPE} == "amd64" ]]
then
  wget https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
elif [[ ${TYPE} == "arm64" ]]
then
  wget https://storage.googleapis.com/minikube/releases/latest/minikube-linux-arm64
else
  wget https://storage.googleapis.com/minikube/releases/latest/minikube-linux-armv
fi

sudo cp minikube-linux-amd64 /usr/local/bin/minikube
sudo chmod +x /usr/local/bin/minikube

if [[ ${TYPE} == "x86_64" ]] || [[ ${TYPE} == "amd64" ]]
then
  curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl
elif [[ ${TYPE} == "arm64" ]]
then
  curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/arm64/kubectl
else
  curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/armv/kubectl
fi

chmod +x kubectl
sudo mv kubectl /usr/local/bin

minikube start --driver=docker

# Helm based on -- https://helm.sh/docs/intro/install/
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash