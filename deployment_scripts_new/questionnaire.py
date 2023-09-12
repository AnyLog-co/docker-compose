import ast
import re

from __support__ import validate_ip, validate_port, validate_ports, validate_process_time

def __generate_question(config_question:str, config_default=None, config_options=None, config_rng=None)->str:
    question = config_question
    default = ""
    options = ""
    rng = ""
    params = " "
    if config_default is not None:
        default = f"default: {config_default}"
    if config_options is not None:
        options = f"options: {', '.join(config_options)}"
    if config_rng is not None:
        rng = f"range: {'-'.join(map(str, config_rng))}"

    if default != "":
        params += f"[{default}"
    if options != "":
        if params == " ":
            params += f"[{options}"
        else:
            params += f" | {options}"
    if rng != "":
        if params == " ":
            params += f"[{rng}"
        else:
            params += f" | {rng}"
    if params == " ":
        params = ": "
    else:
        params += "]: "

    return f"{question}{params}"


def __ask_question(question:str, param:str, description:str, default=None, err_msg:str=""):
    """
    Ask aak question & validate inputs based on arguments
    :args:
        question:str - question to ask user
        param:str - param looking for
        description:str - param description
        default - default value
        options:list - param options
        rng:list - range for a given default (usually for ports)
        err_msg:str - error message
    :params:
        status:bool
        user_input:str - user input
    """
    status = False
    while status is False:
        status = True
        if err_msg.strip() != "":
            err_msg = err_msg.strip() + " "
        user_input = input(f"\t{err_msg}{question}").strip()
        if user_input == 'help':
            err_msg = ""
            print(f"\t`{param}` param description - {description}")
            continue
        elif user_input in ["", None]:
            user_input = default
        elif isinstance(default, int):
            try:
                user_input = int(user_input)
            except:
                err_msg = f"Invalid value type {type(user_input)} for {param.title().replace('_', ' ')}..."
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
    if 'default' in configs and configs['default'] != '':
        default =  configs['default']
    if 'options' in configs:
        options = configs['options']
    if 'range' in configs:
        rng = configs['range']

    question = __generate_question(config_question=configs['question'], config_default=default,
                                   config_options=options, config_rng=rng)

    user_input = __ask_question(question=question, param=param, description=configs['description'],
                                default=default, options=options, rng=rng, err_msg=err_msg)

    configs['value'] = user_input

    return configs

def operator_number()->int:
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

        if not isinstance(user_input, int) or user_input <= 0:
            status = False
            err_msg = "Operator number must be a positive integer value, please try again"

    return user_input


def generic_configs(configs:dict)->dict:
    """
    Generic configurations questioniare
    :sections:
        - authentication
    :args:
        configs:dict - section configuraiions
    :retunr:
        configs
    """
    for param in configs:
        configs[param]['value'] = configs[param]['default']
        if configs[param]['enable'] is True:
            configs[param] = __get_answer(param=param, configs=configs[param], err_msg="")
    return configs


def general_configs(configs:dict)->dict:
    """
    General configurations user input
    :args:
        configs:dict - configurations
    :params:
        status:bool
        err_msg:str - error message
    :return:
        status
    """
    for param in configs:
        configs[param]['value'] = configs[param]['default']
        if configs[param]['enable'] is True:
            status = False
            err_msg = ""
            while status is False:
                configs[param] = __get_answer(param=param, configs=configs[param], err_msg=err_msg)
                if param in ['LICENSE_KEY', 'NODE_TYPE', 'COMPANY_NAME'] and configs[param]['value'] in ["", None]:
                    err_msg = f"Missing {param.replace('_', ' ').lower()} value... "
                    continue
                else:
                    status = True
            if param in ['LOCATION', 'COUNTRY', 'STATE', 'CITY'] and configs[param]['value'] == configs[param]['default']:
                configs[param]['value'] = ""

    return  configs


def configs_questions(configs:dict)->dict:
    for param in configs:
        configs[param]['value'] = configs[param]['default']
        if configs[param]['enable'] is True:
            pass


