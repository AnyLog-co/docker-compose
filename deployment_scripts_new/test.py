import json
import os

ROOT_PATH = os.path.expandvars(os.path.expanduser(__file__)).split('deployment_scripts_new')[0]
DEFAULT_CONFIG_FILE = os.path.join(ROOT_PATH, 'deployment_scripts_new', 'config_files', 'configurations.json')

with open(DEFAULT_CONFIG_FILE, 'r') as f:
    content = json.loads(f.read())

params = []
for section in content:
    for param in content[section]:
        params.append(f"{param}")
print(params)