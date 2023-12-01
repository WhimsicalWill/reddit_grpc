import grpc
import reddit_pb2
import reddit_pb2_grpc

class RedditClient:
    def __init__(self, host='localhost', port=50051):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = reddit_pb2_grpc.RedditServiceStub(self.channel)

    def create_post(self, title, text, image_url=None, video_url=None, author=None):
        # Create the request and set image_url or video_url based on input
        request = reddit_pb2.CreatePostRequest(title=title, text=text, author=author)
        if image_url:
            request.image_url = image_url
        elif video_url:
            request.video_url = video_url
        
        return self.stub.CreatePost(request)

    def vote_post(self, post_id, upvote):
        request = reddit_pb2.VotePostRequest(post_id=post_id, upvote=upvote)
        return self.stub.VotePost(request)

    def get_post(self, post_id):
        request = reddit_pb2.GetPostRequest(post_id=post_id)
        return self.stub.GetPost(request)

    def create_comment(self, text, author, parent_post_id=None, parent_comment_id=None):
        # Create the request and set the parent based on input
        request = reddit_pb2.CreateCommentRequest(text=text, author=author)
        if parent_post_id:
            request.parent_post_id = parent_post_id
        elif parent_comment_id:
            request.parent_comment_id = parent_comment_id

        return self.stub.CreateComment(request)

    def vote_comment(self, comment_id, upvote):
        request = reddit_pb2.VoteCommentRequest(comment_id=comment_id, upvote=upvote)
        return self.stub.VoteComment(request)

    def get_top_comments_under_post(self, post_id, count):
        request = reddit_pb2.GetTopCommentsUnderPostRequest(post_id=post_id, count=count)
        return self.stub.GetTopCommentsUnderPost(request)

    def expand_comment_branch(self, comment_id, count):
        request = reddit_pb2.ExpandCommentBranchRequest(comment_id=comment_id, count=count)
        return self.stub.ExpandCommentBranch(request)