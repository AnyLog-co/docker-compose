import argparse
import os

import questionnaire
from questionnaire_kubernetes import questionnaire as kubernetes_questionnaire
from __support__ import format_configs, print_questions

from file_io import read_configs_file, docker_create_path, kubernetes_create_path, dotenv_update_configs_files, docker_write_configs_files, kubernetes_write_configs_files

NODE_TYPES = ['generic', 'master', 'operator', 'query', 'publisher']

ROOT_PATH = os.path.expandvars(os.path.expanduser(__file__)).split('deployment_scripts_new')[0]
DEFAULT_CONFIG_FILE = os.path.join(ROOT_PATH, 'deployment_scripts_new', 'config_files', 'configurations.json')
KUBERNETES_CONFIG_FILE = os.path.join(ROOT_PATH, 'deployment_scripts_new', 'config_files', 'kubernetes_configurations.json')


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
    parser.add_argument('node_type', type=str, choices=NODE_TYPES, default='generic', help='Node type to deploy')
    parser.add_argument('--build', type=str, choices=['latest', 'beta'], default='latest',
                        help='Which AnyLog version to run')
    parser.add_argument('--deployment-type', type=str, choices=['docker', 'kubernetes'], default='docker',
                        help='Deployment type - docker generates .env file, kubernetes generates YAML file')
    parser.add_argument('--config-file', type=str, default=DEFAULT_CONFIG_FILE, help='Configuration file to use for default values')
    parser.add_argument('--k8s-config-file', type=str, default=KUBERNETES_CONFIG_FILE, help='Kubernetes configuration_file')
    parser.add_argument('--basic-config', type=bool, default=False, nargs='?', const=True, help='Only basic questions, used for demo purposes')
    parser.add_argument('-e', '--exception', type=bool, default=False, nargs='?', const=True, help='Whether to print exceptions')
    args = parser.parse_args()

    node_configs = read_configs_file(config_file=args.config_file, exception=args.exception)
    node_configs = format_configs(node_type=args.node_type, configs=node_configs, basic_config=args.basic_config)

    if args.deployment_type == 'kubernetes':
        kubernetes_configs = read_configs_file(config_file=args.k8s_config_file, exception=args.exception)
        kubernetes_configs['image']['tag']['default'] = args.build
    else:
        node_configs['networking'].pop('KUBERNETES_SERVICE_IP')

    for section in node_configs:
        status = print_questions(node_configs[section])
        if status is True:
            if section == 'general':
                print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                node_configs[section] = questionnaire.general_configs(configs=node_configs[section])
            if section == "authentication":
                print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                node_configs[section] = questionnaire.generic_configs(configs=node_configs)
            if section == 'networking':
                print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                node_configs[section] = questionnaire.network_configs(configs=node_configs[section])
                ledger_conn = f"127.0.0.1:{node_configs['networking']['ANYLOG_SERVER_PORT']['value']}"
            elif section == 'database':
                print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                node_configs[section] = questionnaire.database_configs(configs=node_configs[section])
            elif section == 'blockchain':
                print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                node_configs['blockchain']['LEDGER_CONN']['default'] = ledger_conn
                node_configs[section] = questionnaire.blockchain_section(configs=node_configs[section])
            elif section == 'operator':
                print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                node_configs[section] = questionnaire.operator_section(configs=node_configs[section])
            elif section == 'publisher':
                print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                node_configs[section] = questionnaire.publisher_section(configs=node_configs[section])
            elif section == 'mqtt':
                print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                node_configs[section] = questionnaire.mqtt_section(configs=node_configs[section])
            elif section == 'advanced settings':
                print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                node_configs[section] = questionnaire.advanced_settings_section(configs=node_configs[section])

    print(node_configs)

if __name__ == '__main__':
    main()
