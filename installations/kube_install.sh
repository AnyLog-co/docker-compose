<< comment
The following install microk8s via snap (tested) on Ubuntu

When deploying a node - if fails with error: "kubelet does not have ClusterDNS IP configured in Microk8s", add the
following lines to `/var/snap/microk8s/current/args/kubelet`
--cluster-dns=A.B.C.D
--cluster-domain=cluster.local
comment


# update / upgrade env
for CMD in update upgrade update
do
    sudo apt-get -y ${CMD}
done

# install microk8s
sudo snap install microk8s --classic
sudo microk8s.start

# set alias for helm and kubectl
sudo snap alias microk8s.kubectl kubectl
sudo snap alias microk8s.helm helm

# Grant user permission to docker
USER=`whoami`
sudo usermod -a -G microk8s ${USER}
newgrp microk8s

# enable storage
microk8s enable storage


# update / upgrade env
for CMD in update upgrade update
do
    sudo apt-get -y ${CMD}
done
