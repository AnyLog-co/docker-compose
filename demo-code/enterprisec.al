#-----------------------------------------------------------------------------------------------#
# Message Client for Enterprise C - each sensor is written to a single timestamp / value table  #
# - Setup: 1 Operator Node that contains all the data for `sum` in Enterprise C                 #
# - Blockchain: enterprise -> namespace -> device -> sensor                                     #
#-----------------------------------------------------------------------------------------------#

<run msg client where broker=local and log=false and topic=(
   name=enterprisec and
   dbms="bring [dbms]" and
   table="bring [table]" and
   column.timestamp.timestamp = "bring [timestamp]" and
   column.value.str="bring [value]"
)>

