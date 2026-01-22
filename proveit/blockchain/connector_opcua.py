from opcua import Client, ua

# get opcua values where url=opc.tcp://virtualfactory.proveit.services:4841/discovery and user=proveitreadonly and password=proveitreadonlypassword and node = "ns=2;s=Site1.assetidentifier"

username = "proveitreadonly"
password = "proveitreadonlypassword"
# node_id =


class TreeStruct:
    def __init__(self, url:str):
        self.client = self.connect(url=url)

    def connect(self, url:str):
        try:
            client = Client(url)
            client.set_user(username)
            client.set_password(password)
            client.connect()
        except Exception as error:
            raise Exception(f"Failed to connect to client (Error: {error})")

        return client

    def get_children(self, node_id:str=None):
        try:
            namespaces = self.client.get_node(nodeid=node_id)

            return namespaces.get_children()
        except Exception as error:
            raise Exception(f"Failed to get children for {node_id} (Error: {error})")

    def get_value(self, node_id:str=None):
        try:
            value = self.client.get_values(nodes=node_id)
        except Exception as error:
            raise Exception(f"Failed to get children for {node_id} (Error: {error})")

    def disconnect(self):
        try:
            self.client.disconnect()

        except Exception as error:
            pass

# if __name__ == "__main__":
#     tress_struct = TreeStruct(url="opc.tcp://virtualfactory.proveit.services:4841/discovery")
#     tress_struct.enterprise()