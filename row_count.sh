#!/usr/bin/env bash

NODE_CONN=${1:-127.0.0.1:32349}
DB_NAME=${2:-mybd}
TIMESTAMP=${3:-insert_timestamp}

# check status - fails do not continue
curl -X GET "http://${NODE_CONN}" -w "\n"

TABLES=$(curl -s -X GET "http://${NODE_CONN}" \
  -H "command: blockchain get table where dbms=${DB_NAME} bring [*][name] separator=\n" \
  -H "User-Agent: AnyLog/1.23"
)

echo "Current Timestamp (UTC): $(date -u +"%Y-%m-%d %H:%M:%S")"

for TABLE in ${TABLES}; do
  echo "${TABLE}"

  for WHERE_CONDITION in \
    "${TIMESTAMP} >= NOW() - 1 hour" \
    "period(hour, 1, now(), ${TIMESTAMP})"
  do
    echo "${TABLE} - ${WHERE_CONDITION}"

    curl -s -X GET "http://${NODE_CONN}" \
      -H "command: sql ${DB_NAME} format=table and timezone=utc and extend=(+node_name) \
SELECT MIN(${TIMESTAMP}) as min_ts, MAX(${TIMESTAMP}), COUNT(*) FROM ${TABLE} WHERE ${WHERE_CONDITION}" \
      -H "User-Agent: AnyLog/1.23" \
      -H "destination: network" \
      -w "\n"
  done
done