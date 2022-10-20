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


def __ask_question(question:str, description:str, error_msg:str="")->str:
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
            print(f"\tparam description - {description}")
        else:
            status = True
    return user_input


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
        error_msg=f'Port value {answer} is invalid. Please try again... '
    else:
        if check_range is True and (30000 < port  or port > 32767):
            error_msg=f'Value {answer} out of range. Please try again... '

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
            answer = answer = __ask_question(error_msg=error_msg, question=full_question, description=rest_info['description'])
            if answer != "":
                port, error_msg = __validate_port(port=answer)
                if error_msg == "":
                    configs[param]['value'] = answer
                    status = True
            else:
                rest_info['value'] = rest_info[param]['default']
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
                answer = __ask_question(error_msg=error_msg, question=full_question, description=broker_info['description'])
                if answer != "":
                    port, error_msg = __validate_port(port=answer)
                    if error_msg == "":
                        configs[param]['value'] = answer
                        status = True
                else:
                    # if originally
                    broker_info['value'] = broker_info['default']
                    status = True

    return rest_info, broker_info


def generic_questions(configs:dict)->dict:
    """
    Generic configuration questionnaire
    :args:
        configs:dict - configuration information for generic params
    :params:
        full_question:str - generated full question
        answer:str - user inputted answer
    """
    for param in configs:
        if configs[param]['enable'] is True:
            full_question = __generate_question(configs=configs[param])
            answer = __ask_question(question=full_question, description=configs[param]['description'])
            if answer == "" and param in ['NODE_NAME', 'COMPANY_NAME']:
                configs[param]['value'] = configs[param]['default']
        else:
            configs[param]['value'] = configs[param]['default']

    return configs


def networking_questions(configs:dict):
    """
    Networking configurations questionnaire
    :args:
        configs:dict - networking configuration
    :params:
        status:bool
        error_msg:str - error message
        full_question:str - question
        answer:str - user input
    :return:
        updated configs
    """
    for param in configs:
        if configs[param]['enable'] is True:
            error_msg = ""
            full_question = __generate_question(configs=configs[param])
            status = False
            while status is False: # iterate through options if type PORT then convert to int
                answer = __ask_question(error_msg=error_msg, question=full_question, description=configs[param]['description'])
                if param in ['ANYLOG_SERVER_PORT', 'ANYLOG_REST_PORT', 'ANYLOG_BROKER_PORT'] and answer != "":
                    port, error_msg = __validate_port(port=answer)
                    if error_msg == "":
                        configs[param]['value'] = answer
                        status = True
                else:
                    configs[param]['value'] = configs[param]['default']
                    status = True
        else:
            configs[param]['value'] = configs[param]['default']

    configs['ANYLOG_REST_PORT'], configs['ANYLOG_BROKER_PORT'] = __validate_ports(tcp_port=configs['ANYLOG_SERVER_PORT']['value'],
                                                                                  rest_info=configs['ANYLOG_REST_PORT'],
                                                                                  broker_info=configs['ANYLOG_BROKER_PORT'])
    return configs


def database_questions(configs:dict)->dict:
    """
    Database configurations
    :args:
        configs:dict - database configurations
    :params:
        status:bool
        error_msg:str - error message
        full_question:str - question
        answer:str - user input
    :return:
        updated configs
    """
    for param in configs:
        if configs[param]['enable'] is True:
            error_msg = ""
            full_question = __generate_question(configs=configs[param])
            status = False
            while status is False:
                answer = __ask_question(error_msg=error_msg, question=full_question, description=configs[param]['description'])
                if param in ['DB_TYPE', 'NOSQL_TYPE'] and answer != "":
                    if answer not in configs[param]['options']:
                        error_msg = f"Invalid database type {answer}. Please try again... "
                    else:
                        configs[param]['value'] = answer
                        status = True
                elif param in ["DB_PORT", "NOSQL_PORT"] and answer != "":
                    port, error_msg = __validate_port(port=answer, check_range=False)
                    if error_msg == "":
                        configs['param']['value'] = port
                        status = True
                elif param in ['AUTOCOMMIT', 'SYSTEM_QUERY', 'MEMORY', 'ENABLE_NOSQL'] and answer != "":
                    if answer not in configs[param]['options']:
                        error_msg = f"Invalid value {answer}. Please try again... "
                    else:
                        configs[param]['value'] = answer
                        status = True
                else:
                    configs[param]['value'] = configs[param]['default']
                    status = True
        else:
            configs[param]['value'] = configs[param]['default']

        # skip all other questions if DB_TYPE is SQLite or NoSQL is disabled
        if param == 'DB_TYPE' and configs['DB_TYPE']['value'] == 'sqlite':
            for key in configs:
                if 'NOSQL' not in key:
                    configs[key]['enable'] = False
        elif param == 'NOSQL_ENABLE' and configs['NOSQL_ENABLE']['value'] == 'false':
            for key in configs:
                if 'NOSQL' in key:
                    configs[key]['enable'] = False

    if configs['DB_TYPE']['value'] != 'sqlite': # if missing username and/or password then set DB_TYPE back to sqlite
        if configs['DB_USER']['value'] == "" or configs['DB_PASSWD']['value'] == "":
            configs['DB_TYPE']['value'] = 'sqlite'

    return configs


