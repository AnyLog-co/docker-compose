@echo off
REM The following code initiates a Python3 script that helps setup configurations for an AnyLog instance.

REM Function to display node type options
:function_display_node_type_options
echo Node type options to deploy:
echo     generic - sandbox for understanding AnyLog as only TCP & REST are configured
echo     master - a database node replacing an actual blockchain
echo     operator - node where data will be stored
echo     publisher - node to distribute data among operators
echo     query - node dedicated to master node (installed with Remote-CLI)
echo     info - display node type options
exit /b
:end

REM Function to validate yes/no options
:function_validate_yes_no_option
set /p "input=%~1: "
:loop
if "%input%"=="y" exit /b 0
if "%input%"=="n" exit /b 1
set /p "input=Invalid option: %input%. %~1: "
goto loop
:end

set /p "NODE_TYPE=Node Type [default: generic | options: generic, master, operator, publisher, query, info]: "
if "%NODE_TYPE%"=="info" call :function_display_node_type_options

REM Loop until a valid node type is provided
:loop_node_type
if "%NODE_TYPE%"=="" set "NODE_TYPE=generic"
if not "%NODE_TYPE%"=="generic" if not "%NODE_TYPE%"=="master" if not "%NODE_TYPE%"=="operator" if not "%NODE_TYPE%"=="publisher" if not "%NODE_TYPE%"=="query" goto :input_node_type
goto :end_loop_node_type
:input_node_type
set /p "NODE_TYPE=Invalid node type '%NODE_TYPE%'. Node Type [default: generic | options: generic, master, operator, publisher, query, info]: "
goto :loop_node_type
:end_loop_node_type

set /p "DEPLOYMENT_TYPE=Deployment Type [default: docker | options: docker, kubernetes]: "
if "%DEPLOYMENT_TYPE%"=="" set "DEPLOYMENT_TYPE=docker"
if not "%DEPLOYMENT_TYPE%"=="docker" if not "%DEPLOYMENT_TYPE%"=="kubernetes" goto :input_deployment_type
goto :end_loop_deployment_type
:input_deployment_type
set /p "DEPLOYMENT_TYPE=Invalid deployment type '%DEPLOYMENT_TYPE%'. Deployment Type [default: docker | options: docker, kubernetes]: "
goto :loop_deployment_type
:end_loop_deployment_type

call :function_validate_yes_no_option "Deploy Existing Configs [y/n]"
set "EXISTING_CONFIGS=%errorlevel%"

set /p "BUILD_TYPE=AnyLog Build Version [default: latest | options: latest, predevelop, test]: "
if "%BUILD_TYPE%"=="" set "BUILD_TYPE=latest"
if not "%BUILD_TYPE%"=="latest" if not "%BUILD_TYPE%"=="predevelop" if not "%BUILD_TYPE%"=="test" goto :input_build_type
goto :end_loop_build_type
:input_build_type
set /p "BUILD_TYPE=Invalid build type: %BUILD_TYPE%. AnyLog Build Version [default: latest | options: latest, predevelop, test]: "
goto :loop_build_type
:end_loop_build_type

REM If the user decides not to use existing configs, then ask questions to help fill out the configurations.
if "%EXISTING_CONFIGS%"=="1" (
  python $HOME\deployments\deployment_scripts\main.py %NODE_TYPE% --build %BUILD
