"""
The following provides the needed methods for configuration file I/O
- YAML: https://pynative.com/python-yaml/#:~:text=Use%20the%20PyYAML%20module%E2%80%99s%20yaml.dump%20%28%29%20method%20to,to%20convert%20Python%20dictionary%20into%20a%20YAML%20stream.
- .env: https://www.makeuseof.com/dotenv-file-read-data-python-nodejs-golang/#:~:text=How%20to%20Read%20the.env%20File%20in%20Python%20You,the%20functionality%20to%20read%20data%20from%20a.env%20file.
"""
import dotenv
import json
import os
import yaml

def __validate_file(file_name:str)->str:
    """
    Validate if file exists
    :args:
        file_name:str - file to validate it exists
    :params:
        full_path:str - full path of YAML file
    :return:
        if success return full path, else return None
    """
    full_path = os.path.expandvars(os.path.expanduser(file_name))
    if not os.path.isfile(full_path):
        print(f'Failed to locate file {file_name}. Cannot continue')
        full_path = None
    return full_path


def __create_file(file_name:str)->str:
    """
    Create file to write content into if DNE
    :Args:
        file_name:str - file to create
    :params:
        full_path:str - full path of file_name
    """
    full_path = os.path.expandvars(os.path.expanduser(file_name))

    if not os.path.isfile(full_path):
        try:
            open(full_path, 'x')
        except Exception as error:
            print(f'Failed to create file {file_name}. Cannot continue (Error: {error})')
            full_path = None

    return full_path


def read_json(json_file:str)->dict:
    """
    Given a JSON file, read its content
    :args:
        json_file:str - JSON file to read
    :params:
        content:dict - content from JSON file
        full_path:str - get full path of JSON file
    :return:
        if file is properly read, then it returns a (content) dictionary, else None
    """
    content = None
    full_path = __validate_file(file_name=json_file)
    if full_path is not None:
        try:
            with open(json_file) as jsn:
                try:
                    content = json.load(jsn)
                except Exception as error:
                    print(f'Failed to load content from {json_file} (Error: {error})')
        except Exception as error:
            print(f'Failed to open JSON file {json_file} (Error: {error})')
    return content


def read_yaml_file(yaml_file:str)->dict:
    """
    Given a YAML file, read its content
    :args:
        yaml_file:str - YAML file to read
    :params:
        content:dict - content from YAML file
        full_path:str - get full path of YAML file
    :return:
        if file is properly read, then it returns a (content) dictionary, else None
    """
    content = None
    full_path = __validate_file(file_name=yaml_file)
    if full_path is not None:
        try:
            with open(full_path) as yml:
                try:
                    content = yaml.load(yml, Loader=yaml.loader.SafeLoader)
                except Exception as error:
                    print(f'Failed to load content from {yaml_file} (Error: {error})')
        except Exception as error:
            print(f'Failed to open YAML file {yaml_file} (Error: {error})')

    return content


def write_yaml_file(content:dict, yaml_file:str='$HOME/deployments/helm/sample-configurations/test.yml')->bool:
    """
    Write content into YAML file
    :disclaimer:
        The Order of sections changes, but this should not affect the code as the values within the section(s) stay
        consistent
    :args:
        content:dict - content to write into YAML file
        yaml_file:str - file to write content into
    :params:
        status:bool
        full_path:str - full path of the node
    :return:
        if success True, else False
    """
    status = False
    full_path = __create_file(file_name=yaml_file)
    if full_path is not None:
        try:
            with open(full_path, 'w') as yml:
                try:
                    yaml.dump(content, yml)
                except Exception as error:
                    print(f'Failed to write content into {yaml_file} (Error: {error})')
        except Exception as error:
            print(f'Failed to open file {yaml_file} (Error: {error})')
        else:
            status = True

    return status


def read_dotenv_file(dotenv_file:str)->dict:
    """
    Given a dotenv file, read its content & return it
    :args:
        dotenv_file:str - file to read content from
    :params:
        content:dict - content to return
        full_path:str - full file path
    :return:
        content
    """
    content = None
    full_path = __validate_file(file_name=dotenv_file)
    if full_path is not None:
        try:
            content = json.loads(json.dumps(dotenv.dotenv_values(full_path)))
        except Exception as error:
            print(f'Failed to load {dotenv_file} (Error: {error})')

    return content


def write_dotenv_file(content:dict, dotenv_file='$HOME/deployments/docker-compose/test.dotenv')->bool:
    """
    Write content into YAML file
    :disclaimer:
        The Order of sections changes, but this should not affect the code as the values within the section(s) stay
        consistent
    :args:
        content:dict - content to write into YAML file
        dotenv_file:str - file to write content into
    :params:
        status:bool
        full_path:str - full path of the node
    :return:
        if success True, else False
    """
    status = False
    full_path = __create_file(file_name=dotenv_file)
    stmt = ""
    if os.path.isfile(full_path):
        for section in content:
            for param in content[section]:
                if 'value' in content[section][param] and content[section][param]['value'] != "":
                    if content[section][param]['value'] in [True, False]:
                        content[section][param]['value'] = str(content[section][param]['value']).lower()
                    input = f"{param}={content[section][param]['value']}"
                elif content[section][param]['default'] != "":
                    if content[section][param]['default'] in [True, False]:
                        content[section][param]['default'] = str(content[section][param]['default']).lower()
                    input = f"{param}={content[section][param]['default']}"
                else:
                    input = f"#{param}=<{param}>"
                stmt += f"# {content[section][param]['description']}\n{input}\n"

            stmt += "\n"

        try:
            with open(full_path, 'w') as denv:
                try:
                    denv.write(stmt)
                except Exception as error:
                    print(f'Failed to write params into file: {file_name} (Error: {error})')
        except Exception as error:
            print(f'Failed to write open file: {file_name} (Error: {error})')
        else:
            status = True

    return status
