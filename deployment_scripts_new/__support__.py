import ipaddress
import re

import questionnaire


NODE_TYPES = {
    'generic': ['ANYLOG_PATH', 'ANYLOG_LIB', 'ANYLOG_HOME_PATH', 'ANYLOG_ID_DIR', 'BLOCKCHAIN_DIR', 'DATA_DIR',
                'LOCAL_SCRIPTS', 'TEST_DIR', 'LICENSE_KEY', 'NODE_TYPE', 'NODE_NAME', 'COMPANY_NAME', 'LOCATION',
                'COUNTRY', 'STATE', 'CITY', 'ENABLE_AUTH', 'ENABLE_REST_AUTH', 'NODE_PASSWORD', 'USER_NAME',
                'USER_PASSWORD', 'USER_TYPE', 'ROOT_PASSWORD', 'POLICY_BASED_NETWORKING', 'CONFIG_POLICY_NAME',
                'EXTERNAL_IP', 'LOCAL_IP', 'KUBERNETES_SERVICE_IP', 'OVERLAY_IP', 'PROXY_IP', 'ANYLOG_SERVER_PORT',
                'ANYLOG_REST_PORT', 'ANYLOG_BROKER_PORT', 'TCP_BIND', 'TCP_THREADS', 'REST_BIND', 'REST_TIMEOUT',
                'REST_THREADS', 'REST_SSL', 'BROKER_BIND', 'BROKER_THREADS', 'DB_TYPE', 'DB_USER', 'DB_PASSWD',
                'DB_IP', 'DB_PORT', 'AUTOCOMMIT', 'SYSTEM_QUERY', 'MEMORY', 'NOSQL_ENABLE', 'NOSQL_TYPE',
                'NOSQL_USER', 'NOSQL_PASSWD', 'NOSQL_IP', 'NOSQL_PORT', 'NOSQL_BLOBS_DBMS', 'NOSQL_BLOBS_FOLDER',
                'NOSQL_BLOBS_COMPRESS', 'NOSQL_BLOBS_REUSE', 'LEDGER_CONN', 'SYNC_TIME', 'BLOCKCHAIN_SOURCE',
                'BLOCKCHAIN_DESTINATION', 'MEMBER', 'CLUSTER_NAME', 'DEFAULT_DBMS', 'ENABLE_HA', 'START_DATE',
                'ENABLE_PARTITIONS', 'TABLE_NAME', 'PARTITION_COLUMN', 'PARTITION_INTERVAL', 'PARTITION_KEEP',
                'PARTITION_SYNC', 'CREATE_TABLE', 'UPDAE_TSD_INFO', 'ARCHIVE', 'COMPRESS_FILE', 'OPERATOR_THREADS',
                'DBMS_FILE_LOCATION', 'TABLE_FILE_LOCATION', 'PUBLISHER_COMPRESS_FILE', 'ENABLE_MQTT', 'MQTT_LOG',
                'MQTT_BROKER', 'MQTT_PORT', 'MQTT_USER', 'MQTT_PASSWD', 'MQTT_TOPIC', 'MQTT_DBMS', 'MQTT_TABLE',
                'MQTT_TIMESTAMP_COLUMN', 'MQTT_VALUE_COLUMN', 'MQTT_VALUE_COLUMN_TYPE', 'DEPLOY_LOCAL_SCRIPT',
                'QUERY_POOL', 'WRITE_IMMEDIATE', 'THRESHOLD_TIME', 'THRESHOLD_VOLUME', 'MONITOR_NODES',
                'MONITOR_NODE', 'MONITOR_NODE_COMPANY'],
    # 'generic': ['LICENSE_KEY', 'NODE_NAME', 'COMPANY_NAME', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'DB_TYPE',
    #              'DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT', 'SYSTEM_QUERY', 'MEMORY', 'NOSQL_ENABLE',
    #              'NOSQL_USER', 'NOSQL_PASSWD', 'NOSQL_IP', 'NOSQL_PORT', 'LEDGER_CONN', 'ENABLE_MQTT', 'MQTT_LOG',
    #              'MQTT_BROKER', 'MQTT_PORT', 'MQTT_USER', 'MQTT_PASSWD', 'MQTT_TOPIC',
    #              'MQTT_DBMS', 'MQTT_TABLE', 'MQTT_TIMESTAMP_COLUMN', 'MQTT_VALUE_COLUMN', 'MQTT_VALUE_COLUMN_TYPE',
    #              'DEPLOY_LOCAL_SCRIPT', 'MONITOR_NODES', 'MONITOR_NODE', 'MONITOR_NODE_COMPANY'],
    'master': ['LICENSE_KEY', 'NODE_NAME', 'COMPANY_NAME', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'DB_TYPE',
               'DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT', 'SYSTEM_QUERY', 'MEMORY', 'LEDGER_CONN', 'DEPLOY_LOCAL_SCRIPT',
               'MONITOR_NODES', 'MONITOR_NODE', 'MONITOR_NODE_COMPANY'],
    'operator': ['LICENSE_KEY', 'NODE_NAME', 'COMPANY_NAME', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'ANYLOG_BROKER_PORT',
                 'DB_TYPE', 'DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT', 'SYSTEM_QUERY', 'MEMORY', 'NOSQL_ENABLE',
                 'NOSQL_USER', 'NOSQL_PASSWD', 'NOSQL_IP', 'NOSQL_PORT', 'LEDGER_CONN', 'ENABLE_MQTT', 'MQTT_LOG',
                 'MQTT_BROKER', 'MQTT_PORT', 'MQTT_USER', 'MQTT_PASSWD', 'MQTT_TOPIC',
                 'MQTT_DBMS', 'MQTT_TABLE', 'MQTT_TIMESTAMP_COLUMN', 'MQTT_VALUE_COLUMN', 'MQTT_VALUE_COLUMN_TYPE',
                 'DEPLOY_LOCAL_SCRIPT', 'MONITOR_NODES', 'MONITOR_NODE', 'MONITOR_NODE_COMPANY'],
    'publisher': ['LICENSE_KEY', 'NODE_NAME', 'COMPANY_NAME', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'ANYLOG_BROKER_PORT',
                  'DB_TYPE', 'DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT', 'SYSTEM_QUERY', 'MEMORY', 'LEDGER_CONN',
                  'ENABLE_MQTT', 'MQTT_LOG', 'MQTT_BROKER', 'MQTT_PORT', 'MQTT_USER', 'MQTT_PASSWD', 'MQTT_TOPIC',
                  'MQTT_DBMS', 'MQTT_TABLE', 'MQTT_TIMESTAMP_COLUMN', 'MQTT_VALUE_COLUMN', 'MQTT_VALUE_COLUMN_TYPE',
                  'DEPLOY_LOCAL_SCRIPT', 'MONITOR_NODES', 'MONITOR_NODE', 'MONITOR_NODE_COMPANY'],
    'query': ['LICENSE_KEY', 'NODE_NAME', 'COMPANY_NAME', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'DB_TYPE',
               'DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT', 'SYSTEM_QUERY', 'MEMORY', 'LEDGER_CONN', 'DEPLOY_LOCAL_SCRIPT',
               'MONITOR_NODES', 'MONITOR_NODE', 'MONITOR_NODE_COMPANY']
    }

