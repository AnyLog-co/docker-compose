import ast
import datetime
import json

import grpc

import dados_pb2
import dados_pb2_grpc

channel = grpc.insecure_channel("192.168.1.211:50055")

stub = dados_pb2_grpc.PersistenceServiceStub(channel)

request = dados_pb2.WatchRequest(
    table_id="ds_data"
)

rows = {}
now = datetime.datetime.now()
for row in stub.WatchTable(request):
    print(row)
    print(type(row))
    exit(1)
    # if ast.literal_eval(row) not in list(rows.keys()):
    #     rows[ast.literal_eval(row)] = 0
    # rows[row] += 1
    # if datetime.datetime.now() - now > datetime.timedelta(minutes=1):
    #     print(json.dumps(rows, indent=2))
    #     exit(1)
