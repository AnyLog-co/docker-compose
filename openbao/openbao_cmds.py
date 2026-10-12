# URL: https://openbao.org/api-docs/
import argparse
import ast
import json
import os
import requests

ERRORS_GENERIC = {
    1: "Informational",
    2: "Successful",
    3: "Redirection",
    4: "Client Error",
    5: "Server Error",
    7: "Developer Error"
}

NETWORK_ERRORS = {
    100: "Continue",
    101: "Switching Protocols",
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    307: "Temporary Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Payload Too Large",
    414: "URI Too Long",
    415: "Unsupported Media Type",
    416: "Range Not Satisfiable",
    417: "Expectation Failed",
    418: "I'm a teapot",
    426: "Upgrade Required",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Time-out",
    505: "HTTP Version Not Supported",
    102: "Processing",
    207: "Multi-Status",
    226: "IM Used",
    308: "Permanent Redirect",
    422: "Unprocessable Entity",
    423: "Locked",
    424: "Failed Dependency",
    428: "Precondition Required",
    429: "Too Many Requests",
    431: "Request Header Fields Too Large",
    451: "Unavailable For Legal Reasons",
    506: "Variant Also Negotiates",
    507: "Insufficient Storage",
    511: "Network Authentication Required"
}

DEFAULT_CONFIG_FILE = os.path.join(os.path.expandvars(os.path.expanduser(__file__.split("openbao_cmds.py")[0])), 'openbao.env')


