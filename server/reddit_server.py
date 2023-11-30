import logging
import grpc
from concurrent import futures
import time
import uuid
import sys
import argparse

# Import the generated classes
import reddit_pb2, reddit_pb2_grpc

# Store posts and comments in memory
posts = {}
comments = {}

# Implement the RedditService
class RedditService(reddit_pb2_grpc.RedditServiceServicer):

    def CreatePost(self, request, context):
        post_id = str(uuid.uuid4())  # Generate a random UUID

        posts[post_id] = reddit_pb2.Post(
            title=request.title,
            text=request.text,
            media=request.media,
            author=request.author,
            score=0,
            state=reddit_pb2.Post.NORMAL,
            publication_date=str(time.strftime("%Y-%m-%d %H:%M:%S"))
        )
        
        return reddit_pb2.CreatePostResponse(message=f"Post created with ID: {post_id}")

    def VotePost(self, request, context):
        if request.post_id not in posts:
            return reddit_pb2.VotePostResponse(message="Post not found")

        posts[request.post_id].score += 1 if request.upvote else -1
        return reddit_pb2.VotePostResponse(message="Vote recorded")

    def GetPost(self, request, context):
        if request.post_id in posts:
            return reddit_pb2.GetPostResponse(post=posts[request.post_id])
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Post not found')
            return reddit_pb2.GetPostResponse()

    def CreateComment(self, request, context):
        comment_id = str(uuid.uuid4())  # Generate a random UUID

        comments[comment_id] = reddit_pb2.Comment(
            text=request.text,
            author=request.author,
            score=0,
            status=reddit_pb2.Comment.NORMAL,
            publication_date=str(time.strftime("%Y-%m-%d %H:%M:%S")),
            post_id=request.post_id
        )

        return reddit_pb2.CreateCommentResponse(message=f"Comment created with ID: {comment_id}")

    def VoteComment(self, request, context):
        if request.comment_id not in comments:
            return reddit_pb2.VoteCommentResponse(message="Comment not found")

        comments[request.comment_id].score += 1 if request.upvote else -1
        return reddit_pb2.VoteCommentResponse(message="Vote recorded")

    def GetTopComments(self, request, context):
        filtered_comments = [comment for comment in comments.values() if comment.post_id == request.post_id]
        sorted_comments = sorted(filtered_comments, key=lambda x: x.score, reverse=True)
        top_comments = sorted_comments[:request.count]
        
        return reddit_pb2.GetTopCommentsResponse(comments=top_comments)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Reddit gRPC Server')
    parser.add_argument('--port', type=int, default=50051, help='Port to listen on (default: 50051)')
    parser.add_argument('--max_workers', type=int, default=10, help='Number of thread workers (default: 10)')
    return parser.parse_args()

# Create a gRPC server
def serve(port, max_workers):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    reddit_pb2_grpc.add_RedditServiceServicer_to_server(RedditService(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    args = parse_arguments()
    serve(args.port, args.max_workers)
