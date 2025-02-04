import argparse
import os
import requests

def post_data(conn:str, token:str, data:dict):
    headers = {
        "X-Vault-Token": token,
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url=f"http://{conn}/v1/secret/data/anylog-data", headers=headers,
                                     json={"data": {"anylog-data": data}})
        response.raise_for_status()
    except Exception as error:
        raise Exception(f"Failed to POST data against {conn} (Error: {error})")


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('dotenv_configs', type=str, default=None, help='dotenv configs')
    parse.add_argument('--vault-url', type=str, default='127.0.0.1:8200', help='OpenBao URL')
    parse.add_argument('--vault-token',  type=str, default=None, help='OpenBao access token')
    args = parse.parse_args()

    data = {}

    for file_name in args.dotenv_configs.split(","):
        full_path = os.path.expanduser(os.path.expandvars(file_name))
        if not os.path.isfile(full_path):
            raise FileNotFoundError(f"Failed to locate {full_path}")
        with open(full_path, 'r') as f:
            for line in f.read().split("\n"):
                if not line.startswith('#') and line != "":
                    key, value = line.split("=", 1)
                    data[key.strip()] = value.strip() if value.strip() != '""' else ""

    post_data(conn=args.vault_url, token=args.vault_token, data=data)




if __name__ == '__main__':
    main()