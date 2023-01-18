import dotenv
import json
import os
import yaml

import support


def __create_file(file_path:str, exception:bool=False)->(str, bool):
    """
    create a new file if DNE
    :args:
        file_path:str - file path
        exception:bool - whether to print exceptions
    :params:
        status:bool
        full_path:str - full path of file_path
    :return:
        full_path, status
    """
    status = True
    full_path = os.path.expanduser(os.path.expandvars(file_path))
    if not os.path.isfile(full_path):
        try:
            open(full_path, 'w').close()
        except Exception as error:
            status = False
            if exception is True:
                print(f'Failed to create file {file_path} (Error: {error})')

    return full_path, status


def __read_dotenv(config_file:str, exception:bool=False)->dict:
    """
    Read configs from .env file
    :args:
        config_file:str - .env file to read configs from
        exception:bool - whether to print exceptions
    :params:
        configs:dict - configs read from .env file
    :return:
        configs
    """
    configs = {}

    try:
        configs = dict(dotenv.dotenv_values(config_file))
    except Exception as error:
        if exception is True:
            print(f'Failed to read configs from {config_file} (Error: {error})')

    return configs


def __read_json(config_file:str, exception:bool=False)->dict:
    """
    Read configs from .env file
    :args:
        config_file:str - .json file to read configs from
        exception:bool - whether to print exceptions
    :params:
        configs:dict - configs read from .env file
    :return:
        configs
    """
    configs = {}

    try:
        with open(config_file) as f:
            try:
                configs = json.load(f)
            except Exception as error:
                if exception is True:
                    print(f'Failed read content in {config_file} (Error: {error})')
    except Exception as error:
        if exception is True:
            print(f'Failed to read configs from {config_file} (Error: {error})')

    return configs


def __read_yaml(config_file:str, exception:bool=False)->dict:
    """
    Read configs from .env file
    :args:
        config_file:str - .json file to read configs from
        exception:bool - whether to print exceptions
    :params:
        configs:dict - configs read from .env file
    :return:
        configs
    """
    configs = {}

    try:
        with open(config_file) as f:
            try:
                configs = yaml.load(f, Loader=yaml.FullLoader)
            except Exception as error:
                if exception is True:
                    print(f'Failed read content in {config_file} (Error: {error})')
    except Exception as error:
        if exception is True:
            print(f'Failed to read configs from {config_file} (Error: {error})')

    return configs


def read_configs(config_file:str, exception:bool=False)->dict:
    """
    Given a configuration file, extract configurations
    :supports:
        - .env
        - .yml (to be developed)
    :args:
        config_file:str - YAML file
        exception:bool - whether to write exception
    :params:
        file_extension:str - file extension
        configs:dict - content in YAML file
    :return:
        configs
    """
    config_file = os.path.expanduser(os.path.expandvars(config_file))
    configs = {}

    if os.path.isfile(config_file):
        file_extension = config_file.rsplit('.', 1)[-1]

        if file_extension == 'env':
            configs = __read_dotenv(config_file=config_file, exception=exception)
        elif file_extension in ['yml', 'yaml']:
            configs = __read_yaml(config_file=config_file, exception=exception)
        elif file_extension == 'json':
            configs = __read_json(config_file=config_file, exception=exception)
        else:
            print(f'Invalid extension type: {file_extension}')
    else:
        print(f'Failed to locate config file {config_file}')

    return configs


def write_configs(file_path:str, configs:dict, kubernetes_configs:dict=None, exception:bool=False)->bool:
    """
    Given a configuration file,
    """
    status = True
    config_file = os.path.expanduser(os.path.expandvars(file_path))

    if os.path.isfile(config_file):
        file_extension = config_file.rsplit('.', 1)[-1]

        if file_extension == 'env':
            content = support.create_env_configs(configs=configs)
        elif file_extension in ['yml', 'yaml']:
            node_name = configs['general']['NODE_NAME']['value'].replace(' ','-').repacel('_','-').lower()
            metadata_content = support.create_kubernetes_metadata(node_name=node_name, configs=kubernetes_configs)
            content = support.create_kubernetes_configs(configs=configs)
        else:
            status = False
            print(f'Invalid extension type: {file_extension}')
    else:
        status = False
        print(f'Failed to locate config file {config_file}')

    return status