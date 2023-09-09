import argparse
import os
import questionnaire
import support
from docker_file_io import read_configs_file, docker_create_path, docker_create_configs_section


ROOT_PATH = os.path.expandvars(os.path.expanduser(__file__)).split('deployment_scripts')[0]
DEFAULT_CONFIG_FILE = os.path.join(ROOT_PATH, 'deployment_scripts', 'configurations.json')
KUBERNETES_CONFIG_FILE = os.path.join(ROOT_PATH, 'deployment_scripts', 'kubernetes_configurations.json')

NODE_TYPES = {
    'generic': ['LICENSE_KEY', 'NODE_NAME', 'COMPANY_NAME', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'DB_TYPE',
                 'DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT', 'SYSTEM_QUERY', 'MEMORY', 'NOSQL_ENABLE',
                 'NOSQL_USER', 'NOSQL_PASSWD', 'NOSQL_IP', 'NOSQL_PORT', 'LEDGER_CONN', 'ENABLE_MQTT', 'MQTT_LOG',
                 'MQTT_BROKER', 'MQTT_PORT', 'MQTT_USER', 'MQTT_PASSWD', 'MQTT_TOPIC',
                 'MQTT_DBMS', 'MQTT_TABLE', 'MQTT_TIMESTAMP_COLUMN', 'MQTT_VALUE_COLUMN', 'MQTT_VALUE_COLUMN_TYPE',
                 'DEPLOY_LOCAL_SCRIPT', 'MONITOR_NODES', 'MONITOR_NODE', 'MONITOR_NODE_COMPANY'],
    'master': ['LICENSE_KEY', 'NODE_NAME', 'COMPANY_NAME', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'DB_TYPE',
               'DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT', 'SYSTEM_QUERY', 'MEMORY', 'LEDGER_CONN', 'DEPLOY_LOCAL_SCRIPT',
               'MONITOR_NODES', 'MONITOR_NODE', 'MONITOR_NODE_COMPANY'],
    'operator': ['LICENSE_KEY', 'NODE_NAME', 'COMPANY_NAME', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'ANYLOG_BROKER_PORT',
                 'DB_TYPE', 'DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT', 'SYSTEM_QUERY', 'MEMORY', 'NOSQL_ENABLE',
                 'NOSQL_USER', 'NOSQL_PASSWD', 'NOSQL_IP', 'NOSQL_PORT', 'LEDGER_CONN', 'ENABLE_MQTT', 'MQTT_LOG',
                 'MQTT_BROKER', 'MQTT_PORT', 'MQTT_USER', 'MQTT_PASSWD', 'MQTT_TOPIC',
                 'MQTT_DBMS', 'MQTT_TABLE', 'MQTT_TIMESTAMP_COLUMN', 'MQTT_VALUE_COLUMN', 'MQTT_VALUE_COLUMN_TYPE',
                 'DEPLOY_LOCAL_SCRIPT', 'MONITOR_NODES', 'MONITOR_NODE', 'MONITOR_NODE_COMPANY'],
    'publisher': ['LICENSE_KEY', 'NODE_NAME', 'COMPANY_NAME', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'ANYLOG_BROKER_PORT',
                  'DB_TYPE', 'DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT', 'SYSTEM_QUERY', 'MEMORY', 'LEDGER_CONN',
                  'ENABLE_MQTT', 'MQTT_LOG', 'MQTT_BROKER', 'MQTT_PORT', 'MQTT_USER', 'MQTT_PASSWD', 'MQTT_TOPIC',
                  'MQTT_DBMS', 'MQTT_TABLE', 'MQTT_TIMESTAMP_COLUMN', 'MQTT_VALUE_COLUMN', 'MQTT_VALUE_COLUMN_TYPE',
                  'DEPLOY_LOCAL_SCRIPT', 'MONITOR_NODES', 'MONITOR_NODE', 'MONITOR_NODE_COMPANY'],
    'query': ['LICENSE_KEY', 'NODE_NAME', 'COMPANY_NAME', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'DB_TYPE',
               'DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT', 'SYSTEM_QUERY', 'MEMORY', 'LEDGER_CONN', 'DEPLOY_LOCAL_SCRIPT',
               'MONITOR_NODES', 'MONITOR_NODE', 'MONITOR_NODE_COMPANY']
    }

BASIC_CONFIG = ["LICENSE_KEY", "NODE_NAME", "COMPANY_NAME", "LEDGER_CONN", "MONITOR_NODES", "ENABLE_MQTT"]

