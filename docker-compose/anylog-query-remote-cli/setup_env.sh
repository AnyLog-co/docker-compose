export ANYLOG_SERVER_PORT=`cat anylog_configs.env | grep "ANYLOG_REST_PORT" | awk -F "=" '{print $2}'`
export ANYLOG_REST_PORT=`cat anylog_configs.env | grep "ANYLOG_SERVER_PORT" |  awk -F "=" '{print $2}'`

docker-compose up -d
