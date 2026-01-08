import os
import json
import requests

headers = {
    "command": "blockchain insert where policy=!new_policy and local=true and master=!ledger_conn",
    "User-Agent": "AnyLog/1.23"
}

with open(os.path.expanduser(os.path.expandvars('$HOME/20226_01_07_to_reload.json')), 'r') as f: 
    for policy in json.load(f):
        new_policy = f"<new_policy={json.dumps(policy)}>" 
        try: 
            response = requests.post(url="http://192.168.3.3:32049", headers=headers, data=new_policy)
            response.raise_status_code()
        except Exception as error: 
            print(error)
        else: 
            input("Continue")
