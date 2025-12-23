import argparse
import datetime
import json
import gzip
import shutil
import requests


CONN = "http://23.239.12.151:32349"

def rest_request(headers:dict):
    print(headers['command'])
    try:
        response = requests.get(url=CONN, headers=headers, timeout=(300, 300))
        response.raise_for_status()
        return response
    except requests.exceptions.ChunkedEncodingError:
        pass
    except Exception as error:
        if 'destination' in headers:
            raise Exception(f"Conn: {CONN} | Command: run client ({headers['destination']}) {headers['command']} (Error: {error})")
        else:
            raise Exception(f"Conn: {CONN} | Command: {headers['command']} (Error: {error})")

def get_conns(company:str):
    headers = {
        "command": f'blockchain get operator where company="{company}" bring.ip_port',
        "User-Agent": "AnyLog/1.23"
    }

    response = rest_request(headers=headers)
    return response.text.split(",")

def get_tables(conn, db_name):
    tables = []
    headers = {
        "command": f"get tables where dbms={db_name} and format=json",
        "User-Agent": "AnyLog/1.23",
        "destination": conn
    }
    response = rest_request(headers=headers)
    output = response.json()
    for output_table in output[conn][db_name]:
        if not output_table.startswith("par"):
            tables.append(output_table)
    return tables


def get_columns(db_name:str, table_name:str):
    columns = []
    timestamp = None

    headers = {
        "command": f"get columns where dbms={db_name} and table={table_name} and format=json",
        "User-Agent": "AnyLog/1.23"
    }

    response = rest_request(headers=headers)
    output = response.json()
    for column in output:
        if column not in ['row_id', 'insert_timestamp', 'tsd_name', 'tsd_id']:
            columns.append(column)
            if not timestamp and 'timestamp' in output[column]:
                timestamp = column
    if not timestamp:
        timestamp = 'insert_timestamp'
        columns.append(timestamp)
    return timestamp, columns


def get_data(conn:str, db_name:str, table_name:str, columns, timestamp):
    content = []
    headers = {
        "command": f"sql {db_name} format=json:list and stat=false select min({timestamp}) as min_ts, max({timestamp}) as max_ts from {table_name}",
        "User-Agent": "AnyLog/1.23",
        "destination": conn
    }
    response = rest_request(headers=headers)
    output = response.json()
    min_ts = datetime.datetime.strptime(output[0]['min_ts'], "%Y-%m-%d %H:%M:%S.%f")
    max_ts = datetime.datetime.strptime(output[0]['max_ts'],  "%Y-%m-%d %H:%M:%S.%f")

    current_timestamp = min_ts - datetime.timedelta(days=3)
    while current_timestamp <= max_ts + datetime.timedelta(days=7):
        next_timestamp = current_timestamp + datetime.timedelta(days=1)
        headers = {
            "command": f"sql {db_name} format=json:list and stat=false select {','.join(columns)} from {table_name} WHERE period(day, 1, '{current_timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")}', {timestamp}) ORDER BY {timestamp}",
            "User-Agent": "AnyLog/1.23",
            "destination": conn
        }

        response = rest_request(headers=headers)
        if response:
            new_content = response.json()
            if new_content:
                content += new_content
        current_timestamp = next_timestamp

    return content


def dedupe_dicts(dicts):
    seen = set()
    result = []

    for d in dicts:
        key = tuple(sorted(d.items()))
        if key not in seen:
            seen.add(key)
            result.append(d)

    return result


def store_content(db_name:str, table:str, content:list):
    start_ts = datetime.datetime.strptime(content[0]['timestamp'], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y_%m_%d_%H_%M_%S_%f")
    end_ts = datetime.datetime.strptime(content[1]['timestamp'], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y_%m_%d_%H_%M_%S_%f")
    fname = f"{db_name}.{table}.{start_ts}.{end_ts}.json"
    with open(fname, 'w') as f:
        for row in content:
            f.write(f"{json.dumps(row)},\n") if row != content[-1] else f.write(f"{json.dumps(row)}")
    return fname

def zipfile(fname):
    gzip_fname = f"{fname}.gz"
    with open(fname, "rb") as f_in:
        with gzip.open(gzip_fname, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)


def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('--conn', type=str, default=CONN, help="REST conn for query node")
    parse.add_argument('--company', type=str, default="Smart City", help="Node(s) owner")
    parse.add_argument("--db-name", type=str, default="cos", help="Logical database")
    args = parse.parse_args()
    args.conn = f"http://{args.conn}" if not args.conn.startswith("http") else args.conn

    my_data = {}

    conns = get_conns(company="Smart City")
    for conn in conns:
        tables = get_tables(conn, db_name="cos")
        for table in tables:
            if table not in my_data:
                my_data[table] = [conn]
            else:
                my_data[table].append(conn)

    for table in my_data:
        print(table)
        timestamp, columns = get_columns(db_name="cos", table_name=table)
        full_content = []
        for conn in conns:
            full_content += get_data(conn=conn, db_name="cos", table_name=table, columns=columns, timestamp=timestamp)
        content = dedupe_dicts(full_content)
        fname = store_content(db_name='cos', table=table, content=content)
        zipfile(fname=fname)


if __name__ == '__main__':
    main()