#!/usr/bin/env bash
USER_INPUT=$1

export MY_DIR=`pwd`
cd $HOME/docker-compose
if [[ "${USER_INPUT}" == "run" ]] ; then
  make up ANYLOG_TYPE=demo-node TAG=latest
  docker log -f demo-node
else
  make clean-vols ANYLOG_TYPE=demo-node
fi
cd ${MY_DIR}