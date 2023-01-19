import os
import support
import questionnaire


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


def __kubernetes_prep(node_name:str, configs:dict)->dict:
    """
    Prepare default values for Kubernetes configurations
    :args:
        node_name:str - node name
        configs:dict  configurations
    :return:
        configurations with updated values
    """
    node_name = node_name.replace(' ', '-').replace('_', '-')
    configs['metadata']['hostname']['default'] = node_name
    for param in ['app', 'pod', 'service', 'configmap']:
        configs['metadata'][f'{param}_name']['default'] = f"{node_name}-{param}"
    for param in ['anylog', 'blockchain', 'data']:
        configs['volume'][f'{param}_volume']['default'] = f'{node_name}-{param}-volume'

    return configs


def __question(configs:dict)->dict:
    for param in configs:
        error_msg = ""
        if param  != 'default':
            full_question = __generate_question(configs=configs[param])
            status = False
            while status is False:
                answer = __ask_question(question=full_question, description=configs[param]['description'], param=param,
                                        error_msg=error_msg)
                if 'options' in configs[param] and answer not in configs[param] and answer != '':
                    print(f'Invalid answer {answer}. Please try again... ')
                elif answer != '':
                    configs[param]['value'] = answer
                    status = True
                else:
                    configs[param]['value'] = configs[param]['default']
                    status = True

    return configs


def questionnaire(node_name:str, configs:dict)->dict:
    configs = __kubernetes_prep(node_name=node_name, configs=configs)
    print('--- Kubernetes Metadata Configurations ---')
    for section in configs:
        status = support.print_questions(configs[section])
        if status is True:
            print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
            if section != 'volume':
                configs[section] = __question(configs=configs[section])
            else:
                for sub_section in configs[section]:
                    if sub_section == 'enable_volume':
                        sub_configs = {
                            'enable_volume': configs[section]['enable_volume']
                        }
                        output = __question(configs=sub_configs)
                        configs[section]['enable_volume'] = output['enable_volume']
                    else:
                        print(f'\t--> Volume: {sub_section}')
                        configs[section][sub_section] = __question(configs=configs[section][sub_section])

    return configs







