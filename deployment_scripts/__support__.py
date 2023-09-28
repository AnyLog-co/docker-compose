import ipaddress

TRAINING_CONFIGS = {
    "master": ['LICENSE_KEY', 'NODE_TYPE', 'NODE_NAME', 'COMPANY_NAME', 'LEDGER_CONN', 'ANYLOG_SERVER_PORT',
               'ANYLOG_REST_PORT', 'MONITOR_NODES'],
    "operator": ['LICENSE_KEY', 'NODE_TYPE', 'NODE_NAME', 'COMPANY_NAME', 'LEDGER_CONN', 'ANYLOG_SERVER_PORT',
               'ANYLOG_REST_PORT', 'DEFAULT_DBMS', 'CLUSTER_NAME', 'ENABLE_MQTT', 'MONITOR_NODES'],
    "query": ['LICENSE_KEY', 'NODE_TYPE', 'NODE_NAME', 'COMPANY_NAME', 'LEDGER_CONN', 'ANYLOG_SERVER_PORT',
               'ANYLOG_REST_PORT', 'MONITOR_NODES'],
}

def prepare_configs(node_type:str, configs:dict, node_configs:list, anylog_configs:dict={}, advanced_configs:dict={},
                    is_training:bool=False)->dict:
    """
    Decide which configurations to enable / disable
    :global:
       TRAINING_CONFIGS:dict - enabled configuration for training based on node type
    :args:
        node_type:str - AnyLog Node type
        configs:dict - AnyLog configurations to enable / disable
        node_configs:list - node specific configurations
        is_training:bool - whether its training configurations
    :return:
        configs with enabled / disabled configss
    """
    for section in configs:
        for param in configs[section]:
            if param in anylog_configs:
                configs[section][param]['default'] = anylog_configs[param]
            elif param in advanced_configs:
                configs[section][param]['default'] = advanced_configs[param]
            if param == 'LOCAL_SCRIPTS' and is_training is True:
                configs[section][param]['default'] = '/app/deployment-scripts/training-deployment'
            elif param == 'NODE_TYPE':
                configs[section][param]['default'] = node_type
            elif is_training is True and param in TRAINING_CONFIGS[node_type]:
                configs[section][param]['enable'] = True
            elif is_training is False and param in node_configs:
                configs[section][param]['enable'] = True
            else:
                configs[section][param]['enable'] = False

    if node_type == 'master':
        configs['general']['NODE_NAME']['default'] = 'anylog-master'
        configs['networking']['ANYLOG_SERVER_PORT']['default'] = 32048
        configs['networking']['ANYLOG_REST_PORT']['default'] = 32049
    elif node_type == 'operator':
        configs['general']['NODE_NAME']['default'] = 'anylog-operator'
        configs['networking']['ANYLOG_SERVER_PORT']['default'] = 32148
        configs['networking']['ANYLOG_REST_PORT']['default'] = 32149
    elif node_type == 'query':
        configs['general']['NODE_NAME']['default'] = 'anylog-query'
        configs['networking']['ANYLOG_SERVER_PORT']['default'] = 32348
        configs['networking']['ANYLOG_REST_PORT']['default'] = 32349
    elif node_type == 'publisher':
        configs['general']['NODE_NAME']['default'] = 'anylog-query'
        configs['networking']['ANYLOG_SERVER_PORT']['default'] = 32248
        configs['networking']['ANYLOG_REST_PORT']['default'] = 32249

    if node_type in ['master', 'query']:
        del configs['operator']
        del configs['mqtt']
    if node_type == 'publisher':
        del configs['operator']

    return configs


