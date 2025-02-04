import argparse
import json
import os
import requests

DIR_PATH = os.path.expnaduser(os.path.expandvars('$ANYLOG_PATH/openbao'))
ENV_FILE = os.path.join(DIR_PATH, 'configs.env')

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
        full_data = response.json()['data']['data']['anylog-data']
        data = {key: value for key, value in full_data.items() if value != ""}
    return data

def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('vault_url', type=str, default='127.0.0.1:8200', help='OpenBao URL')
    parse.add_argument('vault_token',  type=str, default=None, help='OpenBao access token')
    parse.add_argument('--check-health', type=bool, const=True, default=False, nargs='?', help='Check OpenBao status')
    parse.add_argument('--disable-get-data', type=bool, const=True, default=False, nargs='?', help="Don't get configs")
    args = parse.parse_args()

    if args.check_health is True:
        check_health(conn=args.vault_url, token=args.vault_token)

    if args.disable_get_data is False:
        data = get_data(conn=args.vault_url, token=args.vault_token)
        with open(ENV_FILE, 'w') as f:
            for key in data:
                value = data[key]
                if " " in value:
                    f.write(f'{key}="{value}"\n')
                else:
                    f.write(f'{key}={value}\n')





if __name__ == '__main__':
    main()