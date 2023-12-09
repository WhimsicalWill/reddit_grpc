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
python test_unit.py
```

# End-to-end testing

Additionally, follow the below steps to complete the end-to-end testing:

## Start the server

```bash
python -m server.reddit_server
```

## Run the end-to-end test code

```bash
python test_end_to_end.py
```
