from connector_opcua import get_struct
from blockchain_cmds import publish_policy

CONN = "http://50.116.13.109:32049"
DB_NAME = "manufacturing_historian"


def declare_enterprise():
    new_policy = {"enterprise": {
            "id": "Enterprise C",
            "uid": "C",
            "namespace": "Enterprise C"
        }}

    publish_policy(conn=CONN, policy=new_policy)

def declare_namespace(namespace:str):
    new_policy = {"namespace": {
        "id": namespace,
        "parent": "Enterprise C",
        "namespace": "Enterprise C/{namespace}"
    }}

    publish_policy(conn=CONN, policy=new_policy)

def declare_device(namespace, device_name):
    policy = {
        "device": {
            "id": device_name,
            "parent": namespace,
            "namespace": f"Enterprise C/{namespace}/{device_name}"
        }
    }
    publish_policy(conn=CONN, policy=policy)

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

    publish_policy(conn=CONN, policy=policy)


def main():
    declare_enterprise()
    for namespace in ["sub"]:
        declare_namespace(namespace)
        variables = get_struct(node_id=f"ns=2;s={namespace}")
        for device_name in variables:
            declare_device(namespace=namespace, device_name=device_name)
            for sensor in variables[device_name]:
                declare_sensor(db_name=DB_NAME, namespace=namespace, device_name=device_name, sensor=sensor)



if __name__ == "__main__":
    main()