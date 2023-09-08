import os

from __file_support__ import read_notes,  create_file

ROOT_PATH = os.path.expandvars(os.path.expanduser(os.path.abspath(__file__))).split("deployment_scripts")[0]


def __docker_create_path(node_type:str, file_name:str, exception:bool=False):
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
    if os.path.isfile(file_path):
        try:
            os.rename(file_path, f"{file_path}.old")
        except Exception as error:
            file_path = ""
            if exception is True:
                print(f"Failed to rename {file_path} (Error: {error})")
        else:
            try:
                open(file_path, 'w').close()
            except Exception as error:
                file_path = ""
                if exception is True:
                print(f"Failed to recreate file {file_path} (Error: {error})")

    return file_path

def write_file(config_file:str, content:str):
    """
    write content to file
    :args:
        config_file:str - file to write into
        contnet:str - contnet to write into file
    """
    try:
        with open(config_file, 'a') as f:
            try:
                f.write(content)
            except Exception as error:
                print(f"Failed to write content in {config_file} (Error: {error}")
    except Exception as error:
        print(f"Failed to open {config_file} (Error: {error}")



def __docker_create_configs_section(anylog_configs:str, advance_configs:str, configs:dict):
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
            write_file(config_file=anylog_configs, content=anylog_configs_content)
        if advanced_configs_content != "":
            advanced_configs_content += "\n"
            write_file(config_file=advance_configs, content=advanced_configs_content)


def write_configs(deployment_type:str, configs:dict, build:str=None, exception:bool=False):
    if deployment_type == 'docker':
        advance_configs = __docker_create_path(node_type=configs['general']['NODE_TYPE']['value'], file_name='advance_configs')
        anylog_configs = __docker_create_path(node_type=configs['general']['NODE_TYPE']['value'], file_name='anylog_configs')
        __docker_create_configs_section(anylog_configs=anylog_configs, advance_configs=advance_configs, configs=configs)





