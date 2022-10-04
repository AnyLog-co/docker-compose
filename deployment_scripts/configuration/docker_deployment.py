import argparse
import json
import os
import requests
import shutil

import file_io
import questionnaire

ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployment_scripts')[0]
DOCKER_FILE = os.path.join(ROOT_DIR, 'docker-compose', 'anylog-%s', 'anylog_configs.env')

#
def __local_ip()->str:
    """
    Get the local IP address of the machine
    """
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return '127.0.0.1'


def __external_ip()->str:
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


def __locations()->dict:
    """
    Using ipinfo.io/json get location information about the node
    :params:
        output:dict - content for  relevant param
    :return:
        output
    """
    output = {
        'loc': '0.0, 0.0',
        'country': 'Unknown',
        'state': 'Unknown',
        'city': 'Unknown'
    }
    try:
        r = requests.get("https://ipinfo.io/json")
    except Exception as error:
        pass
    else:
        if int(r.status_code) == 200:
            try:
                content = r.json()
            except Exception as error:
                pass
            else:
                if 'loc' in content:
                    output['loc'] = content['loc']
                if 'country' in content:
                    output['country'] = content['country']
                if 'region' in content:
                    output['state'] = content['region']
                if 'city' in content:
                    output['city'] = content['city']

    return output


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

    config_file_content = file_io.read_json(json_file='configs.json')
    config_file_content['general']['NODE_TYPE']['value'] = args.node_type

    location_info = __locations()
    config_file_content['general']['LOCATION']['default'] = location_info['loc']
    config_file_content['general']['COUNTRY']['default'] = location_info['country']
    config_file_content['general']['STATE']['default'] = location_info['state']
    config_file_content['general']['CITY']['default'] = location_info['city']

    for section in config_file_content:
        view_section = True
        if args.node_type in ['master', 'query'] and section == 'mqtt':
            view_section = False
        elif args.node_type in ['master', 'query', 'publisher', 'rest'] and section == 'operator':
            view_section = False
        elif args.node_type in ['master', 'query', 'operator', 'rest'] and section == 'publisher':
            view_section = False
        if view_section is True and section == 'mqtt':
            print(f'Section: {section.upper()}')
        elif view_section is True:
            print(f'Section: {section.title()}')
        if view_section is True:
            questionnaire.questions(section=config_file_content[section])



if __name__ == '__main__':
    main()