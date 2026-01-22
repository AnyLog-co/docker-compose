from blockchain_cmds import publish_policy, get_id
from connector_opcua import TreeStruct

URL = "opc.tcp://virtualfactory.proveit.services:4842/discovery"
TREE_BASE = "sub"
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

    # publish_policy(conn=CONN, policy=new_policy)
    return get_id(conn=CONN, policy_type="enterprise", uid='C')


def create_namespace():
    new_policy = {
        "namespace" : {
            "id": "sub",
            "parent": "EnterpriseC",
            "namespace": "Enterprise C/sub"
        }
    }

    # publish_policy(conn=CONN, policy=new_policy)
    return get_id(conn=CONN, policy_type="enterprise", uid='C')



def main():
    tree_struct = TreeStruct(url=URL)
    declare_enterprise()
    create_namespace()

    namespaces = tree_struct.get_children(node_id="ns=2;s=sub")
    for namespace in namespaces:
        print(namespace.node.nodeid.Identifier)
    tree_struct.disconnect()

if __name__ == "__main__":
    main()