import re
from __support__ import generate_question, ask_question, validate_ipaddress

def section_general(configs:dict)->dict:
    """
    general information
    :args:
        configs:dict - node configurations
    :params:
        answer:str - answer from user
    :return:
        update configs
    """
    for param in configs:
        err_msg = ""
        question = generate_question(param=param, configs=configs[param])
        if configs[param]['enable'] is True:
            answer = ask_question(question=question, description=configs[param]['description'], param=param, error_msg=err_msg)
            if answer == "" and param in ['LOCATION', 'COUNTRY', 'STATE', 'CITY']:
                    configs[param]['value'] = ''
            elif answer == "":
                configs[param]['value'] = configs[param]['default']
            else:
                configs[param]['value'] = answer
        else:
            configs[param]['value'] = configs[param]['default']
            if param in ['LOCATION', 'COUNTRY', 'STATE', 'CITY']:
                    configs[param]['value'] = ''

    return configs


def section_networking(configs:dict)->dict:
    """
    networking information
    :args:
        configs:dict - node configurations
    :params:
        answer:str - answer from user
    :return:
        update configs
    """
    for param in configs:
        err_msg = ""
        question = generate_question(param=param, configs=configs[param])
        status = False
        if configs[param]['enable'] is True:
            while status is False:
                answer = ask_question(question=question, description=configs[param]['description'], param=param, error_msg=err_msg)
                if answer == "":
                    configs[param]['value'] = configs[param]['default']
                    status = True
                elif param in ['OVERLAY_IP', 'PROXY_IP']:
                    answer, err_msg =  validate_ipaddress(address=answer)
                    if err_msg == "":
                        configs[param]['value'] = answer
                        status = True
                elif isinstance(configs[param]['default'], int):
                    try:
                        answer = int(answer)
                    except Exception as error:
                        err_msg = f"Invalid type {type(answer)} for {param}"
                    else:
                        if 'range' in configs[param] and answer not in range(*configs[param]['range']):
                            err_msg = f"input value {answer} is out of range"
                        elif 'options' in configs[param] and answer not in configs[param]['options']:
                            err_msg = f"input value {answer} is an invalid options"
                        elif param == 'ANYLOG_REST_PORT' and answer == configs['ANYLOG_SERVER_PORT']['value']:
                            err_msg = f"Port value {answer} is already being used by the TCP value"
                        elif param == 'ANYLOG_BROKER_PORT' and answer == configs['ANYLOG_SERVER_PORT']['value']:
                            err_msg = f"Port value {answer} is already being used by the TCP value"
                        elif param == 'ANYLOG_BROKER_PORT' and answer == configs['ANYLOG_REST_PORT']['value']:
                            err_msg = f"Port value {answer} is already being used by the REST value"
                        else:
                            configs[param]['value'] = answer
                            status = True
                elif 'options' in configs[param]:
                    if answer not in configs[param]['options']:
                        err_msg = f"input value {answer} is an invalid options"
                    else:
                        configs[param]['value'] = answer
                        status = True
        else:
            configs[param]['value'] = configs[param]['default']



    return configs


def section_database(configs:dict)->dict:
    for param in configs:
        err_msg = ""
        question = generate_question(param=param, configs=configs[param])
        if configs[param]['enable'] is True:
            status = False
            while status is False:
                answer = ask_question(question=question, description=configs[param]['description'], param=param, error_msg=err_msg)
                if param in ['DB_USER', 'DB_PASSWD'] and answer == "":
                    err_msg = f"Missing value for {param}"
                elif answer == "":
                    configs[param]['value'] = configs[param]['default']
                    status = True
                elif isinstance(configs[param]['default'], int):
                    try:
                        answer = int(answer)
                    except Exception as error:
                        err_msg = f"Invalid type {type(answer)} for {param}"
                    else:
                        status = True
                        configs[param]['value'] = answer
                elif 'options' in configs[param] and answer not in configs[param]['options']:
                    err_msg = f"Invalid value for {param} - {answer}"
                elif param in ['DB_IP', 'NOSQL_IP']:
                    answer, err_msg = validate_ipaddress(address=answer)
                    if err_msg == '':
                        configs[param]['value'] = answer
                        status = True
                else:
                    configs[param]['value'] = answer
                    status = True
        else:
            configs[param]['value'] = configs[param]['default']

        if param == 'DB_TYPE' and configs[param]['value'] != 'sqlite':
            for key in ['DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT']:
                configs[key]['enable'] = True
        elif param == 'DB_TYPE' and configs[param]['value'] == 'sqlite':
            for key in ['DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT']:
                configs[key]['enable'] = False
        elif param == 'ENABLE_NOSQL' and configs[param]['value'] == 'true':
            for key in ['NOSQL_USER', 'NOSQL_PASSWD', 'NOSQL_IP', 'NOSQL_PORT']:
                configs[key]['enable'] = True
            configs['BLOBS_DBMS']['value'] = 'true'
        elif param == 'ENABLE_NOSQL' and configs[param]['value'] == 'false':
            for key in ['NOSQL_USER', 'NOSQL_PASSWD', 'NOSQL_IP', 'NOSQL_PORT']:
                configs[key]['enable'] = True
            configs['BLOBS_DBMS']['value'] = 'false'


