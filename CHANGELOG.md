---
title: Changelog
description: Notable changes to docker-compose deployment tooling, configs, and support services.
layout: page
---
<!--
## Changelog
- 2026-04-23 | Created document
-->

<!-- last-processed: 86fb6f34b35e2b349235649deb26e4bb9a5423a2 -->

This repo does not track a single AnyLog release version. Instead, users now define both the AnyLog image version and the deployment-scripts version independently in their config. The changelog below tracks changes to the **deployment tooling itself** — config structure, Makefile/script behavior, support service management, and Docker compose logic.

---

## Unreleased

<!-- Developers: add bullets below as changes land in your branch -->

---

## 2026

### April 2026

**Makefile and deployment scripting**

The Makefile for support services was refactored to run through a shell script (`docker_compose_builder.sh`), replacing the previous direct `make` invocation pattern. This change improves cross-platform support and makes the builder logic easier to extend. The corresponding README was updated to reflect the new workflow.

`REMOTE_CONN` support was added to the support services builder, allowing users to specify a remote connection endpoint for the GUI. If not provided, it falls back to `127.0.0.1`. The support Makefile now handles multi-container configurations including simultaneous PostgreSQL, MongoDB, and Grafana deployments.

A `version_control.py` script was introduced to automate changelog and version tracking. The script creates a new changelog file if none exists and raises an error if the file is already present but malformed.

**Container management improvements**

`docker attach` now works correctly for database containers. `docker exec` was extended to support all container types. A `--exec-root` option was added to allow attaching into a container as the root user, useful for debugging.

`debug busybox` support was enabled for in-container inspection.

**User-defined image versions**

Users can now specify AnyLog and deployment-scripts image versions without the `anylog-` prefix for default options, simplifying config file entries.

`remote-gui` version pinned to `1.0.0`.

**Config file changes**

Config file structure was updated. If you are upgrading, review your `node_configs.env` against the latest templates — field names and defaults may have shifted.

---

### March 2026

**Deployment process improvements**

The overall deployment process was significantly improved across March. Key changes include: better support for a local `deployment-scripts` directory, a `sys_query` logical database enabled by default for standalone nodes, and `env var` support across multiple config paths.

**Docker socket support**

Support for Docker socket pass-through was added and refined. macOS-specific socket paths were handled. A fallback for missing Docker sockets was added so deployments don't fail silently when the socket path doesn't exist.

**License key handling**

Better support for user-input license key formatting was added, including `replace exit with else` logic and improved formatting validation. A `sed` fix for `LICENSE_KEY` updates was corrected after a typo was introduced.

**msg client update**

The `run msg client` configuration was updated in the deployment templates to reflect current parameter names.

**Version logic**

Version update logic was corrected after a regression was introduced. The version workflow now triggers reliably on push.

**Nebula overlay**

Nebula overlay network config was reorganized. The Nebula config was moved out of the core deployment directory into its own location.

**Config cleanup (March 30)**

A round of cleanup removed unused files, reset configs to defaults, and updated the README.

---

### January–February 2026

**Makefile rewrite**

The Makefile was significantly reworked to support both `docker` and `podman`, clean up `make` targets, and add a proper `help` target. Empty file detection was added.

**Config reorg**

Node configs were reorganized into a cleaner structure supporting standalone, multi-node (operator/publisher split), and HA operator topologies. Single-file vs. multi-file config logic was separated. Publisher node configs were added.

**Ollama example**

An Ollama example configuration was added under `support/`.

**Thread configs**

Thread configuration params were updated across node types.

---

## 2025

2025 focused on **networking, Kubernetes removal, support service expansion, and config stabilization**. The overlay network (Nebula) was moved outside the core deployment. Remote GUI support was added and iterated. Podman/Docker dual-support was formalized. License key management was introduced. ARM/AMD image configs were merged. A significant cleanup of unused Docker files and legacy configs happened in September. The `SYNC_TIME` parameter was renamed to `BLOCKCHAIN_SYNC`.

| Date | Summary |
|---|---|
| 2025-12 | Docker updates; license key handling added |
| 2025-11 | Nebula moved outside core; merge cleanup |
| 2025-10 | Remote GUI added; `enable_remote_cli` enables both CLI and GUI; macOS support; Windows README added |
| 2025-09 | ARM/AMD config merge; legacy Docker files removed; path and README cleanup; `BLOCKCHAIN_SYNC` rename |
| 2025-08 | Version bump `1.3.X → 1.4.2508`; Docker image path updates |
| 2025-05 | EtherNet/IP config added; publisher-only config; NIC type config |
| 2025-04 | New Makefile; OPC-UA documentation; `docker-compose` restart support; Remote CLI in manual mode |
| 2025-03 | License change; `CONTAINER_CMD` support; `SYNC_TIME → BLOCKCHAIN_SYNC` rename |
| 2025-02 | Networking improvements (Linux vs. other OS); template support for broker; auto docker-compose builder; OpenBao configs added |
| 2025-01 | Network configs; Podman/Docker support; health check removal; Dockerfiles restructured |

---

## 2024

2024 focused on **Kubernetes removal, blockchain config improvements, Nebula overlay iteration, and Remote CLI/GUI integration**. The Kubernetes configs were moved to a dedicated `deploy-k8s` repo. Blockchain source was renamed from `platform` to `BLOCKCHAIN_SOURCE`. Overlay network (Nebula) was extensively tested and iterated on. Docker compose configs were aligned across AnyLog, EdgeLake, and OpenHorizon deployments.

| Date | Summary |
|---|---|
| 2024-11 | Version tag `1.3.2411`; config cleanup |
| 2024-10 | `BLOCKCHAIN_SOURCE` param rename; Nebula/overlay network iteration; `debug_mode` config added; new contract/blockchain configs |
| 2024-09 | Remote CLI/GUI support added; configs for `DEBUG_MODE`; license and ARM64 param updates |
| 2024-07 | Docker compose configs; Makefile fixes; Podman support added |
| 2024-06 | Podman support; Makefile minor changes |
| 2024-05 | Version tag `1.3.2405`; Windows docker-compose; network bridge mode |
| 2024-04 | K8s configs moved to `deploy-k8s`; `edgelake → anylog` rename in configs |
| 2024-03 | Open source docker-compose for master node |
| 2024-02 | Nebula overlay iteration; k8s testing; cluster networking configs |
| 2024-01 | Makefile revert; sample docker configs reset |

---

*For full commit-level history, run `git log` or browse the repository on GitHub.*