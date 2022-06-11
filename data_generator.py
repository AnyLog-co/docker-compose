import datetime
import json
import random
import requests


TIMESTAMP = datetime.datetime.strptime('2022-04-01 08:00:00.0000', '%Y-%m-%d %H:%M:%S.%f')


def put_data(conn:str, row:str)->bool:
    """
    Execute PUT command
    :args:
        conn:str - REST connection information
        data_set:list - list of JSON to put in database
    :params:
        status:bool
        headers:dict - REST header information
    """
    status = True
    headers = {
        'type': 'json',
        'dbms': 'nvidia',
        'table': 'traffic_data',
        'mode': 'streaming',
        'Content-Type': 'text/plain'
    }

    try:
        r = requests.put(url='http://%s' % conn, headers=headers, data=row)
    except Exception as e:
        print('Failed to PUT data into %s (Error: %s)' % (conn, e))
        status = False
    else:
        if int(r.status_code) != 200:
            print('Failed to PUT data into %s (Network Error: %s)' % r.status_code)
            status = False

    return status


def palo_alto():
    data = [
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-01T08:00:00.000000Z', 'speed': 80.32},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-01T20:00:48.000000Z', 'speed': 78.54},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-02T08:01:20.000000Z', 'speed': 69.77},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-02T20:02:13.000000Z', 'speed': 62.49},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-03T08:02:51.000000Z', 'speed': 73.06},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-03T20:03:10.000000Z', 'speed': 80.95},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-04T08:03:50.000000Z', 'speed': 81.71},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-04T20:04:46.000000Z', 'speed': 57.91},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-05T08:05:19.000000Z', 'speed': 57.07},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-05T20:06:14.000000Z', 'speed': 66.73},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-06T08:06:24.000000Z', 'speed': 66.07},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-06T20:06:31.000000Z', 'speed': 77.27},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-07T08:07:10.000000Z', 'speed': 69.4},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-07T20:08:01.000000Z', 'speed': 75.44},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-08T08:08:48.000000Z', 'speed': 57.85},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-08T20:08:56.000000Z', 'speed': 69.56},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-09T08:09:43.000000Z', 'speed': 62.2},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-09T20:10:01.000000Z', 'speed': 76.25},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-10T08:10:32.000000Z', 'speed': 77.77},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-10T20:11:13.000000Z', 'speed': 59.32},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-11T08:11:27.000000Z', 'speed': 57.0},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-11T20:11:40.000000Z', 'speed': 54.03},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-12T08:11:45.000000Z', 'speed': 57.98},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-12T20:12:27.000000Z', 'speed': 78.88},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-13T08:12:57.000000Z', 'speed': 66.26},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-13T20:13:55.000000Z', 'speed': 62.6},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-14T08:14:45.000000Z', 'speed': 65.96},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-14T20:15:25.000000Z', 'speed': 58.4},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-15T08:15:44.000000Z', 'speed': 72.21},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-15T20:15:51.000000Z', 'speed': 79.71},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-16T08:16:06.000000Z', 'speed': 67.47},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-16T20:16:34.000000Z', 'speed': 73.94},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-17T08:16:34.000000Z', 'speed': 73.1},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-17T20:17:15.000000Z', 'speed': 58.9},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-18T08:18:11.000000Z', 'speed': 81.49},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-18T20:18:33.000000Z', 'speed': 69.58},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-19T08:18:48.000000Z', 'speed': 67.82},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-19T20:19:16.000000Z', 'speed': 64.93},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-20T08:19:27.000000Z', 'speed': 81.53},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-20T20:20:14.000000Z', 'speed': 57.79},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-21T08:20:55.000000Z', 'speed': 81.9},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-21T20:21:34.000000Z', 'speed': 81.57},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-22T08:22:13.000000Z', 'speed': 72.32},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-22T20:22:19.000000Z', 'speed': 65.11},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-23T08:23:01.000000Z', 'speed': 73.38},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-23T20:23:30.000000Z', 'speed': 65.76},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-24T08:23:43.000000Z', 'speed': 74.95},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-24T20:24:12.000000Z', 'speed': 59.32},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-25T08:25:04.000000Z', 'speed': 60.24},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-25T20:25:07.000000Z', 'speed': 78.5},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-26T08:25:30.000000Z', 'speed': 78.59},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-26T20:26:10.000000Z', 'speed': 65.84},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-27T08:26:11.000000Z', 'speed': 78.26},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-27T20:27:00.000000Z', 'speed': 78.68},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-28T08:27:01.000000Z', 'speed': 80.66},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-28T20:27:01.000000Z', 'speed': 70.74},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-29T08:27:32.000000Z', 'speed': 76.35},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-29T20:27:39.000000Z', 'speed': 79.96},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-30T08:28:15.000000Z', 'speed': 81.68},
        {'city': 'Palo Alto', 'location': '37.460674, -122.140963', 'intersection': '101 N / University Ave', 'timestamp': '2022-04-30T20:28:50.000000Z', 'speed': 84.63}
    ]
    for row in data:
        put_data(conn='localhost:32149', row=json.dumps(row))


