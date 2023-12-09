export ANYLOG_SERVER_PORT=`grep "ANYLOG_REST_PORT" anylog_configs.env |  awk -F "=" '{print $2}'`
export ANYLOG_REST_PORT=`grep "ANYLOG_SERVER_PORT" anylog_configs.env |  awk -F "=" '{print $2}'`

if [[ ! `grep "ANYLOG_BROKER_PORT" advance_configs.env |  awk -F "=" '{print $2}'` = '""' ]] ; then
  export ANYLOG_BROKER_PORT=`grep "ANYLOG_BROKER_PORT" advance_configs.env |  awk -F "=" '{print $2}'`
  docker-compose -f docker-compose-broker.yml up -d
else
  docker-compose -f docker-compose.yml up -d
fi
