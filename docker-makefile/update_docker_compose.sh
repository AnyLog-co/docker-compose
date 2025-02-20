#!/bin/bash

# code requires brew install gnu-sedsed for mac

# Define input and output files
COMPOSE_FILE="docker-makefile/docker-compose-temp-base.yaml"
OUTPUT_FILE="docker-makefile/docker-compose-template.yaml"
cp docker-makefile/docker-compose-template-base.yaml ${COMPOSE_FILE}

# Check if ANYLOG_BROKER_PORT is set
if [[ -n "$ANYLOG_BROKER_PORT"  && "$ANYLOG_BROKER_PORT" != "''" && "$ANYLOG_BROKER_PORT" != '""' ]]; then
  awk -v port="\${ANYLOG_BROKER_PORT}:\${ANYLOG_BROKER_PORT}" '
/    ports:/ {print; print "      - " port; next}1' "$COMPOSE_FILE" > temp.yaml && mv temp.yaml "$COMPOSE_FILE"
fi


# Save modifications to a new file
cp "$COMPOSE_FILE" "$OUTPUT_FILE"

echo "Modified docker-compose file saved as $OUTPUT_FILE"
rm -rf ${COMPOSE_FILE}
