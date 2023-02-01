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
        error_msg=f'Port value {answer} is invalid. Please try again... '
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
            answer = __ask_question(question=full_question, description=configs[param]['description'], 
                                    param=param, error_msg=error_msg)
            if answer != "":
                port, error_msg = __validate_port(port=answer)
                if error_msg == "":
                    rest_info['value'] = answer
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
                answer = __ask_question(question=full_question, description=configs[param]['description'],
                                        param=param, error_msg=error_msg)
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
        error_msg = ""
        if configs[param]['enable'] is True:
            full_question = __generate_question(configs=configs[param])
            answer = __ask_question(question=full_question, description=configs[param]['description'],
                                    param=param, error_msg=error_msg)
            if answer == "" and param in ['LOCATION', 'COUNTRY', 'STATE', 'CITY']:
                configs[param]['value'] = ''
            elif answer == "":
                configs[param]['value'] = configs[param]['default']
            else:
                configs[param]['value'] = answer

    return configs


def networking_questions(configs:dict)->dict:
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
            while status is False:
                answer = __ask_question(question=full_question, description=configs[param]['default'],
                                        param=param, error_msg=error_msg)
                if param in 'PORT' and answer != '':
                    port, error_msg = __validate_port(port=answer)
                    if error_msg == "":
                        configs[param]['value'] = answer
                        status = True
                elif 'options' in configs[param] and answer != ''  and answer not in configs[param]['options']:
                    error_msg = f'Invalid option {answer}. Please try again... '
                elif answer != "":
                    configs[param]['value'] = answer
                    status = True
                else:
                    configs[param]['value'] = configs[param]['default']
                    status = True
        else:
            configs[param]['value'] = configs[param]['default']

        # if disable network based on policy, provide params for user to configure their network with
        if configs['POLICY_BASED_NETWORKING']['value'] == "false":
            for param in ['TCP_THREADS','REST_TIMEOUT', 'REST_THREADS', 'BROKER_THREADS']:
                configs[param]['enable'] = True
        if configs['CONFIG_POLICY']['value'] == 'false':
            configs['CONFIG_POLICY_NAME']['enable'] = False

    # validate consistent ports
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
                answer = __ask_question(question=full_question, description=configs[param]['description'],
                                        param=param, error_msg=error_msg)
                if param in ['DB_TYPE', 'AUTOCOMMIT', 'SYSTEM_QUERY', 'MEMORY', 'NOSQL_ENABLE', 'NOSQL_TYPE',
                             'NOSQL_BLOBS_DBMS', 'NOSQL_BLOBS_FOLDER', 'NOSQL_BLOBS_COMPRESS', 'NOSQL_BLOBS_REUSE']:
                    if answer != "" and answer not in configs[param]['options']:
                        print(f'Invalid value {answer}. Please try again...')
                    elif answer != "":
                        configs[param]['value'] = answer
                        status = True
                    else:
                        configs[param]['value'] = configs[param]['default']
                        status = True
                else:
                    configs[param]['value'] = answer
                    status = True
            if param == 'DB_TYPE' and configs[param]['value'] == 'sqlite':
                for prm in ['DB_USER', 'DB_PASSWD', 'DB_IP', 'DB_PORT']:
                    configs[prm]['enable'] = False
            elif param == 'SYSTEM_QUERY' and configs[param]['value'] == 'false':
                configs['MEMORY']['enable'] = False
                configs['MEMORY']['value'] = False
            elif param == 'NOSQL_ENABLE' and configs[param]['value'] == 'false':
                for prm in configs:
                    if 'NOSQL' in param:
                        configs[prm]['enable'] = False

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
                answer = __ask_question(question=full_question, description=configs[param]['description'],
                                        param=param, error_msg=error_msg)
                if param == 'LEDGER_CONN':
                    # need to change to support etherium blockchain
                    #if re.search(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\:[30000-32767]', answer):
                    #   configs[param]['value'] = answer
                    #   status = True
                    if answer == "":
                        configs[param]['value'] = configs[param]['default']
                        status = True
                    else:
                       configs[param]['value'] = answer
                       status = True
                        #error_msg = f"Invalid LEDGER_CONN information value {answer}. Please try again... "
                elif param == 'SYNC_TIME':
                    if answer == "":
                        configs[param]['value'] = configs[param]['default']
                        status = True
                    elif answer[-1] == "s":
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
                    elif answer != "":
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
                answer = __ask_question(question=full_question, description=configs[param]['description'],
                                        param=param, error_msg=error_msg)
                if param in ['ENABLE_HA', 'ENABLE_PARTITIONS', 'CREATE_TABLE', 'UPDAE_TSD_INFO', 'ARCHIVE', 'COMPRESS_FILE']:
                    if answer not in configs[param]['options'] and answer != "":
                        error_msg = f"Invalid value {answer}. Please try again... "
                    elif answer in configs[param]['options']:
                        configs[param]['value'] = answer
                        status = True
                    if answer == "" or answer == 'false':
                        configs[param]['value'] = configs[param]['default']
                        if param == 'ENABLE_HA':
                            configs['START_DATE']['enable'] = False
                        elif param == 'ENABLE_PARTITIONS':
                            for config in ['TABLE_NAME', 'PARTITION_COLUMN', 'PARTITION_INTERVAL', 'PARTITION_KEEP',
                                           'PARTITION_SYNC']:
                                configs[config]['enable'] = False
                        status = True
                elif param == 'START_DATE':
                    if answer != "":
                        try:
                            answer = int(answer)
                        except:
                            error_msg = f"Invalid value {answer}. Please try again... "
                        else:
                            configs[param]['value'] = f"-{answer}d"
                            status=True
                    else:
                        configs[param]['value'] = f"-{configs[param]['default']}d"
                        status = True
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
                elif answer != "":
                    configs[param]['value'] = answer
                    status = True
                else:
                    configs[param]['value'] = configs[param]['default']
                    status = True
        else:
            configs[param]['value'] = configs[param]['default']
            status = True

    return configs


