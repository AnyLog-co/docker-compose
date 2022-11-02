import argparse
import os

import support
import questionnaire
import write_file

ROOT_PATH = os.path.expandvars(os.path.expanduser(__file__)).split('deployment_scripts')[0]
DEFAULT_CONFIG_FILE = os.path.join(ROOT_PATH, 'deployment_scripts', 'configuration', 'configurations.json')


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
        --config-file   CONFIG_FILE     JSON file to get configurations from
            * develop
            * predevelop
            * test
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
    parser.add_argument('--config-file', type=str, default=DEFAULT_CONFIG_FILE,
                        help='JSON file to get configurations from')
    args = parser.parse_args()

    # read configuration file
    config_file = support.json_read_file(file_name=args.config_file)
    configs = support.clean_configs(node_type=args.node_type, configs=config_file)
    if len(configs) == "":
        print('Empty configurations, cannot continue...')
        exit(1)
    else:
        print('Welcome to AnyLog configurations tool, type `help` to get details about a parameter')

    # iterate through configurations and get user input
    for section in configs:
        status = support.print_questions(configs[section])
        if status is True or section in ['general', 'networking', 'database']:
            print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
            if section == 'general':
                configs['general'] = questionnaire.generic_questions(configs=configs[section])
            elif section == 'networking':
                configs[section] = questionnaire.networking_questions(configs=configs[section])
            elif section == 'database':
                configs[section] = questionnaire.database_questions(configs=configs[section])
            elif section == 'blockchain':
                configs[section] = questionnaire.blockchain_questions(configs=configs[section])
            elif section == 'operator':
                configs[section] = questionnaire.operator_questions(configs=configs[section])
            elif section == 'publisher':
                configs[section] = questionnaire.publisher_questions(configs=configs[section])
            # we need to enable authentication code within deployment scripts
            # elif param == 'authentication':
            #     configs[section] = questionnaire.authentication_questions(configs=configs[section])
            elif section == 'mqtt':
                configs[section] = support.prepare_mqtt_params(configs=configs[section],
                                                               db_name=configs['operator']['DEFAULT_DBMS']['value'],
                                                               port=configs['networking']['ANYLOG_BROKER_PORT']['value'],
                                                               user=configs['authentication']['AUTH_USER']['value'],
                                                               password=configs['authentication']['AUTH_PASSWD']['value'])

                configs[section] = questionnaire.mqtt_questions(configs=configs[section])
            elif section == 'advanced settings':
                configs[section] = questionnaire.advanced_settings(configs=configs[section])
            print('\n')

        if args.deployment_type == 'docker':
            write_file.write_docker_configs(node_type=args.node_type, configs=configs)
            write_file.update_build_version(node_type=args.node_type,
                                            container_name=configs['general']['NODE_NAME']['value'],
                                            build=args.build)


if __name__ == '__main__':
    main()