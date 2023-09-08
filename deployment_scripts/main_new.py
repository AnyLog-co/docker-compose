import argparse
import os
import questionnaire
import support
from docker_file_io import read_configs_file, write_configs


ROOT_PATH = os.path.expandvars(os.path.expanduser(__file__)).split('deployment_scripts')[0]
DEFAULT_CONFIG_FILE = os.path.join(ROOT_PATH, 'deployment_scripts', 'configurations.json')
KUBERNETES_CONFIG_FILE = os.path.join(ROOT_PATH, 'deployment_scripts', 'kubernetes_configurations.json')

NODE_TYPES = {
    'none': ['LICENSE_KEY', 'NODE_NAME', 'COMPANY_NAME', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'DB_TYPE',
                 'DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT', 'SYSTEM_QUERY', 'MEMORY', 'NOSQL_ENABLE',
                 'NOSQL_USER', 'NOSQL_PASSWD', 'NOSQL_IP', 'NOSQL_PORT', 'LEDGER_CONN', 'ENABLE_MQTT', 'MQTT_LOG',
                 'MQTT_BROKER', 'MQTT_PORT', 'MQTT_USER', 'MQTT_PASSWD', 'MQTT_TOPIC',
                 'MQTT_DBMS', 'MQTT_TABLE', 'MQTT_TIMESTAMP_COLUMN', 'MQTT_VALUE_COLUMN', 'MQTT_VALUE_COLUMN_TYPE',
                 'DEPLOY_LOCAL_SCRIPT', 'MONITOR_NODES', 'MONITOR_NODE', 'MONITOR_NODE_COMPANY'],
    'generic': ['LICENSE_KEY', 'NODE_NAME', 'COMPANY_NAME', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'DB_TYPE',
                 'DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT', 'SYSTEM_QUERY', 'MEMORY', 'NOSQL_ENABLE',
                 'NOSQL_USER', 'NOSQL_PASSWD', 'NOSQL_IP', 'NOSQL_PORT', 'LEDGER_CONN', 'ENABLE_MQTT', 'MQTT_LOG',
                 'MQTT_BROKER', 'MQTT_PORT', 'MQTT_USER', 'MQTT_PASSWD', 'MQTT_TOPIC',
                 'MQTT_DBMS', 'MQTT_TABLE', 'MQTT_TIMESTAMP_COLUMN', 'MQTT_VALUE_COLUMN', 'MQTT_VALUE_COLUMN_TYPE',
                 'DEPLOY_LOCAL_SCRIPT', 'MONITOR_NODES', 'MONITOR_NODE', 'MONITOR_NODE_COMPANY'],
    'master': ['LICENSE_KEY', 'NODE_NAME', 'COMPANY_NAME', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'DB_TYPE',
               'DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT', 'SYSTEM_QUERY', 'MEMORY', 'LEDGER_CONN', 'DEPLOY_LOCAL_SCRIPT',
               'MONITOR_NODES', 'MONITOR_NODE', 'MONITOR_NODE_COMPANY'],
    'operator': ['LICENSE_KEY', 'NODE_NAME', 'COMPANY_NAME', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'DB_TYPE',
                 'DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT', 'SYSTEM_QUERY', 'MEMORY', 'NOSQL_ENABLE',
                 'NOSQL_USER', 'NOSQL_PASSWD', 'NOSQL_IP', 'NOSQL_PORT', 'LEDGER_CONN', 'ENABLE_MQTT', 'MQTT_LOG',
                 'MQTT_BROKER', 'MQTT_PORT', 'MQTT_USER', 'MQTT_PASSWD', 'MQTT_TOPIC',
                 'MQTT_DBMS', 'MQTT_TABLE', 'MQTT_TIMESTAMP_COLUMN', 'MQTT_VALUE_COLUMN', 'MQTT_VALUE_COLUMN_TYPE',
                 'DEPLOY_LOCAL_SCRIPT', 'MONITOR_NODES', 'MONITOR_NODE', 'MONITOR_NODE_COMPANY'],
    'publisher': ['LICENSE_KEY', 'NODE_NAME', 'COMPANY_NAME', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'DB_TYPE',
                  'DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT', 'SYSTEM_QUERY', 'MEMORY', 'LEDGER_CONN',
                  'ENABLE_MQTT', 'MQTT_LOG', 'MQTT_BROKER', 'MQTT_PORT', 'MQTT_USER', 'MQTT_PASSWD', 'MQTT_TOPIC',
                  'MQTT_DBMS', 'MQTT_TABLE', 'MQTT_TIMESTAMP_COLUMN', 'MQTT_VALUE_COLUMN', 'MQTT_VALUE_COLUMN_TYPE',
                  'DEPLOY_LOCAL_SCRIPT', 'MONITOR_NODES', 'MONITOR_NODE', 'MONITOR_NODE_COMPANY'],
    'query': ['LICENSE_KEY', 'NODE_NAME', 'COMPANY_NAME', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'DB_TYPE',
               'DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT', 'SYSTEM_QUERY', 'MEMORY', 'LEDGER_CONN', 'DEPLOY_LOCAL_SCRIPT',
               'MONITOR_NODES', 'MONITOR_NODE', 'MONITOR_NODE_COMPANY']
    }


