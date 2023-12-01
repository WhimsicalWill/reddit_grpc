# Install dependencies

pip install grpc_tools grpc

# Generate stubs and gRPC code from .proto file

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. reddit.proto
```

# Run the server code

```bash
python -m server.reddit_server
```

# Run the client code

```bash
python -m client.reddit_client
```
