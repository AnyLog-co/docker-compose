""""
Convert .env file to JSON formaat for OpenHorizon
"""
import argparse
import dotenv
import json
import os

ROOT_PATH = os.path.dirname(os.path.expanduser(os.path.expanduser(os.path.abspath(__file__))))
DEMO_OPERATOR_CONFIGS = os.path.join(ROOT_PATH, 'demo_operator_configs.env')

def __read_dotenv(config_file:str)->dict:
    configs = {}
    try:
        configs = dict(dotenv.dotenv_values(config_file))
    except Exception as error:
        print(f"Failed to read configs from {config_file} (Error: {error})")

    return configs

def __write_json_file(config_file:str, payload:dict):
    try:
        with open(config_file, 'w') as f:
            try:
                f.write(json.dumps(payload, indent=4))
            except Exception as error:
                print(f"Failed to write content to {config_file} (Error: {error})")
    except Exception as error:
        print(f"Failed open file {config_file} for writing (Error: {error})")

def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('--config-file', type=str, default=DEMO_OPERATOR_CONFIGS, help='.env configuration file to update')
    args = parse.parse_args()
    dotenv_file_path = os.path.expanduser(os.path.expandvars(args.config_file))
    json_file_path = dotenv_file_path.replace(".env", ".json")
    if not os.path.isfile(dotenv_file_path):
        print(f'Failed to locate {dotenv_file_path}. Cannot continue...')
        exit(1)
    dot_env_configs = __read_dotenv(config_file=dotenv_file_path)
    if dot_env_configs != {}:
        __write_json_file(config_file=json_file_path, payload=dot_env_configs)


if __name__ == '__main__':
    main()

