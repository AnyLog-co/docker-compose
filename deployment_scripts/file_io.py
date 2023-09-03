import os
import file_support
import support

ROOT_PATH = os.path.expandvars(os.path.expanduser(__file__)).split('deployment_scripts')[0]


def __create_file_name_docker(node_type:str)->str:
    """
    Create file path  based on node_type for Docker nodes
    :args:
        node_type;str - node type
            - rest
            - master
            - operator
            - publisher
            - query
    :params:
        file_name:str - file to store data in
    :return:
        file_name
    """
    file_name = os.path.join(ROOT_PATH, 'docker-compose', 'anylog-%s' % node_type.lower(), 'anylog_configs.env')

    return file_name


def __create_file_name_kubernetes(node_type:str)->str:
    """
    Create file path  based on node_type for Kubernetes nodes
    :note:
        query is stored in anylog-query-remote-cli
    :args:
        node_type;str - node type
            - rest
            - master
            - operator
            - publisher
            - query
    :params:
        file_name:str - file to store data in
    :return:
        file_name
    """
    file_name = os.path.join(ROOT_PATH, 'helm', 'sample-configurations', 'anylog_%s.yaml' % node_type.lower())

    return file_name


def read_configs(config_file:str, exception:bool=False)->dict:
    """
    Given a configuration file, extract configuration values
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
            configs = file_support.read_dotenv(config_file=config_file, exception=exception)
        elif file_extension in ['yml', 'yaml']:
            configs = file_support.read_yaml(config_file=config_file, exception=exception)
            configs = support.prep_imported_kubernetes(configs=configs)
        elif file_extension == 'json':
            configs = file_support.read_json(config_file=config_file, exception=exception)
        else:
            print(f'Invalid extension type: {file_extension}')
    else:
        print(f'Failed to locate config file {config_file}')

    return configs


def update_dotenv_tag(file_path:str, build:str, node_name:str, exception:bool=False)->bool:
    """
    For Docker deployment, update .env file
    :args:
        file_path:str - `anylog_configs.env` file path
        build:str - docker version
        node_name:str - node name
        exception:bool - whether to print exceptions
    :params:
        status:bool
        line:str - content to store in file
        content:dict - preset default content
        file_path:str - directory path
        dotenv_file - full path of dotenv file
    :return:
        status
    """
    line = ""
    content = {
        'BUILD': build,
        'ENV_FILE': 'anylog_configs.env',
        'CONTAINER_NAME': node_name,
        'NETWORK': 'host'
    }

    dotenv_file = os.path.join(file_path, '.env')
    if os.path.isfile(dotenv_file):
        file_content = file_support.read_dotenv(config_file=dotenv_file, exception=exception)
        for key in content:
            if key not in file_content:
                line += f"{key}={content[key]}\n"
            elif key in ['BUILD', 'CONTAINER_NAME'] and file_content[key] != content[key]:
                line += f"{key}={content[key]}\n"
            else:
                line += f"{key}={file_content[key]}\n"
    else:
        for key in content:
            line += f"{key}={content[key]}\n"

    dotenv_file = file_support.create_file(file_path=dotenv_file, exception=exception)

    status = file_support.append_content(content=line, file_path=dotenv_file, exception=exception)
    if status is False and exception is True:
        print(f"Failed to insert '{line}' into {dotenv_file}")

    return status


def write_docker_configs(file_path:str, configs:dict, exception:bool=False)->bool:
    """
    Write content into Docker configuration file (anylog_configs.env)
    :args:
        file_path:str - full path for anylog_configs.env
        configs:dict - configuration to store in file
        exception:bool - whether to print exception messages
    :params:
        content:str - generated content to store in file based on configs
    :return:
        True if stored in file
        False if fails
    """
    content = ""
    # generate content
    for section in configs:
        content += f'# --- {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")} ---\n'
        if section == 'networking':
            content += file_support.read_notes() + "\n"
        for param in configs[section]:
            comment = configs[section][param]['description'].replace('\n', '')
            if param in ['LOCATION', 'COUNTRY', 'STATE', 'CITY']:
                value = str(configs[section][param]['value']).replace('\n', '')
                if value == '':
                    line = f'{param}=<{section.upper()}_{param.upper()}>'
                else:
                    line = f"{param}={value}"
            elif configs[section][param]['value'] != '':
                value = str(configs[section][param]['value']).replace('\n', '')
                line = f"{param}={value}"
            elif configs[section][param]['default'] != '':
                value = str(configs[section][param]['default']).replace('\n', '')
                line = f"{param}={value}"
            else:
                line = f"{param}=<{section.upper()}_{param.upper()}>"
            if param == "DB_TYPE":
                pass
            if line == f"{param}=<{section.upper()}_{param.upper()}>":
                line = f"#{line}"
            line = f"# {comment}\n{line}\n"
            content += line

        content += "\n"

    # store content to file
    return file_support.append_content(content=content, file_path=file_path, exception=exception)


def write_kubernetes_configs(file_path:str, metadata_configs:dict, configs:dict, exception:bool=False)->bool:
    """
    Write content into Kubernetes
    :args:
        file_path:str - full path for anylog_${NODE_TYPE}.yaml
        metadata_configs:dict - configuration regarding metadata of kubernetes instance
        configs:dict - configuration to store in file
        exception:bool - whether to print exception messages
    :params:
        content:str - generated content to store in file based on configs
    :return:
        True if stored in file
        False if fails
    """
    content = ""

    # metadata set configurations
    for section in metadata_configs:
        content += f"{section}:\n"
        for param in metadata_configs[section]:
            if param not in ['anylog_volume', 'blockchain_volume', 'data_volume']:
                comment = f"  # {metadata_configs[section][param]['description']}\n"
                line = f"  {param}: %s\n"
                if metadata_configs[section][param]['value'] != "":
                    line = line % metadata_configs[section][param]['value']
                elif metadata_configs[section][param]['default'] != '':
                    line = line % metadata_configs[section][param]['default']
                else:
                    line = line % '""'
                content += comment + line

    # for section in ['anylog_volume', 'blockchain_volume', 'data_volume']:
    #     content += f"  {section.replace(' ', '_')}: "
    #     for param in metadata_configs['volume'][section]:
    #         if param != 'default':
    #             comment = f"    # {metadata_configs['volume'][section][param]['description']}\n"
    #             line = f"    {param}: %s\n"
    #             if metadata_configs['volume'][section][param]['value'] != "":
    #                 line = line % metadata_configs['volume'][section][param]['value']
    #             elif metadata_configs['volume'][section][param]['default'] != "":
    #                 line = line % metadata_configs['volume'][section][param]['default']
    #             else:
    #                 line = line % '""'
    #             content += comment + line
    content += '\n'

    for section in configs:
        content += f"{section.replace(' ', '_')}: \n"
        if section == 'networking':
            content += file_support.read_notes()
        for param in configs[section]:
            if section == 'general' and param in ['LOCATION', 'COUNTRY', 'STATE', 'CITY']:
                if configs[section][param]['value'] == "":
                    configs[section][param]['default'] = ''
            if section == 'operator' and param == 'TABLE_NAME':
                if not configs[section][param]['value'] or configs[section][param]['value'] == '*':
                    configs[section][param]['value'] = '"*"'
                
            comment = f"  # {configs[section][param]['description']}\n"
            line = f"  {param}: %s\n"
            if configs[section][param]['value'] != "":
                line = line % configs[section][param]['value']
            elif configs[section][param]['default'] != '':
                line = line % configs[section][param]['default']
            else:
                line = line % '""'
            content += comment + line

    return file_support.append_content(content=content, file_path=file_path, exception=exception)


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
        file_path = __create_file_name_docker(node_type=node_type)
        if node_type == 'rest':
            file_path = __create_file_name_docker(node_type='generic')
        file_path = file_support.create_file(file_path=file_path, exception=exception)
        if file_path != "":
            status = write_docker_configs(file_path=file_path, configs=configs, exception=exception)
            if status is True:
                status = update_dotenv_tag(file_path=file_path.split('anylog_configs.env')[0], build=build,
                                           node_name=node_name, exception=exception)
    elif deployment_type == 'kubernetes':
        file_path = __create_file_name_kubernetes(node_type=node_type)
        if node_type == 'rest':
            file_path = __create_file_name_kubernetes(node_type='generic')
        file_path = file_support.create_file(file_path=file_path, exception=exception)
        write_kubernetes_configs(file_path=file_path, metadata_configs=kubernetes_configs, configs=configs,
                                 exception=exception)

    return status

