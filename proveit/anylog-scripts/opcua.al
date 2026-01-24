<get opcua struct where
    url=opc.tcp://virtualfactory.proveit.services:4841/discovery and
    user=proveitreadonly and password=proveitreadonlypassword and
    node = "ns=2;s=Site1/liquidprocessing/" and
    dbms = !default_dbms and
    format = policy  and
    schema = true and
    class = variable and
    target = "local = true and master = !ledger_conn" and
    output = !tmp_dir/opcua_policies.al>
process !tmp_dir/opcua_policies.al


<get opcua struct where
    url=opc.tcp://virtualfactory.proveit.services:4841/discovery and
    user=proveitreadonly and password=proveitreadonlypassword and
    node = "ns=2;s=Site1/liquidprocessing/mixroom01/vat01/processdata/process"and
    node = "ns=2;s=Site1/liquidprocessing/mixroom01/vat01/processdata/state"and
    node = "ns=2;s=Site1/liquidprocessing/mixroom01/vat01/processdata/metric"and
    node = "ns=2;s=Site1/liquidprocessing/mixroom01/vat02/processdata/process"and
    node = "ns=2;s=Site1/liquidprocessing/mixroom01/vat02/processdata/state"and
    node = "ns=2;s=Site1/liquidprocessing/mixroom01/vat02/processdata/metric"and
    node = "ns=2;s=Site1/liquidprocessing/mixroom01/vat03/processdata/process"and
    node = "ns=2;s=Site1/liquidprocessing/mixroom01/vat03/processdata/state"and
    node = "ns=2;s=Site1/liquidprocessing/mixroom01/vat03/processdata/metric"and
    node = "ns=2;s=Site1/liquidprocessing/mixroom01/vat04/processdata/process"and
    node = "ns=2;s=Site1/liquidprocessing/mixroom01/vat04/processdata/state"and
    node = "ns=2;s=Site1/liquidprocessing/mixroom01/vat04/processdata/metric" and
    dbms = !default_dbms and
    format = policy  and
    schema = true and
    class = variable and
    target = "local = true and master = !ledger_conn" and
    output = !tmp_dir/opcua_policies.al>

#        "ns=2;s=Site1/liquidprocessing/tankstorage01/tank01/processdata/process",
#        "ns=2;s=Site1/liquidprocessing/tankstorage01/tank01/processdata/state",
#        "ns=2;s=Site1/liquidprocessing/tankstorage01/tank01/metric",
