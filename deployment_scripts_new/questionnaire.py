import ast
import re

from __support__ import validate_ports, validate_ips, validate_ledger

def __generate_question(config_question:str, config_default=None, config_options=None, config_rng=None)->str:
    question = config_question
    default = ""
    options = ""
    rng = ""
    params = " "
    if config_default is not None:
        default = f"default: {config_default}"
    if config_options is not None:
        options = f"options: {config_options}"
    if config_rng is not None:
        rng = f"range: {'-'.join(map(str, config_rng))}"

    if default != "":
        params += f"[default: {default}"
    if options != "":
        if params == " ":
            params += f"[options: {options}"
        else:
            params += f" | options: {options}"
    if rng != "":
        if params == " ":
            params += f"[range: {range}"
        else:
            params += f" | range: {range}"
    if params == " ":
        params = ": "
    else:
        params += "]: "

    return f"{question}{params}"


def __ask_question(question:str, param:str, description:str, options=None, rng=None, err_msg:str=""):
    status = False
    while status is False:
        user_input = input(f"\t{error_msg} {question}").strip()
        if user_input == 'help':
            error_msg = ""
            print(f"\t`{param}` param description - {description}")
            continue

        try:
            user_input = ast.literal_eval(user_input)
        except Exception as error:
            error_msg = f"Failed to properly extract results (Error: {error}). "
            continue

        status = True
        if options is not None and user_input != "" and options != [] and all(isinstance(x, int) for x in options) and (user_input < options[0] or user_input > [1]):
            error_msg = f"Invalid input: {user_input}, value out of range..."
            status = False
        if range is not None and user_input != "" and rng != [] and user_input not in rng:
            error_msg = f"Invalid input: {user_input}..."
            status = False

    return user_input

def __get_answer(param:str, configs:dict, err_msg:str="")->dict:
    """
    Build question and ask users
    :args:
        param:str - param name
        configs:dict - information for param to generate question
    :params:
        defualt - default value
        options - options for param
        range - range of values param lies within
    :return;
        configs with updated value
    """
    default = None
    options = None
    rng = None
    if 'default' in configs:
        default =  configs['default'],
    if 'options' in configs:
        options = configs['options']
    if 'range' in configs:
        rng = configs['rng']

    question = __generate_question(config_question=configs['question'], config_default=default,
                                   config_options=options, config_rng=rng)

    user_input = __ask_question(question=question, param=param, description=configs[param]['description'],
                                options=options, rng=rng, err_msg=err_msg)

    configs['value'] = user_input
    if user_input == "":
        configs['value'] = configs['default']

    return configs

def operator_number():
    """
   for a demo based deployment, get the numeric value for the new operator
   :params:
       default:int - default value
       description:str question description
       question:str - the actual question
       error_msg:str - error message if something fails
       status:bool
       answer - user input
   :return:
       answer as int
   """
    status = False
    default = 1
    param  = "operator number"
    err_msg = ""
    user_input = ""
    configs = {
        "question": f"Which operator is this",
        "description": "In the network, which operator is this node in your network. The value will be used as part of the node name.",
        "default": default,
    }

    while status is False:
        status = True
        user_input = __get_answer(param=param, configs=configs, err_msg=err_msg)

        if not isinstance(user_input, int) and user_input > 0:
            status = False
            err_msg = "Operator number must be a (positive) integer value, please try again"

    return user_input

def generic_section(configs:dict):
    """
    Generic Questionnaire
    :sections:
        - directories
        - general
        - authentication
        - publisher
        - MQTT
        - advanced settings
    :args:
        configs:dict - configuration to review
    :params:
        user_input - user input result
    :return:
        updated configs-
    """
    for param in configs:
        configs[param]['value'] = configs[param]['default']
        status = False
        if configs[param]['enable'] is True:
            configs[param] = __get_answer(param=param, configs=configs[param], err_msg="")
            if param in ['ENABLE_MQTT', 'MONITOR_NODES'] and configs[param]['value'] == 'false':
                if param == 'ENABLE_MQTT':
                    for section in configs:
                        if section != "ENABLE_MQTT":
                            configs[section]['enable'] = False
                elif param == "MONITOR_NODES":
                    configs['MONITOR_NODES']['enable'] = False
                    configs['MONITOR_NODE_COMPANY']['enable'] = False

    return configs

