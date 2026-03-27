# Nebula Overlay Network

AnyLog uses overlay networks to allow nodes distributed across separate physical subnetworks to communicate as if they
share a single network. This guide covers [Nebula](https://github.com/slackhq/nebula), an open-source mutually
authenticated peer-to-peer overlay network originally developed by Slack and now maintained by
[Defined](https://www.defined.net/).

Nebula uses the [Noise Protocol Framework](https://noiseprotocol.org/) and certificate-based identity — each node's
overlay IP, name, and group membership are asserted by a Certificate Authority you control.

> **Note:** Nebula is a standalone service and is **not** managed by the support `Makefile`.

**References**
- [GitHub — slackhq/nebula](https://github.com/slackhq/nebula)
- [Nebula Documentation](https://nebula.defined.net/docs)
- [Defined.net](https://www.defined.net/)
- [Configuring Overlay with AnyLog](https://github.com/oshadmon/nebula-anylog/blob/main/Configuring%20Overlay%20with%20AnyLog.md)

---

## Table of Contents

- [Terminology](#terminology)
- [Certificate and Key Files](#certificate-and-key-files)
- [Deploying an Overlay](#deploying-an-overlay)
  - [1. Prepare Both Machines](#1-prepare-both-machines)
  - [2. Deploy the Lighthouse](#2-deploy-the-lighthouse)
  - [3. Generate Host Keys (on the Lighthouse)](#3-generate-host-keys-on-the-lighthouse)
  - [4. Deploy a Host Node](#4-deploy-a-host-node)
- [Troubleshooting](#troubleshooting)

---

## Terminology

| Term | Description |
|---|---|
| **Lighthouse** | A Nebula host that tracks all other nodes and helps them find each other. Acts as the rendezvous point for the overlay. Multiple lighthouses are supported for redundancy. |
| **Host** | Any single node in the network (server, laptop, edge device). Each host has its own private key used to authenticate when Nebula tunnels are established. |
| **Certificate Authority (CA)** | Two files — a CA certificate (`ca.crt`) and its private key (`ca.key`). The CA certificate is distributed to and trusted by every host. The private key stays offline/secure and is only used to sign new node certificates. |

---

## Certificate and Key Files

### Lighthouse

| File | Purpose | Created |
|---|---|---|
| `ca.crt`, `ca.key` | Root CA certificate and key | Auto-created on first lighthouse deploy if absent |
| `lighthouse.crt`, `lighthouse.key` | Node certificate for the lighthouse | Auto-created on first lighthouse deploy if absent |
| `node.yml` | Runtime configuration | Auto-generated from `nebula_configs.env` |

### Host

| File | Purpose | Created |
|---|---|---|
| `ca.crt` | CA certificate (shared from lighthouse) | Created on lighthouse, copied to host |
| `host.crt`, `host.key` | Host node certificate and key | Created on lighthouse, copied to host |
| `node.yml` | Runtime configuration | Auto-generated from `nebula_configs.env` |

---

## Deploying an Overlay

### 1. Prepare Both Machines

Run the following on **every machine** (lighthouse and all hosts):

```shell
# Clone the repo
cd $HOME
git clone https://github.com/oshadmon/nebula-anylog
cd nebula-anylog

# Create the config directory
sudo mkdir -p /var/bin/nebula/configs
sudo chown -R root:root /var/bin/nebula
sudo chmod -R 755 /var/bin/nebula
```

If you already have existing certificates, copy them into `/var/bin/nebula/configs` before proceeding.

---

### 2. Deploy the Lighthouse

Edit `nebula_configs.env` in the cloned repo directory:

```shell
IS_LIGHTHOUSE=true

CIDR_OVERLAY_ADDRESS=10.10.1.1/24   # CIDR block for the entire overlay
LIGHTHOUSE_IP=10.10.1.1             # Overlay IP of the lighthouse
LIGHTHOUSE_NODE_IP=10.0.0.169       # Physical (public/LAN) IP of the lighthouse
OVERLAY_IP=10.10.1.1                # This node's overlay IP
```

Start Nebula:

```shell
docker compose -f docker-compose.yml up -d
```

Verify the overlay interface is up:

```shell
ifconfig nebula1
# Expected: inet 10.10.1.1  netmask 255.255.255.0
```

---

### 3. Generate Host Keys (on the Lighthouse)

These steps run **inside the lighthouse container**.

```shell
# Attach to the lighthouse container
docker attach --detach-keys=ctrl-d nebula

# Confirm working directory
pwd    # should be /app/nebula

# Generate the host certificate
./nebula-cert sign -name "host" -ip "${CIDR_OVERLAY_ADDRESS}" \
    -ca-key  "$ANYLOG_PATH/nebula/ca.key" \
    -ca-crt  "$ANYLOG_PATH/nebula/ca.crt" \
    -out-crt "$ANYLOG_PATH/nebula/configs/host.crt" \
    -out-key "$ANYLOG_PATH/nebula/configs/host.key" \
    -groups  "anylog-node"
```

Verify the keys were created (on the lighthouse host, outside docker at `/var/bin/nebula/configs`):

```shell
ls -l /var/bin/nebula/configs/
# ca.crt  ca.key  host.crt  host.key  lighthouse.crt  lighthouse.key
```

Copy these three files to each host machine:
- `ca.crt`
- `host.crt`
- `host.key`

---

### 4. Deploy a Host Node

On the **host machine**, with the three key files placed in `/var/bin/nebula/configs`, edit `nebula_configs.env`:

```shell
IS_LIGHTHOUSE=false

CIDR_OVERLAY_ADDRESS=10.10.1.2/24   # This host's CIDR address
LIGHTHOUSE_IP=10.10.1.1             # Overlay IP of the lighthouse
LIGHTHOUSE_NODE_IP=10.0.0.169       # Physical IP of the lighthouse
OVERLAY_IP=10.10.1.2                # This node's overlay IP
```

Start Nebula:

```shell
docker compose -f docker-compose.yml up -d
```

Verify the overlay interface is up:

```shell
ifconfig nebula1
# Expected: inet 10.10.1.2  netmask 255.255.255.0
```

---

## Troubleshooting

**`nebula1` interface not created (Linux)**

Nebula requires the TUN/TAP kernel module. Enable it with:

```shell
sudo modprobe tun
```

To persist across reboots, add `tun` to `/etc/modules`.

**Host can't reach lighthouse**

- Confirm `LIGHTHOUSE_NODE_IP` is the correct physical IP (not the overlay IP).
- Check that UDP port `4242` (Nebula's default) is open on the lighthouse firewall.
- Verify `ca.crt` on the host was signed by the same CA as the lighthouse.

**Certificate errors on startup**

- Ensure `host.crt` / `host.key` were generated for the correct overlay IP.
- The `ca.crt` on every node must match the CA that signed all certificates.