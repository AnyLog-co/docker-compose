#--------------------------------------------------------#
# Manufacturing Historian Msg Client                     #
#--------------------------------------------------------#
on error ignore
:msg-client:
<run msg client where broker=local and log=false and topic=(
   name=manufacturing_historian and
   dbms=!default_dbms and
   table="bring [table]" and
   column.timestamp.timestamp = "bring [timestamp]" and
   column.value.str="bring [value]"
)>
:end-script:
end script