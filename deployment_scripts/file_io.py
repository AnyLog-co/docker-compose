import dotenv
import json
import os
import yaml

import support

ROOT_PATH = os.path.expandvars(os.path.expanduser(__file__)).split('deployment_scripts')[0]

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

def __create_file_docker(node_type:str, exception:bool=False)->str:
    """
    Create file path  based on node_type
    :note:
        query is stored in query-remote-cli
    :args:
        node_type;str - node type
            - rest
            - master
            - operator
            - publisher
            - query
        exception:bool - whether to print exception
    :params:
        file_name:str - file to store data in
    :return:
        file_name
    """
    if node_type != 'query':
        file_name = os.path.join(ROOT_PATH, 'docker-compose', 'anylog-%s' % node_type.lower())
    else:
        file_name = os.path.join(ROOT_PATH, 'docker-compose', 'query-remote-cli' % node_type.lower())

    # if file exists make a backup
    if os.path.isfile(file_name):
        try:
            os.rename(file_name, file_name.replace('.env', '.env.old'))
        except Exception as error:
            file_name = ''
            if  exception is True:
                print(f'Failed to rename {file_name} (Error: {error})')

    return file_name


def __create_file_kubernetes(node_type:str, exception:bool=False)->str:
    """
    Create file path  based on node_type
    :note:
        query is stored in query-remote-cli
    :args:
        node_type;str - node type
            - rest
            - master
            - operator
            - publisher
            - query
        exception:bool - whether to print exception
    :params:
        file_name:str - file to store data in
    :return:
        file_name
    """
    file_name = os.path.join(ROOT_PATH, 'helm', 'sample-configurations', 'anylog_%s' % node_type.lower())

    # if file exists make a backup
    if os.path.isfile(file_name):
        try:
            os.rename(file_name, file_name.replace('.env', '.env.old'))
        except Exception as error:
            file_name = ''
            if  exception is True:
                print(f'Failed to rename {file_name} (Error: {error})')

    return file_name


def __write_file(file_path:str, content:str, exception:bool=False):
    """
    Write content to file
    :args:
        file_path:str - file to write content into
        content:str - content to write
        exception:bool - whether to print exceptions
    """
    try:
        with open(file_path, 'w') as f:
            try:
                f.write(content)
            except Exception as error:
                if exception is True:
                    print(f'Failed to write content into {file_path} (Error: {error})')
    except Exception as error:
        if exception is True:
            print(f'Failed to open file {file_path} (Error: {error})')


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


def write_configs(deployment_type:str, configs:dict, kubernetes_configs:dict=None, exception:bool=False)->bool:
    """
    Given a configuration file,
    """
    status = True
    metadata_content = ""

    node_type = configs['general']['NODE_TYPE']['value']
    node_name = configs['general']['NODE_NAME']['value'].replace(' ', '-').repacel('_', '-').lower()

    if deployment_type == 'docker':
        content = support.create_env_configs(configs=configs)
        file_path  = __create_file_docker(node_type=node_type, exception=exception)
    elif deployment_type == 'kubernetes':
        metadata_content = support.create_kubernetes_metadata(node_name=node_name, configs=kubernetes_configs)
        content = support.create_kubernetes_configs(configs=configs)
        file_name = __create_file_kubernetes(node_type=node_type, exception=exception)

    __write_file(file_path=file_path, content=content, exception=exception)

    return status