def __format_configs(node_type:str, configs:dict):
    configs['general']['NODE_TYPE']['value'] = node_type
    configs['general']['NODE_TYPE']['config_file'] = 'anylog_configs'
    for section in configs:
        for param in configs[section]:
            if param in NODE_TYPES[node_type]:
                configs[section][param]['enable'] = True
                configs[section][param]['config_file'] = 'anylog_configs'
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
    node_configs = __format_configs(node_type=args.node_type, configs=node_configs)

    for section in node_configs:
        status = support.print_questions(node_configs[section])
        if status is True:
            if section == 'networking':
                print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                node_configs[section] = questionnaire.networking_section(configs=node_configs[section])
            elif section == 'database':
                print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                node_configs[section] = questionnaire.database_section(configs=node_configs[section])
            elif section == 'blockchain':
                if args.node_type != 'master':
                    print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                    node_configs['blockchain']['LEDGER_CONN']['default'] = f"127.0.0.1:{node_configs['networking']['ANYLOG_SERVER_PORT']['value']}"
                    node_configs[section] = questionnaire.blockchain_section(configs=node_configs[section])
            elif section == 'operator':
                if args.node_type in ['rest', 'operator', 'standalone']:
                    print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                    node_configs[section] = questionnaire.operator_section(configs=node_configs[section])
            elif section == 'publisher':
                if args.node_type in ['rest', 'publisher', 'standalone-publisher']:
                    print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                    node_configs[section] = questionnaire.generic_section(configs=node_configs[section])
            elif section == 'mqtt':
                if args.node_type in ['rest', 'operator', 'publisher', 'standalone', 'standalone-publisher'] or node_configs['networking']['ANYLOG_BROKER_PORT']['value'] != '':
                    print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                    node_configs[section] = questionnaire.generic_section(configs=node_configs[section])
            else:
                print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                node_configs[section] = questionnaire.generic_section(configs=node_configs[section])
                if section == "general":
                    if args.node_type == 'operator':
                        operator_value = questionnaire.operator_number()
                        node_configs[section]["NODE_NAME"]['value'] = f"{node_configs[section]['NODE_NAME']['default']}{operator_value}"
                    node_configs["advanced settings"]["MONITOR_NODE_COMPANY"]["value"] = node_configs["general"]["COMPANY_NAME"]["value"]
                    node_configs["advanced settings"]["MONITOR_NODE_COMPANY"]["enable"] = False
            print('\n')

    write_configs(deployment_type=args.deployment_type, configs=node_configs, build=args.build, exception=args.exception)



if __name__ == '__main__':
    main()
