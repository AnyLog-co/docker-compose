import os
from write_docker import __create_file, __write_line
ROOT_PATH = os.path.expandvars(os.path.expanduser(__file__)).split('deployment_scripts')[0]



def configure_dir(node_type:str)->(str, str):
    """
    Configure directory & create backup of configs if exists)
    :process:
        1. create directory path
        2. if directory DNE create it
           if directory exists copy anylog_configs (if exists) to bkup
        3. create anylog_configs
    :args:
        node_type:str - AnyLog node type
    :params:
        status:bool
        dir_path:str - docker directory path where configs are stored
        anylog_configs:str - configurations file (full path)
    :return:
        status, anylog_configs
    """
    status = True
    dir_path = os.path.join(ROOT_PATH, 'helm', 'sample-configurations')
    anylog_configs = os.path.join(dir_path, 'anylog_%s.yml' % node_type)

    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    elif os.path.isfile(anylog_configs):
        try:
            os.rename(anylog_configs, anylog_configs.replace('.env', '.env.old'))
        except Exception as error:
            status = False
            print(f'Failed to copy {anylog_configs} into a backup file (Error: {error})')
        else:
            status = __create_file(file_name=anylog_configs)

    return status, anylog_configs


def write_configs(build:str, configs:dict, anylog_configs:str):
    content = ""
    for config in configs:
        if config == list(configs)[0]:
            content += f"{config}:"
        else:
            content += f"\n{config}:"
        if config == 'general':
            content += '\n\t# AnyLog build version'
            content += f'\n\tbuild: {build}'
        for param in configs[config]:
            content += f"\n\t# {configs[config][param]['description']}"
            if configs[config][param]['value'] == '':
                if configs[config][param]["default"] == '':
                    content += f'\n\t{param}: ""'
                else:
                    content += f'\n\t{param}: {configs[config][param]["default"]}'
            else:
                content += f'\n\t{param}: {configs[config][param]["value"]}'
        content += "\n"
    __write_line(file_name=anylog_configs,  input_line=content)
