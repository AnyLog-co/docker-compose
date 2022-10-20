# Configuration Parameters  

The following provides information about the different configurations parameters used by the default AnyLog
deployment scripts.  

## General
<table>
  <tr>
    <td align="center"><b>Environment Variables</b></td>
    <td align="center"><b>AnyLog Variables</b></td>
    <td align="center"><b>Default Value</b></td>
    <td align="center"><b>Description</b></td>
  </tr>
  <tr>
    <td>NODE_TYPE</td>
    <td>
      <li>deploy_ledger</li>
      <li>deploy_operator</li>
      <li>deploy_publisher</li>
      <li>deploy_query</li>
    </td>
    <td>
      <li>none - will start an AnyLog instance with nothing running on it</li>
      <li>rest - will start an AnyLog instance with TCP and REST communication (default option)</li>
      <li>master - will start an AnyLog instance as a master node</li>
      <li>operator - will start an AnyLog instance as an operator node</li>
      <li>publisher - will start an AnyLog instance as a publisher node</li>
      <li>query - will start an AnyLog instance as a query node</li>
      <li>standalone - will start an AnyLog instance that acts as both a master node and an operator node</li>
      <li>standalone-publisher - will start an AnyLog instance that acts as both a master node and a publisher node</li>
    </td>
    <td><p align="justified">Information regarding which AnyLog node configurations to enable. By default, even if everything is disabled, AnyLog starts TCP and REST connection protocols</p></td>
  </tr>
  <tr>
    <td>NODE_NAME</td>
    <td>node_name</td>
    <td>anylog-node</td>
    <td>Name of the AnyLog instance</td>
  </tr>
  <tr>
    <td>COMPANY_NAME</td>
    <td>company_name</td>
    <td>New Company</td>
    <td>Owner of the AnyLog instance</td>
  </tr>
  <tr>
    <td>LOCATION</td>
    <td>location</td>
    <td>0.0, 0.0</td>
    <td>Coordinates of the machine - used by Grafana to map the network</td>
  </tr>
  <tr>
    <td>COUNTRY</td>
    <td>country</td>
    <td>Unknown</td>
    <td>Country where machine is located</td>
  </tr>
  <tr>
    <td>STATE</td>
    <td>state</td>
    <td>Unknown</td>
    <td>State where machine is located</td>
  </tr>
  <tr>
    <td>CITY</td>
    <td>city</td>
    <td>Unknown</td>
    <td>City where machine is located</td>
  </tr>
</table>
Disclaimer: If not hardcoded, location information are found using https://ipinfo.io/json
 

## Networking 
<table>
  <tr>
    <td align="center"><b>Environment Variables</b></td>
    <td align="center"><b>AnyLog Variables</b></td>
    <td align="center"><b>Default Value</b></td>
    <td align="center"><b>Description</b></td>
  </tr>
  <tr>
    <td>EXTERNAL_IP</td>
    <td>external_ip</td>
    <td>Using whatismyip.com generate external IP</td>
    <td>External IP address of the machine</td>
  </tr>
  <tr>
    <td>LOCAL_IP</td>
    <td>local_ip</td>
    <td>IP address from <code>ifconfig</code></td>
    <td>Local or internal network IP address of the machine</td>
  </tr>
  <tr>
    <td>ANYLOG_SERVER_PORT</td>
    <td>anylog_server_port</td>
    <td>32048</td>
    <td>Port address used by AnyLog's TCP protocol to communicate with other nodes in the network</td>
  </tr>
  <tr>
    <td>ANYLOG_REST_PORT</td>
    <td>anylog_rest_port</td>
    <td>32049</td>
    <td>Port address used by AnyLog's REST protocol</td>
  </tr>
  <tr>
    <td>ANYLOG_BROKER_PORT</td>
    <td>anylog_broker_port</td>
    <td></td>
    <td>Port value to be used as an MQTT borker, or some other third-party broker</td>
  </tr>
  <tr>
    <td>K8S_PROXY_IP</td>
    <td>k8s_proxy_ip</td>
    <td></td>
    <td>Configurable (local) IP address that can be used when behind a proxy, or using Kubernetes for static IP</td>
  </tr>
</table>

