import json
from sample_insert import rest_call

ROOT_NAME="Enterprise C"
CONN = "http://50.116.13.109:32049"

def get_tables_via_blockchain(**kwargs)->list:
    headers = {
        "command": "blockchain get * where",
        "User-Agent": "AnyLog/1.23"
    }
    for key, value in kwargs.items():
        headers["command"] += f' {key}="{value}" and'
    headers["command"] = headers["command"].rsplit(" and")[0]

    response = rest_call(call_method="GET", conn=CONN, headers=headers)
    return response.json()

def __extract_info(policy_content)->(str, str, str or None):
    content_name = policy_content.get("name")
    content_id = policy_content.get("id")
    content_table = policy_content.get("table")

    return content_name, content_id, content_table

def get_tables():
    """
    Drill down on the blockchain to get UNS
    """
    enterprise = get_tables_via_blockchain(name=ROOT_NAME)
    enterprise_name,  enterprise_id, enterprise_table = __extract_info(policy_content=enterprise[0][list(enterprise[0])[0]])
    content = {enterprise_name: {}}

    namespaces = get_tables_via_blockchain(parent=enterprise_id)
    for namespace in namespaces:
        namespace_name, namespace_id, namespace_table = __extract_info(policy_content=namespace.get(list(namespace)[0]))
        content[enterprise_name][namespace_name] = {}
        devices = get_tables_via_blockchain(parent=namespace_id)
        for device in devices:
            device_name,device_id, device_table = __extract_info(policy_content=device.get(list(device)[0]))
            content[enterprise_name][namespace_name][device_name] = {}

            sensors = get_tables_via_blockchain(parent=device_id)
            for sensor in sensors:
                sensor_name, sensor_id, sensor_table = __extract_info(policy_content=sensor.get(list(sensor)[0]))
                content[enterprise_name][namespace_name][device_name][sensor_name] = sensor_table

    print(json.dumps(content, indent=2))

def basic_query(db_name:str, table_name:str):
    """
    Basic query
    """
    headers = {
        "command": f'sql {db_name} format=json and stat=false "SELECT * FROM {table_name} WHERE timestamp >= NOW() - 10 minutes"',
        "User-Agent": "AnyLog/1.23",
        "destination": "network"
    }

    response = rest_call(call_method="GET", conn=CONN, headers=headers)
    for row in response.json()['Query']:
        print(row)


def period_query_multiple_sources():
    """
    Sample period query with data coming in from multiple operator nodes
    """
    headers = {
        "command": "sql bottle_factory format=table and extend=(+node_name) SELECT insert_timestamp, type, name, duration, code from state_63 where period(minute, 15, now(),insert_timestamp) order by insert_timestamp",
        "User-Agent": "AnyLog/1.23",
        "destination": "network"
    }
    response = rest_call(call_method="GET", conn=CONN, headers=headers)
    print(response.text)

def increments_query(db_name:str, table_name:str):
    headers = {
        "command": f'sql {db_name} format=json:list and stat=false "SELECT increments(hour, 1, timestamp), min(timestamp), max(timestamp), min(min_val), avg(avg_val)::float(3), max(max_val), sum(events) FROM {table_name} WHERE timestamp >= NOW() - 1 day"',
        "User-Agent": "AnyLog/1.23",
        "destination": "network"
    }
    response = rest_call(call_method="GET", conn=CONN, headers=headers)
    for row in response.json():
        print(row)

def dynics_queries():
    for table in ["switch", "nic_info"]:
        print(f"Table Name: {table}")
        headers =  {
            "command": "sql monitoring select * from %s" % table,
            "User-Agent": "AnyLog/1.23",
            "destination": "network"
        }
        response = rest_call(call_method="GET", conn=CONN, headers=headers)
        print(response.json())


if __name__ == "__main__":
    get_tables()
    basic_query(db_name="manufacturing_historian", table_name="sub_ti_250_001_pv_celsius")
    period_query_multiple_sources()
    increments_query(db_name="manufacturing_historian", table_name="sub_aic_250_001_pv_percent")
    dynics_queries()