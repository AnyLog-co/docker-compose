import dotenv
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


def write_docker_configs(node_type:str, configs:dict):
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
    status = False
    if node_type != 'query':
        docker_path = os.path.join(ROOT_PATH, 'docker-compose', 'anylog-%s' % node_type.lower())
    else:
        docker_path = os.path.join(ROOT_PATH, 'docker-compose', '%s-remote-cli' % node_type.lower())
    anylog_configs = os.path.join(docker_path, 'anylog_configs.env')

    # move exiting configs to backup + create new config file
    if os.path.isdir(docker_path):
        try:
            os.rename(anylog_configs, anylog_configs.replace('.env', '.env.old'))
        except Exception as error:
            status = False
            print(f'Failed to move to move original configuration file into backup (Error: {error})')

    if not os.path.isfile(anylog_configs):
        status = __create_file(file_name=anylog_configs)

    # write configs to file
    if status is True:
        for section in configs:
            __write_line(file_name=anylog_configs, input_line=f'# {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
            for param in configs[section]:
                if param == 'OPERATOR_THREADS':
                    print('test')
                value = ""
                line = f"{param}=%s"
                if param in ['LOCATION', 'COUNTRY', 'STATE', 'CITY']:
                    value = str(configs[section][param]['value'])
                    if value == '':
                        line = f'#{param}={configs[section][param]["default"]}'
                    elif ' ' in value:
                        line = line % f'"{value}"'
                    else:
                        line = line % value
                elif configs[section][param]['value'] != '': # non-empty value
                    value = str(configs[section][param]['value'])
                    if ' ' in value:
                        line = line % f'"{value}"'
                    else:
                        line = line % value
                elif configs[section][param]['default'] != "": # empty value
                    value = str(configs[section][param]['default'])
                    if ' ' in value:
                        line = line % f'"{value}"'
                    else:
                        line = line % value
                else:
                    line = line % f"<{section.upper()}_{param}>"
                if line == f"{param}=<{section.upper()}_{param}>" or configs[section][param]['enable'] is False and param not in ["NODE_TYPE", 'CREATE_TABLE']:
                    line = f"#{line}"
                line=f"# {configs[section][param]['description']}\n{line}"
                __write_line(file_name=anylog_configs, input_line=f"{line}\n")
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



