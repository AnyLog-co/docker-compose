import os
import support
import questionnaire


def __metadata_questions(configs:dict, node_name:str='anylog-node')->dict:
    """
    Generate questions for Kubernetes metadata information
    :args:
        configs:dict - configurations to be updated
        node_name:str - node name
    :params:
        status:bool
        error_msg:str - error message if value is invalid
        full_question:str - generated question
        answer:str - user input
    :return:
        configs
    """
    configs['hostname']['default'] = node_name
    configs['app_name']['default'] = f'{node_name}-app'
    configs['pod_name']['default'] = f'{node_name}-pod'
    configs['app_name']['default'] = f'{node_name}-deployment'
    configs['service_name']['default'] = f'{node_name}-svs'
    configs['configmap_name']['default'] = f'{node_name}-configs'


    for param in configs:
        status = False
        error_msg = ""
        if configs[param]['enable'] is True:

            while status is False:
                full_question = questionnaire.__generate_question(configs=configs[param])
                answer = questionnaire.__ask_question(question=full_question, description=configs[param]['description'],
                                                      param=param, error_msg=error_msg)
                if answer != "" and param == 'replicas':
                    try:
                        answer = int(answer)
                    except Exception as error:
                        error_msg = f"Invalid value for {param} - must be inteeger type (Error: {error})"
                    else:
                        configs[param]['value'] = answer
                        status = True
                elif answer == "":
                    configs[param]['value'] = configs[param]['default']
                    status = True
                else:
                    configs[param]['value'] = answer
                    status = True

    return configs


def __image_questions(configs:dict, build:str='develop')->dict:
    """
    Generate questions for Kubernetes image information
    :args:
        configs:dict - configurations to be updated
        build:str - AnyLog version (aka docker tag)
    :params:
        status:bool
        error_msg:str - error message if value is invalid
        full_question:str - generated question
        answer:str - user input
    :return:
        configs
    """
    configs['tag']['default'] = build

    for param in configs:
        status = False
        error_msg = ""
        if configs[param]['enable'] is True:
            while status is False:
                full_question = questionnaire.__generate_question(configs=configs[param])
                answer = questionnaire.__ask_question(question=full_question, description=configs[param]['description'],
                                                      param=param, error_msg=error_msg)
                if 'options' in configs[param] and answer not in configs[param]['options'] and answer != "":
                    error_msg = f"Invalid value for {answer}."
                elif answer == "":
                    configs[param]['value'] = configs[param]['default']
                    status = True
                else:
                    configs[param]['value'] = answer
                    status = True
    return configs


def __enable_volume()->str:
    """
    Check whether to enable volume for AnyLog
    :params:
        status:bool
        error_msg:str - error message if value is invalid
        full_question:str - generated question
        answer:str - user input
    :return:
        answer (true or false)
    """
    status = False
    error_msg = ""
    while status is False:
        full_question = "Enable Volumes [default: true | options: true, false]: "
        answer = questionnaire.__ask_question(question=full_question,
                                              description='Whether or not to enable volumes for AnyLog',
                                              param='enable_volume', error_msg=error_msg)
        if answer != '' and answer not in ['true', 'false']:
            error_msg = f"Invalid value for `enale_volume`"
        elif answer == "":
            answer = 'true'
            status = True

    return answer

def __volume_questions(configs:dict)->dict:
    """
    Generate questions for Kubernetes volume information
    :args:
        configs:dict - configurations to be updated
        build:str - AnyLog version (aka docker tag)
    :params:
        status:bool
        error_msg:str - error message if value is invalid
        full_question:str - generated question
        answer:str - user input
    :return:
        configs
    """
    for param in configs:
        status = False
        error_msg = ""
        if configs[param]['enable'] is True:
            while status is False:
                full_question = questionnaire.__generate_question(configs=configs[param])
                answer = questionnaire.__ask_question(question=full_question, description=configs[param]['description'],
                                                      param=param, error_msg=error_msg)
                if 'options' in configs[param] and answer not in configs[param]['options'] and answer != "":
                    error_msg = f"Invalid value for {answer}."
                elif answer == "":
                    configs[param]['value'] = configs[param]['default']
                    status = True
                else:
                    configs[param]['value'] = answer
                    status = True
    return configs


def kubernetes_configurations(config_file:str, node_name:str='anylog-node', build:str='develop')->dict:
    """
    Given a kubernetes configuration file, prepare configurations for deployment
    :args:
        config_file:str - kubernetes configuration file
        node_name:str - node name
        build:str - AnyLog version (aka docker tag)
    :params:
        kubernetes_configs:dict - preset kubernetes configurations
    :return:
    """
    config_file = os.path.expanduser(os.path.expandvars(config_file))
    if os.path.isfile(config_file):
        kubernetes_configs = support.json_read_file(file_name=config_file)
    else:
        print(f'Failed to locate: {config_file}')
        return

    node_name = node_name.replace(' ', '-').replace('_', '-')

    for config in kubernetes_configs:
        print(f'Section: {config.title()}')
        if config == 'metadata':
            kubernetes_configs[config] = __metadata_questions(configs=kubernetes_configs[config], node_name=node_name)
        elif config == 'image':
            kubernetes_configs[config] = __image_questions(configs=kubernetes_configs[config], build=build)
        elif config == 'volume':
            kubernetes_configs['volume']['anylog_volume']['name']['default'] = f'{node_name}-anylog-volume'
            kubernetes_configs['volume']['blockchain_volume']['name']['default'] = f'{node_name}-blockchain-volume'
            kubernetes_configs['volume']['data_volume']['name']['default'] = f'{node_name}-data-volume'
            for param in kubernetes_configs[config]:
                if param == 'enable_volume':
                    kubernetes_configs[config][param]['value'] = __enable_volume()
                else:
                    print(f'>> Subsection: {param.replace("_", " ").title()}')
                    kubernetes_configs[config][param] = __volume_questions(configs=kubernetes_configs[config][param])
        print('\n')

    return kubernetes_configs








