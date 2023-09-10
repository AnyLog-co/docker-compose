import ipaddress
import re

from questionnaire import __get_answer

NODE_TYPES = {
    'generic': ['LICENSE_KEY', 'NODE_NAME', 'COMPANY_NAME', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'DB_TYPE',
                 'DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT', 'SYSTEM_QUERY', 'MEMORY', 'NOSQL_ENABLE',
                 'NOSQL_USER', 'NOSQL_PASSWD', 'NOSQL_IP', 'NOSQL_PORT', 'LEDGER_CONN', 'ENABLE_MQTT', 'MQTT_LOG',
                 'MQTT_BROKER', 'MQTT_PORT', 'MQTT_USER', 'MQTT_PASSWD', 'MQTT_TOPIC',
                 'MQTT_DBMS', 'MQTT_TABLE', 'MQTT_TIMESTAMP_COLUMN', 'MQTT_VALUE_COLUMN', 'MQTT_VALUE_COLUMN_TYPE',
                 'DEPLOY_LOCAL_SCRIPT', 'MONITOR_NODES', 'MONITOR_NODE', 'MONITOR_NODE_COMPANY'],
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


def validate_ports(anylog_tcp:dict, anylog_rest:dict, anylog_broker:dict):
    """
    Validate no two ports are the same
    :args:
        anylog_tcp:dict - AnyLog TCP configs
        anylog_rest:dict - AnyLog REST configs
        anaylog_broker:dict - AnyLog broker configs
    :params:
        status:bool
        err_msg:str - error meessage
    :return:
        anylog_rest, anylog_broker
    """
    status = False
    if anylog_tcp['value'] == anylog_tcp['default'] and anylog_rest['value'] == anylog_rest['default'] and anylog_broker['value'] == anylog_broker['default']:
        status = True

    while status is False:
        err_msg = ""
        try:
            anylog_tcp['value'] = int(anylog_tcp['value'])
        except Exception as error:
            err_msg = f"TCP value type is invalid (Error: {error})..."
            anylog_tcp = __get_answer(param='ANYLOG_SERVER_PORT', configs=anylog_tcp, err_msg=err_msg)
            continue
        try:
            anylog_rest['value'] = int(anylog_rest['value'])
        except Exception as error:
            err_msg = f"REST value type is invalid (Error: {error})..."
            anylog_rest = __get_answer(param='ANYLOG_REST_PORT', configs=anylog_rest, err_msg=err_msg)
            continue
        try:
            anylog_broker['value'] = int(anylog_broker['value'])
        except Exception as error:
            err_msg = f"Broker value type is invalid (Error: {error})..."
            anylog_broker = __get_answer(param='ANYLOG_BROKER_PORT', configs=anylog_broker, err_msg=err_msg)
            continue

        if anylog_tcp['value'] == anylog_rest['value']:
            err_msg = f"REST port value {anylog_tcp['value']} is already used by the TCP service..."
            anylog_rest = __get_answer(param='ANYLOG_REST_PORT', configs=anylog_rest, err_msg=err_msg)
            continue
        elif anylog_tcp['value'] == anylog_broker['value']:
            err_msg = f"Broker port value {anylog_tcp['value']} is already used by the TCP service..."
            anylog_broker = __get_answer(param='ANYLOG_BROKER_PORT', configs=anylog_broker, err_msg=err_msg)
            continue
        elif anylog_rest == anylog_broker:
            err_msg = f"Broker port value {anylog_rest} is already used by the REST service..."
            anylog_broker = __get_answer(param='ANYLOG_BROKER_PORT', configs=anylog_broker, err_msg=err_msg)
            continue
        else: # no two services share a port value
            status = True

    return anylog_tcp, anylog_rest, anylog_broker


def validate_ips(param:str, configs:str):
    """
    Validate IP address
    :args:
        param:dict - param name
        configs:dict - configuraiton for givenn param
    ::params:
        status:bool
        valid_patterns:list - list of statuses (must have at least 1 True
        patterns:list - list of patterns
        err_msg:str - error message
    :return:
        config, error_msg
    """
    status = False
    valid_patterns = []
    patterns = [
        r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', # 127.0.0.1
        r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', # my-hostname-123.net
        r'(\d+)\.(\d+)\.(\d+)\.(\d+)', # 10.0.0.255
        r'([a-zA-Z0-9-]+)\.([a-zA-Z0-9-]+)\.([a-zA-Z0-9-]+)\.([a-zA-Z0-9-]+)', # sub-domain.sub.example.co.uk
        r'^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$' # valid hostname format
    ]

    while status is False:
        err_msg = ""
        for pattern in patterns:
            valid_patterns.append(re.match(pattern, configs['value']))
        if True in valid_patterns:
            status = True
            continue

        user_input = ""
        err_msg = ""
        while user_input not in ["y", " n"]:
            user_input = input(f"\t{err_msg.strip()}IP pattern for  not found, do you want to keep IP {configs['value']} [y/n]? ").strip().lower()
            if user_input not in ["y", " n"] and err_msg != "":
                err_msg = f'Invalid answer {user_input}, please try again.. '

        if user_input == "y":
            status = True
            err_msg = ""
            continue

        err_msg = f"Invalid {param} value.. "

    return configs, err_msg


def validate_ledger(ledger_conn:str):
    status = True
    err_msg = ""
    ip_patterns = [
        r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$',  # 127.0.0.1
        r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',  # my-hostname-123.net
        r'(\d+)\.(\d+)\.(\d+)\.(\d+)',  # 10.0.0.255
        r'([a-zA-Z0-9-]+)\.([a-zA-Z0-9-]+)\.([a-zA-Z0-9-]+)\.([a-zA-Z0-9-]+)',  # sub-domain.sub.example.co.uk
        r'^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'  # valid hostname format
    ]
    if ':' in ledger_conn:
        ip, port = ledger_conn.split(":")
        try:
            port = int(port)
        except Exception as error:
            err_msg = f"LEDGER_CONN port is not of type integer (Error: {error})..."
        else:
            if port < 2048 or port > 32767:
                err_msg = f"LEDGER_CONN port value {port} out of range..."
            else:
                status = False
                for ip_pattern in ip_patterns:
                    if re.match(ip_pattern, ip):
                        status = True
        if status is False:
            err_msg = "Invalid LEDGER_CONN IP address..."
    else:
        err_msg = "Invalid ledger_conn connection information..."

    return ledger_conn, err_msg

