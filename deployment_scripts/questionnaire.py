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