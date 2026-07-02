# AnyLog Network Configuration

AnyLog's network configuration is split across two independent layers. Understanding
the distinction is important before deploying — misconfiguring one layer does not
automatically fix the other.

---

## Layer 1 — Docker Network Topology (`NETWORK_TYPE`)

Controls **how the container is connected to the host and to other containers**.
This is a Docker-level concern and has no effect on how AnyLog itself resolves
or advertises its IP address.

Set in `node_configs.env`:

```bash
NETWORK_TYPE=""
```

| Value | Template used | When to use |
|---|---|---|
| *(empty)* | auto-detect | Recommended default — host on Linux/WSL, ports on Windows/macOS |
| `network` | `network_mode: host` | Linux/WSL only — container shares the host network stack directly |
| `ports` | explicit port mapping | Windows, macOS, or Linux when host networking is unavailable/undesirable |
| `<custom-name>` | external named network | Pre-created Docker network (bridge, overlay, macvlan, etc.) |

### How to choose

```
Are you on Linux or WSL?
├── Yes → leave NETWORK_TYPE="" (auto-selects host mode)
│          or set NETWORK_TYPE=network to force it explicitly
└── No (Windows / macOS)
    ├── Single machine → leave NETWORK_TYPE="" (auto-selects ports mode)
    │                    or set NETWORK_TYPE=ports to force it
    └── Multi-machine / VPN / Swarm → create an external network first,
                                      then set NETWORK_TYPE=<network-name>
```

### Creating an external network

For single-host bridge isolation:
```bash
docker network create anylog-net
NETWORK_TYPE=anylog-net
```

For multi-host overlay (Swarm):
```bash
docker network create --scope=swarm --attachable -d overlay anylog-net
NETWORK_TYPE=anylog-net
```

An overlay network allows AnyLog nodes on **different physical machines** to
communicate by container name as if they were on the same LAN, without exposing
ports to the host. Each node that sets `NETWORK_TYPE=anylog-net` joins the same
virtual network regardless of which machine it runs on.

> **Docs:** https://docs.docker.com/reference/cli/docker/network/create/

---

## Layer 2 — AnyLog Network Identity

Controls **how AnyLog resolves and advertises its own IP address** within
whatever Docker topology Layer 1 established. These settings live in the
`#--- Networking ---` section of `node_configs.env`.

```bash
NIC_TYPE=""       # NIC to resolve the node's local IP (e.g. eth0, lo)
OVERLAY_IP=""     # Override the advertised IP (VPN, overlay, or NAT scenarios)
EXTERNAL_DNS=""   # External DNS server for outbound resolution
DNS_DOMAIN=""     # Local domain suffix to append to hostnames (e.g. example.com)
DNS=""            # Full path to the machine's local DNS file
ENABLE_DNS=false  # Enable DNS-based node resolution within AnyLog
```

These settings affect the IP address that AnyLog **registers in the blockchain**
(the distributed metadata layer) and **binds its TCP/REST/Broker ports to**.
Getting this wrong means other nodes can see your node in the metadata but
cannot reach it.

### How each variable is used

**`NIC_TYPE`** — AnyLog will resolve its IP by inspecting this network interface.
Useful when the host has multiple NICs and you need to pin to a specific one.
```bash
NIC_TYPE=eth0     # use the eth0 interface IP
NIC_TYPE=lo       # use loopback (local testing only)
```

**`OVERLAY_IP`** — Overrides the resolved IP entirely. AnyLog will advertise
this address to other nodes regardless of what `NIC_TYPE` resolves to. Use this
when the container's internal IP is not reachable from the outside world:
- VPN/overlay networks where nodes reach each other via a virtual IP
- NAT/cloud environments where the public IP differs from the interface IP
- Swarm overlay where each node gets a virtual IP on the overlay subnet

**`TCP_BIND` / `REST_BIND` / `BROKER_BIND`** — controls whether each protocol
binds to the resolved IP specifically (`true`) or to all interfaces (`false`).
```bash
TCP_BIND=true     # bind TCP only to the resolved/overlay IP
REST_BIND=false   # bind REST to 0.0.0.0 (accept from any interface)
BROKER_BIND=false # bind Broker to 0.0.0.0
```

---

## How Nodes Communicate