def section_blockchain(configs:dict) -> dict:
    """
    blockchain information
    :args:
        configs:dict - node configurations
    :params:
        answer:str - answer from user
    :return:
        update configs
    """
    for param in configs:
        err_msg = ""
        question = generate_question(param=param, configs=configs[param])
        status = False
        if configs[param]['enable'] is True:
            while status is False:
                answer = ask_question(question=question, description=configs[param]['description'], param=param, error_msg=err_msg)
                if answer == "":
                    configs[param]['value'] = configs[param]['default']
                    status = True
                elif param == 'LEDGER_CONN':
                    if ':' not in answer:
                        err_msg = "Invalid LEDGER_CONN format"
                    else:
                        ip, port = answer.split(':')
                        ip, err_msg = validate_ipaddress(address=ip)
                        if err_msg == "":
                            try:
                                port = int(port)
                            except Exception as error:
                                err_msg = f"Invalid port value type {type(port)}"
                        if err_msg == "":
                            configs[param]['value'] = answer
                            status = True
                elif param == 'SYNC_TIME':
                    for keyword in configs['options']:
                        pattern = fr'\b{re.escape(keyword)}\b'
                        if re.search(pattern, answer) is True:
                            configs[param]['value'] = answer
                            status = True
                    if status is False:
                        err_msg = f"Invalid value for {param}"
                elif 'options' in configs[param] and answer not in configs[param]['options']:
                    err_msg = f"Invalid value for {param} - {answer}"
                elif err_msg == "" and status is False:
                    configs[param]['value'] = answer
                    status = True
        else:
            configs[param]['value'] = configs[param]['default']

    return configs


def section_operator(company_name:str, configs:dict, operator_id:int=None, is_training:bool=False)->dict:
    configs['CLUSTER_NAME']['default'] = f"{company_name}-cluster"
    configs['DEFAULT_DBMS']['default'] = company_name.replace("-", '_')
    if is_training is True:
        status = False
        question = "Operator Number [default: 1]: "
        description = "Number of operators already in the network"
        err_msg = ""
        while status is False:
            answer = ask_question(question=question, description=description, param="operator_number", error_msg=err_msg)
            if answer == '':
                configs['CLUSTER_NAME']['default'] = f"{configs['CLUSTER_NAME']['default']}1"
                status = True
                continue
            try:
                answer = int(answer)
            except Exception as error:
                err_msg = f"Invalid value type {type(answer)}, required type: int."
            else:
                status = True
                configs['CLUSTER_NAME']['default'] = f"{configs['CLUSTER_NAME']['default']}{answer}"
        return configs

    for param in configs:
        if configs[param]['enable'] is True:
            err_msg = ""
            status = True
            question = generate_question(param=param, configs=configs[param])
            while status is True:
                answer = ask_question(question=question, description=configs[param]['description'], param=param, error_msg=err_msg)
                if answer == "":
                    configs[param]['value'] = configs[param]['default']
                    status = True
                elif isinstance(configs[param]['default'], int):
                    try:
                        answer = int(answer)
                    except:
                        err_msg = f"Invalid type {type(answer)} for {param}"
                    else:
                        configs[param]['value'] = answer
                        status = True
                elif 'options' in configs[param]:
                    for option in configs[param]['options']:
                        if option in answer.lower():
                            configs[param]['value'] = answer.lower()
                            status = True
                    if status is False:
                        err_msg = f"Invalid value for {param}"
        else:
            configs[param]['value'] = configs[param]['default']
    return configs


def section_monitoring(configs:dict)->dict:
    for param in configs:
        err_msg = ""
        question = generate_question(param=param, configs=configs[param])
        status = False
        if configs[param]['enable'] is True:
            while status is False:
                answer = ask_question(question=question, description=configs[param]['description'], param=param, error_msg=err_msg)
                status = True
                if answer == "":
                    configs[param]['value'] = configs[param]['default']
                elif 'options' in configs[param] and answer not in configs[param]['options']:
                    err_msg = f'Invalid value for {param}'
                    status = False
                else:
                    configs[param]['value'] = answer
        else:
            configs[param]['value'] = configs[param]['default']

    return  configs


def section_mqtt(configs:dict, rest_port:int=None, broker_port:int=None)->dict:
    """
    MQTT information
    :args:
        configs:dict - node configurations
    :params:
        answer:str - answer from user
    :return:
        update configs
    """
    for param in configs:
        err_msg = ""
        question = generate_question(param=param, configs=configs[param])
        status = False
        if param == "MQTT_PORT" and configs["MQTT_BROKER"]['value'] == 'rest':
            configs[param]['value'] = rest_port
        elif param == "MQTT_PORT" and configs["MQTT_BROKER"]['value'] == 'local':
            configs[param]['value'] = broker_port
        elif configs[param]['enable'] is True:
            while status is False:
                answer = ask_question(question=question, description=configs[param]['description'], param=param, error_msg=err_msg)
                if answer == "":
                    configs[param]['value'] = configs[param]['default']
                    status = True
                elif param == 'MQTT_BROKER':
                    if answer == 'local' and broker_port is None:
                        err_msg = "No local broker port specified"
                    elif answer in ['local', 'rest']:
                        configs[param]['value'] = answer
                        status = True
                    else:
                        ip, err_msg = validate_ipaddress(address=answer)
                        if err_msg == "":
                            configs[param]['value'] = answer
                            status = True
                elif param == "MQTT_PORT":
                    if answer != '':
                        try:
                            answer = int(answer)
                        except Exception as error:
                            err_msg = f"Invalid port value type {type(answer)}"
                        else:
                            configs[param]['value'] = answer
                            status = True
                elif param == 'MQTT_LOG' and answer not in configs[param]['options']:
                    err_msg = f"Invalid value for {param}"
                else:
                    configs[param]['value'] = answer
                    status = True
        else:
            configs[param]['value'] = configs[param]['default']


    return configs

