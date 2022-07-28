import requests
import socket

def __local_ip():
    """
    Get the local IP address of the machine
    """
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return '127.0.0.1'

def __external_ip():
    """
    Get the external IP address of the machine
    """
    try:
        r = requests.get('https://ifconfig.me/')
    except:
        pass
    else:
        try:
            return r.text
        except:
            pass

def __locations():
    """
    Using ipinfo.io/json get location information about the node
    """
    loc = "0.0, 0.0"
    country="Unknown"
    state="Unknown"
    city="Unknown"

    try:
        r = requests.get("https://ipinfo.io/json")
    except Exception as error:
        pass
    else:
        if int(r.status_code) == 200:
            content = r.json()
            loc = content['loc']
            country = content['country']
            state = content['state']
            city = content['city']
    return loc, country, state, city

LOC, COUNTRY, STATE, CITY = __locations()

PARAMS = {
    "general": {
        # General Information
        "Node Name": {
            "default": "anylog-node",
            "docker": "NODE_NAME",
            "kubernetes": "node_name",
            "description": "Unique name for the node"
        },
        "Company": {
            "default": "New Company",
            "docker": "COMPANY_NAME",
            "kubernetes": "company_name",
            "description": "Company owner of the node"
        },
        "Coordinates": {
            "default": LOC,
            "docker": "LOCATION",
            "kubernetes": "location",
            "description": "Physical location of the node"
        },
        "Country": {
            "default": COUNTRY,
            "docker": "COUNTRY",
            "kubernetes": "country",
            "description": "Country node is located in"
        },
        "State": {
            "default": STATE,
            "docker": "STATE",
            "kubernetes": "state",
            "description": "State node is located in"
        },
        "City": {
            "default": CITY,
            "docker": "CITY",
            "kubernetes": "city",
            "description": "City node is located in"
        },

        # Networking
        "TCP Port": {
            "default": 32048,
            "docker": "ANYLOG_SERVER_PORT",
            "kubernetes": "server",
            "description": "Port for TCP communication between nodes"
        },
        "REST Port": {
            "default": 32049,
            "docker": "ANYLOG_REST_PORT",
            "kubernetes": "rest",
            "description": "Port for REST communication with the node"
        },
        "BROKER Port": {
            "default": "",
            "docker": "ANYLOG_BROKER_PORT",
            "kubernetes": "broker",
            "description": "Message Broker port for the node"
        },
        "External IP": {
            "default": __external_ip(),
            "docker": "EXTERNAL_IP",
            "kubernetes": "external_ip",
            "description": "External Network IP address"
        },
        "Local IP": {
            "default": __local_ip(),
            "docker": "LOCAL_IP",
            "kubernetes": "k8s_proxy_ip",
            "description": "Local IP of the machine - if running on Kubernetes this value will be set as the Proxy IP"
        },

        # Blockchain sync
        "Ledger Conn": {
            "default": "",
            "docker": "LEDGER_CONN",
            "kubernetes": "ledger_conn",
            "description": "Blockchain ledger connection information"
        },
        "Sync Time": {
            "default": "30 seconds",
            "docker": "SYNC_TIME",
            "kubernetes": "sync_time",
            "description": "How often to sync against the blockchain",
        },
        "Blockchain Source": {
            "default": "master",
            "options": ["blockchain", "master"],
            "docker": "SOURCE",
            "kubernetes": "source",
            "description": "Source of where the data is coming from"
        },
        "Destination": {
            "default": "file",
            "options": ["file", "dbms"],
            "docker": "DESTINATION",
            "kubernetes": "destination",
            "description": "Where will the copy of the blockchain be stored"
        },

        # Database
        "Database Type": {
            "default": "psql",
            "options": ["psql", "sqlite"],
            "docker": "db_type",
            "kubernetes": "type",
            "description": "Physical database type"
        },
        "Database IP": {
            "default": "127.0.0.1",
            "docker": "db_ip",
            "kubernetes": "ip",
            "description": "Database IP"
        },
        "Database Port": {
            "default": 5432,
            "docker": "db_port",
            "kubernetes": "ip",
            "description": "Database port"
        },
        "Database User": {
            "default": "admin",
            "docker": "db_user",
            "kubernetes": "user",
            "description": "User correlated to this database"
        },
        "Database User Password": {
            "default": "demo",
            "docker": "db_passwd",
            "kubernetes": "password",
            "description": "Password correlated to user for accessing database"
        },
        "Enable system_query": {
            "default": False,
            "docker": "DEPLOY_SYSTEM_QUERY",
            "kubernetes": "deploy_system_query",
            "description": "Whether or not to automatically create system_query logical database on node"
        },
        "Set system_query in memory": {
            "default": True,
            "docker": "MEMORY",
            "kubernetes": "memory",
            "description": "Run system_query logical database in-memory"
        },
    },
    "operator": { #  Operator specific params
        "Database Name": {
            "default": "test",
            "docker": "DEFAULT_DBMS",
            "kubernetes": "db_name",
            "description": "Logical database to store data coming into Operator"
        },
        "Operator Member ID": {
            "default": "",
            "docker": "MEMBER",
            "kubernetes":" member",
            "description": "Operator member ID - by default it's autogenerated, should be set only when resetting blockchain, but want to keep exactly the same information"
        },
        "Cluster Name": {
            "default": "new-cluster",
            "docker": "CLUSTER_NAME",
            "kubernetes": "cluster-name",
            "description": "Name of the cluster operator will be associated with"
        },
        "Create Table": {
            "default": True,
            "docker": "CREATE_TABLE",
            "kubernetes": "create_table",
            "description": "creates a table if the table doesn't exists"
        },
        "Update TSD Info": {
            "default": True,
            "options": [True, False],
            "docker": "UPDATE_TSD",
            "kubernetes": "update_tsd",
            "description": "update a summary table (tsd_info table in almgm dbms) with status of files ingested. (by default, almgm database & tsd_info table get created on all operator nodes)"
        },
        "Archive Data": {
            "default": True,
            "options": [True, False],
            "docker": "ARCHIVE",
            "kubernetes": "archive",
            "description": "move JSON files to archives"
        },
        "Distribute Data": {
            "default": True,
            "options": [True, False],
            "docker": "DISTRIBUTOR",
            "kubernetes": "distributor",
            "description": "Transfer data files to members of the cluster"
        },
        # Data partitioning
        "Enable Partitions": {
            "default": True,
            "options": [True, False],
            "docker": "ENABLE_PARTITIONS",
            "kubernetes": "enable_partitions",
            "description": "whether or not to partition data on node"
        },
        "Table(s) to Partition": {
            "default": "*",
            "docker": "PARTITION_TABLE",
            "kubernetes": "partition_table",
            "description": "table(s) to partition (default - all tables)"
        },
        "Partitioning Column": {
            "default": "insert_timestamp",
            "docker": "PARTITION_COLUMN",
            "kubernetes": "column",
            "description": "Timestamp column to partition by"
        },
        "Partition Interval": {
            "default": "14 days",
            "options": ["year", "month", "week", "days", "day"],
            "docker": "PARTITION_INTERVAL",
            "kubernetes": "interval",
            "description": "Amount of time to partition by"
        },
        "Partition Keep": {
            "default": 6,
            "docker": "PARTITION_KEEP",
            "kubernetes": "keep",
            "description": "Number of partition to keep"
        },
        "Partition Sync": {
            "default": "1 day",
            "options": ["year", "month", "week", "days", "day"],
            "docker": "PARTITION_SYNC",
            "kubernetes": "sync",
            "description": "How often remove excess partitions"
        }
    },
    "publisher": { # Publisher specific params
        "Compress JSON": {
            "default": True,
            "options": [True, False],
            "docker": "COMPRESS_JSON",
            "kubernetes": "compress",
            "description": "Compress archived JSON files"
        },
        "Backup JSON": {
            "default": True,
            "docker": "MOVE_JSON",
            "kubernetes": "move",
            "description": "Backup JSON files in publisher after distributing them to operator node(s)"
        },
        "Database Name Location": {
            "default": "file_name[0]",
            "docker": "DB_LOCATION",
            "kubernetes": "db_location",
            "description": "In JSON file name, the location of the logical database to store file in (ex. [db_name].[file_name].0.json)"
        },
        "Table Name Location": {
            "default": "file_name[1]",
            "docker": "TABLE_LOCATION",
            "kubernetes": "table_location",
            "description": "In JSON file name, the location of the table to store file in (ex. [db_name].[file_name].0.json)"
        }
    },
    "mqtt": { # mqtt (for operator + publisher)
        "Enable MQTT": {
            "default": False,
            "options": [True, False],
            "docker": "ENABLE_MQTT",
            "kubernetes": "enable",
            "description": "Whether or not to enable MQTT client process"
        },
        "MQTT Broker": {
            "default": "driver.cloudmqtt.com",
            "docker": "BROKER",
            "kubernetes": "broker",
            "description": "MQTT broker address"
        },
        "MQTT Port": {
            "default": 18785,
            "docker": "MQTT_PORT",
            "kubernetes": "port",
            "description": "Port correlated to MQTT broker"
        },
        "MQTT User": {
            "default": "ibglowct",
            "docker": "MQTT_USER",
            "kubernetes": "user",
            "description": "Set MQTT user - to remove MQTT user, set value to 'empty'",
        },
        "MQTT Password": {
            "default": "MSY4e009J7ts",
            "docker": "MQTT_PASSWORD",
            "kubernetes": "password",
            "description": "Set password for MQTT user - to remove MQTT password, set value to 'empty'",
        },
        "MQTT Log": {
            "default": False,
            "options": [True, False],
            "docker": "MQTT_LOG",
            "kubernetes": "log",
            "description": "output the broker log messages"
        },
        "Topic": {
            "default": "anylogedgex",
            "docker": "MQTT_TOPIC_NAME",
            "kubernetes": "name",
            "description": "MQTT topic"
        },
        "Database Name": {
            "default": "test",
            "docker": "MQTT_TOPIC_DBMS",
            "kubernetes": "db_name",
            "description": "Logical database to store data coming in from MQTT client"
        },
        "Table Name": {
            "default": "rand_data",
            "docker": "MQTT_TABLE_NAME",
            "kubernetes": "table",
            "description": "Table to store data in"
        },
        "Timestamp Column": {
            "default": "now",
            "docker": "MQTT_TOPIC_TIMESTAMP",
            "kubernetes": "timestamp",
            "description": "timestamp column value"
        },
        "Value Column Type": {
            "default": "float",
            "options": ["str", "int", "float", "timestamp", "bool"],
            "docker": "MQTT_COLUMN_VALUE_TYPE",
            "kubernetes": "value_type",
            "description": "Data type for value column"
        },
        "Value Column": {
            "default": "bring [readings][][value]",
            "docker": "MQTT_COLUMN_VALUE",
            "kubernetes": "value",
            "description": "How to extract value from data coming into MQTT client"
        }
    },
    "other": {
        "Deploy Local Script": {
            "default": False,
            "options": [True, False],
            "docker": "DEPLOY_LOCAL_SCRIPT",
            "kubernetes": "deploy_local_script",
            "description": "Deploy user created script",
        },
        "TCP Thread": {
            "default": 6,
            "docker": "TCP_THREAD_POOL",
            "kubernetes": "tcp_thread_pool",
            "description": "number of workers threads that process requests which are send to the provided IP and Port."
        },
        "REST Timeout": {
            "default": 30,
            "docker": "REST_TIMEOUT",
            "kubernetes": "rest_timeout",
            "description": "Amount of time (in seconds) until REST timeout"
        },
        "REST Concurrent Threads":{
            "default": 5,
            "docker": "REST_THREADS",
            "kubernetes": "rest_threads",
            "description": "The number of concurrent threads supporting HTTP requests."
        },
        "Query Pool Count": {
            "default": 3,
            "docker": "OPERATOR_POOL",
            "kubernetes": "operator_pool",
            "description": "Sets the number of threads supporting queries (the default is 3)."
        },
        "Store Data Immediately": {
            "default": True,
            "options": [True, False],
            "docker": "WRITE_IMMEDIATE",
            "kubernetes": "write_immediate",
            "description": "Local database is immediate (independent of the calls to flush)"
        },
        "Threshold Time":{
            "default": "60 seconds",
            "options": ["minute", "seconds", "second"],
            "docker": "THRESHOLD_TIME",
            "description": "The time threshold to flush the streaming data	"
        },
        "Threshold Size": {
            "default": "10KB",
            "options": ["KB", "MB", "GB"],
            "docker": "THRESHOLD_VOLUME",
            "kubernetes": "threshold_volume",
            "description": "The accumulated data volume that calls the data flush process	"
        }
    }
}
def policy_questsions