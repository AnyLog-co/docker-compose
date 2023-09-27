import argparse
import dotenv
import json
import os
import yaml

ROOT_DIR = os.path.dirname(os.path.abspath(os.path.expandvars(os.path.expanduser(__file__)))).split("deployment_scripts")[0]

def __read_json_file(file_path:str, exception:bool=False)->dict:
    """
    Given a configuration (JSON) file, read its content
    :args:
        file_path:str - file path
        exception:bool - whether to print exception
    :return:
        content as dictionary
    """
    try:
        with open(file_path, 'r') as f:
            try:
                return json.load(f)
            except Exception as error:
                if exception is True:
                    print(f"Failed to load the environment variables from {file_path}")
    except Exception as error:
        if exception is True:
            print(f"Failed to open {file_path} for content to be read (Error: {error})")
        exit(1)


def __read_file(file_path:str, exception:bool=False)->dict:
    """
    Given configuration file (dotenv) file, read its content
    :args:
        file_path:str - file path
        exception:bool - whether to print exception
    :return:
        content as dictionary
    """
    file_content = {}
    try:
        with open(file_path, 'r') as f:
            try:
                for line in f.readlines():
                    if '#' not in line and '=' in line:
                        key, value = line.split('=')
                        key = key.replace("\n","").strip()
                        value = value.replace("\n","").strip()
                        if value not in  ['""', "''"]:
                            try:
                                file_content[key] = int(value.split('\n')[0])
                            except:
                                file_content[key] = value.split('\n')[0]
                        else:
                            file_content[key] = ""
            except Exception as error:
                if exception is True:
                        print(f"Failed to read content in {file_path} (Error: {error})")
    except Exception as error:
        if exception is True:
            print(f"Failed to open file {file_path} (Error: {error})")

    return file_content


def __read_yaml_file(file_path:str, exception:bool=False)->dict:
    """
    Given configuration file (YAML) file, read its content
    :args:
        file_path:str - file path
        exception:bool - whether to print exception
    :return:
        content as dictionary
    """
    try:
        with open(file_path, 'r') as f:
            try:
                return yaml.safe_load(f)
            except Exception as error:
                if exception is True:
                    print(f"Failed to load the environment variables from {file_path} (Error: {error})")
    except Exception as error:
        if exception is True:
            print(f"Failed to open file {file_path} to be read (Error: {error})")
        exit(1)


def write_file(file_path:str, content:str, exception:bool=False):
    try:
        with open(file_path, 'w') as f:
            try:
                f.write(content)
            except Exception as error:
                status = False
                if exception is True:
                    print(f"Failed to write content into {file_path} (Error: {error})")
    except Exception as error:
        if exception is True:
            print(f"Failed to open file {file_path} to write content (Error: {error})")


def copy_file(file_path:str, exception:bool=False)->str:
    file_path = is_file(file_path=file_path, is_argparse=False, exception=exception)
    if file_path is not None:
        try:
            os.rename(file_path, f"{file_path}.old")
        except Exception as error:
            if exception is True:
                print(f"Failed to copy file (Error: {error})")


def is_file(file_path:str, is_argparse:bool=True, exception:bool=False)->str:
    """
    Check if file exists or not
    :args:
        file_path:str - file path
        is_argparse:bool - whether its being checked via argument parsing or not
        exception:bool - whether to print exception
    :params:
        full_path:str - expanded file path
    :return:
        full_path or None if file DNE
        for is_argparse raises exception if fails to locate file
    """
    full_path = os.path.expanduser(os.path.expandvars(file_path))
    if not os.path.isfile(full_path):
        full_path = None
        if is_argparse is True:
            raise argparse.ArgumentError(f"Failed to locate file {file_path}")
        elif exception is True:
                print(f"Failed to locate file {file_path}")

    return full_path


def read_config_file(file_path:str, exception:bool=False)->dict:
    """
    Read configuration file
    :args:
        file_path:str - file path
        exception:bool - whether to print exception
    :params:
        file_ext:str - file extension
    :return:
        content in file (based on file extension)
    """
    file_path = is_file(file_path=file_path, is_argparse=False, exception=exception)
    file_ext = file_path.rsplit(".", 1)[-1]
    if file_path is None:
        print(f"Unable to continue due to missing configuration file {file_path}...")
        exit(1)
    if file_ext in ['jsn', 'json']:
        return __read_json_file(file_path=file_path, exception=exception)
    elif file_ext in ['env']:
        return  __read_file(file_path=file_path, exception=exception)
    elif file_ext in ['yml', 'yaml']:
        return __read_yaml_file(file_path=file_path, exception=exception)



def write_dotenv_file(file_path:str, node_type:str, build:str, node_name:str, is_trainig:bool=False, exception:bool=False):
    configs = {
        "BUILD": build,
        "CONTAINER_NAME": node_name.replace(" ", "-").replace("_", '-'),
        'NETWORK': "host",
        'INIT_TYPE': 'prod'
    }
    if is_trainig is True:
        configs['INIT_TYPE'] = 'training'
    if node_type == 'query': # include Remote-CLI information
        configs['CONN_IP'] = '0.0.0.0'
        configs['CLI_PORT'] = '31800'

    content = ""
    for param in configs:
        content += f"{param}={configs[param]}\n"

    write_file(file_path=file_path, content=content, exception=exception)