BASIC_CONFIG = ["LICENSE_KEY", "NODE_NAME", "COMPANY_NAME", "LEDGER_CONN", "MONITOR_NODES", "ENABLE_MQTT"]


def format_configs(node_type:str, configs:dict, basic_config:bool=False):
    """
    Enable configurations based on node_type
    :global:
        NODE_TYPES:dict - Node types (generic, operator, master, query, publisher) & configurations user should update
        BASIC_CONFIG:list - required configs when running in demo mode
    :args:
        node_type:str - Node type
        configs:dict - configurations to be updated
        basic_config:bool - whether set only demo configs or "all" configs for a specific node type
    :return:
        enabled configs based on node_type and demo_configs
    """
    configs['general']['NODE_TYPE']['default'] = node_type
    configs['general']['NODE_TYPE']['config_file'] = 'anylog_configs'
    configs['general']['NODE_TYPE']['enable'] = False
    if node_type != "generic":
        configs['general']['NODE_NAME']['default'] = f"anylog-{node_type}"
    if node_type == "master":
        configs['networking']['ANYLOG_SERVER_PORT']['default'] = 32048
        configs['networking']['ANYLOG_REST_PORT']['default'] = 32049
    elif node_type == "operator":
        configs['networking']['ANYLOG_SERVER_PORT']['default'] = 32148
        configs['networking']['ANYLOG_REST_PORT']['default'] = 32149
    elif node_type == "query":
        configs['networking']['ANYLOG_SERVER_PORT']['default'] = 32348
        configs['networking']['ANYLOG_REST_PORT']['default'] = 32349
    elif node_type == "publisher":
        configs['networking']['ANYLOG_SERVER_PORT']['default'] = 32248
        configs['networking']['ANYLOG_REST_PORT']['default'] = 32249

    for section in configs:
        for param in configs[section]:
            if param in NODE_TYPES[node_type]:
                configs[section][param]['enable'] = True
                configs[section][param]['config_file'] = 'anylog_configs'

            if basic_config is True and param not in BASIC_CONFIG:
                configs[section][param]['enable'] = False

    return configs

def print_questions(configs:dict)->bool:
    """
    Whether to print question
    :args:
        configs:dict - configuration
    :param:
        status:bool
    :return:
        if one or more of the config params is enabled return True, else returns False
    """
    for param in configs:
        if configs[param]['enable'] is True:
            return True
    return False

