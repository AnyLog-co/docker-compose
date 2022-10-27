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
    docker_path = os.path.join(ROOT_PATH, 'docker-compose', 'anylog-%s' % node_type.lower())

    # move exiting configs to backup + create new config file
    if os.path.isdir(docker_path):
        anylog_configs = os.path.join(docker_path, 'anylog_configs.env')
        try:
            os.rename(anylog_configs, anylog_configs.replace('.env', '.env.old'))
        except Exception as error:
            status = False
            print(f'Failed to move to move original configuration file into backup (Error: {error})')
        else:
            if os.path.isfile(anylog_configs):
                status = __create_file(file_name=anylog_configs)

    if status is True:
        for section in configs:
            __write_line(file_name=anylog_configs, input_line=f'# {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
            for param in section:
                if configs[section][param]['enable'] is False or configs[section][param]['value'] == "":
                    if len(configs[section][param]['default'].split(' ')) > 1:
                        line = f'#{param}=\"{configs[section][param]["default"]}\"'
                    else:
                        line = f'#{param}={configs[section][param]["default"]}'
                else:
                    if len(configs[section][param]['value'].split(' ')) > 1:
                        line = f'{param}=\"{configs[section][param]["value"]}\"'
                    else:
                        line = f'{param}={configs[section][param]["value"]}'
                __write_line(file_name=anylog_configs, input_line=line)
            __write_line(file_name=anylog_configs, input_line="\n")



if __name__ == '__main__':
    write_docker_configs('rest', configs={})