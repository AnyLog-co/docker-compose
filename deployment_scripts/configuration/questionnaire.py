import ast


def __validate_options(value:str, options:list)->bool:
    """
    Validate if value is valid
    :args:
        value:str - value to check
        options:list - list of options to check against
    :params:
        status
    :return:
        if success returns True, else False
    """
    status = False
    if len(value.split(' ')) > 1:
        value = value.split(' ')[-1]
    if value in options:
        status = True
    return status


def __validate_range(value:int, min_value:int, max_value:int)->bool:
    """
    Validate value within range
    :args:
        value:int - value to validate
        min_value:int - min value in range
        max_value:int - max value in range
    :params:
        status:bool
    :return:
        if success return True, else False
    """
    status = False
    if min_value <= value <= max_value:
        status = True
    return status


def questions(section:dict)->dict:
    for topic in section:
        if section[topic]['default'] != '' and 'question' in section[topic] and 'value' in section[topic] and section[topic]['value'] == '':
            status = True
            options = f"[default: {section[topic]['default']}]"
            if 'options' in section[topic]:
                try:
                    options = options.replace(']', f" | options: {', '.join(section[topic]['options'])}]")
                except TypeError:
                    options = options.replace(']', f" | options: ")
                    for option in section[topic]['options']:
                        options += str(option)
                        if option != section[topic]['options'][-1]:
                            options += ", "
                        else:
                            options += "]"
            if 'range' in section[topic]:
                options = options.replace(']', f" | range: {section[topic]['range'][0]} - {section[topic]['range'][1]}]")


            question = f"\t{section[topic]['question']} {options}: "
            while status is True:
                user_input = input(question)
                if not user_input:
                    section[topic]['value'] = section[topic]['default']
                    status = False
                elif user_input == 'help':
                    print(f"Question description: section[topic]['description'] ")
                else:
                    user_input = ast.literal_eval(user_input.rstrip().lstrip())
                    if 'options' in section[topic]:
                        param_status = __validate_options(value=user_input, options=section[topic]['options'])
                        if param_status is False:
                            print(f'\n\tInvalid value {user_input} for {topic}...\n')

                    if 'range' in section[topic]:
                        param_status = __validate_range(value=user_input, min_value=section[topic]['range'][0], max_value=section[topic]['range'][1])
                        if param_status is False:
                            print(f'\n\tValue {user_input} is out of range...\n')
                    if param_status is True:
                        section[topic]['value'] = user_input
                        status = False


