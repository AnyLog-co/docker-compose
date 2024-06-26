@echo off
setlocal EnableDelayedExpansion

rem Determine ANYLOG_PATH
if "%1"=="" (
    set ANYLOG_PATH=generic
) else (
    set ANYLOG_PATH=%1
)

rem Determine TAG
set TAG=1.3.2405-beta6
for /f "tokens=*" %%i in ('wmic os get osarchitecture ^| findstr /I "64"') do (
    if "%%i"=="64-bit" (
        set TAG=1.3.2405-arm64
    )
)

rem Determine ANYLOG_TYPE
for /f "tokens=2 delims==" %%i in ('findstr "NODE_TYPE" docker-makefile\%ANYLOG_PATH%-configs\base_configs.env') do (
    set ANYLOG_TYPE=%%i
)

rem Check for docker-compose or docker compose
docker compose version >nul 2>&1 && set DOCKER_COMPOSE=docker compose || docker-compose version >nul 2>&1 && set DOCKER_COMPOSE=docker-compose

:all
call :help
goto :eof

:login
docker login -u anyloguser --password %ANYLOG_PATH%
goto :eof

:build
docker pull anylogco/anylog-network:%TAG%
goto :eof

:dry-run
echo "Dry Run %ANYLOG_PATH%"
set ANYLOG_PATH=%ANYLOG_PATH%
set ANYLOG_TYPE=%ANYLOG_TYPE%
envsubst < docker-makefile\docker-compose-template.yaml > docker-makefile\docker-compose.yaml
goto :eof

:up
echo "Deploy AnyLog %ANYLOG_TYPE%"
set ANYLOG_PATH=%ANYLOG_PATH%
set ANYLOG_TYPE=%ANYLOG_TYPE%
envsubst < docker-makefile\docker-compose-template.yaml > docker-makefile\docker-compose.yaml
%DOCKER_COMPOSE% -f docker-makefile\docker-compose.yaml up -d
del /q docker-makefile\docker-compose.yaml
goto :eof

:down
set ANYLOG_PATH=%ANYLOG_PATH%
set ANYLOG_TYPE=%ANYLOG_TYPE%
envsubst < docker-makefile\docker-compose-template.yaml > docker-makefile\docker-compose.yaml
%DOCKER_COMPOSE% -f docker-makefile\docker-compose.yaml down
del /q docker-makefile\docker-compose.yaml
goto :eof

:clean
set ANYLOG_PATH=%ANYLOG_PATH%
set ANYLOG_TYPE=%ANYLOG_TYPE%
envsubst < docker-makefile\docker-compose-template.yaml > docker-makefile\docker-compose.yaml
%DOCKER_COMPOSE% -f docker-makefile\docker-compose.yaml down
%DOCKER_COMPOSE% -f docker-makefile\docker-compose.yaml down -v --rmi all
del /q docker-makefile\docker-compose.yaml
goto :eof

:attach
docker attach --detach-keys=ctrl-d anylog-%ANYLOG_TYPE%
goto :eof

:node-status
if "%ANYLOG_PATH%"=="master" (
    curl -X GET 127.0.0.1:32049 -H "command: get status" -H "User-Agent: AnyLog/1.23" -w "\n"
) else if "%ANYLOG_PATH%"=="operator" (
    curl -X GET 127.0.0.1:32149 -H "command: get status" -H "User-Agent: AnyLog/1.23" -w "\n"
) else if "%ANYLOG_PATH%"=="query" (
    curl -X GET 127.0.0.1:32349 -H "command: get status" -H "User-Agent: AnyLog/1.23" -w "\n"
) else if "%NODE_TYPE%"=="publisher" (
    curl -X GET 127.0.0.1:32249 -H "command: get status" -H "User-Agent: AnyLog/1.23" -w "\n"
) else if "%NODE_TYPE%"=="generic" (
    curl -X GET 127.0.0.1:32549 -H "command: get status" -H "User-Agent: AnyLog/1.23" -w "\n"
)
goto :eof

:test-node
if "%ANYLOG_PATH%"=="master" (
    curl -X GET 127.0.0.1:32049 -H "command: test node" -H "User-Agent: AnyLog/1.23" -w "\n"
) else if "%ANYLOG_PATH%"=="operator" (
    curl -X GET 127.0.0.1:32149 -H "command: test node" -H "User-Agent: AnyLog/1.23" -w "\n"
) else if "%ANYLOG_PATH%"=="query" (
    curl -X GET 127.0.0.1:32349 -H "command: test node" -H "User-Agent: AnyLog/1.23" -w "\n"
) else if "%ANYLOG_PATH%"=="publisher" (
    curl -X GET 127.0.0.1:32249 -H "command: test node" -H "User-Agent: AnyLog/1.23" -w "\n"
) else if "%NODE_TYPE%"=="generic" (
    curl -X GET 127.0.0.1:32549 -H "command: test node" -H "User-Agent: AnyLog/1.23" -w "\n"
)
goto :eof

:test-network
if "%ANYLOG_PATH%"=="master" (
    curl -X GET 127.0.0.1:32049 -H "command: test network" -H "User-Agent: AnyLog/1.23" -w "\n"
) else if "%ANYLOG_PATH%"=="operator" (
    curl -X GET 127.0.0.1:32149 -H "command: test network" -H "User-Agent: AnyLog/1.23" -w "\n"
) else if "%ANYLOG_PATH%"=="query" (
    curl -X GET 127.0.0.1:32349 -H "command: test network" -H "User-Agent: AnyLog/1.23" -w "\n"
) else if "%ANYLOG_PATH%"=="publisher" (
    curl -X GET 127.0.0.1:32249 -H "command: test network" -H "User-Agent: AnyLog/1.23" -w "\n"
) else if "%NODE_TYPE%"=="generic" (
    curl -X GET 127.0.0.1:32549 -H "command: test network" -H "User-Agent: AnyLog/1.23" -w "\n"
)
goto :eof

:exec
docker exec -it anylog-%ANYLOG_TYPE% bash
goto :eof

:logs
docker logs anylog-%ANYLOG_TYPE%
goto :eof

:help
echo Usage: call scriptname.bat [target] [anylog-type]
echo Targets:
echo   login       Log into AnyLog's Dockerhub - use ANYLOG_PATH to set password value
echo   build       Pull the docker image
echo   up          Start the containers
echo   attach      Attach to AnyLog instance
echo   test        Using cURL validate node is running
echo   exec        Attach to shell interface for container
echo   down        Stop and remove the containers
echo   logs        View logs of the containers
echo   clean       Clean up volumes and network
echo   help        Show this help message
echo   supported AnyLog types: generic, master, operator, and query
echo Sample calls: call scriptname.bat up master ^| call scriptname.bat attach master ^| call scriptname.bat clean master
goto :eof

:end
endlocal