## Database 
<table>
  <tr>
    <td align="center" style="font-weight: bold"></td>
    <td align="center"><b>Environment Variables</b></td>
    <td align="center"><b>AnyLog Variables</b></td>
    <td align="center"><b>Default Value</b></td>
    <td align="center"><b>Description</b></td>
  </tr>
  <tr>
    <td align="center"><b>SQL Database</b></td>
    <td>DB_TYPE</td>
    <td>db_type</td>
    <td>sqlite</td>
    <td>Physical database type</td>
  </tr>
  <tr>
    <td></td>
    <td>DB_USER</td>
    <td>db_user</td>
    <td></td>
    <td>Username for SQL database connection</td>
  </tr>
  <tr>
    <td></td>
    <td>DB_PASSWD</td>
    <td>db_passwd</td>
    <td></td>
    <td>Password ccorrelated to database user</td>
  </tr>
  <tr>
    <td></td>
    <td>DB_IP</td>
    <td>db_ip</td>
    <td>127.0.0.1</td>
    <td>Database IP address</td>
  </tr>
  <tr>
    <td></td>
    <td>DB_PORT</td>
    <td>db_port</td>
    <td>5432</td>
    <td>Database port number</td>
  </tr>
  <tr>
    <td></td>
    <td>AUTOCOMMIT</td>
    <td>autocommit</td>
    <td>false</td>
    <td>Whether or not autocommit data</td>
  </tr>
  <tr>
    <td></td>
    <td>SYSTEM_QUERY</td>
    <td>system_query</td>
    <td>false by default, unless NODE_TYPE=query</td>
    <td>Whether or not to start to start system_query logical database</td>
  </tr>
  <tr>
    <td></td>
    <td>MEMORY</td>
    <td>memory</td>
    <td>true</td>
    <td>Run system_query using in-memory SQLite. If set to false, will use pre-set database type</td>
  </tr> 
  <tr>
    <td align="center"><b>NoSQL Database</b></td>
    <td>NOSQL_ENABLE</td>
    <td>enable_nosql</td>
    <td>false</td>
    <td>Whether or not to enable NoSQL logical database</td>
  </tr>
  <tr>
    <td></td>
    <td>NOSQL_TYPE</td>
    <td>nosql_type</td>
    <td>mongo</td>
    <td>Physical database type</td>
  </tr>
  <tr>
    <td></td>
    <td>NOSQL_USER</td>
    <td>nosql_user</td>
    <td></td>
    <td>Username for NoSQL database connection</td>
  </tr>
  <tr>
    <td></td>
    <td>NOSQL_PASSWD</td>
    <td>nosql_passwd</td>
    <td></td>
    <td>Password ccorrelated to database user</td>
  </tr>
  <tr>
    <td></td>
    <td>NOSQL_IP</td>
    <td>nosql_ip</td>
    <td>127.0.0.1</td>
    <td>Database IP address</td>
  </tr>
  <tr>
    <td></td>
    <td>NOSQL_PORT</td>
    <td>nosql_port</td>
    <td>27017</td>
    <td>Database port number</td>
  </tr>
</table>

## Blockchain 
<table>
  <tr>
    <td align="center"><b>Environment Variables</b></td>
    <td align="center"><b>AnyLog Variables</b></td>
    <td align="center"><b>Default Value</b></td>
    <td align="center"><b>Description</b></td>
  </tr>
  <tr>
    <td>LEDGER_CONN</td>
    <td>ledger_conn</td>
    <td>{LOCAL_IP}:{ANYLOG_SERVER_PORT}</td>
    <td>Leger connection information, either to the master node or an actual blobckahin</td>
  </tr>
  <tr>
    <td>SYNC_TIME</td>
    <td>sync_time</td>
    <td>30 seconds</td>
    <td>How often to sync from blockchain</td>
  </tr>
  <tr>
    <td>BLOCKCHAIN_SOURCE</td>
    <td>blockchain_source</td>
    <td>master</td>
    <td>source of the blockchain</td>
  </tr>
  <tr>
    <td>BLOCKCHAIN_DESTINATION</td>
    <td>blockchain_destination</td>
    <td>file</td>
    <td>Where to store the copied blockchain</td>
  </tr>
</table>

