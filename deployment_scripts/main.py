import argparse
import os

import support
import questionnaire

ROOT_PATH = os.path.expandvars(os.path.expanduser(__file__)).split('deployment_scripts')[0]
DEFAULT_CONFIG_FILE = os.path.join(ROOT_PATH, 'deployment_scripts', 'configuration', 'configurations.json')
NODE_TYPES = ['node', 'rest', 'master', 'operator', 'publisher,', 'query', 'standalone', 'standalone-publisher']


def main():
    """
    :params:
        config_file:dict - content from configuration file
        configs:dict - removed un-needed configurations
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('node_type', type=str, choices=NODE_TYPES, default='rest', help='Node type to deploy')
    parser.add_argument('--config-file', type=str, default=DEFAULT_CONFIG_FILE,
                        help='JSON file to get configurations from')
    args = parser.parse_args()
    config_file = support.json_read_file(file_name=args.config_file)
    configs = support.clean_configs(node_type=args.node_type, configs=config_file)
    for section in configs:
        print(f'Section: {section.title().replace("Sql", "SQL")}')
        if section == 'general':
            configs['general'] = questionnaire.generic_param_questions(configs=configs[section])
        elif section == 'networking':
            configs[section] = questionnaire.networking_questions(configs=configs[section])
            rest_info, broker_info = questionnaire.validate_ports(tcp_port=configs[section]['ANYLOG_SERVER_PORT']['value'],
                                                                      rest_info=configs[section]['ANYLOG_REST_PORT'],
                                                                      broker_info=configs[section]['ANYLOG_BROKER_PORT']
                                                                      )
            configs[section]['ANYLOG_REST_PORT'] = rest_info
            configs[section]['ANYLOG_BROKER_PORT'] = broker_info
        elif 'database' in section: 
            configs[section] = questionnaire.questions(configs=configs[section])
        elif 







if __name__ == '__main__':
    main()