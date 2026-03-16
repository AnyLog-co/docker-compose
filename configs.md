# Configuration Reference

All node configuration lives in a single `node_configs.env` file, organized into sections. New users typically only
need to edit the `basic` and `secrets` sections. The `southbound` and `advanced` sections are optional and safe to
leave at their defaults.

```tree
node_configs.env
├── .env        — Docker deployment settings
├── basic       — Core node config (required)
├── southbound  — Data ingestion protocols (MQTT, OPC-UA, video, monitoring)
├── advanced    — Fine-tuning for experienced users
├── secrets     — Credentials (do not commit to version control)
└── remote-gui  — Companion UI application
```

---

## .env
Docker deployment settings — not mapped to K8s configs.

| Parameter          | Default                                              | Description                                      |
|--------------------|------------------------------------------------------|--------------------------------------------------|
| `INIT_TYPE`        | `prod`                                               | `prod` runs AnyLog; `bash` opens a shell         |
| `IMAGE`            | `anylogco/anylog-network`                            | Docker image repository                          |
| `DEPLOYMENTS_REPO` | `https://github.com/AnyLog-co/deployment-scripts`   | GitHub repo used to configure the node           |
| `DEPLOYMENTS_BRANCH` | `os-dev2`                                          | Branch associated with the deployment repo       |
| `DOCKER_MONITORING`| `false`                                              | Enable Docker-level monitoring                   |

---

## basic
Core node configuration — required for all deployments.

### General

| Parameter      | Default       | Description                              |
|----------------|---------------|------------------------------------------|
| `NODE_TYPE`    | `generic`     | Node type (see table below)              |
| `NODE_NAME`    | `anylog-node` | Name of the AnyLog instance — must be unique |
| `COMPANY_NAME` | `AnyLog Co.`  | Owner of the instance                    |

**Node Types:**

| Value              | Description                                              |
|--------------------|----------------------------------------------------------|
| `generic`          | Sandbox with only network configured                     |
| `master`           | Blockchain emulator                                      |
| `operator`         | Stores data from edge devices                            |
| `query`            | Dedicated query node (enables `system_query` database)   |
| `publisher`        | Distributes data among operator nodes                    |
| `master-operator`  | Combined master and operator on a single agent           |
| `master-publisher` | Combined master and publisher on a single agent          |

### Networking

| Parameter             | Default  | Description                                      |
|-----------------------|----------|--------------------------------------------------|
| `ANYLOG_SERVER_PORT`  | `32548`  | TCP protocol port — must be unique per machine   |
| `ANYLOG_REST_PORT`    | `32549`  | REST protocol port — must be unique per machine  |
| `ANYLOG_BROKER_PORT`  | `32550`  | Message broker port (optional)                   |

### Database

| Parameter    | Default     | Description                          |
|--------------|-------------|--------------------------------------|
| `DB_TYPE`    | `sqlite`    | Database type: `sqlite` or `psql`    |
| `DB_IP`      | `127.0.0.1` | Database IP address                  |
| `DB_PORT`    | `5432`      | Database port                        |
| `AUTOCOMMIT` | `true`      | Whether to autocommit data           |

### NoSQL

| Parameter          | Default     | Description                                           |
|--------------------|-------------|-------------------------------------------------------|
| `BLOBS_STORAGE`    | `false`     | Enable external blob storage                          |
| `BLOB_STORAGE_TYPE`| `mongo`     | Backend type: `mongo`, `s3`, `akave`, `minio`         |
| `BLOB_STORAGE_IP`  | `127.0.0.1` | Storage endpoint                                      |
| `BLOB_STORAGE_PORT`| `27017`     | Storage port (primarily for MongoDB)                  |

### System Query

| Parameter        | Default   | Description                                              |
|------------------|-----------|----------------------------------------------------------|
| `SYSTEM_QUERY`   | `false`   | Enable `system_query` logical database                   |
| `SYSTEM_QUERY_DB`| `sqlite`  | Database type for `system_query`                         |
| `MEMORY`         | `false`   | Run `system_query` using in-memory SQLite                |

### Blockchain

| Parameter               | Default              | Description                                        |
|-------------------------|----------------------|----------------------------------------------------|
| `LEDGER_CONN`           | `127.0.0.1:32048`    | TCP address of the master node — **must be updated** |
| `BLOCKCHAIN_SYNC`       | `60 second`          | How often to sync from the blockchain              |
| `BLOCKCHAIN_SOURCE`     | `master`             | Source: `master` or `optimism`                     |
| `BLOCKCHAIN_DESTINATION`| `file`               | Where to store the local blockchain copy           |

