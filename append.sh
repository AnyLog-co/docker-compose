#!/bin/bash

for DIR in `ls -d docker-makefiles/* | grep -v anylog-generic` ; do
  mv ${DIR}/node_configs.env ${DIR}/tmp.env
  head -21 docker-makefiles/anylog-generic/node_configs.env > ${DIR}/node_configs.env
  cat ${DIR}/tmp.env >> ${DIR}/node_configs.env
  rm -rf ${DIR}/tmp.env
done