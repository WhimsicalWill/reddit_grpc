from client.reddit_client import RedditClient

def retrieve_and_expand_comments(client, post_id):
    """
    Retrieves a post, its most upvoted comments, expands the most upvoted comment,
    and returns the most upvoted reply under it, or None if no comments or replies exist.
    """
    post = client.get_post(post_id).post
    if not post:
        return None
    print(f"Post: {post}")

    top_comments = client.get_top_comments(post_id, count=5).comments
    if not top_comments:
        return None
    print(f"Top comments: {top_comments}")

    most_upvoted_comment = top_comments[0]
    replies_to_most_upvoted_comment = client.get_top_comments(most_upvoted_comment.comment_id, count=5).comments
    print(f"Replies to most upvoted comment: {replies_to_most_upvoted_comment}")
    
    return replies_to_most_upvoted_comment[0] if replies_to_most_upvoted_comment else None

def setup_data(client):
    post_response = client.create_post(title="Hello", text="This is a test post", media="image_url", author="user123")
    original_post_id = post_response.post_id

    # Create three comments under the post
    response_comment1 = client.create_comment(text="This is a test comment", author="user1", post_id=original_post_id)
    response_comment2 = client.create_comment(text="This is another test comment", author="user2", post_id=original_post_id)
    response_comment3 = client.create_comment(text="This test comment has no upvotes", author="user3", post_id=original_post_id)

    # First comment has two likes
    client.vote_comment(comment_id=response_comment1.comment_id, upvote=True)
    client.vote_comment(comment_id=response_comment1.comment_id, upvote=True)

    # Second comment has one like
    client.vote_comment(comment_id=response_comment2.comment_id, upvote=True)

    # Create two comments under the first comment
    response_reply1 = client.create_comment(text="You're a test comment!", author="user1", parent=response_comment1.comment_id)
    response_reply2 = client.create_comment(text="This guy is weird", author="user2", parent=response_comment1.comment_id)

    # Return the id of the original post for testing
    return original_post_id

if __name__ == "__main__":
    client = RedditClient()
    original_post_id = setup_data(client)
    retrieve_and_expand_comments(client, original_post_id)