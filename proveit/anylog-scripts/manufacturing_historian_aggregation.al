#--------------------------------------------------------#
# Manufacturing Historian aggregations                   #
#--------------------------------------------------------#
on error ignore
:kpi-aggregation:
<set aggregation where
    dbms=!default_dbms and
    table=* and
    intervals=10 and
    time="1 minute"  and
    time_column=timestamp and
    value_column=value>

<set aggregation ingest where
    dbms=!default_dbms and
    table=* and
	source = false and
	derived = true>

<set aggregation encoding where
    dbms = !default_dbms and
    table =* and
    value_column = value and
    encoding = bounds>

:end-script:
end script