def santa_clara()->list:
    data = [
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-01T08:00:00.000000Z', 'speed': 56.33},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-01T20:00:20.000000Z', 'speed': 68.53},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-02T08:00:36.000000Z', 'speed': 54.84},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-02T20:01:31.000000Z', 'speed': 62.43},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-03T08:02:02.000000Z', 'speed': 53.62},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-03T20:02:20.000000Z', 'speed': 56.99},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-04T08:03:07.000000Z', 'speed': 64.08},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-04T20:04:00.000000Z', 'speed': 50.81},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-05T08:04:07.000000Z', 'speed': 59.56},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-05T20:04:08.000000Z', 'speed': 66.92},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-06T08:04:36.000000Z', 'speed': 53.94},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-06T20:04:42.000000Z', 'speed': 59.62},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-07T08:05:19.000000Z', 'speed': 67.96},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-07T20:06:13.000000Z', 'speed': 64.45},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-08T08:07:05.000000Z', 'speed': 68.6},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-08T20:08:00.000000Z', 'speed': 65.97},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-09T08:08:40.000000Z', 'speed': 61.87},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-09T20:09:25.000000Z', 'speed': 63.5},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-10T08:10:07.000000Z', 'speed': 65.03},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-10T20:10:07.000000Z', 'speed': 57.47},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-11T08:10:16.000000Z', 'speed': 57.85},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-11T20:10:31.000000Z', 'speed': 66.6},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-12T08:10:32.000000Z', 'speed': 66.62},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-12T20:11:00.000000Z', 'speed': 65.45},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-13T08:11:12.000000Z', 'speed': 58.26},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-13T20:11:45.000000Z', 'speed': 60.78},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-14T08:12:20.000000Z', 'speed': 65.12},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-14T20:12:33.000000Z', 'speed': 57.0},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-15T08:13:17.000000Z', 'speed': 69.87},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-15T20:13:17.000000Z', 'speed': 68.33},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-16T08:13:57.000000Z', 'speed': 61.12},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-16T20:14:33.000000Z', 'speed': 49.44},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-17T08:14:52.000000Z', 'speed': 63.44},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-17T20:15:35.000000Z', 'speed': 51.74},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-18T08:16:09.000000Z', 'speed': 64.96},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-18T20:16:10.000000Z', 'speed': 65.98},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-19T08:16:44.000000Z', 'speed': 51.73},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-19T20:17:04.000000Z', 'speed': 50.05},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-20T08:17:31.000000Z', 'speed': 60.0},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-20T20:17:51.000000Z', 'speed': 67.46},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-21T08:18:35.000000Z', 'speed': 68.88},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-21T20:19:25.000000Z', 'speed': 60.07},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-22T08:20:12.000000Z', 'speed': 54.18},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-22T20:20:17.000000Z', 'speed': 49.15},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-23T08:20:44.000000Z', 'speed': 59.67},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-23T20:21:21.000000Z', 'speed': 55.26},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-24T08:21:27.000000Z', 'speed': 65.77},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-24T20:22:08.000000Z', 'speed': 57.59},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-25T08:22:50.000000Z', 'speed': 60.89},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-25T20:23:16.000000Z', 'speed': 56.27},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-26T08:23:26.000000Z', 'speed': 49.64},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-26T20:23:40.000000Z', 'speed': 64.37},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-27T08:23:41.000000Z', 'speed': 60.2},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-27T20:24:02.000000Z', 'speed': 62.38},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-28T08:24:47.000000Z', 'speed': 63.2},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-28T20:25:05.000000Z', 'speed': 51.51},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-29T08:25:25.000000Z', 'speed': 65.45},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-29T20:26:20.000000Z', 'speed': 57.9},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-30T08:27:10.000000Z', 'speed': 60.91},
        {'city': 'Santa Clara', 'location': '37.382005, -121.963962', 'intersection': '101 N / San Thomas Expy', 'timestamp': '2022-04-30T20:27:51.000000Z', 'speed': 59.69}
    ]
    for row in data:
        put_data(conn='localhost:32159', row=json.dumps(row))

if __name__ == '__main__':
    palo_alto()
    santa_clara()
