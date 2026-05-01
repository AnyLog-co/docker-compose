# https://github.com/AnyLog-co/documentation/blob/master/queries.md

import ast
import copy

from query_blockchain import get_request, get_policies

def __get_children(conn:str):
    """
    Based on device_id - get children policies in the UNS
    """
    device_id = "SIC-250-002"
    # blockchain get sensors
    policies = get_policies(conn=conn, policy_type="*", policy_parent=device_id)
    return policies

def basic_query(conn:str):
    """
    Basic SELECT statements across 3 operator nodes
    :output:
        table format
    """
    headers = {
        "command": f'sql bottle_factory format=table "select timestamp, site, lot_id, state, duration, flowrate, temperature, weight from processing where timestamp >= NOW() - 10 minutes ORDER BY timestamp"',
        "User-Agent": "AnyLog/1.23",
        "destination": "network"
    }

    response = get_request(conn=conn, headers=headers)
    print(response)

def increments(conn:str):
    """
    Demonstrate Increments - specifically against Site1
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/queries.md#the-increment-function
    :output:
        list of JSONs with content from Site1
    """
    sql_cmd = "select increments(hour, 1, timestamp), min(timestamp) AS min_ts, max(timestamp) AS max_ts, min(weight)::float(3) as min_weight, max(weight)::float(3) as max_weight, avg(weight)::float(3) as avg_weight from processing where timestamp >= NOW() - 1 day ORDER BY min_ts"
    headers = {
        "command": f"sql bottle_factory format=json:list and stat=false {sql_cmd}",
        "User-Agent": "AnyLog/1.23",
        "destination": "blockchain get operator where name=Site1 bring.ip_port"
    }

    response = get_request(conn=conn, headers=headers)
    print(response)

def period(conn:str):
    """
    Demonstrate period - against multiple tables
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/queries.md#the-period-function
    :process:
        1. get device (first)
        2. from device get list of sensors (tables)
        3. query based sensors
    :output:
        table format with data from the different sensors based on the blockchain
    """
    tables = []

    headers = {
        "command": "sql",
        "User-Agent": "AnyLog/1.23",
        "destination": "network"
    }
    policies = __get_children(conn=conn)

    for policy in policies:
        tables.append(f"{policy.get(list(policy)[0]).get('dbms')}.{policy.get(list(policy)[0]).get('table')}")

    db_name, table = tables[0].split(".")
    headers["command"] += f" {db_name} format=table and include=("
    for table_info in tables:
        if not table_info == tables[0]:
            headers["command"] += f"{table_info},"
    headers["command"] = headers["command"].rsplit(",", 1)[0] + ") and extend=(@table_name)"
    headers["command"] += f" select timestamp, min_val, avg_val, max_val, events  from {table} where period(hour, 1, now(), timestamp) order by timestamp"

    response = get_request(conn=conn, headers=headers)
    print(response)

def aggregation(conn:str):
    """
    Aggregation is the ability to view data before its being stored on the logical database
    It can also be used in order to not store repeating values - as shown with historian_manufacturing data
    :url:
        https://github.com/AnyLog-co/documentation/blob/master/aggregations.md
    :steps:
        1. get a list of sensors (tables) for a specific device
        2. get aggregations on historian logical database
        3. clean aggregations to only show information about the provided sensors in step 1
    :output:
        sensor
            -> aggregations
    """
    headers = {
        "command": "get aggregation where format=json",
        "User-Agent": "AnyLog/1.23",
        "destination": "blockchain get operator where name=historian bring.ip_port"
    }
    policies = __get_children(conn=conn)
    output = {table_name.get("sensor").get("table"): [] for table_name in policies}

    responses = get_request(conn=conn, headers=headers)
    for response in responses[list(responses)[0]]:
        if response.get("table") in output:
            append_values = copy.deepcopy(response)
            for param in ["events_sec", "count", "min", "max", "avg", "value"]:
                if response.get(param) == "---":
                    del append_values[param]
            output[response.get("table")].append(append_values)

    for table in output:
        print(table)
        for row in output[table]:
            print(f"\t{row}")

if __name__ == "__main__":
    basic_query(conn="http://50.116.13.109:32049") # basic anylog command
    increments(conn="http://50.116.13.109:32049")  # increments example
    period(conn="http://50.116.13.109:32049")      # period example
    aggregation(conn="http://50.116.13.109:32049") # aggregation example