# AnyLog Video Inference Models

A **YOLOv5 CPU inference server** exposed over a **gRPC API**, used to run object-detection inference on video frame streams from AnyLog / EdgeLake edge nodes.

Source: [AnyLog-co/AnyLog-Video-Inference-Models](https://github.com/AnyLog-co/AnyLog-Video-Inference-Models)

> **Note:** This service is standalone and is not managed by the support `Makefile`. Deploy and manage it directly from its own repository.

---

## How it fits in

```
Edge camera / video source
        │  raw BGR frames
        ▼
AnyLog / EdgeLake node  ──gRPC──►  YOLOv5 inference server  (port 50051)
                                          │  bounding boxes + class labels
                                          ▼
                                   Remote-GUI / downstream pipeline
```

The inference server accepts raw frame bytes (`bgr24` / `rgb24`) and returns bounding boxes with class labels. Both unary (`Predict`) and streaming (`PredictStream`) gRPC calls are supported.

---

## Quick Start

```shell
# Clone the repo
git clone https://github.com/AnyLog-co/AnyLog-Video-Inference-Models.git
cd AnyLog-Video-Inference-Models/yolov5

# Build and start the gRPC server (localhost:50051)
make up
```

Verify it's running:
```shell
make health-grpc
```

Run a smoke test against a local image:
```shell
make test-grpc IMAGE=./path/to/frame.jpg
```

---

## Makefile Reference

Run all commands from the `yolov5/` directory.

| Command | Description |
|---|---|
| `make build` | Build the Docker image (`yolov5-infer-cpu:latest`) |
| `make rebuild` | Build without cache (use after proto or code changes) |
| `make up` | Build + run gRPC server |
| `make down` | Stop running container(s) |
| `make run-grpc` | Run gRPC server on `localhost:50051` |
| `make run-http` | Run HTTP server on `localhost:8000` |
| `make run-both` | Run both HTTP + gRPC as two containers |
| `make stop` | Stop container(s) |
| `make logs` | Tail container logs |
| `make shell` | Open a shell inside the container |
| `make pull-models` | Download common YOLOv5 weights into `./weights` |
| `make venv` | Create local `.venv` with client deps |
| `make gen-proto` | Regenerate gRPC stubs from `proto/infer.proto` |
| `make test-grpc IMAGE=<path>` | Smoke test — unary gRPC inference call |
| `make test-http IMAGE=<path>` | Smoke test — HTTP inference call |
| `make health-grpc` | Check if `localhost:50051` is reachable |

---

## Configuration

Set via environment variables when running the container:

| Variable | Default | Description |
|---|---|---|
| `MODEL_WEIGHTS` | *(required)* | Path to `.pt` weights file inside the container |
| `GRPC_PORT` | `50051` | Port the gRPC server listens on |
| `GRPC_WORKERS` | `4` | Thread pool worker count |
| `GRPC_MAX_MSG_MB` | `64` | Max message size in MB — increase for large raw frames |

To use a different YOLOv5 weight (e.g. `yolov5n.pt`):
```shell
make run-grpc USE_HOST_WEIGHTS=1 MODEL_WEIGHTS=/app/weights/yolov5n.pt
```

---

## gRPC API Summary

**Service:** `InferenceService` (`proto/infer.proto`)

| RPC | Type | Description |
|---|---|---|
| `Predict` | Unary | Single frame → detections |
| `PredictStream` | Bidirectional streaming | Frame stream → detection stream |

**Request** — send raw pixels as `uint8` bytes:
- `frame` must be exactly `height × width × 3` bytes
- Set `format = BGR24` for OpenCV frames, `RGB24` otherwise

**Response** — per detection: `xmin`, `ymin`, `xmax`, `ymax`, `confidence`, `class_id`, `class_name`

---

## Requirements

- Docker ≥ 20.10
- `make`
- CPU-only (no GPU required) — PyTorch CPU build is baked into the image