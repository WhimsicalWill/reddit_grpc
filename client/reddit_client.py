from protos.reddit_pb2 import User, Post

user = User(user_id="user123")
post = Post(title="Example Title", text="This is a post", score=10)
print(user)
print(post)

# Serialize
serialized_post = post.SerializeToString()

# Deserialize
new_post = Post()
new_post.ParseFromString(serialized_post)
print(new_post)
