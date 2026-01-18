import requests

def get_request(conn:str, headers:dict):
    try:
        response = requests.get(url=conn, headers=headers)
        response.raise_for_status()
    except Exception as error:
        raise Exception(error)

    return response


def get_uns_hierarchy(conn:str, enterprise_id:str):
    """
    Get unified namespace hierarchy
    :args:
        conn:str -
    :param conn:
    :param enterprise_id:
    :return:
    """
    response = get_request(conn=conn, headers={
        "command": f'blockchain get * where id="{enterprise_id}"',
        "User-Agent": "AnyLog/1.23"
    })
    print(response.json())


if __name__ == "__main__":
    get_uns_hierarchy(conn="50.116.13.109:32049", enterprise_id="Enterprise B")
