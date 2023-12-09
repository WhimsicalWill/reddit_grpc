from client.reddit_client import RedditClient

import unittest
from client.reddit_client import RedditClient
from retrieval import retrieve_and_expand_comments  # Import your first function if it's in a different module

class TestRedditClient(unittest.TestCase):
    def setUp(self):
        self.client = RedditClient()
        self.post_id = self.setup_data()

    def setup_data(self):
        """
        Sets up real data in the server for end-to-end testing.
        """
        # Create a post and directly access its object from the response
        post = self.client.create_post(title="Hello", text="This is a test post", image_url="image_url", author="user123").post

        # Create comments under the post
        comment1 = self.client.create_comment(text="This is a test comment", author="user1", parent_post_id=post.post_id).comment
        comment2 = self.client.create_comment(text="This is another test comment", author="user2", parent_post_id=post.post_id).comment
        self.client.create_comment(text="This test comment has no upvotes", author="user3", parent_post_id=post.post_id)

        # Upvote the comments
        self.client.vote_comment(comment_id=comment1.comment_id, upvote=True)
        self.client.vote_comment(comment_id=comment1.comment_id, upvote=True)
        self.client.vote_comment(comment_id=comment2.comment_id, upvote=True)

        # Create replies under the first comment
        self.client.create_comment(text="You're a test comment!", author="user4", parent_comment_id=comment1.comment_id)
        self.client.create_comment(text="This guy is weird", author="user5", parent_comment_id=comment1.comment_id)

        return post.post_id

    def test_retrieve_and_expand_comments(self):
        # Example test method
        most_upvoted_reply = retrieve_and_expand_comments(self.client, self.post_id)

        # Assert that each expected field is in the response
        self.assertTrue(hasattr(most_upvoted_reply, 'comment_id'))
        self.assertTrue(hasattr(most_upvoted_reply, 'text'))
        self.assertTrue(hasattr(most_upvoted_reply, 'author'))
        self.assertTrue(hasattr(most_upvoted_reply, 'publication_date'))
        self.assertTrue(hasattr(most_upvoted_reply, 'parent_comment_id'))

if __name__ == "__main__":
    unittest.main()
