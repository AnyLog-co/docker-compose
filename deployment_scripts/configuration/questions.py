"""
Updates needed:
--------------
1. default true for system_query under Query node
2. hide complex params
    - other
    - advanced operator
    - advanced publisher -- all of them should just have default value(s)
    - external / local IPs
    - add k8s proxy IP for K8s deployment
3. if / else for operator
4. better testing for user input
5. add default from file
"""
import argparse
import copy
import json
import os
import requests
import socket
import file_io


def __validate_options(value:str, options:list)->bool:
    """
    Validate value is valid based on list of options
    :args:
        value:str - value to validate
        options:list - list of options to validate against
    :params:
        status:bool
    :return:
        if valid params return True, else False
    """
    status = True
    if isinstance(value, bool) and value in options:
        pass
    elif isinstance(value, str):
        value = ''.join(element for element in value if not element.isdigit()).strip()
        if value[-1] == 's':
            value = value[:len(value)-1]
        if value not in options:
            status = False
    return status


def __validate_rage(value:int, range:list)->bool:
    status = True
    if value < range[0] or value > range[1]:
        status = False
    return status


def questions(section_name:str, section_params:str)->dict:
    """
    Allow for user(s) to input values for configurations
    :args:
        section_name:str - section name
        section_params:dict - section parameters
    :params:
        status:bool
        updated_section_params:dict - dictionary copy of section_params, that gets updated.
        stmt:str - generated user input question
    :return:
        updated params
    """
    updated_section_params = copy.deepcopy(section_params)
    for param in section_params:
        # if database is SQLite remove non-SQLite params
        if section_name == 'database' and updated_section_params['DB_TYPE']['value'] == 'sqlite' and param in ['DB_IP', 'DB_PORT', 'DB_USER', 'DB_PASSWD']:
            del updated_section_params[param]
        # if MQTT is disabled, do not ask about other params - but don't remove either
        elif section_name == 'mqtt' and updated_section_params['ENABLE_MQTT']['value'] == False:
            pass
        elif 'value' in section_params[param]:
            status = False
            stmt = "\t" + param.replace('_', ' ').lower().title().replace('Mqtt', 'MQTT').replace('Ip', 'IP').replace('Anylog', 'AnyLog').replace('Db', 'DB')
            if section_params[param]['default'] != '':
                stmt += f" [default: {section_params[param]['default']}"
            if 'options' in section_params[param] and section_params[param]['default'] != '':
                stmt += f" | options: {str(section_params[param]['options']).split('[', 1)[-1].split(']', 1)[0]}]: "
            elif 'options' in section_params[param]:
                stmt += f" [options: {str(section_params[param]['options']).split('[', 1)[-1].split(']', 1)[0]}]: "
            elif 'range' in section_params[param] and section_params[param]['default'] != '':
                stmt += f" | range: {section_params[param]['range'][0]} - {section_params[param]['range'][1]}]: "
            elif 'range' in section_params[param]:
                stmt += f" [range: {section_params[param]['range'][0]} - {section_params[param]['range'][1]}]: "
            else:
                stmt += "]: "

            while status is False:
                value = input(stmt)
                try:
                    value = int(value)
                except Exception as error:
                    if value == 'true':
                        value = True
                    elif value == 'false':
                        value = False

                if value == 'help':
                    print(f"{param} - {section_params[param]['description']}")
                elif value == '':
                    updated_section_params[param]['value'] = section_params[param]['default']
                    status = True
                elif 'options' in section_params[param]:
                    if not __validate_options(value=value, options=section_params[param]['options']):
                        print(f"\tInvalid value '{value}' for {param}")
                    else:
                        updated_section_params[param]['value'] = value
                        status = True
                elif 'range' in section_params[param]:
                    if not __validate_rage(value=value, range=section_params[param]['range']):
                        print(f"\tValue ot of range. Allowed Range: {section_params[param]['range'][0]} - {section_params[param]['range'][1]}")
                    elif param in ['ANYLOG_REST_PORT', 'ANYLOG_BROKER_PORT']:
                        if value == section_params['ANYLOG_SERVER_PORT']['value']:
                            print(f"\tPort {value} is already taken by ANYLOG_TCP_PORT")
                        elif value == section_params['ANYLOG_REST_PORT']['value']:
                            print(f"\tPort {value} is already taken by ANYLOG_REST_PORT")
                    else:
                        updated_section_params[param]['value'] = value
                        status = True
                elif section_params[param]['default'] == '' and value == '':
                    status = True

    return updated_section_params