class OpenBao:
    def __init__(self, conn:str, token:str):
        self.conn = conn if conn is not None else '0.0.0.0:8200'
        self.token = token
        if self.token is None:
            raise ValueError("Missing token value, cannot continue...")

    def __execute_get(self, url:str, headers:dict):
        """
        Execute GET request
        :args:
            url:str - request URl
            headers:dict - REST headers
        :params:
            response:requests.GET - response fromm GET
        :return:
            response
            if response.status_code has a Client Error, return empty dict
        """
        try:
            response = requests.get(url=url, headers=headers)
        except Exception as error:
            raise Exception(f"Failed to execute GET against {url} (Error: {error}")
        else:
            if 400 <= response.status_code < 500:
                response = {}
            elif not 200 <= response.status_code < 300:
                if int(response.status_code) in NETWORK_ERRORS:
                    raise ConnectionError(f"Failed to execute GET against {url} (Network Error {response.status_code}: {NETWORK_ERRORS[int(response.status_code)]})")
                elif int(response.status_code[0]) in ERRORS_GENERIC:
                    raise ConnectionError(f"Failed to execute GET against {url} (Network Error {response.status_code}: {ERRORS_GENERIC[int(response.status_code[0])]}")

        return response


    def get_openbao_status(self):
        """
        health check for OpenBao
        :anylog-cmd:
            get openbao status where name=mybao
        :args:
            openbao_name:str - OpenBao connection name
        :params:
            headers:dict - REST headers
            url:str - URL to access OpenBao
        :return:
            dictionary for OpenBao status
        :sample output:
        {
            'initialized': True, 'sealed': False, 'standby': False, 'performance_standby': False,
            'replication_performance_mode': 'disabled', 'replication_dr_mode': 'disabled',
            'server_time_utc': 1738794866, 'version': '2.1.1', 'cluster_name': 'vault-cluster-8acc91c5',
            'cluster_id': 'bd9670ca-b594-3c6b-6431-2d81afa9bdd0'
        }
        """
        headers = {
            "X-Vault-Token": self.token,
            "Content-Type": "application/json"
        }

        url = f"http://{self.conn}/v1/sys/health"
        response = self.__execute_get(url=url, headers=headers)
        try:
            return response.json()
        except Exception as error:
            raise Exception(f"Failed to extract results for {self.conn} (Error: {error})")


    def get_openbao_value(self, section:str, key:str=None):
        """
        Get secret value(s) within OpenBao
        :anylog-cmd:
            get openbao status where name=mybao and section=XXX [and key=XXX]
        :args:
            openbao_name:str - OpenBao connection name
            section:str - subsection within secrets data key/value pairs will be stored
            key:str - specific key to get value for
        :params:
            headers:dict - REST headers
            url:str - URL to access OpenBao
        :return:
            if key - return specific value
            if no key - return full dict of params
        :note:
            if section or key is invalid then returns error 404 - error should be "failed to get valid data"
        """
        headers = {
            "X-Vault-Token": self.token,
        }

        url = f"http://{self.conn}/v1/secret/data/{section}"
        response = self.__execute_get(url=url, headers=headers)
        if response == {}:
            return  response

        try:
            output = response.json()
        except Exception as error:
            raise Exception(f"Failed to extract key/values for {url} (Error: {error})")

        content = output['data']['data'][section]
        if key:
            if key in content:
                return content[key]
            else:
                raise ValueError(f'Failed to find value for {key}')
        else:
            return content


    def publish_data(self, section:str, payload:dict):
        """
        Publish value to OpenBao
        :args:
            :args:
            openbao_name:str - OpenBao connection name
            section:str - subsection within secrets data key/value pairs will be stored
            payload:dict - key/value pairs
        :params:
            headers:dict - REST headers
            url:str - URL to access OpenBao
        """
        headers = {
            "X-Vault-Token": self.token,
            "Content-Type": "application/json"
        }

        orig_payloads = self.get_openbao_value(section=section)
        updated_payloads = {**orig_payloads, **payload}
        publish_payloads = {'data': {
            section: updated_payloads
        }}

        url = f"http://{self.conn}/v1/secret/data/{section}"

        try:
            response = requests.post(url=url, headers=headers, json=publish_payloads)
        except Exception as error:
            raise Exception(f"Failed to POST data against {url} (Error: {error})")
        else:
            if not 200 <= response.status_code < 300:
                if int(response.status_code) in NETWORK_ERRORS:
                    raise ConnectionError(f"Failed to execute POST against {url} (Network Error {response.status_code}: {NETWORK_ERRORS[int(response.status_code)]})")
                elif int(response.status_code[0]) in ERRORS_GENERIC:
                    raise ConnectionError(f"Failed to execute POST against {url} (Network Error {response.status_code}: {ERRORS_GENERIC[int(response.status_code[0])]}")


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('--config-file', type=str,default=DEFAULT_CONFIG_FILE, help='OpenBao .env config files')
    parse.add_argument('--conn', type=str, default='0.0.0.0:8200', help='URL connection')
    parse.add_argument('--token', type=str, default=None, help='OpenBao token')
    parse.add_argument('--section', type=str, default='mybao', help='Section to secrets data location')
    args = parse.parse_args()

    openbao = OpenBao(conn=args.conn, token=args.token)
    args.config_file = os.path.expandvars(os.path.expanduser(args.config_file))
    if not os.path.isfile(args.config_file):
        raise FileNotFoundError(f"Failed to locate config file {args.config_file}")

    # check status
    print(openbao.get_openbao_status())
    configs = {}
    with open(args.config_file, 'r') as f:
        for line in f.read().split("\n"):
            if not (line.startswith("#") or not line):
                key, value = line.split("=")
                try:
                    configs[key.strip()] = ast.literal_eval(value.strip())
                except:
                    configs[key.strip()] = value.strip()

    openbao.publish_data(section=args.section, payload=configs)
    print(openbao.get_openbao_value(section=args.section))


if __name__ == '__main__':
    main()
    # # 127.0.0.1:8200  --check-health
    # openbao = OpenBao()
    # openbao.connect_openbao(name='mybao', conn='0.0.0.0:8200', token='s.57hG4fLMZzRbbPF7mF5fA2Md')
    #
    # # check status
    # print(openbao.get_openbao_status(openbao_name='mybao'))
    #
    # # create section and set payload value(s)
    # openbao.publish_data(openba_name='mybao', section='anylog-data', payload={'param1': True, 'param2': 3, 'param3': 'abc'})
    # print(openbao.get_openbao_value(openbao_name='mybao', section='anylog-data'))
    #
    # # add another value and update value to payload
    # openbao.publish_data(openba_name='mybao', section='anylog-data', payload={'param1': False, 'param4': ''})
    # print(openbao.get_openbao_value(openbao_name='mybao', section='anylog-data'))