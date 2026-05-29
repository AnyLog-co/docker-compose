set create_policy = false

:check-policy:
is_policy = blockchain get (mapping, transform) where id = dados
if not !is_policy and !create_policy == false then goto declare-policy
else if !is_policy then goto end-script
else if not !is_policy and !create_policy == true then goto declare-policy-error

:declare-policy:
set new_policy = {}

<new_policy = {
    "mapping" : {
        "id" : "dados",
        "dbms" : !default_dbms,
        "table" : "ds_data",
        "readings": "",
        "schema": {
            "timestamp": {
                "type": "timestamp",
                "default": "now()",
                "bring": "[timestamp]"
            },
            "snapshot_id": {
                "type": "string",
                "default": Null,
                "bring": "[snapshot_id]"
            },
            "seq": {
                "type": "int",
                "default": Null,
                "bring": "[seq]"
            },
            "data_type": {
                "type": "int",
                "default": Null,
                "bring": "[data_type]"
            },
            "broker": {
                "type": "string",
                "default": Null,
                "bring": "[broker]"
            },
            "topic": {
                "type": "string",
                "default": Null,
                "bring": "[topic]"
            },
            "metric_name": {
                "type": "string",
                "default": Null,
                "bring": "[metric_name]"
            },
            "sys_publisher_egress": {
                "type": "timestamp",
                "default": Null,
                "bring": "[sys_publisher_egress]"
            },
            "sys_dadosflow_ingress": {
                "type": "timestamp",
                "default": Null,
                "bring": "[sys_dadosflow_ingress]"
            },
            "sys_dadosflow_egress": {
                "type": "timestamp",
                "default": Null,
                "bring": "[sys_dadosflow_egress]"
            },
            "value_bool": {
                "type": "bool",
                "default": Null,
                "bring": "[value_bool]"
            },
            "value_int": {
                "type": "int",
                "default": Null,
                "bring": "[value_int]"
            },
            "value_double": {
                "type": "float",
                "default": Null,
                "bring": "[value_double]"
            },
            "value_string": {
                "type": "string",
                "default": Null,
                "bring": "[value_string]"
            },
            "value_bytes": {
                "type": "string",
                "default": Null,
                "bring": "[value_bytes]"
            },
            "value_uint": {
                "type": "int",
                "default": Null,
                "bring": "[value_uint]"
            }
        }
    }
}>

:publish-policy:
process !local_scripts/node-deployment/policies/publish_policy.al
if not !error_code.int then
do set create_policy = true
goto check-policy

if !error_code == 1 then goto sign-policy-error
else if !error_code == 2 then goto prepare-policy-error
else if !error_code == 3 then goto declare-policy-error

:end-script:
end script

:terminate-scripts:
exit scripts

:sign-policy-error:
print "Failed to sign mapping policy"
goto terminate-scripts

:prepare-policy-error:
print "Failed to prepare mapping policy for publishing on blockchain"
goto terminate-scripts

:declare-policy-error:
print "Failed to declare mapping policy on blockchain"
goto terminate-scripts

