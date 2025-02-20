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

# Enable Remote-CLI
if [[ "${REMOTE_CLI}" == "true" ]] ; then
  # Add remote-cli volume to the bottom of volumes section
  awk -v volume="remote-cli:/app/Remote-CLI/djangoProject/static/json" '
/    volumes:/ && !vol_found {print; print "      - " volume; vol_found=1; next}
!/  remote-cli:/ {print}
END {print "  remote-cli:"}' "$COMPOSE_FILE" > temp.yaml && mv temp.yaml "$COMPOSE_FILE"

  # Add volume entry in the services section
  awk -v volume="remote-cli-current:/app/Remote-CLI/djangoProject/static/blobs/current/" '
/    volumes:/ && !vol_found {print; print "      - " volume; vol_found=1; next}
!/  remote-cli-current:/ {print}
END {print "  remote-cli-current:"}' "$COMPOSE_FILE" > temp.yaml && mv temp.yaml "$COMPOSE_FILE"

  # Add remote-cli service to services section
  awk '/services:/ {
    print;
    print "  remote-cli:";
    print "    image: anylogco/remote-cli:latest";
    print "    container_name: remote-cli";
    print "    restart: always";
    print "    stdin_open: true";
    print "    tty: true";
    print "    ports:";
    print "      - 31800:31800";
    print "    environment:";
    print "      - CONN_IP=0.0.0.0";
    print "      - CLI_PORT=31800";
    print "    volumes:";
    print "      - remote-cli:/app/Remote-CLI/djangoProject/static/json";
    print "      - remote-cli-current:/app/Remote-CLI/djangoProject/static/blobs/current/";
    next
}1' "$COMPOSE_FILE" > temp.yaml && mv temp.yaml "$COMPOSE_FILE"

fi



# Save modifications to a new file
cp "$COMPOSE_FILE" "$OUTPUT_FILE"

echo "Modified docker-compose file saved as $OUTPUT_FILE"
rm -rf ${COMPOSE_FILE}
