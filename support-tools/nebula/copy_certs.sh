#---------------------------------------------------------------------------------------------#
# The following is to be run on node instance after new certificates have been created on lighthouse
#
# Steps to create certificates for host (on lighthouse instance)
#   1. Attach to the lighthouse docker instance - `docker attach --detach-keys=ctrl-d nebula`
#   2. Make sure you're in - /app/nebula
#   3. Create host keys
#       ./nebula-cert sign -name "host" -ip "${CIDR_OVERLAY_ADDRESS}" \
#         -ca-key "$ANYLOG_PATH/nebula/ca.key" \
#         -ca-crt "$ANYLOG_PATH/nebula/ca.crt" \
#         -out-crt "$ANYLOG_PATH/nebula/configs/host.crt" \
#         -out-key "$ANYLOG_PATH/nebula/configs/host.key" \
#         -groups "anylog-node"
#   4. To validate
#     root@localhost:/app/nebula# ls -l /app/nebula/configs/
#     total 24
#     -rw------- 1 root root 243 Nov  7 03:22 ca.crt
#     -rw------- 1 root root 174 Nov  7 03:22 ca.key
#     -rw------- 1 root root 312 Nov  7 16:29 host.crt
#     -rw------- 1 root root 127 Nov  7 16:29 host.key
#     -rw------- 1 root root 300 Nov  7 03:22 lighthouse.crt
#     -rw------- 1 root root 127 Nov  7 03:22 lighthouse.key
#---------------------------------------------------------------------------------------------#
#!/bin/sh

LIGHTHOUSE_SSH_CONN="$1"
LIGHTHOUSE_SSH_PORT="${2:-22}"

FILES="ca.crt host.crt host.key"

for file in $FILES; do
    if [ -d /var/bin/nebula/configs ]; then
        # Copy directly into the configs directory
        scp -P "$LIGHTHOUSE_SSH_PORT" \
            "${LIGHTHOUSE_SSH_CONN}:/var/bin/nebula/configs/${file}" \
            /var/bin/nebula/configs/
    else
        # Copy into the current directory
        scp -P "$LIGHTHOUSE_SSH_PORT" \
            "${LIGHTHOUSE_SSH_CONN}:/var/bin/nebula/configs/${file}" \
            .
    fi
done

if [ ! -d /var/bin/nebula/configs ]; then
    echo "Certificates were copied, but /var/bin/nebula/configs does not exist."
    echo "Files are stored in the current working directory."
fi


