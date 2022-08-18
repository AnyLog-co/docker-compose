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
import copy
import os
import re


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


def __validate_range(value:int, range:list)->bool:
    """
    Given a range, validate value within range
    :args:
        value:int - value within range
        range:list - range of values to compare [smaller, larger]
    :params:
        status:bool
    :return:
        if within range return True, else False
    """
    status = True
    if value < range[0] or value > range[1]:
        status = False
    return status


def __validate_ports(ports:dict)->dict:
    """
    Validate ports are unique
    :process:
        1. check if any 2 port values are the same
        2. print error
        3. reask for port values
    repeat until all values are unique
    :args:
        ports:dict - subset of section_params, for AnyLog network ports
    :return:
        ports
    """
    validate = False
    if (ports['ANYLOG_SERVER_PORT']['value'] == ports['ANYLOG_REST_PORT']['value'] or
        ports['ANYLOG_SERVER_PORT']['value'] == ports['ANYLOG_BROKER_PORT']['value'] or
        ports['ANYLOG_REST_PORT']['value'] == ports['ANYLOG_BROKER_PORT']['value']):
        validate = True

    while ports['ANYLOG_SERVER_PORT']['value'] == ports['ANYLOG_REST_PORT']['value']:
        print(f'REST Port is set to the same value as TCP Port')
        port = questions(section_params={'ANYLOG_REST_PORT': ports['ANYLOG_REST_PORT']})
        ports['ANYLOG_REST_PORT'] = port['ANYLOG_REST_PORT']

    while ports['ANYLOG_SERVER_PORT']['value'] == ports['ANYLOG_BROKER_PORT']['value']:
        print(f'Broker Port is set to the same value as TCP Port')
        port = questions(section_params={'ANYLOG_BROKER_PORT': ports['ANYLOG_BROKER_PORT']})
        ports['ANYLOG_BROKER_PORT'] = port['ANYLOG_BROKER_PORT']

    while ports['ANYLOG_REST_PORT']['value'] == ports['ANYLOG_BROKER_PORT']['value']:
        print(f'Broker Port is set to the same value as REST Port')
        port = questions(section_params={'ANYLOG_BROKER_PORT': ports['ANYLOG_BROKER_PORT']})
        ports['ANYLOG_BROKER_PORT'] = port['ANYLOG_BROKER_PORT']

    if validate is True: # once all three params are changed, validate values are actualy unique
        ports = __validate_ports(ports=ports)

    return ports


