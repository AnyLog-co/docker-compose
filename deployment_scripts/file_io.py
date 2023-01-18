import os
try:
    import dotenv
except Exception as error:
    print(f'Failed to find dotenv import package (Error: {error})')

try:
    import json
except Exception as error:
    print(f'Failed to find json import package (Error: {error})')

try:
    import yaml
except Exception as error:
    print(f'Failed to find yaml import package (Error: {error})')


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
        file_name = os.path.join(ROOT_PATH, 'docker-compose', 'anylog-%s' % node_type.lower(), 'anylog_configs.env')
    else:
        file_name = os.path.join(ROOT_PATH, 'docker-compose', 'query-remote-cli', 'anylog_configs.env')

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
    file_name = os.path.join(ROOT_PATH, 'helm', 'sample-configurations', 'anylog_%s.yaml' % node_type.lower())

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


def update_dotenv_tag(file_path:str, build:str, node_name:str, excepton:bool=False)->bool:
    """
    For Docker deployment, update .env file
    :args:
        file_path:str - `anylog_configs.env` file path
        build:str - docker version
        node_name:str - node name
        exception:bool - whether to print exceptions
    :params:
        status:bool
        file_path:str - directory path
        dotenv_file - full path of dotenv file
    :return:
        status
    """
    content = {
        'BUILD': build,
        'ENV_FILE': 'anylog_configs.env',
        'CONTAINER_NAME': node_name,
        'NETWORK': 'host'
    }

    status = True
    dotenv_file = os.path.join(file_path, '.env')

    if os.path.isfile(dotenv_file):
        content = __read_dotenv(config_file=dotenv_file, exception=excepton)
        content['BUILD'] = build
        content['CONTAINER_NAME'] = node_name

    try:
        with open(dotenv_file, 'w') as f:
            for key in content:
                line = f'{key}={content[key]}\n'
                try:
                    f.write(line)
                except Exception as error:
                    if excepton is True:
                        print(f'Failed to write line "{line}" into {dotenv_file} (Error: {error})')
    except Exception as error:
        if excepton is True:
            print(f'Failed to open file {dotenv_file} to write content into (Error: {error})')



    return status



def write_configs(deployment_type:str, configs:dict, build:str=None, kubernetes_configs:dict=None,
                  exception:bool=False)->bool:
    """
    given the information provided, store into the correct file
    :args:
        deployment_type:str - deployment type
            - docker
            - kubernetes
        configs:dict - AnyLog configurations
        kubernetes_configs:dict - Kubernetes configurations
        exception:bool - whether to print exceptions
    :params:
        status:bool
        metadata_content:str - Kubernetes metadata
        node_type:str - node type
        node_name:str - none name
    """
    status = True
    metadata_content = ""

    node_type = configs['general']['NODE_TYPE']['value']
    node_name = configs['general']['NODE_NAME']['value'].replace(' ', '-').replace('_', '-').lower()

    if deployment_type == 'docker':
        content = support.create_env_configs(configs=configs)
        file_path = __create_file_docker(node_type=node_type, exception=exception)
        update_dotenv_tag(file_path=file_path.split('anylog_configs.env')[0], build=build, node_name=node_name,
                          excepton=exception)
    elif deployment_type == 'kubernetes':
        metadata_content = support.create_kubernetes_metadata(node_name=node_name, configs=kubernetes_configs)
        content = support.create_kubernetes_configs(configs=configs)
        file_path = __create_file_kubernetes(node_type=node_type, exception=exception)
        __write_file(file_path=file_path, content=metadata_content, exception=exception)

    __write_file(file_path=file_path, content=content, exception=exception)

    return status