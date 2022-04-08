<<COMMENT
Code to deploy Remote-CLI
--> Repo: https://github.com/AnyLog-co/Remote-CLI
COMMENT 

CONN_IP=0.0.0.0
GUI_PORT=8000

docker run -p ${GUI_PORT}:${GUI_PORT} --name remote-cli \
   -e CONN_IP=${CONN_IP} \
   -e GUI_PORT=${GUI_PORT} \
   -v remote-cli:/app/Remote-CLI/anylog_query/static/json \
   --rm -d -it --detach-keys="ctrl-d" anylogco/remote-cli:latest
   