def __format_configs(node_type:str, configs:dict, basic_config:bool=False):
    """
    Enable configurations based on node_type
    :global:
        NODE_TYPES:dict - Node types (generic, operator, master, query, publisher) & configurations user should update
        BASIC_CONFIG:list - required configs when running in demo mode
    :args:
        node_type:str - Node type
        configs:dict - configurations to be updated
        basic_config:bool - whether set only demo configs or "all" configs for a specific node type
    :return:
        enabled configs based on node_type and demo_configs
    """
    configs['general']['NODE_TYPE']['default'] = node_type
    configs['general']['NODE_TYPE']['config_file'] = 'anylog_configs'
    configs['general']['NODE_TYPE']['enable'] = False
    if node_type != "generic":
        configs['general']['NODE_NAME']['default'] = f"anylog-{node_type}"
    if node_type == "master":
        configs['networking']['ANYLOG_SERVER_PORT']['default'] = 32048
        configs['networking']['ANYLOG_REST_PORT']['default'] = 32049
    elif node_type == "operator":
        configs['networking']['ANYLOG_SERVER_PORT']['default'] = 32148
        configs['networking']['ANYLOG_REST_PORT']['default'] = 32149
    elif node_type == "query":
        configs['networking']['ANYLOG_SERVER_PORT']['default'] = 32348
        configs['networking']['ANYLOG_REST_PORT']['default'] = 32349
    elif node_type == "publisher":
        configs['networking']['ANYLOG_SERVER_PORT']['default'] = 32248
        configs['networking']['ANYLOG_REST_PORT']['default'] = 32249

    for section in configs:
        for param in configs[section]:
            if param in NODE_TYPES[node_type]:
                configs[section][param]['enable'] = True
                configs[section][param]['config_file'] = 'anylog_configs'
            if not (basic_config is True and param in BASIC_CONFIG and param in NODE_TYPES[node_type]):
                configs[section][param]['enable'] = False

    return configs



def main():
    """
    :positional arguments:
        node_type   Node type to deploy
            * none
            * generic
            * master
            * operator
            * publisher
            * query
            * standalone
            * standalone-publisher
    :optional arguments:
        -h, --help                                show this help message and exit
        --build               BUILD               Which AnyLog version to run
        --deployment-type     DEPLOYMENT_TYPE     Deployment type - docker generates .env file, kubernetes generates YAML file
            * docker
            * kubernetes
        --config-file   CONFIG_FILE               Configuration file to use for default values
            * latest
            * predevelop
            * test
        -e, --exception  [EXCEPTION]              Whether to print exception
    :params:
        config_file:dict - content from configuration file
        configs:dict - removed un-needed configurations
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('node_type', type=str, choices=list(NODE_TYPES.keys()), default='generic', help='Node type to deploy')
    parser.add_argument('--build', type=str, choices=['latest', 'beta'], default='latest',
                        help='Which AnyLog version to run')
    parser.add_argument('--deployment-type', type=str, choices=['docker', 'kubernetes'], default='docker',
                        help='Deployment type - docker generates .env file, kubernetes generates YAML file')
    parser.add_argument('--config-file', type=str, default=DEFAULT_CONFIG_FILE, help='Configuration file to use for default values')
    parser.add_argument('--basic-config', type=bool, default=False, nargs='?', const=True, help='Only basic questions, used for demo purposes')
    parser.add_argument('-e', '--exception', type=bool, default=False, nargs='?', const=True, help='Whether to print exceptions')
    args = parser.parse_args()

    node_configs = read_configs_file(config_file=args.config_file, exception=args.exception)
    node_configs = __format_configs(node_type=args.node_type, configs=node_configs, basic_config=args.basic_config)

    for section in node_configs:
        status = support.print_questions(node_configs[section])
        if status is True:
            print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
            if section == 'networking':
                node_configs[section] = questionnaire.networking_section(configs=node_configs[section])
            elif section == 'database':
                node_configs[section] = questionnaire.database_section(configs=node_configs[section])
            elif section == 'blockchain':
                node_configs[section] = questionnaire.blockchain_section(configs=node_configs[section])
            elif section == 'operator' and args.node_type in ["operator", "generic"]:
                if args.basic_configs is True:
                    operator_value = questionnaire.operator_number()
                    company_name = node_configs['general']['COMPANY_NAME']['value'].lower().replace(" ", "-")
                    if node_configs['general']['NODE_NAME']['value'] == "anylog-operator":
                        node_configs['general']['NODE_NAME']['value'] = f"{company_name}-operator{operator_value}"
                        node_configs[section]['CLUSTER_NAME']['default'] = f"{company_name}-cluster{operator_value}"
                node_configs[section] = questionnaire.operator_section(configs=node_configs[section])
            elif section == 'publisher' and args.node_type in ["publisher", "generic"]:
                node_configs[section] = questionnaire.generic_section(configs=node_configs[section])
            elif section == 'mqtt' and args.node_type in ["operator", "publisher", "generic"]:
                node_configs[section] = questionnaire.generic_section(configs=node_configs[section])
            else:
                if section == "advanced settings":
                    node_configs["advanced settings"]["MONITOR_NODE_COMPANY"]["default"] = node_configs["general"]["COMPANY_NAME"]["value"]
                node_configs[section] = questionnaire.generic_section(configs=node_configs[section])
            print('\n')

    if args.deployment_type == "docker":
        advance_configs = docker_create_path(node_type=node_configs['general']['NODE_TYPE']['value'],
                                               file_name='advance_configs', exception=args.exception)
        anylog_configs = docker_create_path(node_type=node_configs['general']['NODE_TYPE']['value'],
                                              file_name='anylog_configs', exception=args.exception)
        docker_create_configs_section(anylog_configs=anylog_configs, advance_configs=advance_configs, configs=node_configs,
                                      exception=args.exception)

    elif args.deployment_type == "kubernetes":
        pass





if __name__ == '__main__':
    main()
