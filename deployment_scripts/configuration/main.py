import argparse
import json
import os
import requests

import file_io
import questions

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


def __update_configs(config_file:str, node_type:str, ledger:str=None)->dict:
    """
    Based on node information, update configurations
    :args:
        config_file:str - JSON configuration file
        node_type:str - Node type (rest, master, operator, query, publisher)
        ledger:str - Master node TCP IP + port connection information
    :params:
        configurations:dict - configs from config_file
    """
    configurations = file_io.read_json(json_file=config_file)
    if configurations is not None:
        loc, country, state, city = __locations()

        configurations['general']['NODE_TYPE']['default'] = node_type

        # configurations['networking']['EXTERNAL_IP']['default'] = __external_ip()
        # configurations['networking']['LOCAL_IP']['default'] = __local_ip()
        if node_type == 'master':
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
            * demo - deployment of 1 master, 2 operator and a query node on a single machine using docker. In addition,
                     the deployment also runs PostgreSQL, Grafana and Remote-CLI. This will overwrite deployment-type
    :optional arguments:
        -h, --help            show this help message and exit
        --deployment-type     Deployment type
            * docker
            * kubernetes
    :params:
        ROOT_DIR:str - root directory
        file_params:dict - parameters from file. For the case of "demo" deployment, it's a dictionary with all the variables
                            from the different nodes
    """
    ROOT_DIR = os.path.expandvars(os.path.expanduser(__file__)).split('deployment_scripts')[0]

    parse = argparse.ArgumentParser()
    parse.add_argument('node_type', choices=['help', 'rest', 'master', 'operator', 'query', 'publisher', 'demo'],
                       default='rest',
                       help='select node type to prepare. Option help will provide details about the different node types')
    parse.add_argument('--deployment-type', choices=['docker', 'kubernetes'], default='docker', help='Deployment type')
    args = parse.parse_args()
    if args.node_type == 'help':
        print('Node type options to deploy:'
              + '\n\trest - sandbox for understanding AnyLog as only TCP & REST are configured'
              + '\n\tmaster - a database node replacing an actual blockchain'
              + '\n\toperator - node where data will be stored'
              + '\n\tpublisher - node to distribute data among operators'
              + '\n\tquery - node dedicated to master node'
              + '\n\tdemo - configure the (docker) demo-cluster-deployment. This will overwrite the deployment-type'
              )
        exit(1)

    # Based on user input read generic config file
    elif args.node_type == 'demo' or args.deployment_type == 'docker':
        file_path = os.path.join(__file__.rsplit('main.py', 1)[0], 'docker.json')
        args.deployment_type = 'docker'
    elif args.deployment_type == 'kubernetes':
        file_path = os.path.join(__file__.rsplit('main.py', 1)[0], 'kubernetes.json')
    configurations = __update_configs(node_type=args.node_type, config_file=file_path)

    # User input
    for section in configurations:
        print(f'Configurations for {args.node_type.capitalize()} - {section.capitalize().replace("Mqtt", "MQTT")}')
        configurations[section] = questions.questions(section_params=configurations[section])
        if section == 'networking' and configurations[section]['ANYLOG_BROKER_PORT'] != '':
            configurations['mqtt']['BROKER']['default'] = 'local'
        print("\n")
    


if __name__ == '__main__':
    main()