#!/bin/bash

CONNS=`curl -X GET 23.239.12.151:32349 -H 'command: blockchain get operator bring [*][ip] : [*][rest_port] separator = " "' -H "User-Agent: AnyLog/1.23"`

for CONN in ${CONNS} ; do
   echo ${CONN}
   curl -X POST ${CONN} -H "command: connect dbms monitor where type=sqlite" -H "User-Agent: AnyLog/1.23"
   curl -X POST ${CONN} -H "command: partition monitor * using timestamp by 1 day" -H "User-Agent: AnyLog/1.23"
   curl -X POST ${CONN} -H 'command: schedule time = 15 seconds and name = "Monitor CPU - DB" task get node info cpu_percent into dbms = monitor and table = cpu_percent' -H "User-Agent: AnyLog/1.23"
   curl -X POST ${CONN} -H 'command: schedule time = 1 day and start = +1d and name = "Drop 1 day CPU data - DB" task drop partition where dbms = monitor and table = cpu_percent'  -H "User-Agent: AnyLog/1.23"
done