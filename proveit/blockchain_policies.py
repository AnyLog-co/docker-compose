import requests
import json

CONN = "http://50.116.13.109:32149"
TOPIC = "Enterprise C/sub"

def _publish_policy(policy):
    headers = {
        'command': "blockchain insert where policy=!new_policy and local=true and master=!ledger_conn",
        'User-Agent': 'AnyLog/1.23'
    }

    try:
        key = list(policy.keys())[0]
        print(key, policy.get(key).get("id"))
        if not _check_policy(policy_type=key, policy_id=policy.get(key).get("id")):
            response = requests.post(url=CONN, headers=headers, data=f"<new_policy={json.dumps(policy)}>", timeout=90)
            response.raise_for_status()
    except Exception:
        raise Exception

def _check_policy(policy_type:str, policy_id:str):
    headers = {
        "command": f'blockchain get {policy_type} where id="{policy_id}"',
        "User-Agent": "AnyLog/1.23"
    }
    is_policy = False
    try:
        response = requests.get(url=CONN, headers=headers)
        response.raise_for_status()
        if response.json():
            is_policy = True
    except Exception:
        raise Exception
    return is_policy


def get_tables():
    """
    List of tables
    """
    headers = {
        "command": "blockchain get table bring [*][name] separator=,",
        "User-Agent": "AnyLog/1.23"
    }

    try:
        response = requests.get(url=CONN, headers=headers, timeout=90)
        response.raise_for_status()
    except Exception:
        raise Exception
    return response.text.split(",")

def get_columns(table):
    headers = {
        "command": f"get columns where dbms=proveit and table={table} and format=json",
        "User-Agent": "AnyLog/1.23"
    }
    # print(headers['command'])
    try:
        response = requests.get(url=CONN, headers=headers, timeout=90)
        response.raise_for_status()
    except Exception:
        raise Exception
    columns = response.json()
    for column in ['row_id', 'insert_timestamp', 'tsd_name', 'tsd_id', 'timestamp']:
        del columns[column]
    return list(columns.keys())


def declare_enterprise():
    new_policy = [
        {"enterprise": {
            "id": "Enterprise C",
            "uid": "C",
            "namespace": "Enterprise C"
        }},
        {"namespace": {
            "id": "sub",
            "parent": "Enterprise C",
            "namespace": "Enterprise C/sub"
        }}
    ]

    for policy in new_policy:
        _publish_policy(policy)

def declare_device(table):
    table_id = table.replace("_", "-").upper()
    policy = {
        "device": {
            "id": table_id,
            "parent": "sub",
            "table": table,
            "namespace": f"{TOPIC}/{table_id}"
        }
    }
    _publish_policy(policy)
    return table_id

def declare_sensor(table_id, sensor):
    sensor_id = sensor.upper()
    policy = {
        "sensor": {
            "id": f"{table_id}.{sensor_id}",
            "name": sensor.lower(),
            "parent": table_id,
            "namespace": f"{TOPIC}/{table_id}/{sensor_id}"
        }
    }
    _publish_policy(policy)


if __name__ == ('_'
                '_main__'):
    tables = get_tables()

    for table in tables:
        columns = get_columns(table)
        table_id = declare_device(table)
        for column in columns:
            declare_sensor(table_id, column)
