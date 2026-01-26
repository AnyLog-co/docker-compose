import time
from blockchain_cmds import publish_policy, get_id
from mqtt_hierarchy import MqttHierarchy

def create_policy(policy_type:str, policy_name:str, namespace:str, policy_parent:str=None, db_name:str=None,
                  uns_path:str=None, company:str=None):
    new_policy = {
        policy_type: {
            "name": policy_name,
            "namespace": namespace,
            **({"company": company} if company else {}),
            **({"parent": policy_parent} if policy_parent else {}),
            **({"dbms": db_name} if db_name else {}),
            **({"table": namespace.replace('/', '_').replace('-', '_').split("_", 1)[-1].lower()} if policy_type == "sensor" else {}),
            **({"asset_path": uns_path} if uns_path else {})
        }
    }

    publish_policy(conn="http://50.116.13.109:32049", policy=new_policy)
    return get_id(conn="http://50.116.13.109:32049", policy_type=policy_type, name=policy_name, namespace=namespace,
                  parent=policy_parent)



def main():
    """
    The following provides unified namespace logic for Enterprise C
    :logic:
    enterprise (ex. Enterprise C)
        namespace (ex. tff)
            device  (ex.TFF300)
                sensor - FORMULA-NAME --> tff_tff300_formula_name
                         BATCH-ID --> tff_tff300_batch_id
                         RECIPE-NAME --> tff_tff300_recipe_name
    """
    base_topic="Enterprise C"
    mqtt_sub = MqttHierarchy(base_topic=f"{base_topic}/#", broker="virtualfactory.proveit.services",
                             username="proveitreadonly", password="proveitreadonlypassword", collect_seconds=10)

    mqtt_sub.connect()
    time.sleep(mqtt_sub.collect_seconds)


    sub_topics = [
        topic
        for topic in mqtt_sub.topics_seen
        if topic.split("/")[1] in {"sub", "sum", "chrom", "tff"}
    ]

    hierarchy = mqtt_sub.build_hierarchy(sub_topics)
    mqtt_sub.attach_values(hierarchy, mqtt_sub.base_topic.replace("/#", ""))

    enterprise_policy = create_policy(policy_type="enterprise", policy_name=base_topic, namespace=base_topic,
                                      policy_parent=None)
    print(enterprise_policy)
    for namespace in hierarchy:
        namespace_policy = create_policy(policy_type="namespace", policy_name=namespace,
                                         namespace=f"{base_topic}/{namespace}", policy_parent=enterprise_policy)
        print(f"namespace: {namespace}")
        for device in hierarchy[namespace]:
            if isinstance(hierarchy[namespace][device], dict):
                device_policy = create_policy(policy_type="device", policy_name=device,
                                              namespace=f"{base_topic}/{namespace}/{device}",
                                              policy_parent=namespace_policy)
                for sensor in hierarchy[namespace][device]:
                    create_policy(policy_type="sensor", policy_name=sensor,
                                  namespace=f"{base_topic}/{namespace}/{device}/{sensor}", policy_parent=device_policy,
                                  db_name="manufacturing_historian")
            elif "_" in device:
                device_name, sensor = device.split("_", 1)
                device_policy = create_policy(policy_type="device", policy_name=device_name,
                                              namespace=f"{base_topic}/{namespace}/{device_name}",
                                              policy_parent=namespace_policy)
                create_policy(policy_type="sensor", policy_name=sensor,
                              namespace=f"{base_topic}/{namespace}/{device_name}/{sensor}", policy_parent=device_policy,
                              db_name="manufacturing_historian")

            elif device.startswith(("TFF", "CHR01", "XV50", "SUM5")):
                    device_name, sensor = device.split("-", 1)
                    device_policy = create_policy(policy_type="device", policy_name=device_name,
                                                  namespace=f"{base_topic}/{namespace}/{device_name}",
                                                  policy_parent=namespace_policy)
                    create_policy(policy_type="sensor", policy_name=sensor,
                                  namespace=f"{base_topic}/{namespace}/{device_name}/{sensor}",
                                  policy_parent=device_policy, db_name="manufacturing_historian")
            elif device == "phase":
                create_policy(policy_type="sensor", policy_name=device,
                              namespace=f"{base_topic}/{namespace}/{device}",
                              policy_parent=namespace_policy, db_name="manufacturing_historian")
            else:
                print(f"{device} <-- THIS")


    # print(hierarchy)


if __name__ == "__main__":
    main()

