@echo off
setlocal enabledelayedexpansion

:: Default to 'generic' if no type is passed
set ANYLOG_TYPE=%2
if "%ANYLOG_TYPE%"=="" (
    set ANYLOG_TYPE=generic
)

:: Set tag based on architecture
for /f "tokens=*" %%A in ('wmic os get osarchitecture ^| find "bit"') do set ARCH=%%A
if "%ARCH%"=="64-bit" (
    set TAG=1.3.2501-beta11
) else (
    set TAG=1.3.2501-arm64
)

:: Determine container command
where podman >nul 2>nul
if %errorlevel%==0 (
    set CONTAINER_CMD=podman
) else (
    set CONTAINER_CMD=docker
)

:: Determine docker-compose command
where podman-compose >nul 2>nul
if %errorlevel%==0 (
    set DOCKER_COMPOSE_CMD=podman-compose
) else (
    where docker-compose >nul 2>nul
    if %errorlevel%==0 (
        set DOCKER_COMPOSE_CMD=docker-compose
    ) else (
        set DOCKER_COMPOSE_CMD=docker compose
    )
)

:: Main switch for actions
if "%1"=="login" goto login
if "%1"=="build" goto build
if "%1"=="up" goto up
if "%1"=="down" goto down
if "%1"=="clean" goto clean
if "%1"=="logs" goto logs
if "%1"=="help" goto help

echo Invalid command.
goto end

:login
echo Logging into docker...
%CONTAINER_CMD% login docker.io -u anyloguser --password %ANYLOG_TYPE%
goto end

:build
echo Pulling image...
%CONTAINER_CMD% pull docker.io/anylogco/anylog-network:%TAG%
goto end

:up
echo Deploying containers...
call :generate_docker_compose
%DOCKER_COMPOSE_CMD% -f docker-makefiles\docker-compose.yaml up -d
del /f /q docker-makefiles\docker-compose.yaml
goto end

:down
echo Stopping containers...
call :generate_docker_compose
%DOCKER_COMPOSE_CMD% -f docker-makefiles\docker-compose.yaml down
del /f /q docker-makefiles\docker-compose.yaml
goto end

:clean
echo Cleaning containers and volumes...
call :generate_docker_compose
%DOCKER_COMPOSE_CMD% -f docker-makefiles\docker-compose.yaml down --volumes --rmi all
del /f /q docker-makefiles\docker-compose.yaml
goto end

:logs
%CONTAINER_CMD% logs anylog-%ANYLOG_TYPE%
goto end

:help
echo Usage: anylog-make.bat [command] [anylog-type]
echo.
echo Commands:
echo    login       Log into DockerHub using anylog-type as password
echo    build       Pull docker image
echo    up          Deploy container
echo    down        Stop containers
echo    clean       Remove containers, volumes, images
echo    logs        Show container logs
echo    help        Show this help message
echo.
goto end

:generate_docker_compose
:: Placeholder - you'd need to emulate envsubst or generate a file with variables
echo Generating docker-compose.yaml...
copy docker-makefiles\docker-compose-template.yaml docker-makefiles\docker-compose.yaml >nul
goto :eof

:end
endlocal