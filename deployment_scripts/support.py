import json 
import os 


def json_read_file(file_name:str) -> dict:
    """
    Read JSON file 
    :args:
        file_name:str - file to read content from 
    :params: 
        content:dict - content from file 
    :return: 
        content
    """
    content = {}
    full_path = os.path.expandvars(os.path.expanduser(file_name))
    if os.path.isfile(full_path):
        try:
            with open(full_path, 'r') as f:
                try:
                    content = json.load(f)
                except Exception as error:
                    print(f'Failed to read content in {file_name} (Error: {error})')
        except Exception as error:
            print(f'Failed to open file {file_name} (Error: {error})')

    return content 


def clean_configs(node_type:str, configs:dict)->dict:
    """
    Based on the node_type remove un-need configurations
    :args:
        node_type:str
        configs:dict - configurations
    :return:
        cleaned configs
    """
    configs['general']['NODE_TYPE']['value'] = node_type
    if node_type == 'master':
        configs['general']['NODE_TYPE']['value'] = 'ledger'
        configs['general']['NODE_NAME']['default'] = f'anylog-{node_type}'
    elif node_type == 'operator':
        configs['general']['NODE_NAME']['default'] = f'anylog-{node_type}'
        configs['networking']['ANYLOG_SERVER_PORT']['default'] = 32148
        configs['networking']['ANYLOG_REST_PORT']['default'] = 32149
    elif node_type == 'publisher':
        configs['general']['NODE_NAME']['default'] = f'anylog-{node_type}'
        configs['networking']['ANYLOG_SERVER_PORT']['default'] = 32248
        configs['networking']['ANYLOG_REST_PORT']['default'] = 32249
    elif node_type == 'query':
        configs['general']['NODE_NAME']['default'] = f'anylog-{node_type}'
        configs['networking']['ANYLOG_SERVER_PORT']['default'] = 32348
        configs['networking']['ANYLOG_REST_PORT']['default'] = 32349

    for section in configs:
        if section == 'networking' and node_type in ['master', 'query']:
            configs[section]['ANYLOG_BROKER_PORT']['enable'] = False
            configs[section]['BROKER_BIND']['enable'] = False
        elif section == 'database' and node_type in ['master', 'publisher', 'query', 'standalone-publisher']:
            for param in configs[section]:
                if param == 'SYSTEM_QUERY' and node_type == 'query':
                    configs[section][param]['default'] = 'true'
                elif 'NOSQL' in param or param == 'AUTOCOMMIT':
                    configs[section][param]['enable'] = False
        elif section == 'operator' and node_type in ['master', 'publisher', 'query', 'standalone-publisher']:
            for param in configs[section]:
                configs[section][param]['enable'] = False
        elif section == 'publisher' and node_type in ['master', 'operator', 'query', 'standalone']:
            for param in configs[section]:
                configs[section][param]['enable'] = False
        elif section == 'mqtt' and node_type in ['master', 'query']:
            for param in configs[section]:
                configs[section][param]['enable'] = False
        elif section == 'advanced settings' and node_type in ['master', 'query']:
            for param in configs[section]:
                if param != 'DEPLOY_LOCAL_SCRIPT':
                    configs[section][param]['enable'] = False

    return configs


def print_questions(configs:dict)->bool:
    """
    Whether or not to print question
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


def prepare_mqtt_params(configs:dict, db_name:str, port:int, user:str, password:str)->dict:
    """
    update the default MQTT parameters to match information already provided by the user.
    :args:
        configs:dict - (preset) MQTT configurations
        db_name:str - default logical database
        port:int - AnyLog broker port
        user:str - authentication user
        password:str - authentication user
    :return:
        (updated) configs
    """
    configs['MQTT_DBMS']['default'] = db_name
    # if local broker port is set, then update configs accordingly
    if port != "":
        configs['MQTT_PORT']['default'] = port
        configs['MQTT_BROKER']['default'] = 'local'
        configs['MQTT_USER']['default'] = user
        configs['MQTT_PASSWD']['default'] = password

    return configs
