import argparse
import json
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
            state = content['region']
            city = content['city']
    return loc, country, state, city


LOC, COUNTRY, STATE, CITY = __locations()


PARAMS = {
    "general": {
        # General Information
        "Node Type": {
            "default": "rest",
            "value": None,
            "docker": "NODE_TYPE",
            "kubernetes": "node_type",
            "description": "Deployment node type"
        },
        "Node Name": {
            "default": "anylog-node",
            "value": None, 
            "docker": "NODE_NAME",
            "kubernetes": "node_name",
            "description": "Unique name for the AnyLog node"
        },
        "Company": {
            "default": "New Company",
            "value": None, 
            "docker": "COMPANY_NAME",
            "kubernetes": "company_name",
            "description": "Company owner of the node"
        },
        "Coordinates": {
            "default": LOC,
            "value": None, 
            "docker": "LOCATION",
            "kubernetes": "location",
            "description": "Physical location of the node"
        },
        "Country": {
            "default": COUNTRY,
            "value": None, 
            "docker": "COUNTRY",
            "kubernetes": "country",
            "description": "Country node is located in"
        },
        "State": {
            "default": STATE,
            "value": None, 
            "docker": "STATE",
            "kubernetes": "state",
            "description": "State node is located in"
        },
        "City": {
            "default": CITY,
            "value": None, 
            "docker": "CITY",
            "kubernetes": "city",
            "description": "City node is located in"
        },

        # Networking
        "TCP Port": {
            "default": 32048,
            "range": [30000, 32767],
            "value": None, 
            "docker": "ANYLOG_SERVER_PORT",
            "kubernetes": "server",
            "description": "Port for TCP communication between nodes"
        },
        "REST Port": {
            "default": 32049,
            "range": [30000, 32767],
            "value": None, 
            "docker": "ANYLOG_REST_PORT",
            "kubernetes": "rest",
            "description": "Port for REST communication with the node"
        },
        "Broker Port": {
            "default": "",
            "range": [30000, 32767],
            "value": None, 
            "docker": "ANYLOG_BROKER_PORT",
            "kubernetes": "broker",
            "description": "Message Broker Port for the node"
        },
        "External IP": {
            "default": __external_ip(),
            "value": None, 
            "docker": "EXTERNAL_IP",
            "kubernetes": "external_ip",
            "description": "External Network IP address"
        },
        "Local IP": {
            "default": __local_ip(),
            "value": None, 
            "docker": "LOCAL_IP",
            "kubernetes": "k8s_proxy_ip",
            "description": "Local IP of the machine - if running on Kubernetes this value will be set as the Proxy IP"
        },

        # Blockchain sync
        "Ledger Conn": {
            "default": "127.0.0.1:32048",
            "value": None, 
            "docker": "LEDGER_CONN",
            "kubernetes": "ledger_conn",
            "description": "Blockchain ledger TCP connection information"
        },
        "Sync Time": {
            "default": "30 seconds",
            "options": ["seconds", "minute", "hour", "day"],
            "value": None, 
            "docker": "SYNC_TIME",
            "kubernetes": "sync_time",
            "description": "How often to sync against the blockchain",
        },
        "Blockchain Source": {
            "default": "master",
            "options": ["blockchain", "master"],
            "value": None, 
            "docker": "SOURCE",
            "kubernetes": "source",
            "description": "Source of where the data is coming from"
        },
        "Destination": {
            "default": "file",
            "options": ["file", "dbms"],
            "value": None, 
            "docker": "DESTINATION",
            "kubernetes": "destination",
            "description": "Where will the copy of the blockchain be stored"
        },

        # Database
        "Database Type": {
            "default": "psql",
            "options": ["psql", "sqlite"],
            "value": None, 
            "docker": "db_type",
            "kubernetes": "type",
            "description": "Physical database type"
        },
        "Database IP": {
            "default": "127.0.0.1",
            "value": None, 
            "docker": "db_ip",
            "kubernetes": "ip",
            "description": "Database IP"
        },
        "Database Port": {
            "default": 5432,
            "value": None, 
            "docker": "db_port",
            "kubernetes": "ip",
            "description": "Database port"
        },
        "Database User": {
            "default": "admin",
            "value": None, 
            "docker": "db_user",
            "kubernetes": "user",
            "description": "User correlated to this database"
        },
        "Database User Password": {
            "default": "demo",
            "value": None, 
            "docker": "db_passwd",
            "kubernetes": "password",
            "description": "Password correlated to user for accessing database"
        },
        "Enable system_query": {
            "default": False,
            "value": None, 
            "docker": "DEPLOY_SYSTEM_QUERY",
            "kubernetes": "deploy_system_query",
            "description": "Whether or not to automatically create system_query logical database on node"
        },
        "Set system_query in memory": {
            "default": True,
            "value": None, 
            "docker": "MEMORY",
            "kubernetes": "memory",
            "description": "Run system_query logical database in-memory"
        },
    },
    "operator": { #  Operator specific params
        "Database Name": {
            "default": "test",
            "value": None, 
            "docker": "DEFAULT_DBMS",
            "kubernetes": "db_name",
            "description": "Logical database to store data coming into Operator"
        },
        "Operator Member ID": {
            "default": "",
            "value": None, 
            "docker": "MEMBER",
            "kubernetes":" member",
            "description": "Operator member ID - by default it's autogenerated, should be set only when resetting blockchain, but want to keep exactly the same information"
        },
        "Cluster Name": {
            "default": "new-cluster",
            "value": None, 
            "docker": "CLUSTER_NAME",
            "kubernetes": "cluster-name",
            "description": "Name of the cluster operator will be associated with"
        },
        "Create Table": {
            "default": True,
            "options": [True, False],
            "value": None, 
            "docker": "CREATE_TABLE",
            "kubernetes": "create_table",
            "description": "creates a table if the table doesn't exists"
        },
        "Update TSD Info": {
            "default": True,
            "options": [True, False],
            "value": None, 
            "docker": "UPDATE_TSD",
            "kubernetes": "update_tsd",
            "description": "update a summary table (tsd_info table in almgm dbms) with status of files ingested. (by default, almgm database & tsd_info table get created on all operator nodes)"
        },
        "Archive Data": {
            "default": True,
            "options": [True, False],
            "value": None, 
            "docker": "ARCHIVE",
            "kubernetes": "archive",
            "description": "move JSON files to archives"
        },
        "Distribute Data": {
            "default": True,
            "options": [True, False],
            "value": None, 
            "docker": "DISTRIBUTOR",
            "kubernetes": "distributor",
            "description": "Transfer data files to members of the cluster"
        },
        # Data partitioning
        "Enable Partitions": {
            "default": True,
            "options": [True, False],
            "value": None, 
            "docker": "ENABLE_PARTITIONS",
            "kubernetes": "enable_partitions",
            "description": "whether or not to partition data on node"
        },
        "Table(s) to Partition": {
            "default": "*",
            "value": None, 
            "docker": "PARTITION_TABLE",
            "kubernetes": "partition_table",
            "description": "table(s) to partition (default - all tables)"
        },
        "Partitioning Column": {
            "default": "insert_timestamp",
            "value": None, 
            "docker": "PARTITION_COLUMN",
            "kubernetes": "column",
            "description": "Timestamp column to partition by"
        },
        "Partition Interval": {
            "default": "14 days",
            "options": ["year", "month", "week", "days", "day"],
            "value": None, 
            "docker": "PARTITION_INTERVAL",
            "kubernetes": "interval",
            "description": "Amount of time to partition by"
        },
        "Partition Keep": {
            "default": 6,
            "value": None, 
            "docker": "PARTITION_KEEP",
            "kubernetes": "keep",
            "description": "Number of partition to keep"
        },
        "Partition Sync": {
            "default": "1 day",
            "options": ["year", "month", "week", "days", "day"],
            "value": None, 
            "docker": "PARTITION_SYNC",
            "kubernetes": "sync",
            "description": "How often remove excess partitions"
        }
    },
    "publisher": { # Publisher specific params
        "Compress JSON": {
            "default": True,
            "options": [True, False],
            "value": None, 
            "docker": "COMPRESS_JSON",
            "kubernetes": "compress",
            "description": "Compress archived JSON files"
        },
        "Backup JSON": {
            "default": True,
            "options": [True, False],
            "value": None, 
            "docker": "MOVE_JSON",
            "kubernetes": "move",
            "description": "Backup JSON files in publisher after distributing them to operator node(s)"
        },
        "Database Name Location": {
            "default": "file_name[0]",
            "value": None, 
            "docker": "DB_LOCATION",
            "kubernetes": "db_location",
            "description": "In JSON file name, the location of the logical database to store file in (ex. [db_name].[file_name].0.json)"
        },
        "Table Name Location": {
            "default": "file_name[1]",
            "value": None, 
            "docker": "TABLE_LOCATION",
            "kubernetes": "table_location",
            "description": "In JSON file name, the location of the table to store file in (ex. [db_name].[file_name].0.json)"
        }
    },
    "mqtt": { # mqtt (for operator + publisher)
        "Enable MQTT": {
            "default": False,
            "options": [True, False],
            "value": None, 
            "docker": "ENABLE_MQTT",
            "kubernetes": "enable",
            "description": "Whether or not to enable MQTT client process"
        },
        "MQTT Broker": {
            "default": "driver.cloudmqtt.com",
            "value": None, 
            "docker": "BROKER",
            "kubernetes": "broker",
            "description": "MQTT broker address"
        },
        "MQTT Port": {
            "default": 18785,
            "value": None, 
            "docker": "MQTT_PORT",
            "kubernetes": "port",
            "description": "Port correlated to MQTT broker"
        },
        "MQTT User": {
            "default": "ibglowct",
            "value": None, 
            "docker": "MQTT_USER",
            "kubernetes": "user",
            "description": "Set MQTT user - to remove MQTT user, set value to 'empty'",
        },
        "MQTT Password": {
            "default": "MSY4e009J7ts",
            "value": None, 
            "docker": "MQTT_PASSWORD",
            "kubernetes": "password",
            "description": "Set password for MQTT user - to remove MQTT password, set value to 'empty'",
        },
        "MQTT Log": {
            "default": False,
            "options": [True, False],
            "value": None, 
            "docker": "MQTT_LOG",
            "kubernetes": "log",
            "description": "output the broker log messages"
        },
        "Topic": {
            "default": "anylogedgex",
            "value": None, 
            "docker": "MQTT_TOPIC_NAME",
            "kubernetes": "name",
            "description": "MQTT topic"
        },
        "Database Name": {
            "default": "test",
            "value": None, 
            "docker": "MQTT_TOPIC_DBMS",
            "kubernetes": "db_name",
            "description": "Logical database to store data coming in from MQTT client"
        },
        "Table Name": {
            "default": "rand_data",
            "value": None, 
            "docker": "MQTT_TABLE_NAME",
            "kubernetes": "table",
            "description": "Table to store data in"
        },
        "Timestamp Column": {
            "default": "now",
            "value": None, 
            "docker": "MQTT_TOPIC_TIMESTAMP",
            "kubernetes": "timestamp",
            "description": "timestamp column value"
        },
        "Value Column Type": {
            "default": "float",
            "options": ["str", "int", "float", "timestamp", "bool"],
            "value": None, 
            "docker": "MQTT_COLUMN_VALUE_TYPE",
            "kubernetes": "value_type",
            "description": "Data type for value column"
        },
        "Value Column": {
            "default": "bring [readings][][value]",
            "value": None, 
            "docker": "MQTT_COLUMN_VALUE",
            "kubernetes": "value",
            "description": "How to extract value from data coming into MQTT client"
        }
    },
    "other": {
        "Deploy Local Script": {
            "default": False,
            "options": [True, False],
            "value": None, 
            "docker": "DEPLOY_LOCAL_SCRIPT",
            "kubernetes": "deploy_local_script",
            "description": "Deploy user created script",
        },
        "TCP Thread": {
            "default": 6,
            "value": None, 
            "docker": "TCP_THREAD_POOL",
            "kubernetes": "tcp_thread_pool",
            "description": "number of workers threads that process requests which are send to the provided IP and Port."
        },
        "REST Timeout": {
            "default": 30,
            "value": None, 
            "docker": "REST_TIMEOUT",
            "kubernetes": "rest_timeout",
            "description": "Amount of time (in seconds) until REST timeout"
        },
        "REST Concurrent Threads":{
            "default": 5,
            "value": None, 
            "docker": "REST_THREADS",
            "kubernetes": "rest_threads",
            "description": "The number of concurrent threads supporting HTTP requests."
        },
        "Query Pool Count": {
            "default": 3,
            "value": None, 
            "docker": "OPERATOR_POOL",
            "kubernetes": "operator_pool",
            "description": "Sets the number of threads supporting queries (the default is 3)."
        },
        "Store Data Immediately": {
            "default": True,
            "options": [True, False],
            "value": None, 
            "docker": "WRITE_IMMEDIATE",
            "kubernetes": "write_immediate",
            "description": "Local database is immediate (independent of the calls to flush)"
        },
        "Threshold Time":{
            "default": "60 seconds",
            "options": ["minute", "seconds", "second"],
            "value": None, 
            "docker": "THRESHOLD_TIME",
            "description": "The time threshold to flush the streaming data	"
        },
        "Threshold Size": {
            "default": "10KB",
            "options": ["KB", "MB", "GB"],
            "value": None, 
            "docker": "THRESHOLD_VOLUME",
            "kubernetes": "threshold_volume",
            "description": "The accumulated data volume that calls the data flush process	"
        }
    }
}


