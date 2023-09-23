import argparse
import json
import os


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
    Given a configuration (JSON) file, read its content
    :args:
        file_path:str - file path
    """
    file_path = is_file(file_path=file_path, is_argparse=False, exception=exception)
    if file_path is None:
        print(f"Unable to continue due to missing configuration file {file_path}...")
        exit(1)

    try:
        with open(file_path, 'r') as f:
            try:
                return json.load(f)
            except Exception as error:
                if exception is True:
                    print(f"Failed to read content in {file_path} (Error: {error})")
    except Exception as error:
        if exception is True:
            print(f"Failed to open {file_path} for content to be read (Error: {error})")
    exit(1)
