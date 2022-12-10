import os
from write_docker import __create_file, __write_line
ROOT_PATH = os.path.expandvars(os.path.expanduser(__file__)).split('deployment_scripts')[0]

def __metadata_configs(build:str, node_name:str)->str:
    """
    Base Kubernetes (metadata) configurations
    :args:
        build:str - AnyLog version
        node_name:str - node name
    :param:
        content:str - formatted metadata configs
    :return:
        content
    """
    content="metadata: "
    content += "\n\tnamespace: default"
    content += f"\n\thostname: {node_name}"
    content += f"\n\tapp_name: {node_name}-app"
    content += f"\n\tpod_name: {node_name}-pod"
    content += f"\n\tdeployment_name: {node_name}-deployment"
    content += f"\n\tservice_name: {node_name}-svs"
    content += f"\n\tconfigmap_name: {node_name}-configs"
    content += "\n\t#nodeSelector - Allows running Kubernetes remotely. If commented out, code will ignore it"
    content += '\n\t#nodeSelector: ""'
    content += "\n\treplicas: 1"
    content += "\n"
    content += "\nimage: "
    content += "\n\tsecretName: imagepullsecret"
    content += "\n\trepository: anylogco/anylog-network"
    content += f"\n\ttag: {build}"
    content += "\n\tpullPolicy: IfNotPresent"
    content += "\n"

    return content



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
            os.rename(anylog_configs, anylog_configs.replace('.yml', '.yml.old'))
        except Exception as error:
            status = False
            print(f'Failed to copy {anylog_configs} into a backup file (Error: {error})')
        else:
            status = __create_file(file_name=anylog_configs)

    return status, anylog_configs


def write_configs(build:str, configs:dict, anylog_configs:str):
    content = ""
    node_name = 'anylog'

    for config in configs:
        content += f"\n{config}:"
        for param in configs[config]:
            content += f"\n\t# {configs[config][param]['description']}"
            if configs[config][param]['value'] == '':
                if configs[config][param]["default"] == '':
                    content += f'\n\t{param}: ""'
                else:
                    content += f'\n\t{param}: {configs[config][param]["default"]}'
                    if param == 'NODE_NAME':
                        node_name = configs[config][param]['default']
            else:
                content += f'\n\t{param}: {configs[config][param]["value"]}'
                if param == 'NODE_NAME':
                    node_name = configs[config][param]['default']
        content += "\n"

    content = __metadata_configs(build=build, node_name=node_name) + content
    __write_line(file_name=anylog_configs,  input_line=content)
