import argparse
import os

from __file_io__ import is_file, read_config_file
from __support__ import prepare_configs, print_questions
from questionnaire import section_general, section_networking, section_blockchain

NODE_TYPES = {
    "generic": ['LICENSE_KEY', 'NODE_TYPE', 'NODE_NAME', 'COMPANY_NAME', 'LOCATION', 'COUNTRY', 'STATE', 'CITY',
                'CONFIG_NAME', 'OVERLAY_IP', 'PROXY_IP', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'ANYLOG_BROKER_PORT',
                'TCP_BIND', 'TCP_THREADS', 'REST_BIND', 'REST_TIMEOUT', 'REST_THREADS', 'BROKER_BIND', 'BROKER_THREADS',
                'DB_TYPE', 'DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT', 'AUTOCOMMIT', 'SYSTEM_QUERY', 'MEMORY',
                'NOSQL_ENABLE', 'NOSQL_TYPE', 'NOSQL_USER', 'NOSQL_PASSWD', 'NOSQL_IP', 'NOSQL_PORT', 'BLOBS_DBMS',
                'BLOBS_REUSE', 'LEDGER_CONN', 'SYNC_TIME', 'BLOCKCHAIN_SOURCE', 'BLOCKCHAIN_DESTINATION', 'MEMBER',
                'CLUSTER_NAME', 'DEFAULT_DBMS', 'ENABLE_HA', 'START_DATE', 'ENABLE_PARTITIONS', 'TABLE_NAME',
                'PARTITION_COLUMN', 'PARTITION_INTERVAL', 'PARTITION_KEEP', 'PARTITION_SYNC', 'COMPRESS_FILE',
                'OPERATOR_THREADS', 'ENABLE_MQTT', 'MQTT_LOG', 'MQTT_BROKER', 'MQTT_PORT', 'MQTT_USER', 'MQTT_PASSWD',
                'MQTT_TOPIC', 'MQTT_DBMS', 'MQTT_TABLE', 'MQTT_TIMESTAMP_COLUMN', 'MQTT_VALUE_COLUMN',
                'MQTT_VALUE_COLUMN_TYPE', 'DEPLOY_LOCAL_SCRIPT', 'QUERY_POOL', 'WRITE_IMMEDIATE', 'THRESHOLD_TIME',
                'THRESHOLD_VOLUME', 'MONITOR_NODES', 'MONITOR_NODE', 'MONITOR_NODE_COMPANY'],
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
                'NOSQL_ENABLE', 'NOSQL_TYPE', 'NOSQL_USER', 'NOSQL_PASSWD', 'NOSQL_IP', 'NOSQL_PORT', 'BLOBS_DBMS',
                'BLOBS_REUSE', 'LEDGER_CONN', 'SYNC_TIME', 'BLOCKCHAIN_SOURCE', 'BLOCKCHAIN_DESTINATION', 'MEMBER',
                'CLUSTER_NAME', 'DEFAULT_DBMS', 'ENABLE_HA', 'START_DATE', 'ENABLE_PARTITIONS', 'TABLE_NAME',
                'PARTITION_COLUMN', 'PARTITION_INTERVAL', 'PARTITION_KEEP', 'PARTITION_SYNC', 'COMPRESS_FILE',
                'OPERATOR_THREADS', 'ENABLE_MQTT', 'MQTT_LOG', 'MQTT_BROKER', 'MQTT_PORT', 'MQTT_USER', 'MQTT_PASSWD',
                'MQTT_TOPIC', 'MQTT_DBMS', 'MQTT_TABLE', 'MQTT_TIMESTAMP_COLUMN', 'MQTT_VALUE_COLUMN',
                'MQTT_VALUE_COLUMN_TYPE', 'DEPLOY_LOCAL_SCRIPT', 'QUERY_POOL', 'WRITE_IMMEDIATE', 'THRESHOLD_TIME',
                'THRESHOLD_VOLUME', 'MONITOR_NODES', 'MONITOR_NODE', 'MONITOR_NODE_COMPANY'],
    "publisher": ['LICENSE_KEY', 'NODE_TYPE', 'NODE_NAME', 'COMPANY_NAME', 'LOCATION', 'COUNTRY', 'STATE', 'CITY',
                'CONFIG_NAME', 'OVERLAY_IP', 'PROXY_IP', 'ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'ANYLOG_BROKER_PORT',
                'TCP_BIND', 'TCP_THREADS', 'REST_BIND', 'REST_TIMEOUT', 'REST_THREADS', 'BROKER_BIND', 'BROKER_THREADS',
                'DB_TYPE', 'DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT', 'AUTOCOMMIT', 'SYSTEM_QUERY', 'MEMORY',
                'LEDGER_CONN', 'SYNC_TIME', 'BLOCKCHAIN_SOURCE', 'BLOCKCHAIN_DESTINATION',
                'COMPRESS_FILE', 'ENABLE_MQTT', 'MQTT_LOG', 'MQTT_BROKER', 'MQTT_PORT', 'MQTT_USER', 'MQTT_PASSWD',
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
    k8s_config_file_data = read_config_file(file_path=args.k8s_config, exception=args.exception)

    config_file_data = prepare_configs(node_type=args.node_type, configs=config_file_data,
                                       node_configs=NODE_TYPES[args.node_type], is_training=args.training)

    for section in config_file_data:
        status = print_questions(config_file_data[section])
        if status is True:
            print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
            if section == 'general':
                config_file_data[section] = section_general(configs=config_file_data[section])
            if section == 'networking':
                config_file_data[section] = section_networking(configs=config_file_data[section])
            if section == 'blockchain':
                config_file_data[section] = section_blockchain(configs=config_file_data[section])


if __name__ == '__main__':
    main()

