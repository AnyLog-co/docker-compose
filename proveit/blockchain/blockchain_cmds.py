import requests
import json

def publish_policy(conn:str, policy):
    headers = {
        'command': "blockchain insert where policy=!new_policy and local=true and master=!ledger_conn",
        'User-Agent': 'AnyLog/1.23'
    }

    try:
        key = list(policy.keys())[0]
        if not check_policy(conn=conn, policy_type=key, id=policy.get(key).get("id"),
                            name=policy.get(key).get("name"), sensor=policy.get(key).get("sensor"),
                            namespace=policy.get(key).get("namespace"), parent=policy.get(key).get("parent")):
            response = requests.post(url=conn, headers=headers, data=f"<new_policy={json.dumps(policy)}>", timeout=90)
            response.raise_for_status()
    except Exception:
        print(policy)
        raise Exception


def check_policy(conn:str, policy_type:str, **kwargs):
    headers = {
        "command": f'blockchain get {policy_type}',
        "User-Agent": "AnyLog/1.23"
    }
    if kwargs:
        headers["command"] += " where"
        for key, value in kwargs.items():
            if value:
                headers["command"] += f' {key}="{value}" and'
        headers["command"] = headers["command"].rsplit(" and", 1)[0]
    is_policy = False
    try:
        response = requests.get(url=conn, headers=headers)
        response.raise_for_status()
        if response.json():
            is_policy = True
    except Exception:
        raise Exception

    return is_policy



def get_id(conn:str, policy_type:str, **kwargs):
    headers = {
        "command": f'blockchain get {policy_type}',
        "User-Agent": "AnyLog/1.23"
    }
    if kwargs:
        headers["command"] += " where"
        for key, value in kwargs.items():
            if value:
                headers["command"] += f' {key}="{value}" and'
        headers["command"] = headers["command"].rsplit(" and", 1)[0]
    headers["command"] += " bring [*][id]"

    try:
        response = requests.get(url=conn, headers=headers)
        response.raise_for_status()
    except Exception:
        raise Exception

    return response.text

def declare_enterprise(conn:str, enterprise_id:str):
    """
    Declare enterprise policy
    :args:
        conn:str - connection information
        enterprise_id:str - Enterprise ID
    :params:
        new_policy:str - enterprise policy
    """
    new_policy = {"enterprise": {
            "id": f"Enterprise {enterprise_id}",
            "uid": enterprise_id,
            "namespace": f"Enterprise {enterprise_id}"
        }}

    publish_policy(conn=conn, policy=new_policy)
