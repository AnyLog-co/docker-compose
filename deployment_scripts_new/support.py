def prepare_mqtt_params(configs:dict, db_name:str, port:int, user:str, password:str)->dict:
    """
    update the default MQTT parameters to match information already provided by the user.
    :args:
        configs:dict - (preset) MQTT configurations
        db_name:str - default logical database
        port:int - AnyLog broker port
        user:str - authentication user
        password:str - authentication user
    :return:
        (updated) configs
    """
    configs['MQTT_DBMS']['default'] = db_name
    # if local broker port is set, then update configs accordingly
    if port != "":
        configs['MQTT_PORT']['default'] = port
        configs['MQTT_BROKER']['default'] = 'local'
        configs['MQTT_USER']['default'] = user
        configs['MQTT_PASSWD']['default'] = password

    return configs


def merge_configs(default_configs:dict, updated_configs:dict)->dict:
    """
    Given 2 sets of configurations merge them into a single dictionary
    :args:
        default_configs:dict - the original (or default) configurations
        updated_configs:dict - the new (user defined configurations)
    :return:
        merged configurations of default_configs
    """
    for key in updated_configs:
        if isinstance(updated_configs[key], dict):
            """
            either YAML or JSON file, in which case we need to go section by section 
            """
            if key in default_configs:
                for param in updated_configs[key]:
                    if param in default_configs[key]:
                        default_configs[key][param]['default'] = updated_configs[key][param]
                        # default_configs[key][param]['default'] = updated_configs[param]
        else:
            for key in default_configs:
                for param in updated_configs:
                    if param in default_configs[key]:
                        default_configs[key][param]['default'] = updated_configs[param]

    return default_configs


def print_questions(configs:dict)->bool:
    """
    Whether or not to print question
    :args:
        configs:dict - configuration
    :param:
        status:bool
    :return:
        if one or more of the config params is enabled return True, else returns False
    """
    for param in configs:
        if configs[param]['enable'] is True:
            return True
    return False

