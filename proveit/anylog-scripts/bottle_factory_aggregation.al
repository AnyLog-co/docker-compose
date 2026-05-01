#--------------------------------------------------------#
# Bottle factory aggregations                            #
#--------------------------------------------------------#
on error ignore
:kpi-aggregation:
<set aggregation where
    dbms = !default_dbms and
    table = kpi and
    intervals = 10 and
    time = "1 minute" and
    time_column = timestamp and
    value_column = oee>

<set aggregation where
    dbms = !default_dbms and
    table = kpi and
    intervals = 10 and
    time = "1 minute" and
    time_column = timestamp and
    value_column = performance>

<set aggregation where
    dbms = !default_dbms and
    table = kpi and
    intervals = 10 and
    time = "1 minute" and
    time_column = timestamp and
    value_column = quality>

<set aggregation where
    dbms = !default_dbms and
    table = kpi and
    intervals = 10 and
    time = "1 minute" and
    time_column = timestamp and
    value_column = availability>

:processing-aggregation:
<set aggregation where
    dbms = !default_dbms and
    table = processing and
    intervals = 10 and
    time = "1 minute" and
    time_column = timestamp and
    value_column = state>

<set aggregation where
    dbms = !default_dbms and
    table = processing and
    intervals = 10 and
    time = "1 minute" and
    time_column = timestamp and
    value_column = duration>

<set aggregation where
    dbms = !default_dbms and
    table = processing and
    intervals = 10 and
    time = "1 minute" and
    time_column = timestamp and
    value_column = flowrate>

<set aggregation where
    dbms = !default_dbms and
    table = processing and
    intervals = 10 and
    time = "1 minute" and
    time_column = timestamp and
    value_column = temperature>

<set aggregation where
    dbms = !default_dbms and
    table = processing and
    intervals = 10 and
    time = "1 minute" and
    time_column = timestamp and
    value_column = weight>

:end-script:
end script