import requests
import json

def publish_policy(conn:str, policy):
    headers = {
        'command': "blockchain insert where policy=!new_policy and local=true and master=!ledger_conn",
        'User-Agent': 'AnyLog/1.23'
    }

    try:
        key = list(policy.keys())[0]
        print(key, policy.get(key).get("id"))
        if not check_policy(conn=conn, policy_type=key, policy_id=policy.get(key).get("id")):
            response = requests.post(url=conn, headers=headers, data=f"<new_policy={json.dumps(policy)}>", timeout=90)
            response.raise_for_status()
    except Exception:
        raise Exception


def check_policy(conn:str, policy_type:str, policy_id:str):
    headers = {
        "command": f'blockchain get {policy_type} where id="{policy_id}"',
        "User-Agent": "AnyLog/1.23"
    }
    is_policy = False
    try:
        response = requests.get(url=conn, headers=headers)
        response.raise_for_status()
        if response.json():
            is_policy = True
    except Exception:
        raise Exception

    return is_policy
