import time
import unittest
from unittest.mock import MagicMock

from client.reddit_client import RedditClient
from retrieval import retrieve_and_expand_comments

class TestRedditClient(unittest.TestCase):
    def test_retrieve_and_expand_comments(self):
        mock_client = RedditClient()
        mock_client.get_post = MagicMock(return_value=mock_response_for_get_post("post_1"))
        mock_client.get_top_comments_under_post = MagicMock(return_value=mock_response_for_top_comments_post("post_1", 5))
        mock_client.expand_comment_branch = MagicMock(return_value=mock_response_for_expand_comment_branch("comment_1", 5))

        post_id = "post_1"
        result = retrieve_and_expand_comments(mock_client, post_id)

        self.assertIsNotNone(result)
        self.assertEqual(result.comment_id, "comment_1_1")
        self.assertEqual(result.author, "user5")

# Helper functions to mock responses
def mock_response_for_get_post(post_id):
    # Return a mock response for getting a post
    return MockPostResponse()

def mock_response_for_top_comments_post(post_id, count):
    # Return a mock response for top comments under a post
    return MockTopCommentsPostResponse()

def mock_response_for_expand_comment_branch(comment_id, count):
    # Return a mock response for expanded comments under a comment
    return MockExpandCommentBranchResponse()

# Mock CommentNode class to represent a comment and its replies
class CommentNode:
    def __init__(self, comment, children):
        self.comment = comment
        self.children = children

# Mock response classes
class MockPost:
    def __init__(self):
        self.post_id = "post_1"
        self.title = "Example Post"
        self.text = "This is a sample post."
        self.image_url = "image_url"
        self.author = "user1"
        self.score = 10
        self.publication_date = str(time.strftime("%Y-%m-%d %H:%M:%S"))

class MockComment:
    def __init__(self, comment_id, text, author, score, parent_id):
        self.comment_id = comment_id
        self.text = text
        self.author = author
        self.score = score
        self.publication_date = str(time.strftime("%Y-%m-%d %H:%M:%S"))
        self.parent_comment_id = parent_id if "comment" in parent_id else None
        self.parent_post_id = parent_id if "post" in parent_id else None

class MockPostResponse:
    def __init__(self):
        self.post = MockPost()

class MockTopCommentsPostResponse:
    def __init__(self):
        self.comments = [MockComment("comment_1", "Test comment 1", "user2", 5, "post_1"),
                         MockComment("comment_2", "Test comment 2", "user3", 3, "post_1"),
                         MockComment("comment_3", "Test comment 3", "user4", 2, "post_1")]

class MockExpandCommentBranchResponse:
    def __init__(self):
        # Assuming only one top comment with replies for simplicity
        self.comment_nodes = [
            CommentNode(
                comment=MockComment("comment_1_1", "Top reply", "user5", 5, "comment_1"),
                children=[
                    MockComment("comment_1_1_1", "Top reply to top reply", "user6", 4, "comment_1_1"),
                    MockComment("comment_1_1_2", "Second reply to top reply", "user7", 2, "comment_1_1")
                ]
            )
        ]


if __name__ == '__main__':
    unittest.main()
