import argparse
import json
import requests


def get_request(rest_conn:str, cmd:str)->dict:
    """
    Execute GET request - used to get blockchain information
    :args:
        rest_conn:str - REST Connection information
        cmd:str - command to execute
    :params:
        output:dict - request results
        headers:dict - REST header
    :return:
        return policy object
    """
    output = None
    headers = {
        "command": cmd,
        "User-Agent": "AnyLog/1.23"
    }

    try:
        r = requests.get(url=f'http://{rest_conn}', headers=headers)
    except Exception as e:
        print(f'Failed to execute GET against {rest_conn} (Error: {e})')
    else:
        if int(r.status_code) != 200:
            print(f'Failed to execute GET against {rest_conn} (Network Error {r.status_code}')
        try:
            output = r.json()
        except Exception as e:
            output = r.text

    return output


def post_request(rest_conn:str, master_node:str, cmd:str, policy:str)->bool:
    """
     Execute POST request - used to drop policy
     :args:
        rest_conn:str - REST Connection information
        master_node:str - Master node TCP connection information
        cmd:str - command to execute
        policy:str - blockchain policy to drop
    :params:
        status:bool
        headers:dict - REST header
    :return:
        status
    """
    status = True
    headers = {
        "command": cmd,
        "destination": master_node,
        "User-Agent": "AnyLog/1.23"
    }

    try:
        r = requests.post(url=f"http://{rest_conn}", headers=headers, data=policy)
    except Exception as e:
        print(f'Failed to drop policy against {rest_conn} (Error: {e})')
        status = False
    else:
        if int(r.status_code) != 200:
            print(f'Failed to drop policy against {rest_conn} (Network Error: {r.status_code})')
            status = False

    return status


def main():
    """
    The following is intended to drop the extra policy from cluster
    code is run against master REST (by default) but can be configured to run against other nodes
    :steps:
        1. get operator policy by name
        2. drop operator policy
        3. from policy variable extract cluster ID
        4. get child cluster policy (by parent ID)
        5. drop child cluster policy
        6. get cluster by ID
        7. drop cluster
    :optional arguments:
        -h, --help                      show this help message and exit
        --rest-conn     REST_CONN       REST Connection information
        --master-node   MASTER_NODE     Master node TCP connection information
    :params:
        policy:dict - blockchain policy from GET request
        policy_str:str - string formatted policy
        cluster_id:str - from operator policy extract cluster ID
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--rest-conn', type=str, default='38.111.194.182:32049', help='REST Connection information')
    parser.add_argument('--master-node', type=str, default='38.111.194.182:32048', help='Master node TCP connection information')
    args = parser.parse_args()

    # Drop operator policy
    policy = get_request(rest_conn=args.rest_conn, cmd="blockchain get policy where name=sunlight-cluster3")
    if not isinstance(policy, dict):
        print('Unable to utilize operator policy as results were not returned in JSON (dict) format. Cannot continue')
        exit(1)
    else:
        policy_str = "<policy=%s>" % json.dump(policy)
    if not post_request(rest_conn=args.rest_conn, master_node=args.master_node, cmd="blockchain drop policy !policy",
                        policy=policy_str):
        print('Failed to drop Operator policy')

    cluster_id = policy['operator']['cluster']

    # drop "child" cluster policy
    policy = get_request(rest_conn=args.rest_conn, cmd="blockchain get cluster where parent=%s" % cluster_id)
    if not isinstance(policy, dict):
        print('Unable to utilize operator policy as results were not returned in JSON (dict) format. Cannot continue')
        exit(1)
    else:
        policy_str = "<policy=%s>" % json.dump(policy)
    if not post_request(rest_conn=args.rest_conn, master_node=args.master_node, cmd="blockchain drop policy !policy",
                        policy=policy_str):
        print('Failed to drop cluster policy')

    # Drop cluster policy
    policy = get_request(rest_conn=args.rest_conn, cmd="blockchain get cluster where id=%s" % cluster_id)
    if not isinstance(policy, dict):
        print('Unable to utilize operator policy as results were not returned in JSON (dict) format. Cannot continue')
        exit(1)
    else:
        policy_str = "<policy=%s>" % json.dump(policy)
    if not post_request(rest_conn=args.rest_conn, master_node=args.master_node, cmd="blockchain drop policy !policy",
                        policy=policy_str):
        print('Failed to drop cluster policy')


if __name__ == '__main__':
    main()