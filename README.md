# Install dependencies

```bash
pip install grpcio grpcio-tools
```

# Generate stubs and gRPC code from .proto file

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. reddit.proto
```

# Unit testing

This just checks the business logic of the retrieve_and_expand_comments() function inside retrieval.py

To run unit tests, execute the following command:

```bash
python test_retrieval.py
```

# End-to-end testing

## Start the server

```bash
python -m server.reddit_server
```

## Run the test code

```bash
python retrieval.py
```
