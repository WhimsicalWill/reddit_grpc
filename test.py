from client.reddit_client import RedditClient

def retrieve_and_expand_comments(client, post_id):
    """
    Retrieves a post, its most upvoted comments, expands the most upvoted comment,
    and returns the most upvoted reply under it, or None if no comments or replies exist.
    """
    post_response = client.get_post(post_id)
    if not post_response or not post_response.post:
        return None
    print(f"Post:\n{post_response.post}")

    top_comments_response = client.get_top_comments_under_post(post_id, count=5)
    if not top_comments_response or not top_comments_response.comments:
        return None
    print(f"Top comments:\n{top_comments_response.comments}")

    most_upvoted_comment = top_comments_response.comments[0]
    replies_response = client.get_top_comments_under_comment(most_upvoted_comment.comment_id, count=5)
    print(f"Replies to most upvoted comment:\n{replies_response.comments}")

    return replies_response.comments[0] if replies_response.comments else None

def setup_data(client):
    # Create a post and directly access its object from the response
    post = client.create_post(title="Hello", text="This is a test post", image_url="image_url", author="user123").post

    # Create comments under the post
    comment1 = client.create_comment(text="This is a test comment", author="user1", parent_post_id=post.post_id).comment
    comment2 = client.create_comment(text="This is another test comment", author="user2", parent_post_id=post.post_id).comment
    client.create_comment(text="This test comment has no upvotes", author="user3", parent_post_id=post.post_id)

    # Upvote the comments
    client.vote_comment(comment_id=comment1.comment_id, upvote=True)
    client.vote_comment(comment_id=comment1.comment_id, upvote=True)
    client.vote_comment(comment_id=comment2.comment_id, upvote=True)

    # Create replies under the first comment
    client.create_comment(text="You're a test comment!", author="user4", parent_comment_id=comment1.comment_id)
    client.create_comment(text="This guy is weird", author="user5", parent_comment_id=comment1.comment_id)

    return post.post_id

if __name__ == "__main__":
    client = RedditClient()
    original_post_id = setup_data(client)
    most_upvoted_reply = retrieve_and_expand_comments(client, original_post_id)
    print("Most upvoted reply under the most upvoted comment:", most_upvoted_reply)
