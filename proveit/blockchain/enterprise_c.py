from blockchain_cmds import publish_policy, get_id
from mqtt_hierarchy import mqtt_hierarchy
import re
from collections import defaultdict


URL = "opc.tcp://virtualfactory.proveit.services:4842/discovery"
# TREE_BASE = "sub"
CONN = "http://50.116.13.109:32049"
DBMS="manufacturing_historian"


def declare_enterprise():
    new_policy = {
        "enterprise": {
            "id": "EnterpriseC",
            "uid": 'C',
            "company": "Manufacturing Historian",
            "namespace": "Enterprise C",
        }
    }

    publish_policy(conn=CONN, policy=new_policy)
    return get_id(conn=CONN, policy_type="enterprise", uid='C')


def create_namespace(namespace:str):
    new_policy = {
        "namespace" : {
            "id": namespace,
            "parent": "EnterpriseC",
            "namespace": f"Enterprise C/{namespace}"
        }
    }

    publish_policy(conn=CONN, policy=new_policy)
    return get_id(conn=CONN, policy_type="enterprise", uid='C')


def create_device(namespace:str, device:str):
    new_policy = {
        "device": {
            "name": device,
            "parent": namespace,
            "namespace": f"Enterprise C/{namespace}/{device}"
        }
    }

    publish_policy(conn=CONN, policy=new_policy)
    return get_id(conn=CONN, policy_type="enterprise", uid='C')

def create_sensor(namespace:str, device:str, sensor:str, parent_id:str, db_name:str):
    new_policy = {
        "sensor": {
            "name": sensor,
            "dbms": db_name,
            "table": f"{namespace}_{device}_{sensor}".lower().replace('-', '_'),
            "parent": parent_id,
            "namespace": f"Enterprise C/{namespace}/{device}/{sensor}"
        }
    }

    publish_policy(conn=CONN, policy=new_policy)
    return get_id(conn=CONN, policy_type="enterprise", uid='C')


def main():
    # declare_enterprise()
    cleand_hierarchies = {}
    hierarchies = mqtt_hierarchy(base_topic="Enterprise C/#")
    for namespace in hierarchies:
        if not cleand_hierarchies.get(namespace):
            cleand_hierarchies[namespace] = {}
        for device in hierarchies[namespace]:
            if device in ["DI-250-010", "phase", "OPR_ID"]:
                if "generic" not in cleand_hierarchies[namespace]:
                    cleand_hierarchies[namespace]["generic"] = []
                if device not in cleand_hierarchies[namespace]["generic"]:
                    cleand_hierarchies[namespace]["generic"].append(device)
            elif "_" in device:
                device_name, sensor = device.split("_", 1)
                if device_name not in cleand_hierarchies[namespace]:
                    cleand_hierarchies[namespace][device_name] = []
                if sensor not in cleand_hierarchies[namespace][device_name]:
                    cleand_hierarchies[namespace][device_name].append(sensor)
            elif "-" in device:
                device_name, sensor = device.split("-", 1)
                if device_name not in cleand_hierarchies[namespace]:
                    cleand_hierarchies[namespace][device_name] = []
                if sensor not in cleand_hierarchies[namespace][device_name]:
                    cleand_hierarchies[namespace][device_name].append(sensor)
            else:
                print(f"\t{device}")

    declare_enterprise()
    for namespace in cleand_hierarchies:
        namespace_id = create_namespace(namespace=namespace)
        for device in cleand_hierarchies[namespace]:
            device_id = create_device(namespace=namespace, device=device)
            for sensor in cleand_hierarchies[namespace][device]:
                create_sensor(namespace=namespace, device=device, sensor=sensor, parent_id=device_id, db_name="manufacturing_historian")


if __name__ == "__main__":
    main()