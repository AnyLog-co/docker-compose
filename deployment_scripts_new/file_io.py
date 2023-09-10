import json
import dotenv
import os
import yaml


ROOT_PATH = os.path.expandvars(os.path.expanduser(os.path.abspath(__file__))).split("deployment_scripts")[0]


def __create_file(file_path:str, exception:bool=False):
    if os.path.isfile(file_path):
        try:
            os.rename(file_path, f"{file_path}.old")
        except Exception as error:
            file_path = ""
            if exception is True:
                print(f"Failed to rename {file_path} (Error: {error})")

    if file_path != "":
        try:
            open(file_path, 'w').close()
        except Exception as error:
            file_path = ""
            if exception is True:
                print(f"Failed to recreate file {file_path} (Error: {error})")

    return file_path

def __write_file(config_file:str, content:str, exception:bool=False):
    """
    write content to file
    :args:
        config_file:str - file to write into
        content:str - content to write into file
    """
    status = False
    try:
        with open(config_file, 'a') as f:
            try:
                f.write(content)
            except Exception as error:
                if exception is True:
                    print(f"Failed to write content in {config_file} (Error: {error}")
    except Exception as error:
        if exception is True:
            print(f"Failed to open {config_file} (Error: {error}")
    else:
        status = True
    return status

def read_notes(exception:bool=False)->str:
    """
    Read comments in network_comment.txt
    :args:
        exception:bool - whether to print exceptions
    :params:
        file_path:str - file path form network_comment.txt
        content:str - content from file
    :return:
        content
    """
    file_path = os.path.join(ROOT_PATH, 'deployment_scripts', 'config_files/network_comment.txt')
    content = ""
    if os.path.isfile(file_path):
        try:
            with open(file_path, 'r') as f:
                try:
                    content +=  f.read() + "\n"
                except Exception as error:
                    if exception is True:
                        print(f'Failed to read comments in {file_path} (Error: {error})')
        except Exception as error:
            if exception is True:
                print(f'Failed to open comments file {file_path} (Error: {error})')
    elif exception is True:
        print(f'Failed to locate comments file {file_path}')

    return content

def read_configs_file(config_file:str, exception:bool=False)->dict:
    """
    Read content from configuration file
    :args:
        config_file:str - configuration file
        exception:bool - whether to print exceptions
    :params:
        full_path:str - expanded config_file path
        file_content:dict - content in configuration file
    """
    full_path = os.path.expanduser(os.path.expandvars(config_file))
    file_content = {}
    if os.path.isfile(full_path):
        try:
            with open(full_path, 'r') as f:
                try:
                    file_content = json.loads(f.read())
                except Exception as error:
                    if exception is True:
                        print(f"Failed to read content from {config_file} (Error: {error})")
        except Exception as error:
            if exception is True:
                print(f"Failed to open {config_file} (Error: {error})")
    elif exception is True:
        print(f"Failed to locate {config_file}")

    return file_content

def docker_create_path(node_type:str, file_name:str, exception:bool=False):
    """
    Based on node_type and file_name create new file
    :process:
        1. if file exists create a backup
        2. create new file
    :global:
        ROOT_PATH - root path
    :args:
        node_type:str - AnyLog node type
        file_name:str - from configs config_file value
        exception:bool - whether to print exceptions
    :params:
        file_path:str - file path
    :return:
        file_path
    """
    if node_type == 'rest':
        node_type = 'generic'
    file_path = os.path.join(ROOT_PATH, "docker-compose", f"anylog-{node_type}", f"{file_name}.env")

    return __create_file(file_path=file_path, exception=exception)

def dotenv_create_path(node_type:str, exception:bool=False):
    """
    Based on node_type and file_name create new file
    :process:
        1. if file exists create a backup
        2. create new file
    :global:
        ROOT_PATH - root path
    :args:
        node_type:str - AnyLog node type
        file_name:str - from configs config_file value
        exception:bool - whether to print exceptions
    :params:
        file_path:str - file path
    :return:
        file_path
    """
    if node_type == 'rest':
        node_type = 'generic'
    file_path = os.path.join(ROOT_PATH, "docker-compose", f"anylog-{node_type}", f".env")

    return __create_file(file_path=file_path, exception=exception)

