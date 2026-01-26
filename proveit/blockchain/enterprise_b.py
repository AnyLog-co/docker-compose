import time

import requests
from typing_extensions import assert_type
from mqtt_hierarchy import MqttHierarchy
from enterprise_c import create_policy


def get_uns_info(node_info:dict):
    asset_type_name = node_info.get("assettypename") # example site
    asset_path = node_info.get("assetpath") # UNS/ProveItBeverage/Plant2/FillerProduction/Node
    asset_name = node_info.get("assetname")
    display_name = node_info.get("displayname")

    return asset_type_name, asset_path, asset_name, display_name


def main():
    base_topic = "Enterprise B"
    # mqtt_sub = MqttHierarchy(base_topic=f"{base_topic}/#", broker="virtualfactory.proveit.services",
    #                          username="proveitreadonly", password="proveitreadonlypassword", collect_seconds=10)

    headers = {
        "command": f"blockchain get uns where [namespace] contains {base_topic}",
        "User-Agent": "AnyLog/1.23"
    }
    \
    try:
        response = requests.request("get", url="http://50.116.13.109:32049", headers=headers, )
        response.raise_for_status()
    except Exception as error:
        raise Exception(f"Failed to execute GET against http://50.116.13.109:32049 (Error: {error})")
    print(response.json())






if __name__ == "__main__":
    main()