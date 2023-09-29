OPERATOR_IDS=`curl -X GET 127.0.0.1:32049 -H 'command: blockchain get * where company=IBM bring [*][id] separator=" "' ` -H "User-Agent: AnyLog/1.23"
for OPERATOR_ID in ${OPERATOR_IDS} ; then
  echo ${OPERATOR_ID}
  curl -X POST 172.105.4.104:32049 -H "command: blockchain drop policy where id=${OPERATOR_ID}" -H "User-Agent: AnyLog/1.23"
done