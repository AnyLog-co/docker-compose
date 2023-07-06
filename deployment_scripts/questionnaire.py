import ipaddress
import re


def __generate_question(configs:dict)->str:
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
        params += f"default: {configs['default']}"
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
        user_input = input(f"\t{error_msg}{question}")
        if user_input == 'help':
            error_msg = ""
            print(f"\t`{param}` param description - {description}")
        else:
            status = True
    return user_input.strip()


def __validate_port(port:str, check_range:bool=True)->(int, str):
    """
    Validate if port value is an integer and within range (30000 - 32767)
    :args:
        port:str - port value
        check_range:bool - whether or not to check the port range
    :params:
        error_msg:str - error message
    :return:
        port, error_message
    """
    error_msg = ""
    try:
        port = int(port)
    except Exception as error:
        error_msg=f'Port value {port} is invalid. Please try again... '
    else:
        if check_range is True and not (30000 <= port <= 32767):
            error_msg=f'Value {port} out of range. Please try again... '

    return port, error_msg


def __validate_ports(tcp_port:int, rest_info:dict, broker_info:dict)->(dict, dict):
    """
    Check if one or more of the ports is already used
    :args:
        tcp_port:int - TCP port number
        rest_info:dict - REST information
        broker_info:dict - broker information
    :params:
        status:bool
        error_msg:str - error message
        full_question:str - full question
        answer:str - user input
    :return:
        rest and broker info (updated)
    """
    # check if REST port is double used
    while tcp_port == rest_info['value'] or rest_info['value'] == broker_info['value']:
        error_msg = f"Port Value {rest_info['value']} already used. Please try again... "
        status = False
        full_question = __generate_question(configs=rest_info)
        while status is False:
            answer = __ask_question(question=full_question, description=rest_info['description'],
                                    param='anylog_reset_port', error_msg=error_msg)
            if answer != "":
                port, error_msg = __validate_port(port=answer)
                if error_msg == "":
                    rest_info['value'] = answer
                    status = True
            else:
                rest_info['value'] = rest_info['default']
                status = True

    # check if Broker port is double used
    if broker_info['value'] != "":
        # if user originally set a value for broker, then the default is 1 value great than REST port value
        broker_info['default'] = rest_info['value'] + 1
        while tcp_port == broker_info['value'] or rest_info['value'] == broker_info['value']:
            error_msg = f"Port Value {broker_info['value']} already used"
            status = False
            full_question = __generate_question(configs=broker_info)
            while status is False:
                answer = __ask_question(question=full_question, description=broker_info['description'],
                                        param='anylog_broker_port', error_msg=error_msg)
                if answer != "":
                    port, error_msg = __validate_port(port=answer)
                    if error_msg == "":
                        broker_info['value'] = answer
                        status = True
                else:
                    # if originally
                    broker_info['value'] = broker_info['default']
                    status = True

    return rest_info, broker_info


def __validate_int(value:str)->(int, str):
    """
    validate value is of type int and >= 1
    :args:
        value:str - user input
    :params:
        error_msg:str - error message
    :return:
        value, error_msg
    """
    error_msg = ""
    try:
        value = int(value)
    except Exception as error:
        error_msg = f"Invalid value: {value}. Please try again..."
    else:
        if value < 1:
            error_msg = f"Value out of range - minimum value 1. Please try again... "

    return value, error_msg


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


def ask_question(param:str, configs:dict, error_msg="")->str:
    status = False
    full_question = __generate_question(configs=configs)
    while status is False:
        answer = __ask_question(question=full_question, description=configs['description'],
                                param=param, error_msg=error_msg).strip()
        status = True
        if answer == '' or answer == "":
            answer = ''
        elif isinstance(configs['default'], int):
            answer, error_msg = __validate_int(value=answer)
            if 'PORT' in param and error_msg == "":
                answer, error_msg = __validate_port(port=answer, check_range=True)
            if error_msg != "":
                status = False
        elif 'options' in configs and " " in answer:
            answer = answer.lower()
            front, back = answer.split(" ")
            front, error_msg = __validate_int(value=front)
            if error_msg != "":
                status = False
            if back not in configs['options'] and back[:-1] not in configs['options'] and error_msg != '':
                error_msg.replace("Please try again...", f"Value {back} out of range. Please try again... ")
            elif back not in configs['options'] and back[:-1] not in configs['options'] and error_msg == '':
                error_msg = f"Value {back} out of range. Please try again... "
                status = False
        elif 'options' in configs:
            answer = answer.lower()
            if answer not in configs['options']:
                error_msg = f"Invalid option {answer}. Please try again..."
                status = False

    return answer


