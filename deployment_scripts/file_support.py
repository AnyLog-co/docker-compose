import os

ROOT_PATH = os.path.expandvars(os.path.expanduser(__file__)).split("deployment_scripts")[0]


def read_dotenv(config_file:str, exception:bool=False)->dict:
    """
    Read configs from .env file
    :args:
        config_file:str - .env file to read configs from
        exception:bool - whether to print exceptions
    :params:
        configs:dict - configs read from .env file
    :return:
        configs
    """
    configs = {}
    try:
        import dotenv
    except Exception as error:
        print(f"Failed to find dotenv import package (Error: {error})")
        return configs

    try:
        configs = dict(dotenv.dotenv_values(config_file))
    except Exception as error:
        if exception is True:
            print(f"Failed to read configs from {config_file} (Error: {error})")

    return configs


def read_json(config_file:str, exception:bool=False)->dict:
    """
    Read configs from .env file
    :args:
        config_file:str - .json file to read configs from
        exception:bool - whether to print exceptions
    :params:
        configs:dict - configs read from .env file
    :return:
        configs
    """
    configs = {}
    try:
        import json
    except Exception as error:
        print(f"Failed to find json import package (Error: {error})")
        return configs

    try:
        with open(config_file) as f:
            try:
                configs = json.load(f)
            except Exception as error:
                if exception is True:
                    print(f"Failed read content in {config_file} (Error: {error})")
    except Exception as error:
        if exception is True:
            print(f"Failed to read configs from {config_file} (Error: {error})")

    return configs


def read_yaml(config_file:str, exception:bool=False)->dict:
    """
    Read configs from .env file
    :args:
        config_file:str - .json file to read configs from
        exception:bool - whether to print exceptions
    :params:
        configs:dict - configs read from .env file
    :return:
        configs
    """
    configs = {}
    try:
        import yaml
    except Exception as error:
        print(f"Failed to find yaml import package (Error: {error})")
        return configs

    try:
        with open(config_file) as f:
            try:
                configs = yaml.load(f, Loader=yaml.FullLoader)
            except Exception as error:
                if exception is True:
                    print(f"Failed read content in {config_file} (Error: {error})")
    except Exception as error:
        if exception is True:
            print(f"Failed to read configs from {config_file} (Error: {error})")

    return configs


def create_file(file_path:str, exception:bool=False)->bool:
    """
    Create file based on file_path
    :args:
        file_path:str - file (with path) to store configurations in
        exception:bool - whether to print exceptions
    :params:
        status:bool
        file_ext:str - extension of file_path
    :return:
        status
    """
    status = True
    file_path = os.path.expanduser(os.path.expandvars(file_path))
    file_ext = file_path.rsplit(".", 1)[-1]

    if os.path.isfile(file_path):
        try:
            os.rename(file_path, file_path.replace(f".{file_ext}", f".{file_ext}.old"))
        except Exception as error:
            status = False
            if exception is True:
                print(f"Failed to rename {file_path} (Error: {error})")

    if status is True: # reset file
        try:
            open(file_path, "w").close()
        except Exception as error:
            status = False
            if exception is True: 
                print(f"Failed to create file {file_path} (Error: {error})")

    return  status


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
    file_path = os.path.join(ROOT_PATH, 'deployment_scripts', 'network_comment.txt')
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


def append_content(content:str, file_path:str, exception:bool=False)->bool:
    """
    Append content into file
    :args:
        content:str - content to write into file
        file_path:str - file (path) to store content into
        exception:bool - whether to print exceptions
    :params:
        status:bool
    :return:
        status
    """
    status = True
    if not os.path.isfile(file_path):
        file_path = create_file(file_path=file_path, exception=exception)
        if file_path == "":
            status = False

    if status is True:
        try:
            with open(file_path, 'a') as f:
                try:
                    f.write(content)
                except Exception as error:
                    status = False
                    if exception is True:
                        print(f"Failed to append content into {file_path} (Error: {error})")
        except Exception as error:
            status = False
            if exception is True:
                print(f"Failed to open file {file_path} to append content (Error: {error})")

    return status
