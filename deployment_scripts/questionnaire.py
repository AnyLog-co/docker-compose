import ipaddress
import re


def __generate_question(param:str, configs:dict)->str:
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


def __ask_question(question:str, description:str, param:str="", error_msg:str="")->str:
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


def __validate_ipaddress(address:str)->(str, str):
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
        question = __generate_question(param=param, configs=configs[param])
        if configs[param]['enable'] is True:
            answer = __ask_question(question=question, description=configs[param]['description'], param=param, error_msg=err_msg)
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
        question = __generate_question(param=param, configs=configs[param])
        status = False
        if configs[param]['enable'] is True:
            while status is False:
                answer = __ask_question(question=question, description=configs[param]['description'], param=param, error_msg=err_msg)
                if answer == "":
                    configs[param]['value'] = configs[param]['default']
                    status = True
                elif param in ['OVERLAY_IP', 'PROXY_IP']:
                    answer, err_msg =  __validate_ipaddress(address=answer)
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
        question = __generate_question(param=param, configs=configs[param])
        status = False
        if configs[param]['enable'] is True:
            while status is False:
                answer = __ask_question(question=question, description=configs[param]['description'], param=param, error_msg=err_msg)
                if answer == "":
                    configs[param]['value'] = configs[param]['default']
                    status = True
                elif param == 'LEDGER_CONN':
                    if ':' not in answer:
                        err_msg = "Invalid LEDGER_CONN format"
                    else:
                        ip, port = answer.split(':')
                        ip, err_msg = __validate_ipaddress(address=ip)
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