def separate_configs(configs:dict)->(dict,dict):
    """
    Given the configurations, separate into either "required" or "advanced"
    :args:
        configs:dict - configurations
    :params:
        anylog_configs:dict - "required" configurations
        advanced_configs:dict - "non-required" configurations
    :return:
        anylog_configs, advanced_configs
    """
    anylog_configs = {}
    advanced_configs = {}
    import json
    for section in configs:
        for param in configs[section]:
            if param in ['LICENSE_KEY', 'NODE_TYPE']:
                if section not in anylog_configs:
                    anylog_configs[section] = {}
                anylog_configs[section][param] = {
                    "description": configs[section][param]['description'],
                    "value": configs[section][param]['value']
                }
            elif configs[section][param]['enable'] is True:
                if section not in anylog_configs:
                    anylog_configs[section] = {}

                anylog_configs[section][param] = {
                    "description": configs[section][param]['description'],
                    "value": configs[section][param]["value"]
                }
                if all(configs[section][param][x] == "" for x in ['value', 'default']):
                    anylog_configs[section][param]["value"] = '""'
                elif configs[section][param]["value"] == "":
                    anylog_configs[section][param]["value"] = configs[section][param]["default"]
            else:
                if section not in advanced_configs:
                    advanced_configs[section] = {}

                advanced_configs[section][param] = {
                    "description": configs[section][param]['description'],
                    "value": configs[section][param]["value"]
                }
                if all(configs[section][param][x] == "" for x in ['value', 'default']):
                    advanced_configs[section][param]["value"] = '""'
                elif configs[section][param]["value"] == "":
                    advanced_configs[section][param]["value"] = configs[section][param]["default"]

    return anylog_configs, advanced_configs



def prepare_configs_dotenv(configs:dict)->str:
    content = ""
    for section in configs:
        if section == 'mqtt':
            content += "#--- MQTT ---\n"
        else:
            content += f"#--- {section.title()} ---\n"
        for param in configs[section]:
            content += f"# {configs[section][param]['description']}\n"
            content += f"{param}={configs[section][param]['value']}\n"
        content += "\n"

    return content


def print_questions(configs:dict)->bool:
    """
    Whether to print question
    :args:
        configs:dict - configuration
    :param:
        status:bool
    :return:
        if one or more of the config params is enabled return True, else returns False
    """
    for param in configs:
        if configs[param]['enable'] is True:
            return True
    return False

def generate_question(param:str, configs:dict)->str:
    """
    Generate question
    :args:
        configs:dict - configuration information
    :params:
        question:str - question based on configs
    :return:
        question
    """
    params = ""
    if 'default' in configs and configs['default'] != "":
        if params == "":
            params += "["
        default_value = configs['default']
        if param == 'LICENSE_KEY':
            start = default_value[:10]
            end = default_value[-26:]
            default_value=f"{start}...{end}"
        params += f"default: {default_value}"
    if 'options' in configs:
        if params == "":
            params += "["
        else:
            params += " | "
        params += f"options: {', '.join(configs['options'])}"
    if 'range' in configs:
        if params == "":
            params += "["
        else:
            params += " | "
        params += f"range: {'-'.join(map(str, configs['range']))}"

    if params != "":
        question = f"{configs['question']} {params}]: "
    else:
        question = f"{configs['question']}: "
    return question


def ask_question(question:str, description:str, param:str="", error_msg:str="")->str:
    """
    ask question
    :args:
        question:str - question to ask
        description:str - issue description
    :params:
        user_input:str - user input
    :return:
        user_input
    """
    status = False
    while status is False:
        user_input = input(f"\t{error_msg} {question}")
        if user_input == 'help':
            error_msg = ""
            print(f"\t`{param}` param description - {description}")
        else:
            status = True

    return user_input.strip()


def validate_ipaddress(address:str)->(str, str):
    """
    Validate if IP address is correct - used for Proxy and Overlay IP
    :args:
        address:str - addrress to check
    :params:
        error_msg:str - error_msg
    :return:
        address, error_msg
    """
    error_msg = ""
    try:
        ipaddress.ip_address(address)
    except Exception:
        try:
            ipaddress.ip_network(address)
        except Exception:
            error_msg = "Invalid IP address. Please try again..."

    return address, error_msg