def __validate_ledger(ledger_obj:dict)->dict:
    """
    Validate Ledger connection information
    :args:
        ledger_conn:dict - ledger dictonary object
    :params:
        status:bool
        ip:str,port:int - extraction from ledger_conn object
        ip_status:bool - whether IP address is valid
        port_status:bool - whether Pot value is valid
    :return:
        ledger_obj
    """
    status = False

    while status is False:
        if ':' not in ledger_obj['LEDGER_CONN']['value']:
            print('Invalid Master Node credentials. Format: ${IP}:${ANYLOG_TCP_PORT}')
        else:
            ip, port = ledger_obj['LEDGER_CONN']['value'].split(':')
            ip_status = re.match(r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$", ip)
            try:
                port = int(port)
            except Exception:
                port_status = False
            else:
                port_status = __validate_range(value=int(port), range=[30000, 32767])
            if ip_status is False or port_status is False:
                print(f'Invalid Master Node connection infromation value {ledger_obj["LEDGER_CONN"]["value"]}')
            else:
                status = True
        if status is False:
            ledger_obj = questions(section_params=ledger_obj)

    return ledger_obj['LEDGER_CONN']


def questions(section_params:dict)->dict:
    updated_section_params = copy.deepcopy(section_params)
    for key in section_params:
        if 'value' in section_params[key] and section_params[key]['value'] == "" and key in updated_section_params:
            status = False
            question = f"\t{section_params[key]['question']}"

            sub_question = ""
            if 'default' in section_params[key] and section_params[key]['default'] != '':
                sub_question = f"default: {section_params[key]['default']}"
            if 'options' in section_params[key]:
                options = str(section_params[key]['options']).split('[')[-1].split(']')[0].replace("'", '')
                if sub_question != "":
                    sub_question += f" | options: {options}"
                else:
                    sub_question = f"options: {options}"
            elif 'range' in section_params[key]:
                rng = str(section_params[key]['range']).split('[')[-1].split(']')[0].replace(', ', ',').replace(' ,', ',').replace(',', '-')
                if sub_question != "":
                    sub_question += f" | range: {rng}"
                else:
                    sub_question = f"range: {rng}"
            question += f" [{sub_question}]: "

            while status is False:
                user_input = input(question).rstrip().lstrip()
                try:
                    user_input = int(user_input)
                except Exception:
                    if user_input == 'true':
                        user_input = True
                    elif user_input == 'false':
                        user_input = False

                if user_input == 'help':
                    print(f'{key} - {section_params[key]["description"]}')
                elif user_input == '':
                    status = True
                    if user_input == '' and section_params[key]['default'] != '':
                        updated_section_params[key]['value'] = section_params[key]['default']
                elif 'options' in section_params[key]:
                    if not __validate_options(value=user_input, options=section_params[key]['options']):
                        print(f'Invalid value "{user_input}" for {key}. Options: {options}')
                    else:
                        updated_section_params[key]['value'] = user_input
                        status = True
                elif 'range' in section_params[key]:
                    if not __validate_range(value=user_input, range=section_params[key]['range']):
                        print(f'Value {key} is out of range at {user_input}. Value Range: {rng}')
                    else:
                        updated_section_params[key]['value'] = user_input
                        status = True
                else:
                    updated_section_params[key]['value'] = user_input
                    status = True

            # based on params remove ones that are not needed
            if key == 'DB_TYPE' and updated_section_params[key]['value'] == 'sqlite':
                for param in ['DB_IP', 'DB_PORT', 'DB_USER', 'DB_PASSWD']:
                    del updated_section_params[param]
            elif key == 'ENABALE_MQTT' and updated_section_params[key]['value'] is False:
                for param in ['BROKER', 'PORT', 'MQTT_USER', 'MQTT_PASSWORD', 'MQTT_LOG', 'MQTT_TOPIC_NAME',
                              'MQTT_TOPIC_DBMS', 'MQTT_TABLE_NAME', 'MQTT_TOPIC_TIMESTAMP', 'MQTT_COLUMN_VALUE',
                              'MQTT_COLUMN_VALUE_TYPE']:
                    del updated_section_params[param]
            # if key is DEPLOY_SYSTEM_QUERY + set to False then set memory to false as well
            elif key == 'DEPLOY_SYSTEM_QUERY' and updated_section_params[key]['value'] is False:
                updated_section_params['MEMORY']['default'] = False
                section_params['MEMORY']['default'] = False
                section_params['MEMORY']['value'] = False


    # validate ports are not the same
    if 'ANYLOG_SERVER_PORT' in updated_section_params and 'ANYLOG_REST_PORT' in updated_section_params and 'ANYLOG_BROKER_PORT' in updated_section_params:
        ports = {
            'ANYLOG_SERVER_PORT': updated_section_params['ANYLOG_SERVER_PORT'],
            'ANYLOG_REST_PORT': updated_section_params['ANYLOG_REST_PORT'],
            'ANYLOG_BROKER_PORT': updated_section_params['ANYLOG_BROKER_PORT']
        }
        ports = __validate_ports(ports=ports)
        updated_section_params['ANYLOG_SERVER_PORT'] = ports['ANYLOG_SERVER_PORT']
        updated_section_params['ANYLOG_REST_PORT'] = ports['ANYLOG_REST_PORT']
        updated_section_params['ANYLOG_BROKER_PORT'] = ports['ANYLOG_BROKER_PORT']
    elif 'LEDGER_CONN' in updated_section_params: # validate master connnection information is correct
       updated_section_params['LEDGER_CONN'] = __validate_ledger(ledger_obj={'LEDGER_CONN': updated_section_params['LEDGER_CONN']})


    return updated_section_params