def blockchain_questions(configs:dict)->dict:
    """
    Generate questions for blockchain configurations
    :args:
        configs:dict - database configurations
    :params:
        status:bool
        error_msg:str - error message
        full_question:str - question
        answer:str - user input
    :return:
        updated configs
    """
    for param in configs:
        if configs[param]['enable'] is True:
            error_msg = ""
            full_question = __generate_question(configs=configs[param])
            status = False
            while status is False:
                answer = __ask_question(error_msg=error_msg, question=full_question, description=configs[param]['description'])
                if param == 'LEDGER_CONN':
                    if re.search(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\:[30000-32767]', answer):
                       configs[param]['value'] = answer
                       status = True
                    else:
                        error_msg = f"Invalid LEDGER_CONN information value {answer}. Please try again... "
                elif param == 'SYNC_TIME':
                    if answer[-1] == "s":
                        answer = answer[:-1]
                    for option in configs[param]['options']:
                        if option not in answer:
                            error_msg = f"Invalid value {answer} for blockchain sync time. Please try again... "
                    if error_msg == "":
                        configs[param]['value'] = answer
                        status = True
                elif param in ["BLOCKCHAIN_SOURCE", "BLOCKCHAIN_DESTINATION"]:
                    if answer in configs[param]['options']:
                        configs[param]['value'] = answer
                        status = True
                    else:
                        error_msg = f"Invalid value {answer}. Please try again... "
                else:
                    configs[param]['value'] = configs[param]['default']
                    status = True
        else:
            configs[param]['value'] = configs[param]['default']

    return configs


def operator_questions(configs:dict)->dict:
    """
    Generate questions for operator configurations
    :args:
        configs:dict - database configurations
    :params:
        status:bool
        error_msg:str - error message
        full_question:str - question
        answer:str - user input
    :return:
        updated configs
    """
    for param in configs:
        if configs[param]['enable'] is True:
            error_msg = ""
            full_question = __generate_question(configs=configs[param])
            status = False
            while status is False:
                answer = __ask_question(error_msg=error_msg, question=full_question, description=configs[param]['description'])
                if param in ['ENABLE_HA', 'ENABLE_PARTITIONS', 'CREATE_TABLE', 'UPDAE_TSD_INFO', 'ARCHIVE',
                             'COMPRESS_FILE']:
                    if answer not in configs[param]['options'] and answer != "":
                        error_msg = f"Invalid value {answer}. Please try again... "
                    elif answer in configs[param]['options']:
                        configs[param]['value'] = answer
                    if answer == "" or answer == 'false':
                        configs[param]['value'] = configs[param]['default']
                        if param == 'ENABLE_HA':
                            configs['START_DATE']['enable'] = False
                        elif param == 'ENABLE_PARTITIONS':
                            for config in ['TABLE_NAME', 'PARTITION_COLUMN', 'PARTITION_INTERVAL', 'PARTITION_KEEP',
                                           'PARTITION_SYNC']:
                                configs[config]['enable'] = False
                elif param == 'START_DATE':
                    if answer != "":
                        try:
                            answer = int(answer)
                        except:
                            error_msg = f"Invalid value {answer}. Please try again... "
                        else:
                            configs[param]['value'] = f"-{answer}d"
                    else:
                        configs[param]['value'] = f"-{configs[param]['defaul']}d"
                elif param in ["PARTITION_INTERVAL", "PARTITION_SYNC"] and answer != "":
                    for option in configs[param]['options']:
                        if 's' == answer[-1]:
                            answer = answer[:-1]
                        if option in answer:
                            configs[param]['value'] = answer
                            status = True
                    if status is False:
                        error_msg = f"Invalid value {answer}. Please try again... "
                elif param in ['PARTITION_KEEP', 'OPERATOR_THREADS'] and answer != "":
                    try:
                        answer = int(answer)
                    except:
                        error_msg = f"Invalid value {answer}. Please try again... "
                    else:
                        if answer < configs[param]['default']:
                            answer = configs[param]['default']
                        configs[param]['value'] = answer
                        status = True
                else:
                    configs[param]['value'] = configs[param]['default']
        else:
            configs[param]['value'] = configs[param]['default']

    return configs


def publisher_questions(configs:dict)->dict:
    """
    Generate questions for operator configurations
    :args:
        configs:dict - database configurations
    :params:
        status:bool
        error_msg:str - error message
        full_question:str - question
        answer:str - user input
    :return:
        updated configs
    """
    for param in configs:
        if configs[param]['enable'] is True:
            error_msg = ""
            full_question = __generate_question(configs=configs[param])
            status = False
            while status is False:
                answer = __ask_question(error_msg=error_msg, question=full_question, description=configs[param]['description'])
                if param in ['DBMS_FILE_LOCATION', 'TABLE_FILE_LOCATION'] and answer != "":
                    try:
                        answer = int(answer)
                    except:
                        error_msg = f"Invalid value {answer}. Please try again... "
                    else:
                        configs[param]['value'] = answer
                        status = True
                elif param == 'COMPRESS_FILE' and answer != "":
                    if answer not in configs[param]['options'] and answer != "":
                        error_msg = f"Invalid value {answer}. Please try again... "
                    elif answer in configs[param]['options']:
                        configs[param]['value'] = answer
                else:
                    configs[param]['value'] = configs[param]['default']
    else:
        configs[param]['value'] = configs[param]['default']









