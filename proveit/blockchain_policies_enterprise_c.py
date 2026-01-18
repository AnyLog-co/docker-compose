import json
import requests
from get_variables import get_struct

CONN = "50.116.13.109:32049"
DB_NAME = "enterprise_c"

def _publish_policy(policy):
    headers = {
        'command': "blockchain insert where policy=!new_policy and local=true and master=!ledger_conn",
        'User-Agent': 'AnyLog/1.23'
    }

    try:
        key = list(policy.keys())[0]
        print(key, policy.get(key).get("id"))
        if not _check_policy(policy_type=key, policy_id=policy.get(key).get("id")):
            response = requests.post(url=f"http://{CONN}", headers=headers, data=f"<new_policy={json.dumps(policy)}>", timeout=90)
            response.raise_for_status()
    except Exception as error:
        raise Exception(error)

def _check_policy(policy_type:str, policy_id:str):
    headers = {
        "command": f'blockchain get {policy_type} where id="{policy_id}"',
        "User-Agent": "AnyLog/1.23"
    }
    is_policy = False
    try:
        response = requests.get(url=f"http://{CONN}", headers=headers)
        response.raise_for_status()
        if response.json():
            is_policy = True
    except Exception as error:
        raise Exception(error)
    return is_policy


def declare_enterprise():
    new_policy = {"enterprise": {
            "id": "Enterprise C",
            "uid": "C",
            "namespace": "Enterprise C"
        }}

    _publish_policy(new_policy)

def declare_namespace(namespace:str):
    new_policy = {"namespace": {
        "id": namespace,
        "parent": "Enterprise C",
        "namespace": "Enterprise C/{namespace}"
    }}

    _publish_policy(new_policy)

def declare_device(namespace, device_name):
    policy = {
        "device": {
            "id": device_name,
            "parent": namespace,
            "namespace": f"Enterprise C/{namespace}/{device_name}"
        }
    }
    _publish_policy(policy)

def declare_sensor(db_name:str, namespace:str, device_name:str, sensor:str):
    policy = {
        "sensor": {
            "id": sensor,
            "parent": device_name,
            "dbms": db_name,
            "table": f"{device_name.replace('-','_')}_{sensor.replace('-', '_').replace('.','_')}".lower(),
            "namespace": f"Enterprise C/{namespace}/{device_name}_{sensor}"
        }
    }
    _publish_policy(policy)


def main():
    declare_enterprise()
    for namespace in ["sub"]:
        declare_namespace(namespace)
        variables = get_struct(node_id=f"ns=2;s={namespace}")
        for device_name in variables:
            declare_device(namespace=namespace, device_name=device_name)
            for sensor in variables[device_name]:
                declare_sensor(db_name=DB_NAME, namespace=namespace, device_name=device_name, sensor=sensor)



if __name__ == '__main__':
    main()


