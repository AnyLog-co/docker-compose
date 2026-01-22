import json
from blockchain_cmds import publish_policy, get_id
from connector_opcua import TreeStruct

URL = "opc.tcp://virtualfactory.proveit.services:4841/discovery"
TREE_BASE = "Site1/liquidprocessing"
CONN = "http://50.116.13.109:32049"
DBMS="bottle_factory"

def declare_enterprise():
    new_policy = {
        "enterprise": {
            "id": "Enterprise B",
            "uid": 'B',
            "company": "Bottle Factory",
            "namespace": "Enterprise B",
        }
    }

    publish_policy(conn=CONN, policy=new_policy)
    return get_id(conn=CONN, policy_type="enterprise", uid='B')

def declare_site(site:str, parent:str, asset_info:dict):
    new_policy = {
        "site": {
            "id": site,
            "parent": parent,
            "name": asset_info.get("displayname", site),
            "assetname": asset_info.get("assetname"),
            "assetpath": asset_info.get("assetpath"),
            "namespace": asset_info.get("namespace")

        }
    }

    publish_policy(conn=CONN, policy=new_policy)
    return get_id(conn=CONN, policy_type="site", name=asset_info.get("displayname", site))

def declare_tank(parent:str, asset_info:dict):
    new_policy = {
        "tank": {
            "parent": parent,
            "name": asset_info.get("displayname", asset_info.get("assetname")),
            "assetname": asset_info.get("assetname"),
            "assetpath": asset_info.get("assetpath"),
            "namespace": asset_info.get("namespace")

        }
    }

    publish_policy(conn=CONN, policy=new_policy)
    return get_id(conn=CONN, policy_type="tank", name=asset_info.get("displayname", asset_info.get("assetname")) )


def declare_kpis(db_name:str, parent:str, asset_info:list):
    for asset in asset_info:
        # asset =
        if asset.nodeid.Identifier.rsplit('/', 1)[-1] in ["oee", "performance", "availability", "quality"]:
            new_policy = {
                "kpi": {
                    "name": asset.nodeid.Identifier.rsplit('/', 1)[-1],
                    "parent": parent,
                    "namespace": asset.nodeid.Identifier,
                    "dbms": db_name,
                    "table": "kpi"
                }
            }

            publish_policy(conn=CONN, policy=new_policy)


def declare_processing(db_name:str, parent:str, processing_info:list, state_info:list):
    for asset in processing_info:
        if asset.nodeid.Identifier.rsplit('/', 1)[-1] in ["flowrate", "weight", "temperature"]:
            new_policy = {
                "sensor": {
                    "name": asset.nodeid.Identifier.rsplit('/', 1)[-1],
                    "parent": parent,
                    "namespace": f"Enterprise B/{asset.nodeid.Identifier}",
                    "dbms": db_name,
                    "table": "processing"
                }
            }

            publish_policy(conn=CONN, policy=new_policy)



    new_policy = {
        "sensor": {
            "name": "state",
            "parent": parent,
            "namespace": f"Enterprise B/{state_info[0].nodeid.Identifier.rsplit('/', 1)[0]}",
            "dbms": db_name,
            "table": "processing"
        }
    }
    publish_policy(conn=CONN, policy=new_policy)



def main():
    tree_struct = TreeStruct(url=URL)

    # declare Enterprise Policy
    enterprise_id = declare_enterprise()

    for site in ["Site1", "Site2", "Site3"]:
        assets = {}
        node_info = node_info = tree_struct.get_children(node_id=f"ns=2;s={site}/node/assetidentifier")
        values = tree_struct.get_value(node_id=node_info)
        assets = {node_info[i].nodeid.Identifier.rsplit("/", 1)[-1]: values[i] for i in range(len(node_info))}
        assets["namespace"] = f"Enterprise B/{site}"
        site_id = declare_site(site=site, parent=enterprise_id, asset_info=assets)

        nmaespaces = tree_struct.get_children(node_id=f"ns=2;s={site}/liquidprocessing")
        for namespace in nmaespaces:
            if "node" in namespace.nodeid.Identifier:
                node_info = tree_struct.get_children(node_id=f"ns=2;s={namespace.nodeid.Identifier}/assetidentifier")
                values = tree_struct.get_value(node_id=node_info)
                assets = {node_info[i].nodeid.Identifier.rsplit("/", 1)[-1]: values[i] for i in range(len(node_info))}
                assets["namespace"] = f"Enterprise B/{node_info[0].nodeid.Identifier.rsplit('/node', 1)[0]}"

            if "tankstorage01" in namespace.nodeid.Identifier: # needs to happen first
                nodes = tree_struct.get_children(node_id=f"ns=2;s={namespace.nodeid.Identifier}")
                for node in nodes:
                    if "tank" in node.nodeid.Identifier.rsplit("/", 1)[-1]:
                        tank_info = tree_struct.get_children(node_id=f"ns=2;s={node.nodeid.Identifier}/node/assetidentifier")
                        values = tree_struct.get_value(node_id=tank_info)
                        assets = {tank_info[i].nodeid.Identifier.rsplit("/", 1)[-1]: values[i] for i in range(len(tank_info))}
                        assets["namespace"] = f"Enterprise B/{tank_info[0].nodeid.Identifier.rsplit('/node', 1)[0]}"
                        tank_id = declare_tank(parent=site_id, asset_info=assets)

                        # KPIs
                        kpi_info = tree_struct.get_children(node_id=f"ns=2;s={node.nodeid.Identifier}/metric")
                        declare_kpis(db_name=DBMS, parent=tank_id, asset_info=kpi_info)

                        # Processing
                        processing_info = tree_struct.get_children(node_id=f"ns=2;s={node.nodeid.Identifier}/processdata/process")
                        state_info = tree_struct.get_children(node_id=f"ns=2;s={node.nodeid.Identifier}/processdata/state")

                        declare_processing(db_name=DBMS, parent=tank_id, processing_info=processing_info, state_info=state_info)

    tree_struct.disconnect()



if __name__ == "__main__":
    main()

