#!/usr/bin/env bash
USER_INPUT=$1

export MY_DIR=`pwd`
cd $HOME/docker-compose
if [[ "${USER_INPUT}" == "run" ]] ; then
  make up ANYLOG_TYPE=demo-node TAG=latest
  docker logs -f anylog-demo-node
else
  make down ANYLOG_TYPE=demo-node
  docker volume rm `docker volume ls | grep -v nebula | awk -F " " '{print $2}'`
fi
cd ${MY_DIR}