---
title: Changelog
description: Release history and notable changes for AnyLog deployment scripts.
layout: page
---

<!-- last-processed: 7b03268 -->

<!-- osdev-predev: 7b03268 (2026-05-25) -->

* **Ori Shadmon** (2023-05-19 – 2026-05-25)
  * CI/CD: Predev osdev (#29); added a changelog logic; if changelog not found then create else raise error; version control; update version logic; issue with version update; flow name; pre-develop
  * Docker config: customer code rm; clean up; comment out 'set -euo pipefail'; prep configs call from build_Docker_ompose.sh; support for comment out empty rather than use empty; improve to support shell; cleanup to match mark's config files; if license came from file ignore license process; integration of license key (#31); license logic integration - in progress; rm unused docker env files; merge from md-dev; support for adding personal scripts into docker container; hidden query + chnage to build process (to test); env params (ori); Predev osdev (#29); config filechange; Predev osdev (#28); include exec-root option to attach into root user for executable; debug busybox enabled; hostname for remote-gui; REMOTE_CONN support for node; added bmonitoring support; working changes; improve docker socket support; sed spacing; os sed; support for docker socket; support for missing docker socket; support for local deploymnet-scripts dir; socket path; mac suport; docker.scoket suppport; docker group; added docker socket confis; merge from pre-develop; better support for user input license key (#24); replace exit with else; support license formatting; pre-develop; docker configs working with both standalone + multi-file; single file vs multiple files logic; generic configs; node naming; ova configs; beta for remote gui; fixed configs; updated configs for generic; cleanup phase 1; Makefile - fix builds; Makefile; publisher / operator configs; clean up unneeded code; updated sample docker configs; rm extra dirs; reset docker based on test-network; docker; docker updates; license key; moved nebula outside; frequency; scripts -> script; leave monitoring; logs -f + configs; anylog master-operator with new monitoring configs; test configs; enable remote-cli will enable both; remove nebula + add remote-gui; readme for configuring windows; updated docker-compose scripts; Pre develop (#18); Oshadmon patch 1 (#17); Pre develop (#16); node name; Pre develop (#15); paths + readme; reset configs; removed unneeded docker files; Os dev (#14); merge md-dev; merge from os-dev; docker configs; update docker image path; placeholder; NIC TYPE; changes; updated configs  with etherip; updated to support restart for docker-compose; blockchain with details; OPC-UA explained; Pre develop (#12); readme; reset configs + v1.3.2503; license change; SYNC_TYIME --> BLOCKCHAIN_SYNC; unique per os; template support; network configs diff for linux vs others; docker service name; SYNC_TIME --> BLOCKCHAIN_SYNC; reorg; auatomaticly build docker-compoose file; copy from pre-dev; ledger; comment ports; working code base for networking; simplify docker; overlay code; fix makefile
  * Docker config / Generic: cleanup to match mark's config files; Predev osdev (#29); Predev osdev (#28); include exec-root option to attach into root user for executable; reset to defaults; support for docker socket; comment; support for local deploymnet-scripts dir; added docker socket confis; update msg client; pre-develop; all other configs; docker configs working with both standalone + multi-file; HA operator; single file vs multiple files logic; single file configs; standalone; generic configs; updated configs; ova configs; system query logical database; video configs; updated configs for generic; re added blobs; DNS + standalones; enable / disable DNS; generic + ports for operator; cleanup phase 1; Makefile; thread configs; .env update; generic; docker-compose params; generic - reset
  * Docker config / Master: cleanup to match mark's config files; Predev osdev (#29); Predev osdev (#28); added bmonitoring support; reset to defaults; added docker socket confis; deployment branch; pre-develop; all other configs; node naming; updated configs; ova configs; system query logical database; DNS + standalones; enable / disable DNS; simplified configs; cleanup phase 1; .env update; master configs; docker-compose params; updated sample docker configs; reset docker based on test-network
  * Docker config / Operator: clean up; cleanup to match mark's config files; Predev osdev (#29); Predev osdev (#28); reset to defaults; added docker socket confis; update msg client; deployment branch; pre-develop; all other configs; node naming; updated configs; ova configs; system query logical database; re added blobs; DNS + standalones; enable / disable DNS; generic + ports for operator; reformat - in progress; cleanup phase 1; .env update; var value; publisher / operator configs; docker configs for operators; docker-compose params; updated sample docker configs
  * Docker config / Publisher: cleanup to match mark's config files; Predev osdev (#29); Predev osdev (#28); reset to defaults; added docker socket confis; update msg client; deployment branch; pre-develop; all other configs; node naming; ova configs; system query logical database; video configs; DNS + standalones; enable / disable DNS; simplified configs; reformat - in progress; cleanup phase 1; .env update; var value; publisher / operator configs; updated sample docker configs; reset docker based on test-network
  * Docker config / Query: integration of license key (#31); cleanup to match mark's config files; hidden query + chnage to build process (to test); Predev osdev (#29); Predev osdev (#28); reset to defaults; added docker socket confis; deployment branch; pre-develop; all other configs; updated configs; ova configs; system query logical database; DNS + standalones; enable / disable DNS; simplified configs; cleanup phase 1; .env update; query; docker-compose params; updated sample docker configs; rm extra dirs; reset docker based on test-network
  * Docker config / Standalone: clean up; improve to support shell; if license came from file ignore license process; cleanup to match mark's config files; support for adding personal scripts into docker container; operator helper/worker threads; ori changes; deployment scripts path; Predev osdev (#29); config filechange; Predev osdev (#28); REMOTE_CONN support for node; reset to defaults; support for local deploymnet-scripts dir; added docker socket confis; update msg client; config changes; enable sys_query for standalone; deployment branch; pre-develop; all other configs; node naming; updated configs; ova configs; system query logical database; video configs; updated configs for generic; re added blobs; DNS + standalones; simplified configs; cleanup phase 1; .env update; var value; publisher / operator configs; anylog standalone; docker-compose params; updated sample docker configs
  * General: customer code rm; clean up; prep configs call from build_Docker_ompose.sh; support for comment out empty rather than use empty; improve to support shell; Baraba for Mark; README for processes; if license came from file ignore license process; integration of license key (#31); cleanup to match mark's config files; license key logic interation; license logic integration - in progress; license generator in single location; merge license key info to a single file; ori changes; missing clean compose repo; env params (ori); Predev osdev (#29); flow check; missing -it; changelog.md; version control; Makefile is now run through a shell script + updated corresponding README; Predev osdev (#28); updated README for support; remove unsed files; readme; cleanup; update version logic; nebula; file path; script to test row count per db; better support for user input license key (#24); pre-develop; README; remove os-dev; re added blobs; reformat - in progress; empty file test; clean up unneeded code; cookies - placeholder; mac support; readme for configuring windows; removed unneeded docker files; publisher only case; OPCUA document; Pre develop (#12); url; license change; reorg; remote-cli; working template for broker; template; on the fly configs - broker; README for support; openmbao; openbao; openbao (may move stuff); fix makefile; edgelakee --> anylog; network configurations; Pre develop (#9); remove health check; pre-develop (#8); networking:; Dockerfiles; rm network-mode to use ports only; cleanup configs; merge from main; mark code; new contract; operator test; test optimisim; reorg op2; bug AB-18; docker configs for operator; blockchain - test; platform --> BLOCKCHAIN_SOURCE; debug mode; rm overlay; contract + instead of local_blockchain use blockchain_destination; blockchain configs; overlay network; netowrk ffor cli; network_mode host; host; nebula container; bridge; CIDR_OVERLAY_ADDRESS; template for netwowrk; broker port; enable MQTT; nebula configs; statatic nebula; generic node; query changes; docker file; nebula - tmp; master - phase23; master - phase1; query - phase2; query - phase1; master nebula test; missing image for Make; generic nebula test; nebula udp ports; image path; default configs; generic configs - consistency for OH / AnyLog / EdgeLake; REAMED - sync between EdgeLake / OH  / AnyLog; name; generic2; Docker compose (#6); add param + license; remote-cli / no license; makefile / remote-cli; makefile; Ori's configs; podman - comment out; docker make; network configuration - mode:brige / able to communicate between nodes but not remote instances; docker-compose for windows - all 3 nodes deploy; missing variable name; docker compose files for windows / docker; TAG=1.3.2405; hardcode remote-cli; mv to deploy-k8s; .gitignore; remove .idea; k8s; copy content from  os-dev/support-tools; broker service - working; configmap working; volumee / node deployment; configuration file; k8s configmap; readme (to do); working local scripts; persistent volumes for data / blockchain / anylog; host path for proxy; removed local scripts volume; volume for deployments (not working); volumes; no need for file; Deploy node; port-forwrad working; overlay IP; NodePort; working  internal network; working license; kubernetes code; archive existing / reorg; archive existing; k8s from publisher; keey; content from branch; mv pycharm; disbale_cli; k8s rwrite /reorg; kubernetes; k8s configs; kubernetes rewrite; location ---> geolocation; rwrite for kubernetes; msg client value; \.env file; abosulte path for docker-compose-template; init tyype; makefile and docs; full configs - to test; docker-compose for non-anylog; missing license; query code; operator configs; master node configs; move EdgeLake docker-compose into AnyLog; docker compose for master - opensource; open source docker-compose; nebula - operator; test nebula - master; reset training configs; nebula to test; anylog publisher k8s - to test; new configs for k8s; .env; cluster2 on new machines; nebula test; operator; ledger conn; grafana; pycharm configs; readme start /stop; docker files; docker deployment; path; publisher; k8s volume; volume; helm deploy / stop; working code; volume code; comment logger; run.sh fix; k8s for AnyLog - working base code; comfig file; anylog master; nginx; k8s code; anylog with k8s in progress; secret for api AnyLog; deployment; configmaps; node service; anylog-node configmap; docs; kubearmor / nginx; nginx / kubearmor deploymnet; helm / k8s - start; docker-compose for master - to test; help; run.sh - readme; ports; run.sh; ports - in progress; anylog-master - ports; rm docker ports; README + generic node; clean up + remove unneeded code at this time; docker ports; docker ports master; dockcer-compose file path; reorg / dir paths; TAG=training; rm readme; build --> tag; docker; beta --> latest; init type; docker with ports; docker compose with ports over bridged for operator(s) - to test; open horizon instead of anylog; operator2; operator1; query; master; service; training; OpenHorzion - master (to test); default dbms; removed unneeded paramsu; read configs into default; mv to archive; Docker code - working; title / removed mqtt + operator when not needed; NODE_TYPE  in  regular configs; node configs; training - base code; deployment rewrtie; updated config params based on changes in deployment; standalone; ENABLE_MQTT; training / ibm demo; mastr conifgs; test master / query / generic; env values; training dirs; network configs; working general configs; new configs - reset; deployment scripts - to test; config for docker working; files - in progress; extra char; docker configs - in progress; broke configs to general and advanced; anylog_configs / advance_configs in config_file; security; OpenHorizon; policies for demo; openhorizon defaults; merge from master; file for k8s; docker ready; docker working - generic :; recreate configs; latest or beta; no mysql; json file; openhorizon - env to json; remote cli volume; missing conn info; test code ffor ddemo; question regarding operator id + optional MQT; question regarding operator id; missing return; working new questions; deployment script to support demo deployment; display_node_type_options indefinite loop fixed; bat - to test; mysql; .env for query/remote; cp .env; question; improved questions for HA / Operator + remove k8s in docker case; rm k8s param in docker; extend code to support monitoring; reset; helm code; cleaned code to support kubernetes; placeholder for code; path change form scripts + tests; working volumes - without local scripts; packaged code - volume not working for tests/scripts; working w/o volume; ori credentials; anylog-node code w/o volumes
  * Makefile: integration of license key (#31); license key logic interation; license logic integration - in progress; version control; Predev osdev (#29); Makefile is now run through a shell script + updated corresponding README; Predev osdev (#28); improved README; user able to define WITHOUT nylog- for 'default options; include exec-root option to attach into root user for executable; debug busybox enabled; provide testing / validation tools within Makefile; support for docker socket; improved deployment process; pre-develop; single file vs multiple files logic; node naming; version; cleanup phase 1; Makefile - fix builds; Makefile; thread configs; .env update; clean cmds; cleanup makefile; generic - reset; reset docker based on test-network; docker updates; makefile change; leave monitoring; logs -f + configs; anylog master-operator with new monitoring configs; version in Make; updated docker-compose scripts; Pre develop (#16); Update Makefile; Pre develop (#15); arm/amd merged; merge from os-dev; version 1.3.X -> 1.4.2508; placeholder; NIC TYPE; changes; rebuild; file path; double path; updated to support restart for docker-compose; Makefile - allow for Reote-CLI in manual; Pre develop (#12); latest; README; makefile; help; new Makefile - to test; New Makefile; reset configs + v1.3.2503; makefile for podman; CONTAINER_CMD; unique per os; network configs diff for linux vs others; docker service name; latest --> 1.3.2501; reorg; on the fly configs - broker; copy from pre-dev; docker; working code for latest; working code base for networking; simplify docker; overlay code; fix makefile; network configurations; if/else - arm6; ($(filter $(shell uname -m),aarch64 arm64),); remove health check; pre-develop (#8); networking:; fix makefile to support options; podman / docker; merge from main; tag - 1.3.2411; test optimisim; bug AB-18; platform --> BLOCKCHAIN_SOURCE; nebula container; CIDR_OVERLAY_ADDRESS; template for netwowrk; broker port; missing \@; statatic nebula; query changes; if test don't read configs; missing cat; image path; latest version for README; makefile - sync between EdgeLake / OH  / AnyLog; nebula; Docker compose (#6); version + arm64 --> aarch64; upadted makefile; remote cli; makefile / remote-cli; Ori's configs; make revert; reevert d9eb4605ea367ad2d31531335b9457ffd7c5c635; Makefile.bat; podman  code; podmanushc; podman; makefile minor changes; docker compose files for windows / docker; content from branch; clean code; edgelake --> anylog; naming; makefile path for ANYLOG_PATH; docker credentials; makefile and docs; move EdgeLake docker-compose into AnyLog
  * Node config: mv to deploy-k8s; archive existing; reorg; k8s rwrite /reorg
  * Support services: integration of license key (#31); license generator in single location; merge license key info to a single file; Makefile support for syslog; ori changes; Predev osdev (#29); Predev osdev (#28); attach for db + exec for all; support makefile code; support multiple dbs + grafana; multiple containers support; incroporated REMOTE_CONN; REMOTE_CONN; remote-gui support; cleanup; improved deployment process; docker compose builder for support services; builder for docker support; ollama example; moved nebula outside; Docker compose (#6); mv to deploy-k8s; remove k8s; copy content from  os-dev/support-tools; reorg k8s; archive existing / reorg; anylog-gui; reorg; k8s rwrite /reorg; removed unneeded paramsu; mv to archive; deployment rewrtie; new configs - reset; deployment scripts - to test; docker configs - in progress; docker working - generic :; cleaned code to support kubernetes
  * Support services / Grafana: Predev osdev (#28); support multiple dbs + grafana; docker compose builder for support services; builder for docker support
  * Support services / MongoDB: Predev osdev (#28); docker compose builder for support services
  * Support services / Ollama: Predev osdev (#28); improved deployment process
  * Support services / PostgreSQL: Predev osdev (#28); accidently removed psql; multiple containers support; docker compose builder for support services
  * Support services / Remote GUI: Predev osdev (#29); Predev osdev (#28); remote-gui is 1.0.0; remote-gui support; docker compose builder for support services; builder for docker support
* **Mark Davidson** (2025-02-12 – 2026-05-13)
  * Docker config: fixed volume issues; fixed deploy.sh and scripts; License Key; Fix variable name in sed command for LICENSE_KEY; Fix formatting issue in LICENSE_KEY update command; Update sed commands to create backup files; Improve normalize_quotes function for better quoting; Use in-place editing for sed commands; Fix quote normalization and backup removal; Fix regex escaping in normalize_quotes function; Replace custom sedi function with direct sed calls; Fix quote normalization in prep_configs.sh; Refactor normalize_quotes function to use sed directly; Fix sed command usage in prep_configs.sh; Update sed command to use extended regex; Refactor sedi function to accept multiple arguments; Fix typo in sed command for LICENSE_KEY update; Refactor sed usage in prep_configs.sh; Delete docker-makefiles/Anylog-standalone-publisher directory; Create node_configs.env for AnyLog publisher; Update base_configs.env (#19); Update advance_configs.env (#13)
  * Docker config / Operator: fixed deploy.sh and scripts
  * Docker config / Standalone: fixed volume issues; fixed deploy.sh and scripts; remotegui enabled; updates to syslog; fixed quotes in key; License Key; Create node_configs.env for AnyLog publisher; Add node configuration environment file; Fix comment formatting in base_configs.env
  * General: fixed volume issues; fixed deploy.sh and license; deploy.sh license key; updated license.txt; Updated changelog; updated anylog license agreement; License Key
  * Makefile: fixed volume issues; fixed deploy.sh and license; fixed make license-server ip address; fixed license-server.py; fixed license server ip addr; Added user friendly messaging for license server; license ip; bug fix; added syslog inclusion; use more instead of cat for license.txt; fixed quotes in key; License Key; Update Makefile; Update Makefile (#10)
  * Support services: fixed license-server.py; added registration server
* **royshadmon** (2023-10-19 – 2026-05-07)
  * Docker config: updated sed to work with Makefile (#26); updated sed to work with Makefile; add high level .env file; fixing templates
  * Docker config / Master: fixing templates
  * Docker config / Operator: fixing templates
  * Docker config / Standalone: adding missing variable; fixing templates
  * General: INIT_TYPE=training
  * Makefile: updated sed to work with Makefile (#26)
  * Support services: dockerizing and using a shared directory for license server; updated sed to work with Makefile (#26)
* **edgelake** (2026-03-20)
  * Docker config: support for env vars
  * Makefile: support for env vars
* **Ori** (2024-07-11 – 2025-11-03)
  * Docker config: remoerge
  * General: remoerge; docker-compose
  * Makefile: remoerge; docker-compose
  * Support services: remoerge
* **oshadmon@gmail.com** (2023-07-06 – 2024-10-04)
  * General: nebula configs; update makefile remote-cli; pull from os-dev
  * Makefile: nebula configs; update makefile remote-cli
* **Your Name** (2024-10-01)
  * General: docker-compose / version
  * Makefile: docker-compose / version
* **Moshe Shadmon** (2023-07-02 – 2024-04-21)
  * General: fix text; ori access - not needed

<!-- Developers: add bullets below as changes land in your branch -->
---

## 2026

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