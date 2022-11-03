# Adding New Configurations
1. In [configurations.json](configurations.json), add a new JSON object above "advanced settings" section.
```json
{
  "section name": {
    "GENERIC_PARAM": {
        "question": "question regarding parameter",
        "description": "parameter description",
        "enable": "Whether or not to show parameter to user",
        "default": "default value",
        "value": "empty value waiting for user to input data"
    },
    "OPTIONS_PARAM": {
        "question": "question regarding parameter",
        "description": "parameter description",
        "enable": "Whether or not to show parameter to user",
        "default": "default value",
        "options": "list of options to choose from",
        "value": "empty value waiting for user to input data"
    },
    "INT_PARAM": {
        "question": "question regarding parameter",
        "description": "parameter description",
        "enable": "Whether or not to show parameter to user",
        "default": "default value (should be min value)",
        "value": "empty value waiting for user to input data"
    }
  }
}
```

2. In [questionnaire.py](questionnaire.py), create a method that asks user(s) to fill in the new configuration
```python
def section_questions(configs:dict)->dict: 
    """
    Sample configuration questionnaire method
    :args: 
        configs:dict - dictionary of configuration just of the section that the method is dealing with
    :params:
        error_msg:str - error message 
        full_question:str - generated question
        status:bool - whether or not answer satisfies parameter
        answer:str - answer based on user input
    :return: 
        configs with value being set either by user-input or default value
    """
    for param in configs: 
        if configs[param]['enable'] is True: # validate if user should view configuration 
            error_msg = "" # set error message 
            full_question = __generate_question(configs=configs[param]) # generate question 
            status = False 
            while status is False: # whether or not user answered question
                # ask question 
                answer = __ask_question(question=full_question, description=configs[param]['description'], 
                                        param=param, error_msg=error_msg)
                if param == 'OPTIONS_PARAM' and answer != "": # sample for list of options     
                    if answer not in configs[param]['options']: # check if answer is in list of options  
                        error_msg = f"Invalid value {answer}. Please try again... " 
                    else: # if valid answer then set value & update status to true 
                        configs[param]['value'] = answer
                        status = True
                elif param == 'INT_PARAM' and answer != "": # sample for integer value configuration
                    try: 
                        answer = int(answer) # convert value to int 
                    except Exception as error: # set error if fails to convert
                        error_msg = f"Invalid value {answer}. Please try again..."
                    else: 
                        if answer < configs[param]['default']: # validate answer is >= than the default value  
                            error_msg = f"Value {answer} is out of range, minimum value is {configs[param]['default']}. Please try again... "
                        else: # if valid answer then set value & update status to true
                            configs[param]['value'] = answer
                            status = True
                elif answer != "": # not an empty answer and has no conditions to check
                    configs[param]['value'] = answer
                    status = True
                else: # if answer is empty then use default value
                    configs[param]['value'] = configs[param]['default']
                    status = True
    
    return configs
```

3. In [main.py](main.py), add an `elif` condition to process the new configurations

4. Make sure the new configuration(s)  are supported by AnyLog