def kubernetes_create_path(node_type:str, exception:bool=False):
    """
    Based on node_type create new kubernetes config file
    :process:
        1. if file exists create a backup
        2. create new file
    :global:
        ROOT_PATH - root path
    :args:
        node_type:str - AnyLog node type
        file_name:str - from configs config_file value
        exception:bool - whether to print exceptions
    :params:
        file_path:str - file path
    :return:
        file_path
    """
    if node_type == 'rest':
        node_type = 'generic'
    file_path = os.path.join(ROOT_PATH, 'helm', 'sample-configurations', f'anylog_{node_type}.yaml')

    return __create_file(file_path=file_path, exception=exception)

def docker_write_configs_files(anylog_configs:str, advance_configs:str, configs:dict, exception:bool=False):
    """
    Create configuration file(s) for anylog  based on the  config_file
    :args:
        anylog_configs:str - anylog_configs file path
        advance_configs:str - advance_configs file path
        configs:dict - configurations
    :params:
        wrote_anylog_configs:bool - whether to write config anylog_configs
        wrote_advanced_configs:bool - whether to write to advanced_configs
        advanced_configs_content:str  - content in  advanced_configs
        anylog_configs_content:str  - content in  anylog_configs
    """
    for section in configs:
        wrote_anylog_configs = False
        wrote_advanced_configs = False
        advanced_configs_content = ""
        anylog_configs_content =""
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

            if configs[section][param]['config_file'] == "anylog_configs":
                if wrote_anylog_configs is False:
                    anylog_configs_content = f'# --- {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")} ---\n'
                    wrote_anylog_configs = True
                anylog_configs_content += line
            elif configs[section][param]['config_file'] == "advance_configs":
                if wrote_advanced_configs is False:
                    advanced_configs_content = f'# --- {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")} ---\n'
                    if section == 'networking':
                        advanced_configs_content += read_notes() + "\n"
                    wrote_advanced_configs = True
                advanced_configs_content += line

        if anylog_configs_content != "":
            anylog_configs_content += "\n"
            __write_file(config_file=anylog_configs, content=anylog_configs_content, exception=exception)
        if advanced_configs_content != "":
            advanced_configs_content += "\n"
            __write_file(config_file=advance_configs, content=advanced_configs_content, exception=exception)

def dotenv_update_configs_files(node_type:str, node_name:str, build:str, exception:bool=False):
    """
    Create configuration file(s) for anylog  based on the  config_file
    :args:
        anylog_configs:str - anylog_configs file path
        advance_configs:str - advance_configs file path
        configs:dict - configurations
    :params:
        DEFAULT_DOTENV_CONFIGS:dict - .env configurations
        wrote_anylog_configs:bool - whether to write config anylog_configs
        wrote_advanced_configs:bool - whether to write to advanced_configs
        advanced_configs_content:str  - content in  advanced_configs
        anylog_configs_content:str  - content in  anylog_configs
    """
    DEFAULT_DOTENV_CONFIGS = {
        "BUILD": build,
        "CONTAINER_NAME":  node_name,
        "NETWORK": "host"
    }

    if node_type == 'rest':
        node_type = 'generic'
    file_path = os.path.join(ROOT_PATH, "docker-compose", f"anylog-{node_type}", ".env")
    file_path = __create_file(file_path=file_path, exception=exception)

    if file_path != "":
        content = ""
        for key in DEFAULT_DOTENV_CONFIGS:
            content += f"{key}={DEFAULT_DOTENV_CONFIGS[key]}\n"
        __write_file(config_file=file_path, content=content, exception=exception)

def kubernetes_write_configs_files(configs:dict, config_file:str, exception:bool=False):
    try:
        yaml_configs = yaml.dump(configs    , default_style='"')
    except Exception as error:
        status = False
        if exception is True:
            print(f"Failed to convert configs to YAML format")
    else:
        status = __write_file(config_file=config_file, content=yaml_configs, exception=exception)
        if status is True:
            status = __write_file(config_file=config_file, content="\n", exception=exception)
    return status