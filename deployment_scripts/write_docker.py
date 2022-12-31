# import dotenv
import os

ROOT_PATH = os.path.expandvars(os.path.expanduser(__file__)).split('deployment_scripts')[0]


def __create_file(file_name:str)->bool:
    """
    Create new configuration file
    :args:
        file_name:str - configuration file name
    :params:
        status:bool
    :return:
        status
    """
    status = True
    try:
        open(file_name, 'w').close()
    except Exception as error:
        status = False
        print(f'Failed to create {file_name} (Error: {error})')

    return status


def __write_line(file_name:str, input_line:str)->bool:
    """
    Write line to file
    :args:
        file_name:str - configuration file name
        input_line:str - content to store into file
    :print:
        if fails to write then error is printed to screen
    """
    try:
        with open(file_name, 'a') as f:
            try:
                f.write(input_line)
            except Exception as error:
                print(f'Failed to append content into {file_name} (Error: {error}')
    except Exception as error:
        print(f'Failed to open file {file_name} to append content (Error: {error})')


def __read_env_file(env_file:str)->dict:
    """
    Read configurations from .env file
    :args:
        env_file:str - .env file
    :params:
        configs:dict - read configs
    :return:
        configs
    """
    configs = {}
    try:
        with open(env_file, 'r') as f:
            try:
                for line in f.readlines():
                    if line != "" and line != "\n":
                        key, value = line.split('\n')[0].split('=')
                        configs[key] = value
            except Exception as error:
                print(f'Failed to read content from {env_file} (Error: {error})')
    except Exception as error:
        print(f'Failed to open file {env_file} to read content (Error: {error})')

    return configs


def configure_dir(node_type:str)->(bool, str):
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
    dir_path = os.path.join(ROOT_PATH, 'docker-compose', 'anylog-%s' % node_type.lower())
    if node_type == 'query':
        dir_path = os.path.join(ROOT_PATH, 'docker-compose', '%s-remote-cli' % node_type.lower())
    anylog_configs = os.path.join(dir_path, 'anylog_configs.env')

    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    if os.path.isfile(anylog_configs):
        try:
            os.rename(anylog_configs, anylog_configs.replace('.env', '.env.old'))
        except Exception as error:
            status = False
            print(f'Failed to copy {anylog_configs} into a backup file (Error: {error})')
        else:
            status = __create_file(file_name=anylog_configs)

    return status, anylog_configs


def write_configs(configs:dict, anylog_configs:str):
    """
    "main" process for writing content into docker file
    :args:
        node_type:str - node type
        configs:dict - configurations to store in file
    :params:
        status:bool
        docker_path:str - full path for docker-compose package
        line:str - content to store in file
    """
    for section in configs:
        __write_line(file_name=anylog_configs, input_line=f'# --- {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")} ---')
        for param in configs[section]:
            comment = configs[section][param]['description'].replace('\n', '')
            if configs[section][param]['default'] != "": 
                comment += f" [Default: {configs[section][param]['default']}]" 
            if param in ['LOCATION', 'COUNTRY', 'STATE', 'CITY', 'MQTT_USER', 'MQTT_PASSWD']:
                value = str(configs[section][param]['value']).replace('\n', '')
                if value == '' or value == 'None':
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

            if line == f"{param}=<{section.upper()}_{param.upper()}>":
                line = f"#{line}"
            line = f"# {comment}\n{line}"
            __write_line(file_name=anylog_configs, input_line=f"\n{line}")
        __write_line(file_name=anylog_configs, input_line="\n\n")


def update_build_version(node_type:str, container_name:str, build:str):
    """
    Update .env file
    :args:
        node_type:str - Node type
        container_name:str - NODE_NAME
        build:str - AnyLog build version
    :params:
        env_file:str - file to store content in
    """
    # set file name
    if node_type != 'query':
        env_file = os.path.join(ROOT_PATH, 'docker-compose', 'anylog-%s' % node_type.lower())
    else:
        env_file = os.path.join(ROOT_PATH, 'docker-compose', '%s-remote-cli' % node_type.lower())
    env_file = os.path.join(env_file, '.env')

    # read + write content into .env file
    if os.path.isfile(env_file):
        configs = __read_env_file(env_file=env_file)
        if len(configs) > 0:
            configs['BUILD'] = build
            configs['CONTAINER_NAME'] = container_name
            __create_file(file_name=env_file)
            for key in configs:
                __write_line(file_name=env_file, input_line=f"{key}={configs[key]}\n")