def network_configs(configs:dict)->dict:
    """
    General configurations user input
    :args:
        configs:dict - configurations
    :params:
        status:bool
        err_msg:str - error message
    :return:
        status
    """
    for param in configs:
        configs[param]['value'] = configs[param]['default']
        if configs[param]['enable'] is True:
            status = False
            err_msg = ""
            while status is False:
                configs[param] = __get_answer(param=param, configs=configs[param], err_msg=err_msg)
                if param in ['EXTERNAL_IP', 'LOCAL_IP', 'KUBERNETES_SERVICE_IP', 'OVERLAY_IP', 'PROXY_IP']:
                    err_msg = validate_ip(param=param, ip_addr=configs[param]['value'])
                    if err_msg == "":
                        status = True
                elif (configs['ANYLOG_BROKER_PORT']['enable'] is False and param == 'ANYLOG_REST_PORT') or param == 'ANYLOG_BROKER_PORT':
                    configs = validate_ports(configs=configs)
                    status = True
                else:
                    status = True

    return  configs


def database_configs(configs:dict)->dict:
    """
    Validate database configurations
    :args:
        configs:dict - databse configurations
    :params:
        status:bool
        err_msg:str - error message
    :return:
        configs
    """
    for param in configs:
        configs[param]['value'] = configs[param]['default']
        if configs[param]['enable'] is True:
            status = False
            err_msg = ""
            while status is False:
                configs[param] = __get_answer(param=param, configs=configs[param], err_msg=err_msg)
                if param == "DB_TYPE" and configs[param]['value'] == 'sqlite':
                    for section in ['DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT']:
                        configs[section]['enable'] = False
                elif param == 'NOSQL_ENABLE' and configs[param]['value'] == 'false':
                    for section in ['NOSQL_TYPE', 'NOSQL_USER', 'NOSQL_PASSWD', 'NOSQL_IP', 'NOSQL_PORT',
                                    'NOSQL_BLOBS_DBMS', 'NOSQL_BLOBS_FOLDER', 'NOSQL_BLOBS_COMPRESS',
                                    'NOSQL_BLOBS_REUSE']:
                        configs[section]['enable'] = False
                elif param in ["DB_IP", 'NOSQL_IP']:
                    err_msg = validate_ip(param=param, ip_addr=configs[param]['value'])
                elif param in ["DB_PORT", "NOSQL_PORT"]:
                    err_msg = validate_port(param=param, port=configs[param]['value'], rng=None)
                if err_msg == "":
                    status = True
    return configs


def blockchain_section(configs:dict)->dict:
    for param in configs:
        configs[param]['value'] = configs[param]['default']
        if configs[param]['enable'] is True:
            status = False
            err_msg = ""
            while status is False:
                configs[param] = __get_answer(param=param, configs=configs[param], err_msg=err_msg)
                if param == "LEDGER_CONN":
                    try:
                        ip, port = configs[param]['value'].split(":")
                    except Exception as error:
                        err_msg = "Invalid ledger connection format (ex. {IP}:{ANYLOG_SERVER_PORT})"
                        continue
                    err_msg = validate_ip(param="LEDGER_CONN", ip_addr=ip)
                    if err_msg != "":
                        continue
                    err_msg = validate_port(param='LEDGER_CONN', port=port, rng=None)
                    if err_msg != "":
                        continue
                    status = True
                elif param == "SYNC_TIME":
                    err_msg = validate_process_time(param=param, value=configs[param]['value'])
                    if err_msg != "":
                        continue
                    status = True
                else:
                    status = True

    return configs


