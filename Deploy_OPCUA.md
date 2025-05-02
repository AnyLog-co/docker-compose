# Deploying OPC-uA 

This guide explains how to retrieve OPC-UA data into AnyLog using configuration-based deployment. For a deeper dive into 
how AnyLog integrates with OPC-UA, refer to our [documentation](https://github.com/AnyLog-co/documentation/blob/master/opcua.md). 

## Deployment Process - Explained

Accepting OPC-UA data to AnyLog is a two-step process - 
1. creating OPC-UA blockchain policies  
2. Accepting data 

The first step involves creating two types of policies: **tag** and **table** definitions.
* A **tag** policy contains metadata about variables coming from the OPC-UA device.
<br/><br/>
    📌 If your OPC-UA server supports both string-based and integer-based Node IDs, we recommend using integer-based 
    Node IDs. This way, the policy can store both the numeric and string representations. Once the policies are created, 
    users can switch back to the string-based Node IDs, if they prefer. 
<br/><br/>
* A **table** policy defines a corresponding SQL schema to store the time-series data.
<br/><br/>
    🛠 These are created together to maintain consistent naming between tag policies and tables. The reason we utilize a
    simple table namme format (example `t1`) is in order to keep consistency, and remove the risk of long table names.  
<br/><br/>

Once the policies are in place, a secondary script is used to start the data ingestion process from the OPC-UA device.
```json
{"tag": {
    "dbms": "nov", 
    "table": "t1",
    "class": "variable",
    "ns": 2,
    "node_iid": "2001",
    "node_sid": "D1001VFDStop",
    "datatype": "Double",
    "parent": "VFD_CNTRL_TAGS",
    "path": "Root/Objects/DeviceSet/WAGO 750-8210 PFC200 G2 4ETH XTR/Resources/Application/GlobalVars/VFD_CNTRL_TAGS/D1001VFDStop",
    "id": "eeb2b64bdd2a8baddbe3a904348919ed",
    "date": "2025-05-01T15:12:29.671330Z",
    "ledger": "global"
}},
{"table": {
    "name": "t1", 
    "dbms": "nov",
    "create": "CREATE TABLE IF NOT EXISTS t1("
              "    row_id SERIAL PRIMARY KEY,"  
              "    insert_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),", 
              "    tsd_name CHAR(3),"
              "    tsd_id INT,"
              "    timestamp timestamp not null default now(),  "
              "    value float "
              ");"
              "CREATE INDEX t1_timestamp_index ON t1(timestamp);" 
              "CREATE INDEX t1_insert_timestamp_index ON t1(insert_timestamp);",
    "source": "OPCUA Interface",
    "id": "af0772d8eeade6297816b3b23022072e",
    "date": "2025-05-01T15:12:29.674751Z",
    "ledger": "global"}}
```

## How to Deploy an OPC-UA Connection in AnyLog
1. **Prepare configuration (dotenv)** — initially disable the OPC-UA service:
```dotenv
# Whether or not to enable to OPC-UA service
ENABLE_OPCUA=false
# OPC-UA URL address (ex. opcua.tcp:;//127.0.0.1:4840)
OPCUA_URL=opc.tcp://10.0.0.220:4840/freeopcua/server
# Node information the root is located in (ex. ns=2;s=DataSet)
OPCUA_NODE="ns=2;i=1000"
# How often to pull data from OPC-UA
OPCUA_FREQUENCY="25 hz"
```

2. **Deploy AnyLog**
```shell
make up ANYLOG_TYPE=operator
```

3. **Attach to node** - press _Enter_ twice, once attached
```shell
make attach ANYLOG_TYPE=operator
```

4. **Run the tag generation script** - this defines blockchain policies and begins OPC-UA data ingestion
```anylog
process !anylog_path/deployment-scripts/demo-scripts/opcua_tags.al
```

**For Publisher Nodes Only** – Define Data Distribution
If you're using a publisher node, you must define data distribution after the first tag creation. This tells the publisher 
where to send incoming data. This step is only needed once—unless new destinations are later added.
```anylog
operator1 = blockchain get operator bring.first [*][ip] : [*][port]
operator2 = blockchain get operator bring.last [*][ip] : [*][port]

<set data distribution where dbms=nov and table=* and 
    dest=!operator1 and
    dest=!operator2>
```


5. **Detach from the node** - `ctrl-d` or `ctrl-pq`

6. **Update the dotenv file to enable OPC-UA for future restarts**
```dotenv
# Whether or not to enable to OPC-UA service
ENABLE_OPCUA=true
# OPC-UA URL address (ex. opcua.tcp:;//127.0.0.1:4840)
OPCUA_URL=opc.tcp://10.0.0.220:4840/freeopcua/server
# Node information the root is located in (ex. ns=2;s=DataSet)
OPCUA_NODE="ns=2;i=1000"
# How often to pull data from OPC-UA
OPCUA_FREQUENCY="25 hz"
```

7. **Rebuild the container** - persist updated configurations for automatic startup 
```shell
make up ANYLOG_TYPE=operator
```

### Ensuring Configurations Persist After Reboot
By default, Docker restarts containers using in-memory configurations, not updated environment files. To apply changes 
like _ENABLE_OPCUA=true_ on reboot, one of two approaches is recommended:

**Option 1**: Rebuild container, as shown in step 7, once configuration file(s) have been updated.

**Option 2**: Rebuild on reboot using `systemd`

1. Create a custom systemd service that re-runs make up at boot
```service
# /etc/systemd/system/anylog-operator-redeploy.service
[Unit]
Description=Redeploy AnyLog Node After Reboot
After=network.target docker.service
Requires=docker.service

[Service]
WorkingDirectory=%h/docker-compose
ExecStart=/usr/bin/make up ANYLOG_TYPE=operator
Restart=on-failure
User=%u

[Install]
WantedBy=multi-user.target
```

2. Update services with the new service 
```shell
sudo systemctl daemon-reload
sudo systemctl enable anylog-operator-redeploy.service
```

Note: Each node type (e.g., operator, publisher) requires its own systemd service

**Optional**: Test service
```shell
sudo systemctl start anylog-redeploy.service
```
