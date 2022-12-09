git
def write_k8s_configs(node_type:str, build:str, configs:dict):
    content = ""
    for config in configs:
        content += f"{config}:"
        if config == 'general':
            content += f'\n\tbuild: {build}'
        for param in configs[config]:
            if configs[config][param]['value'] == '':
                if configs[config][param]["default"] == '':
                    content += f'\n\t{param}: ""'
                else:
                    content += f'\n\t{param}: {configs[config][param]["default"]}'
            else:
                content += f'\n\t{param}: {configs[config][param]["value"]}'
        content += "\n"
    print(content)