def validate_ip(param:str, ip_addr:str)->str:
    """
    Validate IP address format
    :args:
        param:str - param name
        ip_addr:str - ip address
    :params:
        valid_patterns:list - pattern status
        err_msg:str - error message
        patterns:list - list of patterns
    :return:
        err_msg
    """
    valid_patterns = []
    err_msg = f"Invalid format for {param.replace('_', ' ').lower()}..."
    patterns = [
        r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', # 127.0.0.1
        r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', # my-hostname-123.net
        r'(\d+)\.(\d+)\.(\d+)\.(\d+)', # 10.0.0.255
        r'([a-zA-Z0-9-]+)\.([a-zA-Z0-9-]+)\.([a-zA-Z0-9-]+)\.([a-zA-Z0-9-]+)', # sub-domain.sub.example.co.uk
        r'^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$' # valid hostname format
    ]
    if ip_addr not in ["", None]:
        try:
            valid_patterns.append(ipaddress.IPv4Address(ip_addr))
        except ipaddress.AddressValueError or TypeError:
            for pattern in patterns:
                valid_patterns.append(re.match(pattern, ip_addr))
    if True in valid_patterns or ip_addr in ["", None]:
        err_msg = ""

    return err_msg

def validate_port(param:str, port:str, rng:list=None)->str:
    """
    Validate port value
    :args:
        param:str - param name
        value:str - value to check
        rng:list - range value to be within
    :params:
        err_msg:str - error message
    :return:
        err_msg
    """
    err_msg = ""
    try:
        port = int(port)
    except Exception as error:
        err_msg = f"Invalid type {type(port)} for {param.replace('_', ' ').title()}..."
    else:
        if rng is not None and port < rng[0] or port > rng[1]:
            err_msg = f"Value for {param.replace('_', ' ').title()} out of range..."

    return port, err_msg

def validate_ports(configs:dict)->dict:
    """
    Validate port values
    :args:
        configs:dict
    :params:
        status:bool
        anylog_tcp:dict - sub-configs for TCP
        anylog_rest:dict - sub-configs for REST
        anylog_broker:dict - sub-configs for broker
    :configs:
        updated & validated configs
    """
    anylog_tcp = configs['ANYLOG_SERVER_PORT']
    anylog_rest = configs['ANYLOG_REST_PORT']
    anylog_broker = configs['ANYLOG_BROKER_PORT']
    if anylog_broker['value'] is None:
        anylog_broker['value'] = ""

    status = False
    while status is False:
        anylog_tcp['value'], err_msg = validate_port(param='ANYLOG_SERVER_PORT', port=anylog_tcp['value'], rng=anylog_tcp['range'])
        if err_msg != "":
            continue
        anylog_rest['value'], err_msg = validate_port(param='ANYLOG_REST_PORT', port=anylog_rest['value'], rng=anylog_rest['range'])
        if err_msg != "":
            continue
        if anylog_broker['value'] not in ["", None]:
            anylog_broker['value'], err_msg = validate_port(param='ANYLOG_BROKER_PORT', port=anylog_broker['value'], rng=anylog_broker['range'])
            if err_msg != "":
                continue

        if anylog_tcp['value'] == anylog_rest['value']:
            err_msg = f"REST port value {anylog_tcp['value']} is already used by the TCP service..."
            anylog_rest = questionnaire.__get_answer(param='ANYLOG_REST_PORT', configs=anylog_rest, err_msg=err_msg)
            continue
        elif anylog_broker['value'] != '':
            if anylog_tcp['value'] == anylog_broker['value']:
                err_msg = f"Broker port value {anylog_tcp['value']} is already used by the TCP service..."
                anylog_broker = questionnaire.__get_answer(param='ANYLOG_BROKER_PORT', configs=anylog_broker, err_msg=err_msg)
                continue
            elif anylog_rest == anylog_broker:
                err_msg = f"Broker port value {anylog_rest} is already used by the REST service..."
                anylog_broker = questionnaire.__get_answer(param='ANYLOG_BROKER_PORT', configs=anylog_broker, err_msg=err_msg)
                continue
            else: # no two services share a port value
                status = True
        else:
            status = True

    configs['ANYLOG_SERVER_PORT'] = anylog_tcp
    configs['ANYLOG_REST_PORT'] = anylog_rest
    configs['ANYLOG_REST_PORT'] = anylog_broker

    return configs


def validate_process_time(param:str, value:str, options:list)->str:
    """
    Validate process time
    """
    err_msg = ""
    pattern = fr"^(\d+)\s*({'|'.join(options)})"
    if not re.match(pattern, value):
        err_msg = f"Invalid value {value} for {param.lower().replace('_', ' ')}..."
    return err_msg