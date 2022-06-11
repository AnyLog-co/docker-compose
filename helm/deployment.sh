cd anylog
printf "\n\t -- Deploy Master -- \n"
helm fetch https://github.com/AnyLog-co/deployments/raw/nvidia/helm/packages/anylog-master-1.0220301.tgz
helm install anylog-master-1.0220301.tgz --generate-name

sleep 15

printf "\n\t -- Deploy Operator1 --\n"
helm fetch https://github.com/AnyLog-co/deployments/raw/nvidia/helm/packages/anylog-operator1-1.0220301.tgz
helm install anylog-operator1-1.0220301.tgz --generate-name

sleep 10

printf "\n\t -- Deploy Operator2 --\n"
helm fetch https://github.com/AnyLog-co/deployments/raw/nvidia/helm/packages/anylog-operator2-1.0220301.tgz
helm install anylog-operator2-1.0220301.tgz --generate-name

python3 $HOME/anylog/data_generator.py

sleep 60

printf "\n\t -- Deploy Query -- \n"
helm fetch https://github.com/AnyLog-co/deployments/raw/nvidia/helm/packages/anylog-query-1.0220301.tgz
helm install anylog-query-1.0220301.tgz --generate-name

cd $HOME


