import logging
import grpc
from concurrent import futures
import time
import uuid
import sys
import argparse

# Import the generated classes
import reddit_pb2
import reddit_pb2_grpc

# Store posts and comments in memory
posts = {}
comments = {}

# Implement the RedditService
class RedditService(reddit_pb2_grpc.RedditServiceServicer):

    def CreatePost(self, request, context):
        post_id = str(uuid.uuid4())  # Generate a random UUID

        # Create a new Post object
        new_post = reddit_pb2.Post(
            post_id=post_id,
            title=request.title,
            text=request.text,
            author=request.author,
            score=0,
            state=reddit_pb2.Post.NORMAL,
            publication_date=str(time.strftime("%Y-%m-%d %H:%M:%S"))
        )

        # Set the media based on the request
        if request.HasField("image_url"):
            new_post.image_url = request.image_url
        elif request.HasField("video_url"):
            new_post.video_url = request.video_url
        else:  # No media: raise an error
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Must provide either image_url or video_url')
            return reddit_pb2.CreatePostResponse()

        # Store the new post
        posts[post_id] = new_post
        
        return reddit_pb2.CreatePostResponse(post=new_post)

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

        new_comment = reddit_pb2.Comment(
            comment_id=comment_id,
            text=request.text,
            author=request.author,
            score=0,
            status=reddit_pb2.Comment.NORMAL,
            publication_date=str(time.strftime("%Y-%m-%d %H:%M:%S")),
        )
        
        # Set the media based on the request
        if request.HasField("parent_post_id"):
            new_comment.parent_post_id = request.parent_post_id
        elif request.HasField("parent_comment_id"):
            new_comment.parent_comment_id = request.parent_comment_id
        else:  # No media: raise an error
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Must provide either parent_post_id or parent_comment_id')
            return reddit_pb2.CreateCommentResponse()

        # Store the new comment
        comments[comment_id] = new_comment

        return reddit_pb2.CreateCommentResponse(comment=new_comment)

    def VoteComment(self, request, context):
        if request.comment_id not in comments:
            return reddit_pb2.VoteCommentResponse(message="Comment not found")

        comments[request.comment_id].score += 1 if request.upvote else -1
        return reddit_pb2.VoteCommentResponse(message="Vote recorded")

    def GetTopCommentsUnderPost(self, request, context):
        filtered_comments = [comment for comment in comments.values() if comment.parent_post_id == request.post_id]
        sorted_comments = sorted(filtered_comments, key=lambda x: x.score, reverse=True)
        return reddit_pb2.GetTopCommentsUnderPostResponse(comments=sorted_comments[:request.count])

    def GetTopCommentsUnderComment(self, request, context):
        filtered_comments = [comment for comment in comments.values() if comment.parent_comment_id == request.comment_id]
        sorted_comments = sorted(filtered_comments, key=lambda x: x.score, reverse=True)
        return reddit_pb2.GetTopCommentsUnderCommentResponse(comments=sorted_comments[:request.count])


def parse_arguments():
    parser = argparse.ArgumentParser(description='Reddit gRPC Server')
    parser.add_argument('--port', type=int, default=50051, help='Port to listen on (default: 50051)')
    parser.add_argument('--max_workers', type=int, default=10, help='Number of thread workers (default: 10)')
    return parser.parse_args()

# Create a gRPC server
def serve(port, max_workers):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    reddit_pb2_grpc.add_RedditServiceServicer_to_server(RedditService(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Server started, listening on {port}")
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    args = parse_arguments()
    serve(args.port, args.max_workers)
