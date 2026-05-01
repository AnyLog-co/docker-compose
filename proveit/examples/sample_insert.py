import datetime
import json
import requests


# sample data for swtich and nic info
DATA = {
    "switch": {
        "id": 2,
        "name": "Switch 2",
        "ip": "172.79.89.10",
        "created_at": "2026-01-15T21:41:45.131Z",
        "last_echo": None,
        "manufacturer": "Dynics",
        "hardware": "ETH2-DN0802XXD1-01G",
        "software": "E20251027",
        "datapath_id": "100648200AA1",
        "adopted": True,
        "connected": True,
        "net_prefix": None,
        "gateway": None,
        "switch_adoption_state_id": 2,
        "inband_port": 1,
        "learning_mode": False,
        "inband": True,
        "l3_group_id": 0,
        "l3_group_gw_switch": False,
        "devices": [1, 2, 3, 4, 5],
        "switch_adoption_state": "Adopted"
    },
    "nic_info": {
        "name": "eno1",
        "ip": "172.79.89.2",
        "netmask": "255.255.255.0",
        "adoption_ip": "169.254.64.135",
        "is_default": True,
        "gateway": "172.79.89.1",
        "nameserver": "127.0.0.53",
        "is_adoption_interface": None,
        "is_enabled": True
    }
}

# REST connection for Operator node
CONN = "http://50.116.13.109:32159"

def rest_call(call_method:str, conn:str, headers:dict, data:str=None):
    """
    Generic REST call
    """
    try:
        response = requests.request(method=call_method.upper(), url=conn, headers=headers, data=data)
        response.raise_for_status()
    except Exception as error:
        raise Exception(f"Failed to execute {call_method.upper()} against {conn} (Error: {error})")
    return response


def put_publish_data():
    """
    Example for publishing data via PUT
    """
    headers = {
        'type': 'json',
        'dbms': "monitoring",
        'table': None, # <- unique table per payload (type)
        'mode': "streaming",
        'Content-Type': 'text/plain'
    }
    for table in DATA:
        headers["table"] = table
        DATA[table]["timestamp"] = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ") if not DATA[table].get("timestamp") else DATA[table].get("timestamp")

        response = rest_call(call_method="PUT", conn=CONN, headers=headers, data=json.dumps(DATA[table]))

def post_publish_data():
    """
    Example publishing data via POST
    """
    headers = {
       "command": "data",
       "topic": "Enterprise-C",
       "User-Agent": "AnyLog/1.23",
       "Content-Type": "text/plain"
    }

    data = {
       "dbms":"manufacturing_historian",
       "table":"sub_ti_250_001_pv_celsius",
       "timestamp":datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "value":30.1
    }

    response = rest_call(call_method="POST", conn=CONN, headers=headers, data=json.dumps(data))



def main():
    put_publish_data()
    post_publish_data()



if __name__ == "__main__":
    main()


