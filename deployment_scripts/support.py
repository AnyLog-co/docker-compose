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
        del configs['nosql database']
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