# Operator
<table>
  <tr>
    <td align="center"><b>Environment Variables</b></td>
    <td align="center"><b>AnyLog Variables</b></td>
    <td align="center"><b>Default Value</b></td>
    <td align="center"><b>Description</b></td>
  </tr>
  <tr>
    <td>MEMBER</td>
    <td>member</td>
    <td>autogenerated by AnyLog</td>
    <td>Operator ID</td>
  </tr>
  <tr>
    <td>CLUSTER_NAME</td>
    <td>cluster_name</td>
    <td>Company Name</td>
    <td>Owner of the cluster</td>
  </tr>
  <tr>
    <td>DEFAULT_DBMS</td>
    <td>default_dbms</td>
    <td>test</td>
    <td>Logical database name</td>
  </tr>
  <tr>
    <td>ENABLE_HA</td>
    <td>enable_ha</td>
    <td>false</td>
    <td>Whether of not to enable HA against the cluster</td>
  </tr>
  <tr>
    <td>START_DATE</td>
    <td>start_date</td>
    <td>30 days (-30d)</td>
    <td>How far back to sync between nodes</td>
  </tr>
  <tr>
    <td>ENABLE_PARTITIONS</td>
    <td>enable_partitions</td>
    <td>false</td>
    <td>Whether or not to enable partitioning</td>
  </tr>
  <tr>
    <td>TABLE_NAME</td>
    <td>table_name</td>
    <td>all tables (*)</td>
    <td>Which tables to partition</td>
  </tr>
  <tr>
    <td>PARTITION_COLUMN</td>
    <td>partition_column</td>
    <td>insert_timestamp</td>
    <td>Which timestamp column to partition by</td>
  </tr>
  <tr>
    <td>PARTITION_INTERVAL</td>
    <td>partition_interval</td>
    <td>14 days</td>
    <td>Time period to partition by</td>
  </tr>
  <tr>
    <td>PARTITION_KEEP</td>
    <td>partition_keep</td>
    <td>6</td>
    <td>How many paritions to keep</td>
  </tr>
  <tr>
    <td>PARTITION_SYNC</td>
    <td>partition_sync</td>
    <td>1 day</td>
    <td>How often to check if an old partition should be removed</td>
  </tr>
  <tr>
    <td>CREATE_TABLE</td>
    <td>create_table</td>
    <td>true</td>
    <td>Whether or not to create a new table in the operator</td>
  </tr>
  <tr>
    <td>UPDAE_TSD_INFO</td>
    <td>update_tsd_info</td>
    <td>true</td>
    <td>Record data inserted on Operator</td>
  </tr>
  <tr>
    <td>ARCHIVE</td>
    <td>archive</td>
    <td>true</td>
    <td>Archive data coming in</td>
  </tr>
  <tr>
    <td>COMPRESS_FILE</td>
    <td>compress_file</td>
    <td>true</td>
    <td>compress JSON and SQL file(s) backup</td>
  </tr>
  <tr>
    <td>OPERATOR_THREADS</td>
    <td>operator_threads</td>
    <td>1</td>
    <td>How many threads to use in the operator process</td>
  </tr>
</table>

## Publisher
<table>
  <tr>
    <td align="center"><b>Environment Variables</b></td>
    <td align="center"><b>AnyLog Variables</b></td>
    <td align="center"><b>Default Value</b></td>
    <td align="center"><b>Description</b></td>
  </tr>
  <tr>
    <td>DBMS_FILE_LOCATION</td>
    <td>dbms_file_location</td>
    <td>file_name[0]</td>
    <td>Location of logical database name within file name</td>
  </tr>
  <tr>
    <td>TABLE_FILE_LOCATION</td>
    <td>table_file_location</td>
    <td>file_name[1]</td>
    <td>Location of table name within file name</td>
  </tr>
  <tr>
    <td>COMPRESS_FILE</td>
    <td>compress_file</td>
    <td>true</td>
    <td>compress JSON and SQL file(s) backup</td>
  </tr>
</table>

## Authentication
<table>
  <tr>
    <td align="center"><b>Environment Variables</b></td>
    <td align="center"><b>AnyLog Variables</b></td>
    <td align="center"><b>Default Value</b></td>
    <td align="center"><b>Description</b></td>
  </tr>
  <tr>
    <td>AUTHENTICATION</td>
    <td>authentication</td>
    <td>false</td>
    <td>Whether or not to enable authentication</td>
  </tr>
  <tr>
    <td>AUTH_USER</td>
    <td>auth_user</td>
    <td></td>
    <td>authentication user</td>
  </tr>
  <tr>
    <td>AUTH_PASSWD</td>
    <td>auth_passwd</td>
    <td></td>
    <td>authentication password</td>
  </tr>
  <tr>
    <td>AUTH_TYPE</td>
    <td>auth_type</td>
    <td>admin</td>
    <td>authentication administration type</td>
  </tr>
</table>