def operator_section(configs:dict)->dict:
    """
    Operator section configs
    :args:
        configs:dict - configurations for operator
    :params:
        status:bool
        err_msg;str
    :return:
        configs
    """
    for param in configs:
        configs[param]['value'] = configs[param]['default']
        if configs[param]['enable'] is True:
            status = False
            err_msg = ""
            while status is False:
                configs[param] = __get_answer(param=param, configs=configs[param], err_msg=err_msg)
                if param in ['MEMBER', 'START_DATE', 'OPERATOR_THREADS']:
                    try:
                        value = int(configs[param]['value'])
                    except Exception as error:
                        err_msg = f"Invalid value type {type(configs[param]['value'])} for {param.lower()}..."
                    else:
                        if param == 'START_DATE':
                            configs[param]['value'] = "-{value}d"
                        else:
                            configs[param]['value'] = value
                        status = True
                elif param == "ENABLE_HA" and param[param]['value'] == 'false':
                    configs['START_DATE']['enable'] = False
                    status = True
                elif param == 'ENABLE_PARTITIONS' and param[param]['value'] == 'false':
                    for section in ['TABLE_NAME', 'PARTITION_COLUMN', 'PARTITION_COLUMN', 'PARTITION_INTERVAL',
                                    'PARTITION_KEEP', 'PARTITION_SYNC']:
                        configs[section]['enable'] = False
                    status = True
                else:
                    status = True

    return configs


def publisher_configs(configs:dict)->dict:
    """
    Configuration for publisher node
    :args:
        configs:dict
    :params:
        status:bool
        err_msg:str - error message
    :return:
        err_msg
    """
    for param in configs:
        configs[param]['value'] = configs[param]['default']
        if configs[param]['enable'] is True:
            status = False
            err_msg = ""
            while status is False:
                configs[param] = __get_answer(param=param, configs=configs[param], err_msg=err_msg)
                if param in ["DBMS_FILE_LOCATION", "TABLE_FILE_LOCATION"]:
                    try:
                        value = int(configs[param]['value'])
                    except Exception as error:
                        err_msg = f"Invalid value type {type(configs[param]['value'])}"
                    else:
                        configs[param]['value'] = value

                if error == "":
                    status = True


def mqtt_section(configs:dict)->dict:
    """
    Configuration for MQTT configs
    :args:
        configs:dict
    :params:
        status:bool
        err_msg:str - error message
    :return:
        configs
    """
    for param in configs:
        configs[param]['value'] = configs[param]['default']
        if configs[param]['enable'] is True:
            status = False
            err_msg = ""
            while status is False:
                configs[param] = __get_answer(param=param, configs=configs[param], err_msg=err_msg)
                if param == 'ENABLE_MQTT' and configs[param]['value'] == 'false':
                    for section in ['MQTT_LOG', 'MQTT_BROKER', 'MQTT_PORT', 'MQTT_USER', 'MQTT_PASSWD', 'MQTT_TOPIC',
                                    'MQTT_DBMS', 'MQTT_TABLE', 'MQTT_TIMESTAMP_COLUMN', 'MQTT_VALUE_COLUMN',
                                    'MQTT_VALUE_COLUMN_TYPE']:
                        configs[param]['enable'] = False
                elif param == 'MQTT_BROKER':
                    err_msg = validate_ip(param=param, ip_addr=configs[param]['value'])
                elif param == 'MQTT_PORT':
                    try:
                        value = int(configs[param]['value'])
                    except Exception as error:
                        err_msg = f"Invalid value type {type(configs[param]['value'])} for {param.lower()}..."
                    else:
                        configs[param]['value'] = value
                if err_msg == "":
                    status = True

    return configs

def advanced_settings_section(configs:dict)->dict:
    """
    Advanced setting configurations
    :args:
        configs:dict
    :params:
        status:bool
        err_msg:str - error message
    :return:
        configs
    """
    for param in configs:
        configs[param]['value'] = configs[param]['default']
        if configs[param]['enable'] is True:
            status = False
            err_msg = ""
            while status is False:
                configs[param] = __get_answer(param=param, configs=configs[param], err_msg=err_msg)
                if param in 'QUERY_POOL':
                    try:
                        value = int(configs[param]['value'])
                    except Exception as error:
                        err_msg = f"Invalid value type {type(configs[param]['value'])} for {param.lower()}..."
                    else:
                        configs[param]['value'] = value
                if err_msg != "":
                    status = True

    return configs