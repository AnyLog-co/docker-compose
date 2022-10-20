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
        params += f" | options: {''.join(configs['options'])}"
    if 'range' in configs:
        if params == "":
            params += "["
        params += f" | range: {'-'.join(map(str, configs['range']))}"

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
        if user_input == 'description':
            error_msg = ""
            print(f"\tparam description - {description}")
        else:
            status = True
    return user_input



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
                    try:
                        answer = int(answer)
                    except:
                        error_msg=f'Port value {answer} is invalid. Please try again... '
                    else:
                        if configs[param]["range"][0] <= answer <= configs[param]["range"][1]:
                            configs[param]['value'] = answer
                            status = True
                        else:
                            error_msg=f'Value {answer} out of range. Please try again... '
                else:
                    configs[param]['value'] = configs[param]['default']
                    status = True
    return configs


def validate_ports(tcp_port:int, rest_info:dict, broker_info:dict)->(dict, dict):
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
    while tcp_port == rest_info['value'] or rest_info['value'] == broker_port['value']:
        error_msg = f"Port Value {rest_info['value']} already used"
        status = False
        full_question = __generate_question(configs=rest_info)
        while status is False:
            answer = answer = __ask_question(error_msg=error_msg, question=full_question, description=rest_info['description'])
            try:
                answer = int(answer)
            except:
                error_msg = f'Port value {answer} is invalid. Please try again... '
            else:
                if configs[param]["range"][0] <= answer <= configs[param]["range"][1]:
                    rest_info['value'] = answer
                    status = True
                else:
                    error_msg = f'Value {answer} out of range. Please try again... '
        else:
            rest_info['value'] = configs[param]['default']
            status = True

    # check if Broker port is double used
    if broker_info['value'] != "":
        while tcp_port == broker_info['value'] or rest_info['value'] == broker_info['value']:
            error_msg = f"Port Value {broker_info['value']} already used"
            status = False
            full_question = __generate_question(configs=broker_info)
            while status is False:
                answer = answer = __ask_question(error_msg=error_msg, question=full_question, description=broker_info['description'])
                try:
                    answer = int(answer)
                except:
                    error_msg = f'Port value {answer} is invalid. Please try again... '
                else:
                    if configs[param]["range"][0] <= answer <= configs[param]["range"][1]:
                        broker_info['value'] = answer
                        status = True
                    else:
                        error_msg = f'Value {answer} out of range. Please try again... '
            else:
                broker_info['value'] = broker_info['default']
                status = True

    return rest_info, broker_info


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
                if param in ["DB_PORT", "NOSQL_PORT"] and answer != "":
                        try:
                            answer = int(answer)
                        except:
                            error_msg=f'Port value {answer} is invalid. Please try again... '
                        else:
                            configs[param]['value'] = answer
                            status = True
                elif param in ['AUTOCOMMIT', 'SYSTEM_QUERY', 'MEMORY', 'ENABLE_NOSQL'] and answer != "":
                    if answer == 'true':
                        configs[param]['value'] = True
                    elif answer == 'false':
                        configs[param]['value'] = False
                    else:
                        error_msg = f"Invalid value {answer}. Please try again..."
                else:
                    configs[param]['value'] = configs[param]['default']
                    status = True
        # skip all other questions if DB_TYPE is SQLite or NoSQL is disabled 
        if param in ['DB_TYPE', 'ENABLE_NOSQL'] and configs['DB_TYPE']['value'] == 'sqlite' or configs['ENABLE_NOSQL']['value'] is False:
            return configs 
             
    return configs

