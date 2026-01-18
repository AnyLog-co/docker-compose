from opcua import Client, ua

# get opcua values where url=opc.tcp://virtualfactory.proveit.services:4841/discovery and user=proveitreadonly and password=proveitreadonlypassword and node = "ns=2;s=Site1.assetidentifier"

url = "opc.tcp://virtualfactory.proveit.services:4842/discovery"
username = "proveitreadonly"
password = "proveitreadonlypassword"
# node_id =

client = Client(url)
client.set_user(username)
client.set_password(password)

def get_struct(node_id:str="ns=2;s=sub"):
    variables = {}
    try:
        client.connect()
        node = client.get_node(node_id)
        children = node.get_children()
        for child in children:
            if str(child).count(".") > 1:
                key, value = str(child).split(".",1)[-1].split(".", 1)
                if key not in variables:
                    variables[key] = []
                variables[key].append(value)
            elif str(child).count(".") == 1:
                key = str(child).split(".", 1)[-1]
                if key not in variables:
                    variables[key] = []
    except Exception as e:
        print("Error:", e)
        exit(1)
    finally:
        client.disconnect()
        print("Disconnected")
    return variables


if __name__ == "__main__":
    get_struct(node_id="ns=2;s=sub")