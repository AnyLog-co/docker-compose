import json
import requests
from typing import Dict, List, Optional


def get_request(conn: str, headers:Dict[str, str])->List[dict]:
    try:
        response = requests.get(conn, headers=headers)
        response.raise_for_status()
        try:
            return response.json()
        except json.decoder.JSONDecodeError:
            return response.text
    except requests.RequestException as exc:
        print(headers.get("command"))
        raise RuntimeError(exc)


def build_command(policy_type:str, policy_id:Optional[str]=None, policy_parent:Optional[str]=None)->str:
    conditions = []

    if policy_id:
        conditions.append(f'id="{policy_id}"')
    if policy_parent:
        conditions.append(f'parent="{policy_parent}"')

    command = f"blockchain get {policy_type}"

    if conditions:
        command += " where " + " and ".join(conditions)

    return command


def get_policies(conn:str, policy_type:str, policy_id:Optional[str]=None, policy_parent:Optional[str]=None)->List[dict]:
    """

    """
    headers = {
        "command": build_command(policy_type, policy_id, policy_parent),
        "User-Agent": "AnyLog/1.23"
    }

    return get_request(conn, headers)


def get_uns_hierarchy(conn:str, root_id:str, level:int=0)->None:
    """
    Recursively print Unified Namespace hierarchy
    """
    policies = get_policies(
        conn=conn,
        policy_type="*",
        policy_parent=root_id,
    )

    for policy in policies:
        policy_data = next(iter(policy.values()))
        policy_id = policy_data.get("id")

        indent_level = level + 1
        print(f"{'\t' * indent_level}{policy}")

        # Recursive descent
        get_uns_hierarchy(
            conn=conn,
            root_id=policy_id,
            level=level + 1,
        )

def get_children_by_parent(conn:str, parent_id:str):
    """
    Demonstrate providing subset of information for a given namespace / tag based on parent policy ID
    """
    headers = {
        "command": f'blockchain get *  where [id] = "{parent_id}"  bring.children.table.sort(0) [*][parent] [*] [*][id] [*][parent] [*][namespace]',
        "User-Agent": "AnyLog/1.23"
    }

    print(get_request(conn=conn, headers=headers))


if __name__ == "__main__":
    # demonstrate showwing a set of tags (children) based on parent ID
    get_children_by_parent(conn="http://50.116.13.109:32049", parent_id="sub")

    # full UNS hierarchy
    enterprises = get_policies(conn="http://50.116.13.109:32049", policy_type="enterprise")
    for enterprise in enterprises:
        print(enterprise)
        enterprise_id = enterprise["enterprise"].get("id")
        get_uns_hierarchy(conn="http://50.116.13.109:32049", root_id=enterprise_id)
