---
title: Changelog
description: Release history and notable changes for AnyLog deployment scripts.
layout: page
---

<!-- last-processed: 2b9a13e -->

<!-- Developers: add bullets below as changes land in your branch -->
---

## 2026

## v.1.5.2606 (May 2026 · 2b9a13e · 2026-05-25)

### ✨ New Features
- **Default node configs**: baseline default configurations added for all node types (Master, Query, Operator, Publisher, Generic, Standalone)
- **Syslog Makefile support**: `make` targets added for syslog inclusion across deployments
- **PostgreSQL and MongoDB Makefiles**: dedicated support-service Makefiles added for postgres and mongo (#27)
- **`--exec-root` option**: attach into any container as the root user for debugging
- **`debug busybox` support**: enabled for in-container inspection
- **`REMOTE_CONN` support**: users can specify a remote connection endpoint for the GUI; falls back to `127.0.0.1` if not set
- **`remote-gui` version pinned**: locked to `1.0.0` for stability
- **Ollama example**: Ollama support-service configuration added under `support/`
- **License key from file**: if a license key is provided via file, the license registration process is now skipped automatically
- **User-defined image versions**: AnyLog and deployment-scripts versions can now be specified without the `anylog-` prefix

### 🐛 Bug Fixes
- Fixed `docker attach` for database containers
- Fixed accidentally removed `psql` support service entry
- Fixed `sed` command for `LICENSE_KEY` updates — multiple passes to correct typo, regex escaping, quote normalization, and backup-file handling (Mark Davidson, 2026-03-24)
- Fixed `sedi` function to accept multiple arguments
- Fixed license server IP address in Makefile
- Fixed quotes in license key handling
- Fixed volume issues in `deploy.sh`
- Fixed `setup.cfg` version update for release

### 🔧 Improvements
- `docker exec` extended to support all container types
- Support Makefile now handles multi-container configurations (PostgreSQL + MongoDB + Grafana simultaneously)
- `remote-gui` hostname support added to Docker configs
- Master node monitoring (`bmonitoring`) support added
- Standalone node: `sys_query` logical database enabled by default; `REMOTE_CONN` integrated
- Config files cleaned up and aligned to Mark's template structure across all node types
- `replace exit with else` logic added for license key formatting validation
- License key generator consolidated to a single location; license key info merged into a single file
- `msg client` configuration updated across deployment templates
- Docker socket pass-through support added and refined (Linux, macOS, fallback for missing socket)
- Support for local `deployment-scripts` directory path
- `docker compose builder` (`docker_compose_builder.sh`) introduced for support services; README updated
- Personal scripts can now be injected into the Docker container at deploy time
- Customer archive code removed from main deployment path
- Unused Docker env files removed

### ⚙️ Infrastructure & DevOps
- `version_control.py` introduced to automate changelog and version tracking
- CI/CD: changelog automation added; error raised if CHANGELOG is present but malformed
- `sed` updated to work correctly within Makefile context (royshadmon, #26)
- Version update logic corrected after regression; workflow now triggers reliably on push
- `setup.cfg` version bump for `v.1.5.2606`
- Added user-friendly license registration failure messaging; raw HTTP status removed — users directed to `support@anylog.co`

### [4f8345a] · 2026-04-29 (latest)

| Date | Commit | Author | Summary |
|------|--------|--------|---------|
| 2026-04-29 | [4f8345a] | Ori Shadmon | Remove archive / customer logic |
| 2026-04-28 | [8d556c6] | Ori Shadmon | Validate MQTT logic works |
| 2026-04-28 | [e7cb791] | Ori Shadmon | Validate MQTT logic works (follow-up fix) |

---

### [fc2309d] · 2026-04-17 – 2026-04-18

| Date | Commit | Author | Summary |
|------|--------|--------|---------|
| 2026-04-18 | [fc2309d] | Ori Shadmon | Litmus single table |
| 2026-04-17 | [a0c1637] | Ori Shadmon | Litmus 2 tables (supported) |
| 2026-04-17 | [02731e3] | Ori Shadmon | Telegraf supported |

---

### [a73584e] · 2026-04-08 – 2026-04-10

| Date | Commit | Author | Summary |
|------|--------|--------|---------|
| 2026-04-10 | [6fc2530] | Ori Shadmon | Skip publish to remote master when `!master_configs=true` |
| 2026-04-10 | [5e1c1c1] | Ori Shadmon | Integration of version control + slight reorg in `.github` dir |
| 2026-04-10 | [5c1e40f] | Ori Shadmon | Integration of version control + slight reorg in `.github` dir (follow-up) |
| 2026-04-09 | [3d224e4] | Moshe       | Integrate aggregation example as part of vessel demo |
| 2026-04-09 | [d5bca98] | Moshe       | Bug fix |
| 2026-04-08 | [a73584e] | Ori Shadmon | Power plant data |

> **Note:** This release group supersedes the previous [a73584e] entry — that commit is now covered above.

---

## 2025

2025 was defined by **policy maturity, monitoring expansion, and networking improvements**. The blockchain policy system was significantly extended with cluster, license, and relay policy support. Monitoring scripts were expanded across southbound connectors. Syslog integration was refined. Networking and overlay configuration scripts were added for multi-node deployments. Docker-based deployment was introduced for scripts. A major reorg consolidated script paths and naming conventions.

| Date | Commit | Summary |
|------|--------|---------|
| 2025-12 | — | Publish workflow scripts; relay and networking configs added |
|         |   | Cluster policy support in node-deployment |
|         |   | Monitoring script refactors for southbound connectors |
| 2025-10 | [423e749] | Blobs folder / dbms based on param |
|          | [eb0a352] | `blobs_folder` addition |
|          | [9f9a665] | Rename: `branch` → `branch_name` |
|          | [07cf288] | Rename: `$BRANCH` → `$BRANCH_NAME` |
|          | [681e2ff] | Update `node_policy.al` |
|          | [f4d9f42] | Akave demo scripts |
|          | [ef12590] | Akave demo support additions |
| 2025-09 | — | Blockchain policy reorg; path and config cleanup |
|         |   | Syslog script updates and parameter fixes |
| 2025-06 | — | License key management scripts added |
|         |   | Docker deployment support added to scripts |
| 2025-01 | — | License key integration — initial scripts |
|         |   | Monitoring improvements for industrial southbound |

---

## 2024

2024 focused on **smart city, gRPC/KubeArmor integration, and policy tooling**. Smart city demo scripts (power plant, waste water, water plant) were built out under the `customers/` directory. KubeArmor gRPC connector scripts were added and debugged. Policy creation and blockchain sync scripts were improved. Syslog ingestion scripts were introduced. Generic deployment configs were extended, and a set of demo and training scripts was organized.

| Date | Commit | Summary |
|------|--------|---------|
| 2024-12 | — | Generic deployment configs expanded; policy debug scripts added |
|         |   | Monitoring scripts updated with source and params fixes |
| 2024-09 | — | Smart city customer scripts — Grafana dashboards for power plant, waste water, water plant |
|         |   | Syslog ingestion scripts added |
| 2024-06 | — | gRPC / KubeArmor connector scripts added and debugged |
|         |   | Policy tooling improved — company/name fields, healthcheck |
| 2024-01 | [dcd5f17] | Fix KubeArmor integration |
|         | [62c40f7] | Added company and name fields to policy |
|         | [5b2e2bc] | gRPC script initial commit |
|         | [0cf02bf] | KubeArmor healthcheck |

---

## 2023

The `deployment-scripts` repository was established in May 2023. Initial work focused on **repository organization, operator/publisher policy scripts, and EdgeX connector support**. Branch structure was defined, core script paths were laid out, and monitoring and deployment scripts were created for standard AnyLog node roles. License policy scripts were introduced. Training scripts and sample configurations were added to help onboard new users.

| Date | Commit | Summary |
|------|--------|---------|
| 2023-12 | — | License policy scripts; monitoring scripts for operator nodes |
|         |   | Training and sample script additions |
| 2023-09 | — | Deployment script reorg; policy and config path standardization |
|         |   | Master node deployment scripts added |
| 2023-06 | [2ac9aee] | EdgeX connector scripts — initial commit |
|         | [45315b0] | EdgeX code additions |
| 2023-05 | [1938fba] | Initial commit — branch structure and repo organization |
|         | [d4e0bc9] | Reorg of script directories |
|         | [44ef282] | Rename and path additions |

---

*For the full commit-level history, run `git log` or browse the repository on GitHub.*