AnyLog uses three port-based protocols. Each node advertises all three in the
blockchain metadata so other nodes know how to reach it.

```
ANYLOG_SERVER_PORT   — TCP  — node-to-node messaging (queries, sync, HA)
ANYLOG_REST_PORT     — REST — external clients, Grafana, Remote-GUI
ANYLOG_BROKER_PORT   — MQTT — southbound data ingestion (sensors, devices)
```

### Communication flow by topology

**`network_mode: host` (Linux/WSL)**
```
Node A (host 192.168.1.10)          Node B (host 192.168.1.20)
┌──────────────────────────┐        ┌──────────────────────────┐
│  AnyLog                  │        │  AnyLog                  │
│  TCP  :32148  ───────────┼────────┼──▶ 192.168.1.10:32148    │
│  REST :32149             │        │  REST :32149             │
│  Broker :32150           │        │  Broker :32150           │
└──────────────────────────┘        └──────────────────────────┘
Container shares host network stack — no port mapping needed.
OVERLAY_IP not needed unless behind NAT.
```

**`ports` mode (Windows/macOS)**
```
Host machine (192.168.1.10)
┌─────────────────────────────────────────┐
│  Docker Desktop                         │
│  ┌───────────────────────────────────┐  │
│  │  AnyLog container                 │  │
│  │  TCP  :32148 ◀── mapped ──▶ :32148│  │
│  │  REST :32149 ◀── mapped ──▶ :32149│  │
│  │  Broker :32150 ◀─ mapped ──▶:32150│  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
Container IP is internal — other nodes must use the HOST machine's IP.
Set OVERLAY_IP=192.168.1.10 so AnyLog advertises the reachable address.
```

**Custom overlay network (multi-host Swarm)**
```
Host A (192.168.1.10)               Host B (192.168.1.20)
┌──────────────────────────┐        ┌──────────────────────────┐
│  AnyLog container        │        │  AnyLog container        │
│  overlay IP: 10.0.0.2    │        │  overlay IP: 10.0.0.3    │
│                          │        │                          │
│  OVERLAY_IP=10.0.0.2     │        │  OVERLAY_IP=10.0.0.3     │
└────────────┬─────────────┘        └─────────────┬────────────┘
             │          anylog-net (overlay)        │
             └──────────────────────────────────────┘
Nodes communicate via their overlay IPs across physical hosts.
OVERLAY_IP must be set to the virtual overlay address, not the host IP.
```

---

## Common Scenarios

### Single node, Linux server (simplest)
```bash
NETWORK_TYPE=""          # auto: host mode
NIC_TYPE=eth0
OVERLAY_IP=""            # not needed, host IP is directly reachable
```

### Single node, developer laptop (Windows/macOS)
```bash
NETWORK_TYPE=ports       # or leave empty, auto-detects
OVERLAY_IP=192.168.1.50  # your laptop's LAN IP — run: ipconfig getifaddr en0 (Mac)
                         #                                  ipconfig (Windows → IPv4)
```

### Multi-node, same LAN, Linux hosts
```bash
NETWORK_TYPE=""          # host mode on each machine
NIC_TYPE=eth0            # same NIC name on all hosts (adjust if different)
OVERLAY_IP=""
LEDGER_CONN=192.168.1.10:32148   # master node's host IP
```

### Multi-node, Swarm overlay (different machines or cloud)
```bash
# Run once on Swarm manager:
# docker network create --scope=swarm --attachable -d overlay anylog-net

NETWORK_TYPE=anylog-net
OVERLAY_IP=10.0.0.2      # this node's IP on the overlay subnet
LEDGER_CONN=10.0.0.5:32148  # master node's overlay IP
```

---

## Quick Reference

| Scenario | `NETWORK_TYPE` | `OVERLAY_IP` | `NIC_TYPE` |
|---|---|---|---|
| Linux, single node | *(empty)* | *(empty)* | `eth0` or *(empty)* |
| Windows/macOS, single node | `ports` or *(empty)* | host LAN IP | *(empty)* |
| Multi-node, same LAN | *(empty)* | *(empty)* | `eth0` |
| Multi-node, VPN/overlay | `<network-name>` | overlay/VPN IP | *(empty)* |
| Multi-node, cloud NAT | `ports` or `<network-name>` | public/elastic IP | *(empty)* |