import argparse
from connector_opcua import get_struct
from blockchain_cmds import publish_policy, declare_enterprise


def declare_namespace(conn:str, namespace:str):
    """
    Declare namespace
    """
    new_policy = {"namespace": {
        "name": namespace,
        "parent": "Enterprise C",
        "namespace": "Enterprise C/{namespace}"
    }}

    publish_policy(conn=conn, policy=new_policy)

def declare_device(conn:str, namespace, device_name):
    """
    Declare Device
    """
    policy = {
        "device": {
            "name": device_name,
            "parent": namespace,
            "namespace": f"Enterprise C/{namespace}/{device_name}"
        }
    }
    publish_policy(conn=conn, policy=policy)

def declare_sensor(conn:str, db_name:str, namespace:str, device_name:str, sensor:str):
    """
    Declare sensor
    """
    policy = {
        "sensor": {
            "name": sensor,
            "parent": device_name,
            "dbms": db_name,
            "table": f"{device_name.replace('-','_')}_{sensor.replace('-', '_').replace('.','_')}".lower(),
            "namespace": f"Enterprise C/{namespace}/{device_name}_{sensor}"
        }
    }

    publish_policy(conn=conn, policy=policy)


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument("conn", type=str, default="50.116.13.109:32049", help="REST connection to publish policies to")
    parse.add_argument("--db-name", type=str, default="manufacturing_historian", help="logical database name")
    args = parse.parse_args()

    if not args.conn.startswith("http://"):
        args.conn = f"http://{args.conn}"

    declare_enterprise(conn=args.conn, enterprise_id='B')  # declare enterprise policy
    for namespace in ["sub"]:
        declare_namespace(conn=args.conn, namespace=namespace)
        # get device -> sensors for namespace
        variables = get_struct(node_id=f"ns=2;s={namespace}")
        for device_name in variables:
            declare_device(conn=args.conn,namespace=namespace, device_name=device_name)
            for sensor in variables[device_name]:
                declare_sensor(conn=args.conn, db_name=args.db_name, namespace=namespace, device_name=device_name,
                               sensor=sensor)


if __name__ == "__main__":
    main()
