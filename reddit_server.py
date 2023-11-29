import logging
import grpc
from concurrent import futures
import time

# Import the generated classes
import reddit_pb2
import reddit_pb2_grpc

# Implement the RedditService
class RedditService(reddit_pb2_grpc.RedditServiceServicer):

    def CreatePost(self, request, context):
        # Logic to create a post
        # For now, let's just return the title as a confirmation
        return reddit_pb2.PostResponse(message="Post created: " + request.title)

# Create a gRPC server
def serve():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    reddit_pb2_grpc.add_RedditServiceServicer_to_server(RedditService(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()

# def serve():
#     server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
#     reddit_pb2_grpc.add_RedditServiceServicer_to_server(RedditService(), server)

#     # Listen on port 50051
#     server.add_insecure_port('[::]:50051')
#     server.start()
#     print("Server started, listening on port 50051.")

#     try:
#         # Keep the server running
#         while True:
#             time.sleep(86400)
#     except KeyboardInterrupt:
#         server.stop(0)

if __name__ == '__main__':
    logging.basicConfig()
    serve()
