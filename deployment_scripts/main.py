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
    if len(configs) == "":
        print('Empty configurations, cannot continue...')
        exit(1)
    else:
        print('Welcome to AnyLog configurations tool, type `help` to get details about a parameter')
    for section in configs:
        print(f'Section: {section.title().replace("Sql", "SQL")}')
        if section == 'general':
            configs['general'] = questionnaire.generic_questions(configs=configs[section])
        elif section == 'networking':
            configs[section] = questionnaire.networking_questions(configs=configs[section])
        elif section == 'database':
            configs[section] = questionnaire.database_questions(configs=configs[section])
        elif section == 'blockchain':
            configs[section] = questionnaire.database_questions(configs=configs[section])
        elif section == 'operator':
            configs[section] = questionnaire.operator_questions(configs=configs[section])
        elif section == 'publisher':
            configs[section] = questionnaire.publisher_questions(configs=configs[section])
        # we need to enable authentication code within deployment scripts
        # elif param == 'authentication':
        #     configs[section] = questionnaire.authentication_questions(configs=configs[section])
        print('\n')







if __name__ == '__main__':
    main()