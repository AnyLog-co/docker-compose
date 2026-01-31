# Ollama 

Ollama is a lightweight open-source framework for running language models locally. 

AnyLog / EdgeLake use it as the tested model framework for our [Remote-GUI](https://github.com/AnyLog-co/Remote-GUI).  

## Install 

### Docker 

1. Download and deploy Ollama
```shell
# default 
docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ollama-data:/root/.ollama \
  ollama/ollama
```

If there's a NVIDIA GPU, extend the docker run command with `--gpus all`

2. Once the docker container is running - download and install the desired [model](https://ollama.com/search) - For 
AnyLog/EdgeLake the model needs to support MCP function calling. 
```shell
docker exec -it ollama ollama pull qwen2.5:7b-instruct
```

3. Test that the model is installed
```shell
curl http://localhost:11434/api/tags
```

The [docker-compose](docker-compose.yaml) and [docker-compose-gpu](docker-compose-gpu.yaml) provide the same behavior
as steps 1+2
```shell
docker compose -f docker-compose.yaml up -d
docker compose -f docker-compose-gpu.yaml up -d
```

#### NVIDIA support 
When using NVIDIA-based GPUs, there's a need to make sure that the docker container can communicate with the 
docker container(s). 

**Steps**: 
1. Install [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
```shell
sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker
```

2. Test that containers work with GPU 
```shell
docker run --rm --gpus all nvidia/cuda:12.2.0-base nvidia-smi
```

### Mac
Apple-based computers with M-models) are pre-built with their own GPU. 

The GPU doesn't work with docker, and as such needs to be installed using `brew`.

1. Install ollama
```shell
brew install ollama
```

2. Start servers
```shell
export OLLAMA_SERVER=0.0.0.0:11434
ollama serve
```

3. Install model - On M1/M2/M3 Macs: Ollama automatically uses the integrated GPU and the Apple Neural Engine if 
the model supports it.
```shell
ollama pull qwen2.5:7b-instruct
```

4. Check model(s)
```shell
curl http://localhost:11434/api/tags
```

## Configure Remote-CLI

### Steps

1. Deploy Remote-GUI

2. Go to MCP Client

3. Under configs -> Update Docker Ollama connection information

4. Begin asking questions

![img_1.png](ollama-configs.png)