def publisher_questions(configs:dict)->dict:
    """
    Generate questions for publisher configurations
    :args:
        configs:dict - database configurations
    :note:
        for  ['DBMS_FILE_LOCATION', 'TABLE_FILE_LOCATION'] convert int value to file_name[X]
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
                answer = __ask_question(question=full_question, description=configs[param]['description'],
                                        param=param, error_msg=error_msg)
                if param in ['DBMS_FILE_LOCATION', 'TABLE_FILE_LOCATION']:
                    if answer != "":
                        try:
                            answer = int(answer)
                        except:
                            error_msg = f"Invalid value {answer}. Please try again... "
                        else:
                            configs[param]['value'] = f"file_name[{answer}]"
                            status = True
                    else:
                        configs[param]['value'] = f"file_name[{configs[param]['default']}]"
                        status = True
                elif param == 'COMPRESS_FILE' and answer != "":
                    if answer not in configs[param]['options'] and answer != "":
                        error_msg = f"Invalid value {answer}. Please try again... "
                    elif answer in configs[param]['options']:
                        configs[param]['value'] = answer
                        status = True
                else:
                    configs[param]['value'] = configs[param]['default']
                    status = True

    return configs


def authentication_questions(configs:dict)->dict:
    """
    Generate questions for authentication configurations
    :notes:
        need to write code in AnyLog deployment script to support authentication. As such, process is disabled in
        deployment main.
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
            status = False
            full_question = __generate_question(configs=configs[param])
            error_msg = ""
            while status is False:
                answer = __ask_question(question=full_question, description=configs[param]['description'], param=param,
                                        error_msg=error_msg)
                if answer == '':
                    configs[param]['value'] = configs[param]['default']
                    status = True
                elif ('options' in configs[param] and answer in configs[param]['options']) or ('options' not in configs[param] and answer != ''):
                    configs[param]['value'] = answer
                    status = True
                else:
                    error_msg = f"Invalid value {answer}. Please try again... "

                if param in ['ENABLE_REST_AUTH'] and configs[param]['value'] == 'false':
                    for sub_param in ['NODE_PASSWORD', 'USER_NAME', 'USER_PASSWORD', 'USER_TYPE', 'ROOT_PASSWORD']:
                        configs[sub_param]['enable'] = False

    return configs


def mqtt_questions(configs:dict)->dict:
    """
    Generate questions for MQTT configurations
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
                answer = __ask_question(question=full_question, description=configs[param]['description'],
                                        param=param, error_msg=error_msg)
                if param in ['ENABLE_MQTT', 'MQTT_LOG'] and answer != '':
                    if answer not in configs[param]['options']:
                        error_msg = f"Invalid value {answer}. Please try again... "
                    else:
                        configs[param]['value'] = answer
                        status = True
                elif answer != '':
                    configs[param]['value'] = answer
                    status = True
                else:
                    configs[param]['value'] = configs[param]['default']
                    status = True
            if param == 'ENABLE_MQTT' and configs['ENABLE_MQTT']['value'] == 'false':
                for sub_param in configs:
                    if sub_param != "ENABLE_MQTT":
                        configs[sub_param]['enable'] = False

    return configs


def advanced_settings(configs:dict)->dict:
    """
    Generate questions for advanced settings configurations
    :args:
        configs:dict - database configurations
    :params:
        status:bool
        error_msg:str - error message
        full_question:str - question
        answer:str - user input
        str_answer:str - when needing to separate between between REST and
    :return:
        updated configs
    """
    for param in configs:
        if configs[param]['enable'] is True:
            error_msg = ""
            full_question = __generate_question(configs=configs[param])
            status = False
            while status is False:
                answer = __ask_question(question=full_question, description=configs[param]['description'],
                                        param=param, error_msg=error_msg)
                if param in ['DEPLOY_LOCAL_SCRIPT', 'WRITE_IMMEDIATE'] and answer != "":
                    if answer not in configs[param]['options']:
                        error_msg = f"Invalid value {answer}. Please try again... "
                    else:
                        configs[param]['value'] = answer
                        status = True
                elif param in ['TCP_THREAD_POOL', 'REST_THREADS', 'QUERY_POOL', 'REST_TIMEOUT'] and answer != '':
                    try:
                        answer = int(answer)
                    except Exception as error:
                        error_msg = f"Invalid value {answer}. Please try again..."
                    else:
                        if answer < configs[param]['default'] and param != 'REST_TIMEOUT':
                            error_msg = f"Value {answer} is out of range, minimum value is {configs[param]['default']}. Please try again... "
                        elif param == 'REST_TIMEOUT' and -1 >= answer:
                            error_msg = f"Value {answer} is out of range minimum value is 0. Please try again... "
                        else:
                            configs[param]['value'] = answer
                            status = True
                elif param in ['THRESHOLD_TIME', 'THRESHOLD_VOLUME'] and answer != '':
                    answer = answer.replace(" ", "")
                    str_answer = ''.join([i for i in answer if not i.isdigit()]).strip()
                    if str_answer.lower() not in configs[param]['options'] and str_answer.upper() not in configs[param]['options']:
                        error_msg = f"Invalid value {answer}. Please try again"
                    else:
                        configs[param]['value'] = answer
                        status = True
                else:
                    configs[param]['value'] = configs[param]['default']
                    status = True

    return configs
