#!/usr/bin/env bash

# select template Dockerfile
COMPOSE_FILE="docker-makefiles/docker-compose-template.yaml"
TEMPLATE_COMPOSE_FILE="docker-makefiles/docker-compose-template-base.yaml"

# Switch to ports template if not Linux
#if [[ "$(uname -s)" != "Linux" ]] ; then
#  TEMPLATE_COMPOSE_FILE="docker-makefiles/docker-compose-template-ports-base.yaml"
#fi

# Check if the chosen template exists
if [[ ! -f "$TEMPLATE_COMPOSE_FILE" ]] ; then
  echo "Error: Failed to locate path for $TEMPLATE_COMPOSE_FILE"
  exit 1
else
  cp "$TEMPLATE_COMPOSE_FILE" "$COMPOSE_FILE"
fi

# If using the ports template and ANYLOG_BROKER_PORT is set
if [[ "${TEMPLATE_COMPOSE_FILE}" == *"ports"* ]] && \
   [[ -n "${ANYLOG_BROKER_PORT}" && "${ANYLOG_BROKER_PORT}" != "''" && "${ANYLOG_BROKER_PORT}" != '""' ]]; then

   awk -v port="${ANYLOG_BROKER_PORT}:${ANYLOG_BROKER_PORT}" '
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


  # Enable Remote-GUI
  # Fetch current public IP address
  PUBLIC_IP=$(curl -s https://checkip.amazonaws.com)
  if [[ -z "$PUBLIC_IP" ]]; then
    echo "⚠️  Warning: Unable to fetch public IP. Using 127.0.0.1 as fallback."
    PUBLIC_IP="127.0.0.1"
  fi

  # Add remote-gui volumes to the bottom of volumes section
  awk -v vol1="image-vol:/app/CLI/local-cli-backend/static/" -v vol2="usr-mgm-vol:/app/CLI/local-cli/backend/usr-mgm/" '
/    volumes:/ && !vol_found {
  print;
  print "      - " vol1;
  print "      - " vol2;
  vol_found=1;
  next
}
!/  image-vol:/ && !/  usr-mgm-vol:/ {print}
END {
  print "  image-vol:";
  print "  usr-mgm-vol:";
}' "$COMPOSE_FILE" > temp.yaml && mv temp.yaml "$COMPOSE_FILE"

  # Add remote-gui service to services section (with dynamic IP)
  awk -v public_ip="$PUBLIC_IP" '/services:/ {
    print;

    print "  remote-gui:";
    print "    image: anylogco/remote-gui:beta";
    print "    container_name: remote-gui";
    print "    restart: always";
    print "    stdin_open: true";
    print "    tty: true";
    print "    ports:";
    print "      - 3001:3001";
    print "      - 8000:8000";
    print "    environment:";
    print "      - REACT_APP_API_URL=http://" public_ip ":8000";
    print "    volumes:";
    print "      - image-vol:/app/CLI/local-cli-backend/static/";
    print "      - usr-mgm-vol:/app/CLI/local-cli/backend/usr-mgm/";
    next
}1' "$COMPOSE_FILE" > temp.yaml && mv temp.yaml "$COMPOSE_FILE"
fi



## Save modifications to a new file
#cp "$COMPOSE_FILE" "$OUTPUT_FILE"
#
#echo "Modified docker-compose file saved as $OUTPUT_FILE"
#rm -rf ${COMPOSE_FILE}