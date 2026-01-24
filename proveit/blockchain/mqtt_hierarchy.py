#!/usr/bin/env python3
"""
lotnumber is a unique identifier for the node
"""
import ast
import json
import time
import paho.mqtt.client as mqtt


BROKER = "virtualfactory.proveit.services"
PORT = 1883
USERNAME = "proveitreadonly"
PASSWORD = "proveitreadonlypassword"
BASE_TOPIC = "Enterprise C/#"

COLLECT_SECONDS = 10  # how long to listen


topics_seen = set()
latest_values = {}  # store latest payload for each topic


class MqttHierarchy:
    def __init__(self, base_topic, broker:str, port:int, username:str=None, password:str=None):
        self.base_topic = base_topic
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.client = None

    def connect_mqtt(self):
        """
        connect to MQTT client
        """
        try:
            self.client = mqtt.Client()
            self.client.username_pw_set(self.username, self.password)

            self.client.on_connect = on_connect
            self.client.on_message = on_message

            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as error:
            raise Exception(f"Failed to connect to {self.broker}:{self.port} (Error: {error})")

    def subscribe(self, topic:str):
        """
        subscribe to a given topic
        """
        try:
            self.client.subscribe(topic)
        except Exception as error:
            raise Exception(f"Failed to subscribe on topic {self.base_topic} (Error: {error})")






def build_hierarchy(topics, base):
    tree = {}
    base_prefix = base.replace("/#", "")

    for topic in topics:
        # from node - we need to get the LOTNumber
        if not topic.startswith(base_prefix):
            continue

        parts = topic[len(base_prefix):].lstrip("/").split("/")
        current = tree

        for part in parts:
            if part:
                current = current.setdefault(part, {})

    return tree


def attach_values(tree, prefix="Enterprise B"):
    """
    Recursively attach latest values to leaf nodes
    """
    if not isinstance(tree, dict) or not tree:
        return

    for key, subtree in list(tree.items()):
        new_prefix = f"{prefix}/{key}"

        if subtree == {}:
            # leaf node: set value directly
            try:
                tree[key] = latest_values.get(ast.literal_eval(new_prefix), None)
            except:
                tree[key] = latest_values.get(new_prefix, None)
        else:
            attach_values(subtree, new_prefix)


def on_connect(client, userdata, flags, rc):
    global BASE_TOPIC
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(BASE_TOPIC)
    else:
        print("Connection failed:", rc)


def on_message(client, userdata, msg):
    topics_seen.add(msg.topic)
    latest_values[msg.topic] = msg.payload.decode("utf-8")


def mqtt_hierarchy(base_topic=BASE_TOPIC):
    global BASE_TOPIC
    BASE_TOPIC = base_topic


    print(f"Collecting topics for {COLLECT_SECONDS} seconds...")
    time.sleep(COLLECT_SECONDS)

    client.loop_stop()
    client.disconnect()

    print("\nDiscovered topic hierarchy with latest values:\n")

    sub_topics = [
        topic for topic in topics_seen
        # if topic.split("/")[1] in ["Site1", "Site2", "Site3"]
        if topic.split("/")[1] in ["sub", "sum", "chrom", "tff"]
    ]

    hierarchy = build_hierarchy(sub_topics, BASE_TOPIC)
    attach_values(hierarchy)
    return hierarchy

if __name__ == "__main__":
    main()