def check_port(value:int, ports:list, port_range:list)->bool:
    """
    Check if Port is being used or not
    :args:
        value:int - value to test
        ports:list - list of other ports
        range:list - range of ports
    :params:
        status:bool
    :return:
        status
    """
    status = True
    if value == '':
        return status
    if value not in range(port_range[0], port_range[1]+1):
        print(f'Port value {value} is out of range. Port value range: {port_range[0]} - {port_range[1]}')
        status = False
    elif value in ports:
        print(f'Port is already set to be used by another AnyLog process')
        status = False
    return status


def check_string(input:str, options:list)->bool:
    """
    Check if string is a valid input option
    :args:
        input:str - string to check
        options:str - list of options
    :params:
        status:bool
        updated_input:str - input without integer values
    :return:
        status
    """
    status = True
    updated_input = ''.join([char for char in input if not char.isdigit() and char != ' '])
    if updated_input.lower() not in options:
        print(f'configuration option {updated_input} in {input} is invalid. Valid Options: {str(options.split("[")[-1].split("]")[0])}')
        status = False
    return status


def policy_questsion(section:str):
    print(f'Configuring {section.capitalize()} Information Section')
    for key in PARAMS[section]:
        status = False
        while status is False:
            # generate question
            question = f'\t{key} [default: {PARAMS[section][key]["default"]}'
            if 'options' in PARAMS[section][key]:
                question += f" | Options: {str(PARAMS[section][key]['options']).split('[')[-1].split(']')[0]}"
            elif 'range' in PARAMS[section][key]:
                question += f" | Port Range: {PARAMS[section][key]['range'][0]} - {PARAMS[section][key]['range'][1]}"
            question += "]: "

            # validate user input
            value = input(question)
            if value.isnumeric():
                value = int(value)
            elif value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False

            if value == 'help':
                print(f'{key} - {PARAMS[section][key]["description"]}')
            elif key == 'TCP Port':
                status = check_port(value=value, ports=[], port_range=PARAMS[section][key]['range'])
            elif key == 'REST Port':
                status = check_port(value=value, ports=[PARAMS[section]['TCP Port']['default']],
                                    port_range=PARAMS[section][key]['range'])
            elif key == 'Broker Port':
                status = check_port(value=value, ports=[PARAMS[section]['TCP Port']['default'],
                                                        PARAMS[section]['REST Port']['default']],
                                    port_range=PARAMS[section][key]['range'])
            elif key in ['Sync Time', 'Threshold Time', 'Threshold Size'] and value != '':
                status = check_string(input=value, options=PARAMS[section][key]['options'])
            elif 'options' in PARAMS[section][key] and value not in PARAMS[section][key]['options'] and value != '':
                print(f"Invalid Option {value}. Input options: {PARAMS[section][key]['options'].split('[')[-1].split(']')[0]}")
            else:
                status = True

        # print value
        if value == '':
            value = PARAMS[section][key]['default']
        PARAMS[section][key]['value'] = value


def main():
    """

    """
    parse = argparse.ArgumentParser()
    parse.add_argument('node_type', choices=['help', 'rest', 'master', 'operator', 'query', 'publisher'], default='rest',
                       help='select node type to prepare. Option help will provide details about the different node types')
    parse.add_argument('--deployment-type', choices=['docker', 'kubernetes'], default='docker', help='Deployment type')
    args = parse.parse_args()

    if args.node_type == 'help':
        print('Node type options to deploy:'
              +'\n\trest - sandbox for understanding AnyLog as only TCP & REST are configured'
              +'\n\tmaster - a database node replacing an actual blockchain'
              +'\n\toperator - node where data will be stored'
              +'\n\tpublisher - node to distribute data among operators'
              +'\n\tquery - node dedicated to master node'
        )
        exit(1)
    print("AnyLog Configuration Questionnaire. Type 'help' for information regarding param ")
    for section in list(PARAMS.keys()):
        if section == args.node_type: # publisher or operator
            policy_questsion(section=section)
        elif section == 'mqtt' and args.node_type in ['rest', 'operator', 'publisher']:
            policy_questsion(section=section)
        else:
            policy_questsion(section=section)
    print(json.dumps(PARAMS, indent=4))


if __name__ == '__main__':
    main()