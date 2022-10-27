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
            with open(file_name, 'r') as f:
                try:
                    content = json.load(f)
                except Exception as error:
                    print(f'Failed to read content in {CONFIGS_FILE} (Error: {error})')
        except Exception as error:
            print(f'Failed to open file {CONFIGS_FILE} (Error: {error})')

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
    if node_type == 'query': 
        configs['sql database']['SYSTEM_QUERY']['default'] = True
    if node_type in ['master', 'publisher', 'query', 'standalone-publisher']:
        for param in configs['database']:
            if 'NOSQL' in param:
                configs['database'][param]['enable'] = False
    if node_type in ['master', 'query']:
        # remove operator and publisher configs
        pass
    elif node_type in ['operator', 'standalone']:
        # remove publisher configs
        pass
    elif node_type in ['publisher', 'standalone-publisher']:
        # remove operator configs
        pass

    return configs


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
    configs['MQTT_TOPIC_DBMS']['default'] = db_name
    configs['MQTT_PORT']['default'] = port
    if port != "": # if local broker port is set, then update configs accordingly
        configs['MQTT_broker']['default'] = 'local'
        configs['MQTT_USER']['default'] = user
        configs['MQTT_PASSWD']['default'] = password

    return configs