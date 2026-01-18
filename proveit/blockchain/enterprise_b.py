import copy
from blockchain_cmds import get_id, publish_policy

CONN = "http://50.116.13.109:32049"
DB_NAME = "bottle_factory"

NAMESPACE = [
    {"namespace": {
        "id": "Site1",
        "name": "The Cap Shack",
        "plant": 1,
        "parent": "Enterprise B",
        "path": "UNS/ProveItBeverage/Plant1/Node",
        "namespace": "Enterprise B/Site1"
    }},
    {"namespace": {
        "id": "Site2",
        "name": "Filler Central",
        "plant": 2,
        "parent": "Enterprise B",
        "path": "UNS/ProveItBeverage/Plant2/Node",
        "namespace": "Enterprise B/Site2"
    }},
    {"namespace": {
        "id": "Site3",
        "name": "Generic Plant",
        "plant": 3,
        "parent": "Enterprise B",
        "path": "UNS/ProveItBeverage/Plant3/Node",
        "namespace": "Enterprise B/Site3",
    }}
]

ASSET = [
    {"asset": {
        "name": "Processing",
        "type": "LiquidProcessing",
        "parent": "Site1",
        "path": "UNS/ProveItBeverage/Plant1/LiquidProcessing/Node",
        "namespace": "Enterprise B/Site1/liquidprocessing"
    }},
    {"asset": {
        "name": "Processing",
        "type": "LiquidProcessing",
        "parent": "Site2",
        "path": "UNS/ProveItBeverage/Plant2/LiquidProcessing/Node",
        "namespace": "Enterprise B/Site2/liquidprocessing"
    }},
    {"asset": {
        "name": "Processing",
        "type": "LiquidProcessing",
        "parent": "Site3",
        "path": "UNS/ProveItBeverage/Plant3/LiquidProcessing/Node",
        "namespace": "Enterprise B/Site3/liquidprocessing"
    }}
]

TANKS = [
    {"tank": {
        "name": "Tank 1",
        "parent": None,
        "path": "UNS/ProveItBeverage/Plant1/LiquidProcessing/TankStorage01/Tank01/Node",
        "namespace": "Enterprise B/Site1/liquidprocessing/tankstorage01/tank01/"
    }},
    {"tank": {
        "name": "Left Tank",
        "parent": None,
        "path": "UNS/ProveItBeverage/Plant2/LiquidProcessing/TankStorage01/Tank01/Node",
        "namespace": "Enterprise B/Site2/liquidprocessing/tankstorage01/tank01"
    }},
    {"tank": {
        "name": "North Tank",
        "parent": None,
        "path": "UNS/ProveItBeverage/Plant3/LiquidProcessing/TankStorage01/Tank01/Node",
        "namespace": "Enterprise B/Site3/liquidprocessing/tankstorage01/tank01"
    }}
]

LOTS = [
    {"lot": {
        "id": "L01-0242",
        "lot_num": 242,
        "name": "Orange Soda Mix",
        "parent": None,
        "namespace": "Enterprise B/Site1/liquidprocessing/tankstorage01/tank01/lotnumber"
    }},
    {"lot": {
        "id": "L01-0189",
        "lot_num": 189,
        "name": "Orange Soda Mix",
        "parent": None,
        "namespace": "Enterprise B/Site2/liquidprocessing/tankstorage01/tank01/lotnumber"
    }},
    {"lot": {
        "id": "L02-0139",
        "lot_num": 1639,
        "name": "Cola Mix",
        "parent": None,
        "namespace": "Enterprise B/Site3/liquidprocessing/tankstorage01/tank01/lotnumber"
    }}
]

KPIS = [
    {"kpi": {
        "dbms": DB_NAME,
        "table": "kpi",
        "sensor": "oee",
        "parent": None,
        "namespace": None
    }},
    {"kpi": {
        "dbms": DB_NAME,
        "table": "kpi",
        "sensor": "performance",
        "parent": None,
        "namespace": None
    }},
    {"kpi": {
        "dbms": DB_NAME,
        "table": "kpi",
        "sensor": "quality",
        "parent": None,
        "namespace": None
    }},
    {"kpi": {
        "dbms": DB_NAME,
        "table": "kpi",
        "sensor": "availability",
        "parent": None,
        "namespace": None
    }},
]

SENSORS = [
    {"sensor": {
        "dbms": DB_NAME,
        "table": "processing",
        "sensor": "state",
        "parent": None,
        "namespace": None
    }},
    {"sensor": {
        "dbms": DB_NAME,
        "table": "processing",
        "sensor": "duration",
        "parent": None,
        "namespace": None
    }},
    {"sensor": {
        "dbms": DB_NAME,
        "table": "processing",
        "sensor": "flowrate",
        "parent": None,
        "namespace": None
    }},
    {"sensor": {
        "dbms": DB_NAME,
        "table": "processing",
        "sensor": "temperature",
        "parent": None,
        "namespace": None
    }},
    {"sensor": {
        "dbms": DB_NAME,
        "table": "processing",
        "sensor": "weight",
        "parent": None,
        "namespace": None
    }},

]


def declare_enterprise():
    new_policy = {"enterprise": {
            "id": "Enterprise B",
            "uid": "B",
            "namespace": "Enterprise B"
        }}

    publish_policy(conn=CONN, policy=new_policy)

def main():
    declare_enterprise()

    for index in range(3):
        publish_policy(conn=CONN, policy=NAMESPACE[index])
        namespace_id = NAMESPACE[index].get("namespace").get("id")

        publish_policy(conn=CONN, policy=ASSET[index])
        asset_id = get_id(conn=CONN, policy_type="asset", parent=ASSET[index]["asset"].get("parent"))

        tank = TANKS[index]
        if not tank["tank"].get("parent"):
            tank["tank"]["parent"] = asset_id
        publish_policy(conn=CONN, policy=tank)
        tank_id = get_id(conn=CONN, policy_type="tank", parent=asset_id)

        lot = LOTS[index]
        if not lot["lot"].get("parent"):
            lot["lot"]["parent"] = tank_id
        publish_policy(conn=CONN, policy=lot)
        lot_id = get_id(conn=CONN, policy_type="lot", parent=tank_id)

        print(f"{namespace_id} - {lot_id}")
        for kpi in copy.deepcopy(KPIS):
            sensor = kpi.get("kpi").get("sensor")
            if not kpi["kpi"].get("parent"):
                kpi["kpi"]["parent"] = lot_id

            if not kpi["kpi"].get("namespace"):
                kpi["kpi"]["namespace"] = f"Enterprise B/{namespace_id}/liquidprocessing/tankstorage01/tank01/metric/{sensor}"
            publish_policy(conn=CONN, policy=kpi)

        for sensor in copy.deepcopy(SENSORS):
            name = sensor.get("sensor").get("sensor")
            if not sensor["sensor"].get("parent"):
                sensor["sensor"]["parent"] = lot_id
            if name == "state" and not sensor["sensor"]["namespace"]:
                sensor["sensor"]["namespace"] = f"Enterprise B/{namespace_id}/liquidprocessing/tankstorage01/tank01/processdata/state"
            elif not sensor["sensor"]["namespace"]:
                sensor["sensor"]["namespace"] = f"Enterprise B/{namespace_id}/liquidprocessing/tankstorage01/tank01/processdata/process/{name}"
            publish_policy(conn=CONN, policy=sensor)


if __name__ == "__main__":
    main()