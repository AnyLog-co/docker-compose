import argparse
import json
import os
import requests
import shutil

import file_io
import questionnaire

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployment_scripts')[0]
DOCKER_FILE = os.path.join(ROOT_DIR, 'docker-compose', 'anylog-%s', 'anylog_configs.env')

def __local_ip():
    """
    Get the local IP address of the machine
    """
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return '127.0.0.1'


def __external_ip():
    """
    Get the external IP address of the machine
    """
    try:
        r = requests.get('https://ifconfig.me/')
    except:
        pass
    else:
        try:
            return r.text
        except:
            pass


def __locations():
    """
    Using ipinfo.io/json get location information about the node
    """
    loc = "0.0, 0.0"
    country="Unknown"
    state="Unknown"
    city="Unknown"

    try:
        r = requests.get("https://ipinfo.io/json")
    except Exception as error:
        pass
    else:
        if int(r.status_code) == 200:
            content = r.json()
            loc = content['loc']
            country = content['country']
            state = content['region']
            city = content['city']
    return loc, country, state, city


def __merge_configs(original_configs:dict)->dict:
    """
    Using original_configs + JSON in configs merge the two to have a preset configurations
    :args:
        original_configs:dict - configurations from docker-compose file
    :params:
        config_file:str - path to JSON config file
        default_configs:dict - JSON of content in defautl configs
    :params:
        default_configs with defaults as values from original_configs
    """
    config_file = os.path.join(ROOT_DIR, 'deployment_scripts', 'configs', 'docker.json')
    default_configs = file_io.read_json(json_file=config_file)
    for section in default_configs:
        for key in default_configs[section]:
            if key in original_configs:
                default_configs[section][key]['default'] = original_configs[key]

    return default_configs


def __update_configs(configurations:dict, node_type:str, ledger:str=None)->dict:
    """
    Based on node information, update configurations
    :args:
        configurations:dict - configurations content to update
        config_file:str - JSON configuration file
        node_type:str - Node type (rest, master, operator, query, publisher)
        ledger:str - Master node TCP IP + port connection information
    :params:
        configurations:dict - configs from config_file
    """

    loc, country, state, city = __locations()

    configurations['general']['NODE_TYPE']['default'] = node_type

    # configurations['networking']['EXTERNAL_IP']['default'] = __external_ip()
    # configurations['networking']['LOCAL_IP']['default'] = __local_ip()
    if node_type == 'master':
        configurations['general']['NODE_TYPE']['default'] = 'ledger'
        del configurations['networking']['ANYLOG_BROKER_PORT']
        configurations['networking']['ANYLOG_SERVER_PORT']['default'] = 32048
        configurations['networking']['ANYLOG_REST_PORT']['default'] = 32049
        configurations['blockchain']['LEDGER_CONN']['default'] = '127.0.0.1:32048'
        del configurations['operator']
        del configurations['publisher']
        del configurations['mqtt']
    elif node_type == 'operator':
        configurations['networking']['ANYLOG_SERVER_PORT']['default'] = 32148
        configurations['networking']['ANYLOG_REST_PORT']['default'] = 32149
        if ledger is not None:
            configurations['blockchain']['LEDGER_CONN']['default'] = ledger
        del configurations['publisher']
    elif node_type == 'publisher':
        configurations['networking']['ANYLOG_SERVER_PORT']['default'] = 32248
        configurations['networking']['ANYLOG_REST_PORT']['default'] = 32249
        if ledger is not None:
            configurations['blockchain']['LEDGER_CONN']['default'] = ledger
        del configurations['operator']
    elif node_type == 'query':
        del configurations['networking']['ANYLOG_BROKER_PORT']
        configurations['database']['DEPLOY_SYSTEM_QUERY']['default'] = True
        configurations['database']['MEMORY']['default'] = True
        configurations['networking']['ANYLOG_SERVER_PORT']['default'] = 32348
        configurations['networking']['ANYLOG_REST_PORT']['default'] = 32349
        if ledger is not None:
            configurations['blockchain']['LEDGER_CONN']['default'] = ledger
        del configurations['operator']
        del configurations['publisher']
        del configurations['mqtt']

    configurations['general']['LOCATION']['default'] = loc
    configurations['general']['COUNTRY']['default'] = country
    configurations['general']['STATE']['default'] = state
    configurations['general']['CITY']['default'] = city

    return configurations


def main():
    """
    Set configuration file(s)
    :process:
        0. install requirements - separate script
        1. based on params - read configuration file(s)
        2. update default params
        3. user to update params
        5. rewrite configs
        6. deploy node(s) - separate script
    :positional arguments:
        node_type       select node type to prepare. Option help will provide details about the different node types
            * help - provides an explanation for each node type
            * rest - sandbox for understanding AnyLog as only TCP & REST are configured
            * master - a database node replacing an actual blockchain
            * operator - node where data will be stored
            * query - node dedicated to querying data
            * publisher - node for distributing data among operators
    :optional arguments:
        -h, --help            show this help message and exit
    :params:
        base_dotenv_file:str - base .env file from docker-compose. This will also be the file that gets updated at the
                               end of the process.
        base_docker_env_file_content:dict - content in base_dotenv_file
    """

    parse = argparse.ArgumentParser()
    parse.add_argument('node_type', choices=['help', 'rest', 'master', 'operator', 'query', 'publisher'],
                       default='rest',
                       help='select node type to prepare. Option "help" will provide details about the different nodes')
    args = parse.parse_args()

    # Based on user input read generic config file
    if args.node_type == 'help':
        print('Node type options to deploy:'
              + '\n\trest - sandbox for understanding AnyLog as only TCP & REST are configured'
              + '\n\tmaster - a database node replacing an actual blockchain'
              + '\n\toperator - node where data will be stored'
              + '\n\tpublisher - node to distribute data among operators'
              + '\n\tquery - node dedicated to master node'
        )
        exit(1)

    # based on node_type prepare default configurations
    base_docker_env_file = DOCKER_FILE % args.node_type
    shutil.copyfile(base_docker_env_file, base_docker_env_file + ".orig")
    base_docker_env_file_content = file_io.read_dotenv_file(dotenv_file=base_docker_env_file)
    configurations = __merge_configs(original_configs=base_docker_env_file_content)
    configurations = __update_configs(configurations=configurations, node_type=args.node_type)

    for section in configurations:
        print(f'Configurations for {args.node_type.capitalize()} - {section.capitalize().replace("Mqtt", "MQTT").replace("Db", "DB")}')
        configurations[section] = questionnaire.questions(section_params=configurations[section])

        # if AnyLog Broker is enabled, then we can assume user would like to run MQTT client process
        if section == 'networking' and 'ANYLOG_BROKER_PORT' in configurations[section] and configurations[section]['ANYLOG_BROKER_PORT']['value'] != '':
            configurations['mqtt']['ENABLE_MQTT']['default'] = True
            configurations['mqtt']['BROKER']['default'] = 'local'
            configurations['mqtt']['MQTT_PORT']['default'] = configurations[section]['ANYLOG_BROKER_PORT']['value']

            del configurations['mqtt']['ENABLE_MQTT']['value']
            del configurations['mqtt']['BROKER']['value']
            del configurations['mqtt']['MQTT_PORT']['value']

        print('\n')

    file_io.write_dotenv_file(content=configurations, dotenv_file=base_docker_env_file)


if __name__ == '__main__':
    main()