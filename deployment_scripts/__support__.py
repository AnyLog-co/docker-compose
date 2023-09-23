TRAINING_CONFIGS = {
    "master": ['LICENSE_KEY', 'NODE_TYPE', 'NODE_NAME', 'COMPANY_NAME', 'LEDGER_CONN', 'ANYLOG_SERVER_PORT',
               'ANYLOG_REST_PORT'],
    "operator": ['LICENSE_KEY', 'NODE_TYPE', 'NODE_NAME', 'COMPANY_NAME', 'LEDGER_CONN', 'ANYLOG_SERVER_PORT',
               'ANYLOG_REST_PORT', 'ANYLOG_REST_PORT', 'ANYLOG_BROKER_PORT',
                 'DEFAULT_DBMS', 'CLUSTER_NAME', 'ENABLE_MQTT'],
    "query": ['LICENSE_KEY', 'NODE_TYPE', 'NODE_NAME', 'COMPANY_NAME', 'LEDGER_CONN', 'ANYLOG_SERVER_PORT',
               'ANYLOG_REST_PORT', 'ENABLE_MQTT'],
}

def prepare_configs(node_type:str, configs:dict, node_configs:list, is_training:bool=False)->dict:
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
    if is_training is True:
        node_configs = TRAINING_CONFIGS[node_type]

    for section in configs:
        for param in configs[section]:
            if param == 'LOCAL_SCRIPTS' and is_training is True:
                configs[section][param]['default'] = '/app/deployment-scripts/training-deployment'
            if param == 'NODE_TYPE':
                configs[section][param]['default'] = node_type
            elif param not in node_configs:
                configs[section][param]['enable'] = False

    return configs


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