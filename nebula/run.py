import argparse
import os
import shutil
import time
import yaml


ORIG_CONFIG_FILE = os.path.join(os.path.dirname(os.path.expandvars(os.path.expanduser(__file__))), "config.yml")
if not os.path.isfile(ORIG_CONFIG_FILE):
    print(f"Failed to locate config file, cannot continue...")
    exit(1)
CONFIG_FILE = ORIG_CONFIG_FILE.replace('config.yml', 'node.yml')
shutil.copy(ORIG_CONFIG_FILE, CONFIG_FILE)


def __disable_overlay():
    """
    If script fails at any point then disable
    """
    try:
        os.system('export ENABLE_LIGHTHOUSE=hello')
    except Exception as error:
        print(f'Failed to disable lighthouse configs')
        raise

def __read_configs():
    """
    Read configuration file
    :return:
        content in configuration file
    """
    try:
        with open(CONFIG_FILE, 'r') as yml_file:
            try:
                return yaml.safe_load(yml_file)
            except Exception as error:
                print(f"Failed to read configs from {CONFIG_FILE} (Error: {error})")
                __disable_overlay()
    except Exception as error:
        print(f"Failed to open configs file {CONFIG_FILE} (Error: {error})")
        __disable_overlay()


def __static_host_map(lighthouse_ip:str, lighthouse_node_ip:str):
    """
    For non-lighthouse nebula nodes, set the static map values, if both lighthouse and lighthouse_node IPs are available
    :args:
        lighthouse_ip:str - Lighthouse Nebula IP address
        lighthouse_node_ip:str - Lighthouse Node IP address
    :return:
        list policy for configs, if fails prints error message
    """
    if not lighthouse_ip or not lighthouse_node_ip:
        print(f"Missing lighthouse IP or physical node IP, cannot configure Nebula overlay for a non-lighthouse node")
        __disable_overlay()
    return {lighthouse_ip: [{f'{lighthouse_node_ip}:4242'}]}

def __write_configs(configs:dict):
    try:
        with open(CONFIG_FILE, 'w') as yml_file:
            try:
                yaml.dump(configs, yml_file, default_flow_style=False, Dumper=yaml.Dumper)
            except Exception as error:
                print(f"Failed to write configs into {CONFIG_FILE} (Error: {error})")
                __disable_overlay()
    except Exception as error:
        print(f"Failed to open configs file {CONFIG_FILE} (Error:{error})")
        __disable_overlay()

def main():
    """
    Generate configuration file for nebula based on user input
    :args:

    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('anylog_root_path', type=str, default='$HOME', help='AnyLog ROOT path')
    parser.add_argument('tcp_port', type=int, default=32048, help='AnyLog TCP port')
    parser.add_argument('rest_port', type=int, default=32049, help='AnyLog REST port')
    parser.add_argument('--broker-port', type=int, default=None, help='AnyLog Broker port')
    parser.add_argument("--is-lighthouse", type=bool, nargs='?', default=False, const=True, help='whether node is of type Lighthouse or not')
    parser.add_argument('--lighthouse-ip', type=str, default=None, help='Lighthouse Nebula IP address')
    parser.add_argument('--lighthouse-node-ip', type=str, default=None, help='Lighthouse Node IP address')
    args = parser.parse_args()

    os.environ["ENABLE_LIGHTHOUSE"] = 'true'
    configs = __read_configs()
    args.anylog_root_path = os.path.expanduser(os.path.expandvars(args.anylog_root_path))

    configs['pki'] = {
        "ca": os.path.join(args.anylog_root_path, 'nebula', 'ca.crt'),
        'cert': os.path.join(args.anylog_root_path, 'nebula', 'ca.cert'),
        'key': os.path.join(args.anylog_root_path, 'nebula', 'host.key')
    }

    configs['lighthouse']['am_lighthouse'] = args.is_lighthouse
    if args.is_lighthouse is False:
        configs['static_host_map'] = __static_host_map(lighthouse_ip=args.lighthouse_ip, lighthouse_node_ip=args.lighthouse_node_ip)
        configs['lighthouse']['hosts'] = [args.lighthouse_ip]

    configs['firewall']['inbound'].append({
        'port': args.tcp_port,
        'proto': 'tcp',
        'host': 'any'
    })

    configs['firewall']['inbound'].append({
        'port': args.rest_port,
        'proto': 'tcp',
        'host': 'any'
    })

    if args.broker_port and args.broker_port != "":
        configs['firewall']['inbound'].append({
            'port': args.broker_port,
            'proto': 'tcp',
            'host': 'any'
        })

    __write_configs(configs=configs)
    __disable_overlay()



if __name__ == '__main__':
    main()