def generic_section(configs:dict)->dict:
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
        answer - user input result
    :return:
        updated configs-
    """
    for param in configs:
        if configs[param]['enable'] is True:
            answer = ask_question(param=param, configs=configs[param])
            if answer == "" and param in ['LOCATION', 'COUNTRY', 'STATE', 'CITY']:
                    configs[param]['value'] = ''
            elif answer == "":
                configs[param]['value'] = configs[param]['default']
            else:
                configs[param]['value'] = answer
        else:
            configs[param]['value'] = configs[param]['default']

        if param == 'ENABLE_MQTT' and configs['ENABLE_MQTT']['value'] == 'false':
            import json
            print(json.dumps(configs))
            if param == 'ENABLE_MQTT' and configs['ENABLE_MQTT']['value'] == 'false':
                for section in configs:
                    if section != "ENABLE_MQTT":
                        configs[section]['enable'] = False

    return configs


def networking_section(configs:dict)->dict:
    """
    Network configuration credentials
    :args:
        configs:dict - configuration to review
    :params:
        answer - user input result
    :return:
        updated configs
    """
    for param in configs:
        if configs[param]['enable'] is True:
            status = False
            error_msg = ""
            while status is False:
                answer = ask_question(param=param, configs=configs[param], error_msg=error_msg)
                status = True
                if answer == "":
                    configs[param]['value'] = configs[param]['default']
                elif param in ['OVERLAY_IP', 'PROXY_IP']:
                    answer, error_msg = __validate_ipaddress(answer)
                    if error_msg == "":
                        configs[param]['value'] = answer
                    else:
                        status = False
                else:
                    configs[param]['value'] = answer
        else:
            configs[param]['value'] = configs[param]['default']

        if param == "POLICY_BASED_NETWORKING" and configs[param]['value'] == 'false':
            configs["CONFIG_POLICY_NAME"]['enable'] = False
        if param == "ANYLOG_BROKER_PORT":
            # Validate
            configs['ANYLOG_REST_PORT'], configs['ANYLOG_BROKER_PORT'] = __validate_ports(tcp_port=configs['ANYLOG_SERVER_PORT']['value'],
                                                                                          rest_info=configs['ANYLOG_REST_PORT'],
                                                                                          broker_info=configs['ANYLOG_BROKER_PORT'])
            if configs[param]['value'] == '':
                configs["BROKER_BIND"]['enable'] = False
                configs["BROKER_THREADS"]['enable'] = False

    return configs


def database_section(configs:dict)->dict:
    """
    Database configuration credentials
    :args:
        configs:dict - configuration to review
    :params:
        answer - user input result
    :return:
        updated configs
    """
    for param in configs:
        if configs[param]['enable'] is True:
            status = False
            error_msg = ""
            while status is False:
                answer = ask_question(param=param, configs=configs[param], error_msg=error_msg)
                status = True
                if answer == "":
                    configs[param]['value'] = configs[param]['default']
                elif param == "DB_IP":
                    answer, error_msg = __validate_ipaddress(address=answer)
                    if error_msg != "":
                        status = False
                elif param == "DB_PROT":
                    answer, error_msg = __validate_int(value=answer)
                    if error_msg != "":
                        status = False
                else:
                    configs[param]['value'] = answer
        else:
            configs[param]['value'] = configs[param]['default']

        if param == "DB_TYPE" and configs[param]['value'] == 'sqlite':
            for section in ["DB_USER", "DB_PASSWD", "DB_IP", "DB_PORT"]:
                configs[section]['enable'] = False
                configs[section]['default'] = ''
        elif param == "SYSTEM_QUERY" and configs[param]['value'] == 'false':
            configs['MEMORY']['enable'] = False
            configs['MEMORY']['value'] = 'false'
        elif param == "NOSQL_ENABLE" and configs[param]['value'] == 'false':
            for section in ["NOSQL_TYPE", "NOSQL_USER", "NOSQL_PASSWD", "NOSQL_PORT", "NOSQL_BLOBS_DBMS",
                            "NOSQL_BLOBS_FOLDER", "NOSQL_BLOBS_COMPRESS", "NOSQL_BLOBS_REUSE"]:
                configs[section]['enable'] = False

    return configs


def blockchain_section(configs:dict)->dict:
    error_msg = ""
    for param in configs:
        status = False
        if configs[param]['enable'] is True:
            while status is False:
                answer = ask_question(param=param, configs=configs[param])
                status = True
                if answer == "":
                    configs[param]['value'] = configs[param]['default']
                elif param == 'LEDGER_CONN' and not re.match(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\:[30000-32767]', answer):
                    error_msg = "Invalid format for ledger conn - expected format: IP:PORT. Please try again... "
                elif param == 'LEDGER_CONN':
                    ipaddress, port = answer.split(":")
                    ipaddress, error_msg = __validate_ipaddress(address=ipaddress)
                    port, error_msg2 = __validate_int(value=port)
                    status = False
                    if error_msg != "" and error_msg2 != '':
                        error_msg.replace("Please try again...", error_msg2)
                    elif error_msg == '' and error_msg2 != '':
                        error_msg = error_msg2
                    else:
                        configs[param]['value'] = answer
                        status = True
                else:
                    configs[param]['value'] = answer

        else:
            configs[param]['value'] = configs[param]['default']


def operator_section(configs:dict)->dict:
    for param in configs:
        if configs[param]['enable'] is True:
            answer = ask_question(param=param, configs=configs[param])
            if answer == "":
                configs[param]['value'] = configs[param]['default']
            else:
                configs[param]['value'] = answer
        else:
            configs[param]['value'] = configs[param]['default']

        if param == 'ENABLE_HA' and configs[param]['value'] == 'false':
            configs['START_DATE']['enable'] = False
        elif param == 'START_DATE':
            configs[param]['value'] = f"-{configs[param]['value']}d"
        elif param == 'ENABLE_PARTITIONS' and configs[param]['value'] == 'false':
            for section in ['TABLE_NAME', 'PARTITION_COLUMN', 'PARTITION_INTERVAL', 'PARTITION_KEEP', 'PARTITION_SYNC']:
                configs[param]['enable'] = False
                configs[param]['default'] = ''
    return configs