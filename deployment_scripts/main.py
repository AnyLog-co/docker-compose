import argparse
import os

from __file_io__ import is_file, read_config_file, copy_file, write_file, write_dotenv_file
from __support__ import prepare_configs, print_questions, separate_configs, prepare_configs_dotenv
from questionnaire import section_general, section_networking, section_database, section_operator, section_blockchain, section_monitoring, section_mqtt, section_advanced_settings

NODE_TYPES = {
    "generic": ['LICENSE_KEY', 'NODE_TYPE', 'NODE_NAME', 'COMPANY_NAME', 'LOCATION', 'COUNTRY', 'STATE', 'CITY',
                'CONFIG_NAME', 'OVERLAY_IP', 'PROXY_IP', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'ANYLOG_BROKER_PORT',
                'TCP_BIND', 'TCP_THREADS', 'REST_BIND', 'REST_TIMEOUT', 'REST_THREADS', 'BROKER_BIND', 'BROKER_THREADS',
                'DB_TYPE', 'DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT', 'AUTOCOMMIT', 'SYSTEM_QUERY', 'MEMORY',
                'ENABLE_NOSQL', 'NOSQL_USER', 'NOSQL_PASSWD', 'NOSQL_IP', 'NOSQL_PORT',  'LEDGER_CONN', 
                'SYNC_TIME', 'BLOCKCHAIN_SOURCE', 'BLOCKCHAIN_DESTINATION', 'CLUSTER_NAME', 'DEFAULT_DBMS',
                'ENABLE_HA', 'START_DATE', 'ENABLE_PARTITIONS', 'TABLE_NAME', 'PARTITION_COLUMN', 'PARTITION_INTERVAL', 
                'PARTITION_KEEP', 'PARTITION_SYNC', 'COMPRESS_FILE', 'OPERATOR_THREADS', 'ENABLE_MQTT', 'MQTT_BROKER',
                'MQTT_PORT', 'MQTT_USER', 'MQTT_PASSWD', 'MQTT_TOPIC', 'MQTT_DBMS', 'MQTT_TABLE',
                'MQTT_TIMESTAMP_COLUMN', 'MQTT_VALUE_COLUMN', 'MQTT_VALUE_COLUMN_TYPE', 'DEPLOY_LOCAL_SCRIPT',
                'QUERY_POOL', 'WRITE_IMMEDIATE', 'THRESHOLD_TIME', 'THRESHOLD_VOLUME', 'MONITOR_NODES', 'MONITOR_NODE',
                'MONITOR_NODE_COMPANY'],
    "master": ['LICENSE_KEY', 'NODE_TYPE', 'NODE_NAME', 'COMPANY_NAME', 'LOCATION', 'COUNTRY', 'STATE', 'CITY',
               'CONFIG_NAME', 'OVERLAY_IP', 'PROXY_IP', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT',
               'TCP_BIND', 'TCP_THREADS', 'REST_BIND', 'REST_TIMEOUT', 'REST_THREADS',  'DB_TYPE', 'DB_USER',
               'DB_PASSWD', 'DB_IP', 'DB_PORT', 'AUTOCOMMIT', 'SYSTEM_QUERY', 'MEMORY',
               'LEDGER_CONN', 'SYNC_TIME', 'BLOCKCHAIN_SOURCE', 'BLOCKCHAIN_DESTINATION',
               'DEPLOY_LOCAL_SCRIPT', 'QUERY_POOL', 'WRITE_IMMEDIATE', 'MONITOR_NODES', 'MONITOR_NODE',
               'MONITOR_NODE_COMPANY'],
    "operator": ['LICENSE_KEY', 'NODE_TYPE', 'NODE_NAME', 'COMPANY_NAME', 'LOCATION', 'COUNTRY', 'STATE', 'CITY',
                'CONFIG_NAME', 'OVERLAY_IP', 'PROXY_IP', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'ANYLOG_BROKER_PORT',
                'TCP_BIND', 'TCP_THREADS', 'REST_BIND', 'REST_TIMEOUT', 'REST_THREADS', 'BROKER_BIND', 'BROKER_THREADS',
                'DB_TYPE', 'DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT', 'AUTOCOMMIT', 'SYSTEM_QUERY', 'MEMORY',
                'ENABLE_NOSQL', 'NOSQL_TYPE', 'NOSQL_USER', 'NOSQL_PASSWD', 'NOSQL_IP', 'NOSQL_PORT', 
                 'LEDGER_CONN', 'SYNC_TIME', 'BLOCKCHAIN_SOURCE', 'BLOCKCHAIN_DESTINATION',
                'CLUSTER_NAME', 'DEFAULT_DBMS', 'ENABLE_HA', 'START_DATE', 'ENABLE_PARTITIONS', 'TABLE_NAME',
                'PARTITION_COLUMN', 'PARTITION_INTERVAL', 'PARTITION_KEEP', 'PARTITION_SYNC', 'COMPRESS_FILE',
                'OPERATOR_THREADS', 'ENABLE_MQTT',  'MQTT_BROKER', 'MQTT_PORT', 'MQTT_USER', 'MQTT_PASSWD',
                'MQTT_TOPIC', 'MQTT_DBMS', 'MQTT_TABLE', 'MQTT_TIMESTAMP_COLUMN', 'MQTT_VALUE_COLUMN',
                'MQTT_VALUE_COLUMN_TYPE', 'DEPLOY_LOCAL_SCRIPT', 'QUERY_POOL', 'WRITE_IMMEDIATE', 'THRESHOLD_TIME',
                'THRESHOLD_VOLUME', 'MONITOR_NODES', 'MONITOR_NODE', 'MONITOR_NODE_COMPANY'],
    "publisher": ['LICENSE_KEY', 'NODE_TYPE', 'NODE_NAME', 'COMPANY_NAME', 'LOCATION', 'COUNTRY', 'STATE', 'CITY',
                  'CONFIG_NAME', 'OVERLAY_IP', 'PROXY_IP', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'ANYLOG_BROKER_PORT',
                  'TCP_BIND', 'TCP_THREADS', 'REST_BIND', 'REST_TIMEOUT', 'REST_THREADS', 'BROKER_BIND', 'BROKER_THREADS',
                  'DB_TYPE', 'DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT', 'AUTOCOMMIT', 'SYSTEM_QUERY', 'MEMORY',
                  'LEDGER_CONN', 'SYNC_TIME', 'BLOCKCHAIN_SOURCE', 'BLOCKCHAIN_DESTINATION', 'COMPRESS_FILE',
                  'ENABLE_MQTT',  'MQTT_BROKER', 'MQTT_PORT', 'MQTT_USER', 'MQTT_PASSWD',
                  'MQTT_TOPIC', 'MQTT_DBMS', 'MQTT_TABLE', 'MQTT_TIMESTAMP_COLUMN', 'MQTT_VALUE_COLUMN',
                  'MQTT_VALUE_COLUMN_TYPE', 'DEPLOY_LOCAL_SCRIPT', 'QUERY_POOL', 'WRITE_IMMEDIATE', 'THRESHOLD_TIME',
                  'THRESHOLD_VOLUME', 'MONITOR_NODES', 'MONITOR_NODE', 'MONITOR_NODE_COMPANY'],
    "query": ['LICENSE_KEY', 'NODE_TYPE', 'NODE_NAME', 'COMPANY_NAME', 'LOCATION', 'COUNTRY', 'STATE', 'CITY',
               'CONFIG_NAME', 'OVERLAY_IP', 'PROXY_IP', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT',
               'TCP_BIND', 'TCP_THREADS', 'REST_BIND', 'REST_TIMEOUT', 'REST_THREADS',  'DB_TYPE', 'DB_USER',
               'DB_PASSWD', 'DB_IP', 'DB_PORT', 'AUTOCOMMIT', 'SYSTEM_QUERY', 'MEMORY',
               'LEDGER_CONN', 'SYNC_TIME', 'BLOCKCHAIN_SOURCE', 'BLOCKCHAIN_DESTINATION',
               'DEPLOY_LOCAL_SCRIPT', 'QUERY_POOL', 'WRITE_IMMEDIATE', 'MONITOR_NODES', 'MONITOR_NODE',
               'MONITOR_NODE_COMPANY']
}

