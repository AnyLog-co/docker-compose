import argparse
import json

import requests

def check_health(conn:str, token:str):
    headers = {
        "X-Vault-Token": token,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url=f"http://{conn}/v1/sys/health", headers=headers)
        response.raise_for_status()
    except Exception as error:
        raise Exception(f"Failed to execute GET {conn} (Error: {error})")
    else:
        print(json.dumps(response.json(), indent=4))


def get_data(conn:str, token:str):
    headers = {
        "X-Vault-Token": token
    }

    try:
        response = requests.get(url=f"http://{conn}/v1/secret/data/anylog-data", headers=headers)
        response.raise_for_status()
    except Exception as error:
        raise Exception(f"Failed to execute GET {conn} (Error: {error})")
    else:
        print(json.dumps(response.json(), indent=4))


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('vault_url', type=str, default='127.0.0.1:8200', help='OpenBao URL')
    parse.add_argument('vault_token',  type=str, default=None, help='OpenBao access token')
    parse.add_argument('--check-health', type=bool, const=True, default=False, nargs='?', help='Check OpenBao status')
    args = parse.parse_args()

    if args.check_health is True:
        check_health(conn=args.vault_url, token=args.vault_token)

    get_data(conn=args.vault_url, token=args.vault_token)

if __name__ == '__main__':
    main()