import argparse
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

NODE_TYPES = ['none', 'generic', 'master', 'operator', 'publisher', 'query', 'standalone', 'standalone-publisher']


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
    parser.add_argument('--build', type=str, choices=['latest', 'predevelop', 'test'], default='latest',
                        help='Which AnyLog version to run')
    parser.add_argument('--deployment-type', type=str, choices=['docker', 'kubernetes'], default='docker',
                        help='Deployment type - docker generates .env file, kubernetes generates YAML file')
    parser.add_argument('--config-file', type=str, default=None, help='Configuration file to use for default values')
    parser.add_argument('--demo-build', type=bool, default=False, nargs='?', const=True, help='Only basic questions, used for demo purposes')
    parser.add_argument('-e', '--exception', type=bool, default=False, nargs='?', const=True, help='Whether to print exceptions')
    args = parser.parse_args()

    # if user declares "generic" node type then we'll deploy a REST node
    if args.node_type == "generic":
        args.node_type = "rest"

    kubernetes_configs = {}

    # read configurations +
    node_configs = file_io.read_configs(config_file=DEFAULT_CONFIG_FILE, exception=args.exception)
    if args.deployment_type == 'kubernetes':
        kubernetes_configs = file_io.read_configs(config_file=KUBERNETES_CONFIG_FILE, exception=args.exception)
    else:
        node_configs['networking'].pop('KUBERNETES_SERVICE_IP')
    if args.config_file is not None:
        config_file = file_io.read_configs(config_file=args.config_file, exception=args.exception)
        node_configs = support.merge_configs(default_configs=node_configs, updated_configs=config_file)
        if args.deployment_type == 'kubernetes':
            kubernetes_configs = support.merge_configs(default_configs=kubernetes_configs, updated_configs=config_file)

    if args.config_file is None:
        node_configs, kubernetes_configs = support.prep_configs(node_type=args.node_type, node_configs=node_configs,
                                                                build=args.build, kubernetes_configs=kubernetes_configs)

    if args.demo_build is True:
        for section in node_configs:
            for param in node_configs[section]:
                if param not in ["LICENSE_KEY", "COMPANY_NAME", "LEDGER_CONN", "CLUSTER_NAME", "MONITOR_NODES",
                                 "MONITOR_NODE_COMPANY", "ENABLE_MQTT"]:
                    node_configs[section][param]["enable"] = False
                    node_configs[section][param]["value"] = node_configs[section][param]["default"]
                    if param in ['LOCATION', 'COUNTRY', 'STATE', 'CITY']:
                        node_configs[section][param]['default'] = ''
                        node_configs[section][param]['value'] = ''
                    elif param == "NODE_NAME" and args.node_type == 'operator':
                        operator_value = questionnaire.operator_number()
                        node_configs[section][param]['default'] = f"{node_configs[section][param]['default']}{operator_value}"
                elif param == "MONITOR_NODES":
                    node_configs[section][param]["default"] = "true"
                    node_configs[section][param]["enable"] = False

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
                print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                node_configs['blockchain']['LEDGER_CONN']['default'] = f"127.0.0.1:{node_configs['networking']['ANYLOG_SERVER_PORT']['value']}"
                node_configs[section] = questionnaire.blockchain_section(configs=node_configs[section])
            elif section == 'operator' and args.node_type in ['rest', 'operator', 'standalone']:
                print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                node_configs[section] = questionnaire.operator_section(configs=node_configs[section])
            elif section == 'publisher' and args.node_type in ['rest', 'publisher', 'standalone-publisher']:
                print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                node_configs[section] = questionnaire.generic_section(configs=node_configs[section])
            elif section == 'mqtt' and (args.node_type in ['rest', 'operator', 'publisher', 'standalone', 'standalone-publisher'] or node_configs['networking']['ANYLOG_BROKER_PORT']['value'] != ''):
                print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                node_configs[section] = questionnaire.generic_section(configs=node_configs[section])
            else:
                print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
                node_configs[section] = questionnaire.generic_section(configs=node_configs[section])
                if section == "general" and args.demo_build is True:
                    node_configs["advanced settings"]["MONITOR_NODE_COMPANY"]["value"] = node_configs["general"]["COMPANY_NAME"]["value"]
                    node_configs["advanced settings"]["MONITOR_NODE_COMPANY"]["enable"] = False
            print('\n')

    if args.deployment_type == 'docker':
        # del node_configs['networking']['KUBERNETES_SERVICE_IP']
        file_io.write_configs(deployment_type=args.deployment_type, configs=node_configs, build=args.build,
                              kubernetes_configs=None, exception=args.exception)
    elif args.deployment_type == 'kubernetes':
        kubernetes_configs = kubernetes_questionnaire.questionnaire(node_name=node_configs['general']['NODE_NAME']['value'],
                                                                    configs=kubernetes_configs)

        # for local IP address use the service name rather than the generated IP
        if node_configs['networking']['LOCAL_IP']['value'] == "":
            node_configs['networking']['KUBERNETES_SERVICE_IP']['value'] = kubernetes_configs['metadata']['service_name']['value']

        file_io.write_configs(deployment_type=args.deployment_type, configs=node_configs, build=args.build,
                              kubernetes_configs=kubernetes_configs, exception=args.exception)


if __name__ == '__main__':
    main()
