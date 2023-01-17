import dotenv
import json
import os
import yaml


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


def __create_env_configs(configs:dict)->str:
    """

    """
    content = ""
    for section in configs:
        content += f'# --- {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")} ---'
        for param in configs[section]:
            comment = configs[section][param]['description'].replace('\n', '')
            if configs[section][param]['default'] != "":
                comment += f" [Default: {configs[section][param]['default']}]"

            default = str(configs[section][param]['default']).strip().replace('\n', '')
            value = str(configs[section][param]['value']).strip().replace('\n', '')

            if value == "" and default == "":
                line = f"#{param}=<{section.upper()}_{param.upper()}>"
            elif value == "" and param in ['LOCATION', 'COUNTRY', 'STATE', 'CITY']:
                line = f"#{param}=<{section.upper()}_{param.upper()}>"
            elif value == "" and default != "":
                line = f"{param}={default}"
            else:
                line = f"{param}={value}"
            content += f"\n# {comment}\n{line}"

        content += '\n\n'

    print(content)


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


def write_configs(file_path:str, configs:dict, exception:bool=False)->bool:
    status = True
    config_file = os.path.expanduser(os.path.expandvars(file_path))

    if os.path.isfile(config_file):
        file_extension = config_file.rsplit('.', 1)[-1]

        if file_extension == 'env':
            content = __create_env_configs(configs=configs)
        elif file_extension in ['yml', 'yaml']:
            pass
        elif file_extension == 'json':
            pass
        else:
            status = False
            print(f'Invalid extension type: {file_extension}')
    else:
        status = False
        print(f'Failed to locate config file {config_file}')

    return status