def network_configs(configs:dict):
    for param in configs:
        configs[param]['value'] = configs[param]['default']
        err_msg = ""
        if configs[param]['enable'] is True:
            status = False
            while status is False:
                configs[param] = __get_answer(param=param, configs=configs[param], err_msg=err_msg)
                if param == "POLICY_BASED_NETWORKING" and configs[param]['value'] == 'false':
                    configs["CONFIG_POLICY_NAME"]['enable'] = False
                    status=True
                if param == "ANYLOG_BROKER_PORT":
                    if configs[param]['value'] == '':
                        configs["BROKER_BIND"]['enable'] = False
                    configs['ANYLOG_SERVER_PORT'], configs['ANYLOG_REST_PORT'], configs['ANYLOG_BROKER_PORT'] = validate_ports(anylog_tcp=configs['ANYLOG_SERVER_PORT'],
                                                                                                                               anylog_rest=configs['ANYLOG_REST_PORT'],
                                                                                                                               anylog_broker=configs['ANYLOG_BROKER_PORT'])
                    status = True
                if param in ['EXTERNAL_IP', 'LOCAL_IP', 'OVERLAY_IP', 'PROXY_IP']:
                    configs, err_msg = validate_ips(param=param, configs=configs[param])
                    if err_msg == "":
                        status = True

    return configs

def operator_configs(configs:dict):
    for param in configs:
        configs[param]['value'] = configs[param]['default']
        status = False
        err_msg = ""
        if configs[param]['enable'] is True:
            while status is False:
                configs[param] = __get_answer(param=param, configs=configs[param], err_msg=err_msg)
                if param in ['ENABLE_HA', 'ENABLE_PARTITIONS'] and configs[param]['value'] == 'false':
                    for section in ["START_DATE", 'TABLE_NAME', 'PARTITION_COLUMN', 'PARTITION_INTERVAL',
                                    'PARTITION_KEEP', 'PARTITION_SYNC']:
                        configs[param]['enable'] = False
                    status = True
                elif param == 'PARTITION_KEEP' and isinstance(configs[param]['value'], int) is False:
                    err_msg = f"Invalid value type ({type(configs[param]['value'])}) for PARTITION_INTERVAL, try again..."
                elif param in ['PARTITION_INTERVAL', 'PARTITION_SYNC'] and not re.match(r'(\d+)\s*(day|days|hour|hours|month|months|year|years)', configs[param]['value']):
                    err_msg = f"Invalid value for {param}, try again..."
                elif param == 'START_DATE' and not re.match(r'^-?\d+[dhy]$', configs[param]['value']):
                    err_msg = f'Invalid value for {param}, try again...'
                else:
                    status = True

        return configs


def blockchain_configs(configs:dict):
    for param in configs:
        configs[param]['value'] = configs[param]['default']
        status = False
        err_msg = ""
        if configs[param]['enable'] is True:
            while status is False:
                configs[param] = __get_answer(param=param, configs=configs[param], err_msg=err_msg)
                if param == 'LEDGER_CONN':
                    configs['LEDGER']['value'], err_msg = validate_ledger(ledger_conn=configs['LEDGER']['value'])
                    if err_msg == "":
                        status = True
                elif param in == 'SYNC_TIME' and not re.match(r'(\d+)\s*(day|days|hour|hours|month|months|year|years)', configs[param]['value']):
                    err_msg = f"Invalid value for {param}, try again..."
                else:
                    status = True

    return configs


def database_configs()