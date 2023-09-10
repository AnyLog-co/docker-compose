import ast
import re

from __support__ import validate_ledger
# from __support__ import validate_ports, validate_ips, validate_ledger

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
            params += f"[{options}]"
        else:
            params += f" | {options}"
    if rng != "":
        if params == " ":
            params += f"[{rng}]"
        else:
            params += f" | {rng}"
    if params == " ":
        params = ": "
    else:
        params += "]: "

    return f"{question}{params}"


def __ask_question(question:str, param:str, description:str, default=None, options:list=None, rng:list=None, err_msg:str=""):
    status = False
    while status is False:
        if err_msg.strip() != "":
            err_msg = err_msg.strip() + " "
        user_input = input(f"\t{err_msg}{question}").strip()
        if user_input == 'help':
            err_msg = ""
            print(f"\t`{param}` param description - {description}")
            continue
        elif user_input == "":
            user_input = default
            status = True
        elif options is not None and user_input not in options:
            err_msg = f"Invalid value {user_input} for {param.title().replace('_', ' ')}... "
        elif rng is not None:
            try:
                user_input = int(user_input)
            except Exception as error:
                err_msg = f"Invalid value {user_input} type for {param.title().replace('_', ' ')}..."
            else:
                if user_input < rng[0] or user_input > rng[1]:
                    err_msg = f"Value for {param.title().replace('_', ' ')} is out of range..."
                else:
                    status = True
        else:
            status = True

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

        if not isinstance(user_input, int) or user_input <= 0:
            status = False
            err_msg = "Operator number must be a positive integer value, please try again"

    return user_input

def general_configs(configs):
    for param in configs:
        configs[param]['value'] = configs[param]['default']
        if configs[param]['enable'] is True:
            status = False
            err_msg = ""
            while status is False:
                configs[param] = __get_answer(param=param, configs=configs[param], err_msg=err_msg)
                if param in ['LICENSE_KEY', 'NODE_TYPE', 'COMPANY_NAME'] and configs[param]['value'] == "":
                    err_msg = f"Missing {param.replace('_', ' ').lower()} value... "
                    continue
                else:
                    status = True

            if param in ['LOCATION', 'COUNTRY', 'STATE', 'CITY'] and configs[param]['value'] == configs[param]['default']:
                configs[param]['value'] = ""
    return  configs

def blockchain_section(configs:dict):
    for param in configs:
        configs[param]['value'] = configs[param]['default']
        if configs[param]['enable'] is True:
            status = False
            err_msg = ""
            while status is False:
                configs[param] = __get_answer(param=param, configs=configs[param], err_msg="")
                if param == 'LEDGER_CONN':
                    ledger_conn, err_msg =  validate_ledger(ledger_conn=configs[param]['VALUE'])
                    if err_msg == "":
                        status = True


    return configs
