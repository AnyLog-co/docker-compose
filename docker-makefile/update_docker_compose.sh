#!/bin/bash

# code requires brew install gnu-sedsed for mac

# Define input and output files
COMPOSE_FILE="docker-makefile/docker-compose-template-base.yaml"
OUTPUT_FILE="docker-makefile/docker-compose-template.yaml"

# Check if overlay is enabled
if [[ "$OVERLAY" == "true" ]]; then
    echo "Adding overlay settings..."
    sed -i '/container_name: anylog-${ANYLOG_TYPE}/a \
    cap_add:\n      - NET_ADMIN\n    devices:\n      - "/dev/net/tun:/dev/net/tun"\n    volumes:\n      - nebula-overlay:/app/nebula' "$COMPOSE_FILE"
    sed -i '/    ports:/a \      - "4242:4242/udp"' "$COMPOSE_FILE"
fi

# Check if ANYLOG_BROKER_PORT is set

if [[ -n "$ANYLOG_BROKER_PORT" ]]; then
  echo $ANYLOG_BROKER_PORT
  awk -v port="${ANYLOG_BROKER_PORT}:${ANYLOG_BROKER_PORT}" '
/    ports:/ {print; print "      - " port; next}1' "$COMPOSE_FILE" > temp.yaml && mv temp.yaml "$COMPOSE_FILE"

fi


# Check if REMOTE_CLI is enabled
if [[ "$REMOTE_CLI" == "true" ]]; then
    echo "Adding remote-cli settings..."
    sed -i '/container_name: anylog-${ANYLOG_TYPE}/a \
    volumes:\n      - remote-cli-current:/app/Remote-CLI/djangoProject/static/blobs/current/' "$COMPOSE_FILE"

    cat <<EOL >> "$COMPOSE_FILE"
  remote-cli:
    image: anylogco/remote-cli:latest
    container_name: remote-cli
    restart: always
    stdin_open: true
    tty: true
    ports:
      - 31800:31800
    environment:
      - CONN_IP=0.0.0.0
      - CLI_PORT=31800
    volumes:
      - remote-cli:/app/Remote-CLI/djangoProject/static/json
      - remote-cli-current:/app/Remote-CLI/djangoProject/static/blobs/current/
EOL
fi

# Save modifications to a new file
cp "$COMPOSE_FILE" "$OUTPUT_FILE"

echo "Modified docker-compose file saved as $OUTPUT_FILE"
