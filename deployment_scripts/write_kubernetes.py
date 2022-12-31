import os
from write_docker import __create_file, __write_line
ROOT_PATH = os.path.expandvars(os.path.expanduser(__file__)).split('deployment_scripts')[0]


def configure_dir(node_type:str)->(str, str):
    """
    Configure directory & create backup of configs if exists)
    :process:
        1. create directory path if DNE
        Iterate through configs and volume file
            1. check if file exists
            2. if exists then make a bakup
            3. create file
    :args:
        node_type:str - AnyLog node type
    :params:
        status:bool
        dir_path:str - docker directory path where configs are stored
        anylog_configs_file:str - configurations file (full path)
    :return:
        status, anylog_configs_file
    """
    dir_path = os.path.join(ROOT_PATH, 'helm', 'sample-configurations')
    anylog_configs_file = os.path.join(dir_path, 'anylog_%s.yaml' % node_type)

    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

    for file_name in [anylog_configs_file]:
        status = True
        if os.path.isfile(file_name):
            try:
                os.rename(file_name, file_name.replace('.yaml', '.yaml.old'))
            except Exception as error:
                print(f'Failed to copy {file_name} into a backup file (Error: {error})')
                status = False

        if status is True:
            __create_file(file_name=file_name)

    return anylog_configs_file


def metadata_configs(configs:dict, anylog_configs_file:str)->str:
    """
    write Kubernetes (metadata) configurations
    :args:
        configs:dict - user defined configurations
        anylog_configs_file:str - file path to store AnyLog configs
    :param:
        content:str - formatted metadata configs
    :return:
        content
    """
    content = ""
    for config in configs:
        content += f"{config}: "
        if config != 'volume':
            for param in configs[config]:
                content += f"\n  # {configs[config][param]['description']}"
                if configs[config][param]['value'] == "":
                    content += f"\n  {param.lower()}: {configs[config][param]['default']}"
                else:
                    content += f"\n  {param.lower()}: {configs[config][param]['value']}"
        else:
            for sub_config in configs[config]:
                if sub_config == 'enable_volume':
                    content += f"\n  # {configs[config][sub_config]['description']}"
                    if configs[config][sub_config]['value'] == "":
                        content += f"\n  {sub_config}: {configs[config][sub_config]['default']}"
                    else:
                        content += f"\n  {sub_config}: {configs[config][sub_config]['value']}"
                else:
                    content += f"\n  {sub_config}:"
                    for param in configs[config][sub_config]:
                        content += f"\n    # {configs[config][sub_config][param]['description']}"
                        if configs[config][sub_config][param]['value'] == "":
                            content += f"\n    {param.lower()}: {configs[config][sub_config][param]['default']}"
                        else:
                            content += f"\n    {param.lower()}: {configs[config][sub_config][param]['value']}"
        content += "\n\n"

    __write_line(file_name=anylog_configs_file, input_line=content)


def write_configs(configs:dict, anylog_configs_file:str):
    """
    Write configurations for kubernetes (YAML) files
    :args:
        configs:dict - user defined configurations
        anylog_configs_file:str - file path to store AnyLog configs
    :params:
        content:str - content to store in config file
    """
    content = ""
    node_name = 'anylog'

    for config in configs:
        section = config
        content += f"\n{config.replace(' ', '_')}:"
        for param in configs[config]:
            content += f"\n  # {configs[config][param]['description']}"
            if configs[section][param]['default'] != "":
                content += f" [Default: {configs[section][param]['default']}]" 
 
            if configs[config][param]['value'] == '':
                if configs[config][param]["default"] == '':
                    content += f'\n  {param}: ""'
                elif param == 'LOCATION' or param in ['COUNTRY', 'STATE', 'CITY']:
                    content += f'\n  {param}: ""'
                else:
                    content += f'\n  {param}: {configs[config][param]["default"]}'
                    if param == 'NODE_NAME':
                        node_name = configs[config][param]['default']
            else:
                content += f'\n  {param}: {configs[config][param]["value"]}'
                if param == 'NODE_NAME':
                    node_name = configs[config][param]['default']
        content += "\n"

    __write_line(file_name=anylog_configs_file,  input_line=content)


