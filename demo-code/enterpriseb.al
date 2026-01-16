#--------------------------------------------------------------------------#
# Message Client for Enterprise B - data is split into 2 tables            #
# - Setup: Each site on a different operator with data split into 2 tables #
# - Tables:                                                                #
#       KPI: site, lot_id, oee, performance, quality, availability         #
#       Processing: lot_id, oee, duration, flowrate, temp, weight          #
# - Blockchain: site -> data in table                                      #
#--------------------------------------------------------------------------#

<run msg client where broker=local and log=false and topic=(
   name=kpi and
   dbms="bring [dbms]" and
   table="bring [table]" and
   column.timestamp.timestamp = "bring [timestamp]" and
   column.site.str = "bring [site]" and
   column.lot_id.str = "bring [lotnumberid]" and
   column.oee.float = "bring [oee]" and
   column.performance.float = "bring [performance]" and
   column.quality.float = "bring [quality]" and
   column.availability.float = "bring [availability]"
)>

<run msg client where broker=local and log=false and topic=(
   name=process and
   dbms="bring [dbms]" and
   table="bring [table]" and
   column.timestamp.timestamp = "bring [timestamp]" and
   column.site.str = "bring [site]" and
   column.lot_id.str = "bring [lotnumberid]" and
   column.state.str = "bring [state]" and
   column.duration.float = "bring [duration]" and
   column.flowrate.float = "bring [flowrate]" and
   column.temperature.float = "bring [temperature]" and
   column.weight.float = "bring [weight]"
)>
