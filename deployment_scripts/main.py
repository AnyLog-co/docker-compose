import argparse
import json
import os

import file_io
import support
import kubernetes_questionnaire
import questionnaire


# import support
# import questionnaire
# import kubernetes_defaults_prep
# import write_docker
# import write_kubernetes

ROOT_PATH = os.path.expandvars(os.path.expanduser(__file__)).split('deployment_scripts')[0]
DEFAULT_CONFIG_FILE = os.path.join(ROOT_PATH, 'deployment_scripts', 'configurations.json')
KUBERNETES_CONFIG_FILE = os.path.join(ROOT_PATH, 'deployment_scripts', 'kubernetes_configurations.json')

NODE_TYPES = ['none', 'rest', 'master', 'operator', 'publisher', 'query', 'standalone', 'standalone-publisher']


def main():
    """
    :positional arguments:
        node_type   Node type to deploy
            * none
            * rest
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
            * develop
            * predevelop
            * test
        -e, --exception  [EXCEPTION]              Whether to print exception
    :params:
        config_file:dict - content from configuration file
        configs:dict - removed un-needed configurations
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('node_type', type=str, choices=NODE_TYPES, default='rest', help='Node type to deploy')
    parser.add_argument('--build', type=str, choices=['develop', 'predevelop', 'test'], default='develop',
                        help='Which AnyLog version to run')
    parser.add_argument('--deployment-type', type=str, choices=['docker', 'kubernetes'], default='docker',
                        help='Deployment type - docker generates .env file, kubernetes generates YAML file')
    parser.add_argument('--config-file', type=str, default=None, help='Configuration file to use for default values')
    parser.add_argument('-e', '--exception', type=bool, default=False, nargs='?', const=True, help='Whether to print exceptions')
    args = parser.parse_args()

    kubernetes_configs = {}

    # read configurations +
    node_configs = file_io.read_configs(config_file=DEFAULT_CONFIG_FILE, exception=args.exception)
    if args.deployment_type == 'kubernetes':
        kubernetes_configs = file_io.read_configs(config_file=KUBERNETES_CONFIG_FILE, exception=args.exception)
    if args.config_file is not None:
        config_file = file_io.read_configs(config_file=args.config_file, exception=args.exception)
        node_configs = support.merge_configs(default_configs=node_configs, updated_configs=config_file)
        if args.deployment_type == 'kubernetes':
            kubernetes_configs = support.merge_configs(default_configs=kubernetes_configs, updated_configs=config_file)

    if args.config_file is None:
        node_configs, kubernetes_configs = support.prep_configs(node_type=args.node_type, node_configs=node_configs,
                                                                build=args.build, kubernetes_configs=kubernetes_configs)

    for section in node_configs:
        status = support.print_questions(node_configs[section])
        if status is True:
            if section not in ['operator', 'publisher', 'mqtt']:
                print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
            if section == 'general':
                node_configs['general'] = questionnaire.generic_questions(configs=node_configs[section])
                for param in ['LOCATION', 'COUNTRY', 'STATE', 'CITY']:
                    if node_configs['general'][param]['value'] == node_configs['general'][param]['default']:
                        node_configs['general'][param]['value'] = ""
            elif section == 'authentication':
                node_configs['authentication'] = questionnaire.authentication_questions(configs=node_configs[section])
            elif section == 'networking':
                node_configs[section] = questionnaire.networking_questions(configs=node_configs[section])
            elif section == 'database':
                node_configs[section] = questionnaire.database_questions(configs=node_configs[section])
            elif section == 'blockchain':
                if args.node_type in ['master', 'standalone', 'standalone-publisher', 'rest']:
                    node_configs['blockchain']['LEDGER_CONN']['default'] = f"127.0.0.1:{node_configs['networking']['ANYLOG_SERVER_PORT']['value']}"
                node_configs[section] = questionnaire.blockchain_questions(configs=node_configs[section])
            elif section == 'operator' and args.node_type in ['rest', 'operator', 'standalone']:
                print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                node_configs[section] = questionnaire.operator_questions(configs=node_configs[section])
            elif section == 'publisher' and args.node_type in ['rest', 'publisher', 'standalone-publisher']:
                print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                node_configs[section] = questionnaire.publisher_questions(configs=node_configs[section])
            elif section == 'mqtt' and (args.node_type in ['rest', 'operator', 'publisher', 'standalone',
                                                           'standalone-publisher'] or
                                        node_configs['networking']['ANYLOG_BROKER_PORT']['value'] != ''):
                print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                if args.config_file is None:
                    user = None
                    password = None
                    if 'AUTH_USER' in node_configs['authentication'] and node_configs['authentication']['AUTH_USER']['value'] != '':
                        user = node_configs['authentication']['AUTH_USER']['value'],
                    if 'AUTH_PASSWD' in node_configs['authentication'] and node_configs['authentication']['AUTH_PASSWD']['value'] != '':
                        password = node_configs['authentication']['AUTH_PASSWD']['value']
                    node_configs[section] = support.prepare_mqtt_params(configs=node_configs[section],
                                                                        db_name=node_configs['operator']['DEFAULT_DBMS']['value'],
                                                                        port=node_configs['networking']['ANYLOG_BROKER_PORT']['value'],
                                                                        user=user, password=password)
                node_configs[section] = questionnaire.mqtt_questions(configs=node_configs[section])
            elif section == 'advanced settings':
                node_configs[section] = questionnaire.advanced_settings(configs=node_configs[section])
            print('\n')

    if args.deployment_type == 'docker':
        file_io.write_configs(deployment_type=args.deployment_type, configs=node_configs, build=args.build,
                              kubernetes_configs=None, exception=args.exception)
    # elif args.deployment_type == 'kubernetes':
    #     kubernetes_configs = kubernetes_questionnaire.questionnaire(node_name=node_configs['general']['NODE_NAME']['value'],
    #                                                                 configs=kubernetes_configs)
    #
    #     # for local IP address use the service name rather than the generated IP
    #     if node_configs['networking']['LOCAL_IP']['value'] == "":
    #         node_configs['networking']['KUBERNETES_SERVICE_IP']['value'] = kubernetes_configs['metadata']['service_name']['value']
    #
    #     file_io.write_configs(deployment_type=args.deployment_type, configs=node_configs, build=args.build,
    #                           kubernetes_configs=kubernetes_configs, exception=args.exception)


if __name__ == '__main__':
    main()