## MQTT Client
The configurations allow for a basic MQTT client that consists of only a timestamp and value. For complex MQTT client 
processes the user needs to write their own MQTT client process. 
<table>
  <tr>
    <td align="center"><b>Environment Variables</b></td>
    <td align="center"><b>AnyLog Variables</b></td>
    <td align="center"><b>Default Value</b></td>
    <td align="center"><b>Description</b></td>
  </tr>
  <tr>
    <td>ENABLE_MQTT</td>
    <td>enable_mqtt</td>
    <td>false</td>
    <td>Whether or not to enable the default message client process</td>
  </tr>
  <tr>
    <td>MQTT_BROKER</td>
    <td>mqtt_broker</td>
    <td></td>
    <td>Message broker IP</td>
  </tr>
  <tr>
    <td>MQTT_PORT</td>
    <td>mqtt_port</td>
    <td></td>
    <td>Message broker port</td>
  </tr>
  <tr>
    <td>MQTT_USER</td>
    <td>mqtt_user</td>
    <td></td>
    <td>User associated with message broker</td>
  </tr>
  <tr>
    <td>MQTT_PASSWD</td>
    <td>mqtt_passwd</td>
    <td></td>
    <td>Password credential for message broker user</td>
  </tr>
  <tr>
    <td>MQTT_TOPIC_NAME</td>
    <td>mqtt_topic_name</td>
    <td>all (*)</td>
    <td><code>run client</code> topic name</td>
  </tr>
  <tr>
    <td>MQTT_TOPIC_DBMS</td>
    <td>mqtt_topic_dbms</td>
    <td></td>
    <td>Logical database to store data in</td>
  </tr>
  <tr>
    <td>MQTT_TOPIC_TABLE</td>
    <td>mqtt_topic_table</td>
    <td></td>
    <td>Physical table to store data in</td>
  </tr>
  <tr>
    <td>MQTT_COLUMN_TIMESTAMP</td>
    <td>mqtt_column_timestamp</td>
    <td>now - only if previous params are set, but no timestamp column</td>
    <td></td>
  </tr>
  <tr>
    <td>MQTT_COLUMN_VALUE</td>
    <td>mqtt_column_value</td>
    <td></td>
    <td>Name of the JSON key associated with the value column</td>
  </tr>
  <tr>
    <td>MQTT_COLUMN_VALUE_TYPE</td>
    <td>mqtt_column_value_type</td>
    <td>str</td>
    <td>Column type for value column</td>
  </tr>
  <tr>
    <td>MQTT_LOG</td>
    <td>mqtt_log</td>
    <td>false</td>
    <td>Whether or not to print message logs</td>
  </tr>
</table>

## Other Settings
<table>
  <tr>
    <td align="center"><b>Environment Variables</b></td>
    <td align="center"><b>AnyLog Variables</b></td>
    <td align="center"><b>Default Value</b></td>
    <td align="center"><b>Description</b></td>
  </tr>
  <tr>
    <td>DEPLOY_LOCAL_SCRIPT</td>
    <td>deploy_local_script</td>
    <td>false</td>
    <td>Whether or not to automatically run a local (or personalized) script at the end of the process</td>
  </tr>
  <tr>
    <td>TCP_THREAD_POOL</td>
    <td>tcp_thread_pool</td>
    <td>6</td>
    <td>Number of TCP threads</td>
  </tr>
  <tr>
    <td>REST_TIME</td>
    <td>rest_timeout</td>
    <td>30</td>
    <td>REST timeout</td>
  </tr>
  <tr>
    <td>REST_THREADS</td>
    <td>rest_threads</td>
    <td>5</td>
    <td>Number of REST threads</td>
  </tr>
  <tr>
    <td>QUERY_POOL</td>
    <td>query_pool</td>
    <td>3</td>
    <td>Number parallel queries</td>
  </tr>
  <tr>
    <td>WRITE_IMMEDIATE</td>
    <td>write_immediate</td>
    <td>true</td>
    <td>When data comes in write to database immidiately, as opposed to waiting for a  full buffer</td>
  </tr>
  <tr>
    <td>THRESHOLD_TIME</td>
    <td>threshold_time</td>
    <td>60 seconds</td>
    <td>If buffer is not full, how long to wait until pushing data through</td>
  </tr>
<tr>
    <td>THRESHOLD_VOLUME</td>
    <td>threshold_volume</td>
    <td>10KB</td>
    <td>Buffer size to reach, at which point data is pushed through</td>
  </tr>
</table>