### Operator

| Parameter      | Default           | Description                             |
|----------------|-------------------|-----------------------------------------|
| `CLUSTER_NAME` | `anylog-cluster1` | Owner cluster — unique unless HA is on  |
| `DEFAULT_DBMS` | `mydb`            | Logical database name for incoming data |

### Monitoring

| Parameter           | Default | Description                                         |
|---------------------|---------|-----------------------------------------------------|
| `NODE_MONITORING`   | `false` | Monitor the node                                    |
| `STORE_MONITORING`  | `false` | Store monitoring data in operator node(s)           |
| `SYSLOG_MONITORING` | `false` | Accept syslog data (requires message broker)        |

---

## southbound
Data ingestion protocols — all disabled by default.

### MQTT

| Parameter              | Default             | Description                              |
|------------------------|---------------------|------------------------------------------|
| `ENABLE_MQTT`          | `false`             | Enable the MQTT ingestion process        |
| `MQTT_BROKER`          | `172.104.228.251`   | MQTT broker IP address                   |
| `MQTT_PORT`            | `1883`              | MQTT broker port                         |
| `MQTT_LOG`             | `false`             | Enable MQTT logging                      |
| `MSG_TOPIC`            | `anylog-demo`       | Topic to subscribe to                    |
| `MSG_DBMS`             | `mydb`              | Logical database for incoming data       |
| `MSG_TABLE`            | `bring [table]`     | Target table                             |
| `MSG_TIMESTAMP_COLUMN` | `bring [timestamp]` | Timestamp column mapping                 |
| `MSG_VALUE_COLUMN`     | `bring [value]`     | Value column mapping                     |
| `MSG_VALUE_COLUMN_TYPE`| `float`             | Value column data type                   |

### OPC-UA

| Parameter        | Default | Description                                        |
|------------------|---------|----------------------------------------------------|
| `ENABLE_OPCUA`   | `false` | Enable OPC-UA ingestion                            |
| `OPCUA_URL`      | `""`    | OPC-UA endpoint (e.g. `opc.tcp://127.0.0.1:4840`) |
| `OPCUA_NODE`     | `""`    | Root node (e.g. `ns=2;s=DataSet`)                 |
| `OPCUA_FREQUENCY`| `5`     | Pull frequency                                     |

See [Deploy_PLC.md](Deploy_PLC.md) for the full OPC-UA / EtherIP deployment workflow.

### Video Streaming

| Parameter               | Default                                      | Description                              |
|-------------------------|----------------------------------------------|------------------------------------------|
| `ENABLE_VIDEO_STREAMING`| `false`                                      | Enable video streaming                   |
| `VIDEO_URL`             | `https://www.youtube.com/watch?v=rnXIjl_Rzy4`| Video source URL                         |
| `VIDEO_PORT`            | `32800`                                      | Streaming server port                    |
| `VIDEO_NAME`            | `sfstream`                                   | Stream identifier                        |
| `ENABLE_DETECTIONS`     | `false`                                      | Enable YOLO object detection on stream   |
| `YOLO_MODEL_PORT`       | `50051`                                      | YOLO model server port                   |

---

## advanced
Fine-tuning for experienced users — safe to leave as defaults.

### Directories

| Parameter      | Default                   | Description               |
|----------------|---------------------------|---------------------------|
| `ANYLOG_PATH`  | `/app`                    | AnyLog root path          |
| `LOCAL_SCRIPTS`| `/app/deployment-scripts` | Deployment scripts path   |
| `TEST_DIR`     | `/app/deployment-scripts/test` | Test scripts path    |

### General

| Parameter             | Default | Description                                              |
|-----------------------|---------|----------------------------------------------------------|
| `IS_HIDDEN`           | `false` | Hide blockchain policy (not supported for operator)      |
| `DEPLOY_LOCAL_SCRIPT` | `false` | Run a local script at end of deployment                  |
| `LOCATION`            | `""`    | Coordinates — used by Grafana for network mapping        |
| `COUNTRY`             | `""`    | Country                                                  |
| `STATE`               | `""`    | State                                                    |
| `CITY`                | `""`    | City                                                     |

### Networking

