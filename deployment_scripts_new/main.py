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
            if section == 'networking':
                print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                node_configs[section] = questionnaire.network_configs(configs=node_configs[section])
    #         elif section == 'database':
    #             print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
    #             node_configs[section] = questionnaire.database_section(configs=node_configs[section])
    #         elif section == 'blockchain':
    #             print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
    #             if (args.node_type != 'master' and args.basic_config is True) or args.basic_config is False:
    #                 node_configs['blockchain']['LEDGER_CONN']['default'] = f"127.0.0.1:{node_configs['networking']['ANYLOG_SERVER_PORT']['default']}"
    #             node_configs[section] = questionnaire.blockchain_section(configs=node_configs[section])
    #         elif section == 'operator':
    #             if args.node_type in ['rest', 'operator', 'standalone']:
    #                 print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
    #                 node_configs[section] = questionnaire.operator_section(configs=node_configs[section])
    #         elif section == 'publisher':
    #             if args.node_type in ['rest', 'publisher', 'standalone-publisher']:
    #                 print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
    #                 node_configs[section] = questionnaire.generic_section(configs=node_configs[section])
    #         elif section == 'mqtt':
    #             if args.node_type in ['rest', 'operator', 'publisher', 'standalone', 'standalone-publisher'] or \
    #                     node_configs['networking']['ANYLOG_BROKER_PORT']['value'] != '':
    #                 print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
    #                 node_configs[section] = questionnaire.generic_section(configs=node_configs[section])
    #         print('\n')
    #     elif status is False and section == "operator" and args.node_type in ["operator", "generic"]:
    #         print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
    #         operator_value = questionnaire.operator_number()
    #         company_name = node_configs['general']['COMPANY_NAME']['value'].lower().replace(" ", "-")
    #         if node_configs['general']['NODE_NAME']['value'] == "anylog-operator":
    #             node_configs['general']['NODE_NAME']['value'] = f"{company_name}-operator{operator_value}"
    #         node_configs[section]['CLUSTER_NAME']['default'] = f"{company_name}-cluster{operator_value}"
    #         node_configs[section]['CLUSTER_NAME']['config_file'] = 'anylog_configs'
    #         print('\n')
    #
    # if args.deployment_type == "docker":
    #     advance_configs = docker_create_path(node_type=node_configs['general']['NODE_TYPE']['value'],
    #                                            file_name='advance_configs', exception=args.exception)
    #     anylog_configs = docker_create_path(node_type=node_configs['general']['NODE_TYPE']['value'],
    #                                           file_name='anylog_configs', exception=args.exception)
    #     if anylog_configs != "" and advance_configs != "":
    #         docker_write_configs_files(anylog_configs=anylog_configs, advance_configs=advance_configs,
    #                                      configs=node_configs, exception=args.exception)
    #         dotenv_update_configs_files(node_type=node_configs['general']['NODE_TYPE']['value'],
    #                                     node_name=node_configs['general']['NODE_NAME']['value'],
    #                                     build=args.build, exception=args.exception)
    #
    #     elif anylog_configs == "" or advance_configs == "":
    #         print(f"Failed to create anylog_configs and/or advance_configs file. Cannot store survey to file(s) ")

    # elif args.deployment_type == "kubernetes":
    #     kubernetes_configs = kubernetes_questionnaire(node_name=node_configs['general']['NODE_NAME']['value'],
    #                                                   configs=kubernetes_configs)
    #     if node_configs['networking']['LOCAL_IP']['value'] == "":
    #         node_configs['networking']['KUBERNETES_SERVICE_IP']['value'] = kubernetes_configs['metadata']['service_name']['value']
    #
    #     kubernetes_config_file = kubernetes_create_path(node_type=node_configs['general']['NODE_TYPE']['value'], exception=args.exception)
    #     kubernetes_write_configs_files(configs=node_configs, config_file=kubernetes_config_file, exception=args.exception)




if __name__ == '__main__':
    main()