ROOT_DIR = os.path.dirname(os.path.abspath(os.path.expandvars(os.path.expanduser(__file__))))
CONFIG_FILE = os.path.join(ROOT_DIR, 'configurations.json')
K8S_CONFIG = os.path.join(ROOT_DIR, 'kubernetes_configurations.json')

def main():
    """
    Main for configuring an AnyLog node
    :global:
        CONFIG_FILE:str - default configuration file path
        K8S_CONFIG:str - default kubernetes configuration file path
    :positional arguments:
        node_type       Node type to deploy
            * generic - no specific node type, but does start network services
            * master
            * operator
            * publisher
            * query
    :optional arguments:
        -h, --help      show this help message and exit
        --build         Which AnyLog version to run
            * latest [default]
            * beta
        --deployment-type   Deployment type - docker generates .env file, kubernetes generates YAML file
            * docker [default]
            * kubernetes
        --config-file       Configuration file to use for default values
        --k8s-config        Configuration file to use for Kubernetes
        --training          Run in training mode
        -e, --exception     Whether to print exceptions
    :params:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('node_type', type=str, choices=NODE_TYPES, default='generic', help='Node type to deploy')
    parser.add_argument('--build', type=str, choices=['latest', 'beta'], default='latest', help='Which AnyLog version to run')
    parser.add_argument('--deployment-type', type=str, choices=['docker', 'kubernetes'], default='docker', help='Deployment type - docker generates .env file, kubernetes generates YAML file')
    parser.add_argument('--config-file', type=is_file, default=CONFIG_FILE, help='Configuration file to use for default values')
    parser.add_argument('--k8s-config', type=is_file, default=K8S_CONFIG, help='Configuration file to use for Kubernetes')
    parser.add_argument('--training', type=bool, nargs='?', const=True, default=False, help='Run in training mode')
    parser.add_argument('-e', '--exception', type=bool, default=False, nargs='?', const=True, help='Whether to print exceptions')
    args = parser.parse_args()

    if args.training is True and args.node_type not in ['master', 'query', 'operator']:
        print(f"Unsupported training for {args.node_type} at this time...")
        exit(1)

    config_file_data = read_config_file(file_path=args.config_file, exception=args.exception)
    # k8s_config_file_data = read_config_file(file_path=args.k8s_config, exception=args.exception)
    anylog_configs = {}
    advanced_configs = {}

    if args.deployment_type == 'docker':
        dir_path = os.path.join(ROOT_DIR.split('deployment_scripts')[0], 'docker-compose', f'anylog-{args.node_type}')
        anylog_file_configs = os.path.join(dir_path, 'anylog_configs.env')
        advance_file_configs = os.path.join(dir_path, 'advance_configs.env')
        dotenv_file = os.path.join(dir_path, '.env')

        if is_file(file_path=anylog_file_configs, is_argparse=False, exception=args.exception) is not None:
            anylog_configs = read_config_file(file_path=anylog_file_configs, exception=args.exception)
        if is_file(file_path=advance_file_configs, is_argparse=False, exception=args.exception) is not None:
            advanced_configs = read_config_file(file_path=advance_file_configs, exception=args.exception)

    config_file_data = prepare_configs(node_type=args.node_type, configs=config_file_data, node_configs=NODE_TYPES[args.node_type],
                                       anylog_configs=anylog_configs, advanced_configs=advanced_configs, is_training=args.training)

    rest_port = config_file_data['networking']['ANYLOG_REST_PORT']['value']
    broker_port = None

    for section in config_file_data:
        status = print_questions(config_file_data[section])
        if status is True:
            print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
            if section == 'general':
                config_file_data[section] = section_general(configs=config_file_data[section])
            elif section == 'networking':
                config_file_data[section] = section_networking(configs=config_file_data[section])
                rest_port = config_file_data[section]['ANYLOG_REST_PORT']['value']
                if config_file_data[section]['ANYLOG_BROKER_PORT']['value'] != "":
                    broker_port = config_file_data[section]['ANYLOG_BROKER_PORT']['value']
            elif section == 'database':
                if args.node_type not in ['generic', 'operator']:
                    config_file_data[section]['ENABLE_NOSQL']['value'] = 'false'
                    config_file_data[section]['ENABLE_NOSQL']['enable'] = False
                config_file_data[section] = section_database(configs=config_file_data[section])
            elif section == 'operator' and args.node_type in ['generic', 'operator']:
                company_name = config_file_data['general']['COMPANY_NAME']['value'].lower().replace(' ', '-')
                config_file_data[section] = section_operator(company_name=company_name, configs=config_file_data[section], is_training=args.training)
            elif section == 'blockchain':
                config_file_data[section] = section_blockchain(configs=config_file_data[section])
            elif section == 'mqtt' and args.node_type in ['generic', 'operator', 'publisher']:
                config_file_data[section] = section_mqtt(configs=config_file_data[section], rest_port=rest_port, broker_port=broker_port)
            elif section == 'monitoring':
                config_file_data[section]['MONITOR_NODE_COMPANY']['default'] = config_file_data['general']['COMPANY_NAME']['value']
                config_file_data[section] = section_monitoring(configs=config_file_data[section])
            elif section == 'advanced settings':
                config_file_data[section] = section_advanced_settings(configs=config_file_data[section])
            print("\n")

    if args.deployment_type == 'docker':
        anylog_configs, advanced_configs = separate_configs(configs=config_file_data)
        if is_file(file_path=anylog_file_configs, is_argparse=False, exception=args.exception) is not None:
            copy_file(file_path=anylog_file_configs, exception=args.exception)
        if is_file(file_path=advance_file_configs, is_argparse=False, exception=args.exception) is not None:
            copy_file(file_path=advance_file_configs, exception=args.exception)

        write_file(file_path=anylog_file_configs, content=prepare_configs_dotenv(configs=anylog_configs), exception=args.exception)
        write_file(file_path=advance_file_configs, content=prepare_configs_dotenv(configs=advanced_configs), exception=args.exception)
        write_dotenv_file(file_path=dotenv_file, node_type=args.node_type, build=args.build,
                          node_name=config_file_data['general']['NODE_NAME']['value'], is_trainig=args.training,
                          exception=args.exception)

if __name__ == '__main__':
    main()

