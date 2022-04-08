<<COMMENT
Code to deploy AnyLog-GUI 
--> Repo: https://github.com/AnyLog-co/AnyLog-GUI 
--> Docs: https://github.com/AnyLog-co/documentation/blob/master/using%20the%20gui.md
COMMENT 

CONN_IP=0.0.0.0
GUI_PORT=5000

docker run -p ${GUI_PORT}:${GUI_PORT} --name anylog-gui \
   -e CONN_IP=${CONN_IP} \
   -e GUI_PORT=${GUI_PORT} \
   -e CONFIG_FOLDER=views \
   -e CONFIG_FILE=testnet.json \
   -v anylog-gui:/app/AnyLog-GUI/views \
   --rm -d -it --detach-keys="ctrl-d" anylogco/anylog-gui:latest
   

