from __support__ import generate_question, ask_question, print_questions


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
    for param in ['app', 'pod', 'deployment', 'service', 'configmap']:
        configs['metadata'][f'{param}_name']['default'] = f"{node_name}-{param}"
    # for param in ['anylog', 'blockchain', 'data']:
    #     configs['volume'][f'{param}_volume']['default'] = f'{node_name}-{param}-volume'

    return configs


def __question(configs:dict)->dict:
    for param in configs:
        error_msg = ""
        if param  != 'default':
            full_question = generate_question(configs=configs[param])
            status = False
            while status is False:
                answer = ask_question(question=full_question, description=configs[param]['description'], param=param,
                                        error_msg=error_msg)
                if 'options' in configs[param] and answer not in configs[param]["options"] and answer != '':
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
        status = print_questions(configs[section])
        if status is True:
            print(f'Section: {section.title().replace("Sql", "SQL").replace("Mqtt", "MQTT")}')
            if section != 'volume':
                configs[section] = __question(configs=configs[section])
            else:
                for sub_section in configs[section]:
                    if sub_section in ['enable_volume', 'storage_classname']:
                        sub_configs = {
                            sub_section: configs[section][sub_section]
                        }
                        output = __question(configs=sub_configs)
                        configs[section][sub_section] = output[sub_section]
                    else:
                        print(f'\t--> Volume: {sub_section}')
                        configs[section][sub_section] = __question(configs=configs[section][sub_section])

    return configs







