# Install dependencies

pip install grpc_tools grpc

# Generate stubs and gRPC code from .proto file

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. reddit.proto
```

# Start the server

```bash
python -m server.reddit_server
```

# Run the test code

```bash
python test.py
```
