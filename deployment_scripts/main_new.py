import argparse
import os
import support
import kubernetes_questionnaire
import questionnaire
import file_io

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
    parser.add_argument('--build', type=str, choices=['latest', 'beta'], default='latest',
                        help='Which AnyLog version to run')
    parser.add_argument('--deployment-type', type=str, choices=['docker', 'kubernetes'], default='docker',
                        help='Deployment type - docker generates .env file, kubernetes generates YAML file')
    parser.add_argument('--config-file', type=str, default=None, help='Configuration file to use for default values')
    parser.add_argument('--demo-build', type=bool, default=False, nargs='?', const=True, help='Only basic questions, used for demo purposes')
    parser.add_argument('-e', '--exception', type=bool, default=False, nargs='?', const=True, help='Whether to print exceptions')
    args = parser.parse_args()



if __name__ == '__main__':
    main()
