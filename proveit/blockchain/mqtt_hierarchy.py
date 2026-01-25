#!/usr/bin/env python3
"""
lotnumber is a unique identifier for the node
"""
import ast
import time
import paho.mqtt.client as mqtt


class MqttHierarchy:
    def __init__(self, base_topic:str, broker:str, port:int=1883, username:str|None=None, password:str|None=None,
                 collect_seconds:int=10):
        self.base_topic = base_topic
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.collect_seconds = collect_seconds

        self.client: mqtt.Client | None = None
        self.topics_seen: set[str] = set()
        self.latest_values: dict[str, str] = {}

    # ───────────────── MQTT SETUP ─────────────────

    def connect(self) -> None:
        self.client = mqtt.Client()
        if self.username:
            self.client.username_pw_set(self.username, self.password)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def disconnect(self) -> None:
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()

    # ───────────────── CALLBACKS ─────────────────

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT broker")
            client.subscribe(self.base_topic)
        else:
            raise ConnectionError(f"MQTT connection failed (rc={rc})")

    def on_message(self, client, userdata, msg):
        self.topics_seen.add(msg.topic)
        self.latest_values[msg.topic] = msg.payload.decode("utf-8")

    # ───────────────── HIERARCHY BUILDING ─────────────────

    def build_hierarchy(self, topics: list[str]) -> dict:
        tree = {}
        base_prefix = self.base_topic.replace("/#", "")

        for topic in topics:
            if not topic.startswith(base_prefix):
                continue

            parts = topic[len(base_prefix):].lstrip("/").split("/")
            current = tree

            for part in parts:
                if part:
                    current = current.setdefault(part, {})

        return tree

    def attach_values(self, tree: dict, prefix: str):
        if not isinstance(tree, dict) or not tree:
            return

        for key, subtree in list(tree.items()):
            new_prefix = f"{prefix}/{key}"

            if subtree == {}:
                try:
                    tree[key] = self.latest_values.get(
                        ast.literal_eval(new_prefix), None
                    )
                except Exception:
                    tree[key] = self.latest_values.get(new_prefix, None)
            else:
                self.attach_values(subtree, new_prefix)

