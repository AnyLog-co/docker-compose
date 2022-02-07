if [ $# -eq 1 ]
then
   IP_ADDRESS=${1}
else
   echo "Missing IP address"
   exit 1
fi


kubectl port-forward --address ${IP_ADDRESS} service/database 5432:5432 &> /dev/null &
kubectl port-forward --address ${IP_ADDRESS} service/grafana 3000:3000 &> /dev/null &
kubectl port-forward --address ${IP_ADDRESS} service/remote-cli 8000:8000 &> /dev/null &
kubectl port-forward --address ${IP_ADDRESS} service/anylog-gui 5000:5000 &> /dev/null &