| Parameter       | Default | Description                                                         |
|-----------------|---------|---------------------------------------------------------------------|
| `CONFIG_NAME`   | `""`    | Policy name                                                         |
| `ENABLE_DNS`    | `false` | Enable DNS resolution                                               |
| `NIC_TYPE`      | `""`    | NIC used to resolve internal IP (e.g. `eth0`)                       |
| `OVERLAY_IP`    | `""`    | Overlay/static IP — replaces local IP when connecting to network    |
| `EXTERNAL_DNS`  | `""`    | External DNS                                                        |
| `DNS_DOMAIN`    | `""`    | Local DNS domain to append to hostname                              |
| `DNS`           | `""`    | Full path for local DNS                                             |
| `TCP_BIND`      | `true`  | Bind TCP to specific IP:port (false = bind all)                     |
| `REST_BIND`     | `false` | Bind REST to specific IP:port                                       |
| `BROKER_BIND`   | `false` | Bind broker to specific IP:port                                     |
| `TCP_THREADS`   | `6`     | Concurrent TCP threads                                              |
| `REST_THREADS`  | `6`     | Concurrent REST threads                                             |
| `BROKER_THREADS`| `6`     | Concurrent broker threads                                           |
| `REST_TIMEOUT`  | `30`    | REST request timeout in seconds (0 = continuous)                    |

### NoSQL

| Parameter        | Default | Description                                      |
|------------------|---------|--------------------------------------------------|
| `BLOBS_REUSE`    | `true`  | Reuse identical blobs using file hash            |
| `BLOBS_COMPRESS` | `true`  | Compress blobs before storage                    |
| `BLOBS_FOLDER`   | `""`    | Local folder for blobs (empty = default app path)|

### Object Store

| Parameter          | Default | Description              |
|--------------------|---------|--------------------------|
| `BUCKET_GROUP`     | `""`    | Logical bucket grouping  |
| `BUCKET_ID`        | `""`    | Bucket identifier        |
| `BUCKET_REGION`    | `""`    | Cloud region             |

### Operator (HA)

| Parameter          | Default | Description                                      |
|--------------------|---------|--------------------------------------------------|
| `MEMBER`           | `""`    | Operator ID (auto-generated if not set)          |
| `ENABLE_HA`        | `false` | Enable HA against the cluster                    |
| `START_DATE`       | `30`    | Days back to sync between HA nodes               |
| `OPERATOR_THREADS` | `3`     | Threads for the operator process                 |

### Sub Processes

| Parameter          | Default      | Description                                       |
|--------------------|--------------|---------------------------------------------------|
| `COMPRESS_FILE`    | `true`       | Compress JSON/SQL backup files                    |
| `WRITE_IMMEDIATE`  | `true`       | Write to database immediately on data arrival     |
| `THRESHOLD_TIME`   | `60 seconds` | How long to wait before flushing a partial buffer |
| `THRESHOLD_VOLUME` | `10KB`       | Buffer size that triggers a flush                 |
| `QUERY_POOL`       | `6`          | Number of parallel query threads                  |

---

## secrets
Sensitive credentials — **do not commit to version control**.

> Support for Docker secrets and K8s `Secret` resources is planned.

| Parameter             | Description                        |
|-----------------------|------------------------------------|
| `LICENSE_KEY`         | AnyLog license key                 |
| `DB_USER`             | SQL database username              |
| `DB_PASSWD`           | SQL database password              |
| `BLOB_STORAGE_USER`   | NoSQL storage username             |
| `BLOB_STORAGE_PASSWORD` | NoSQL storage password           |
| `MQTT_USER`           | MQTT broker username               |
| `MQTT_PASSWD`         | MQTT broker password               |
| `BUCKET_ACCESS_KEY`   | Object store access key            |
| `BUCKET_SECRET_KEY`   | Object store secret key            |

---

## remote-gui
Companion UI application deployed alongside the AnyLog node.

| Parameter         | Default   | Description                                              |
|-------------------|-----------|----------------------------------------------------------|
| `ENABLE_REMOTE_GUI`| `true`   | Deploy the Remote GUI alongside the node                 |
| `REMOTE_GUI_TAG`  | `beta2`   | Remote GUI image tag                                     |
| `REMOTE_GUI_NIC`  | `""`      | NIC used to resolve the GUI IP (empty = `127.0.0.1`)    |
| `REMOTE_GUI_FE`   | `31800`   | Frontend port                                            |
| `REMOTE_GUI_BE`   | `8080`    | Backend port                                             |
| `GRAFANA_URL`     | `""`      | Grafana endpoint for dashboard integration               |