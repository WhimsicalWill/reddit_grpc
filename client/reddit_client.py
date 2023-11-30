import grpc
import reddit_pb2
import reddit_pb2_grpc

class RedditClient:
    def __init__(self, host='localhost', port=50051):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = reddit_pb2_grpc.RedditServiceStub(self.channel)

    def create_post(self, title, text, media, author=None):
        request = reddit_pb2.CreatePostRequest(title=title, text=text, media=media, author=author)
        return self.stub.CreatePost(request)

    def vote_post(self, post_id, upvote):
        request = reddit_pb2.VotePostRequest(post_id=post_id, upvote=upvote)
        return self.stub.VotePost(request)

    def get_post(self, post_id):
        request = reddit_pb2.GetPostRequest(post_id=post_id)
        return self.stub.GetPost(request)

    def create_comment(self, text, author, post_id):
        request = reddit_pb2.CreateCommentRequest(text=text, author=author, post_id=post_id)
        return self.stub.CreateComment(request)

    def vote_comment(self, comment_id, upvote):
        request = reddit_pb2.VoteCommentRequest(comment_id=comment_id, upvote=upvote)
        return self.stub.VoteComment(request)

    def get_top_comments(self, post_id, count):
        request = reddit_pb2.GetTopCommentsRequest(post_id=post_id, count=count)
        return self.stub.GetTopComments(request)

if __name__ == "__main__":
    client = RedditClient()
    response = client.create_post(title="Hello", text="This is a test post", media="image_url", author="user123")
    print(response)
