import logging
import grpc
from concurrent import futures
import time
import uuid
import argparse
import sqlite3

# Import the generated classes
import reddit_pb2
import reddit_pb2_grpc

# Implement the RedditService
class RedditService(reddit_pb2_grpc.RedditServiceServicer):
    def __init__(self):
        self.initialize_database()

    def initialize_database(self):
        with sqlite3.connect('reddit.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS posts (
                                post_id TEXT PRIMARY KEY, 
                                title TEXT, 
                                text TEXT, 
                                author TEXT, 
                                score INTEGER, 
                                state TEXT, 
                                publication_date TEXT,
                                subreddit_id TEXT,
                                tags TEXT)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS comments (
                                comment_id TEXT PRIMARY KEY, 
                                text TEXT, 
                                author TEXT, 
                                score INTEGER, 
                                status TEXT, 
                                publication_date TEXT,
                                parent_post_id TEXT,
                                parent_comment_id TEXT,
                                has_replies BOOLEAN)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS subreddits (
                                subreddit_id TEXT PRIMARY KEY, 
                                name TEXT, 
                                visibility TEXT,
                                tags TEXT,
                                post_ids TEXT)''')
            conn.commit()

    def CreatePost(self, request, context):
        post_id = str(uuid.uuid4())  # Generate a random UUID

        with sqlite3.connect('reddit.db') as conn:
            cursor = conn.cursor()

            # Check if subreddit exists, and create or update it
            cursor.execute("SELECT post_ids FROM subreddits WHERE subreddit_id = ?", (request.subreddit_id,))
            subreddit_data = cursor.fetchone()
            if subreddit_data:
                updated_post_ids = subreddit_data[0] + ',' + post_id if subreddit_data[0] else post_id
                cursor.execute("UPDATE subreddits SET post_ids = ? WHERE subreddit_id = ?", (updated_post_ids, request.subreddit_id))
            else:
                cursor.execute("INSERT INTO subreddits (subreddit_id, name, visibility, tags, post_ids) VALUES (?, ?, ?, ?, ?)",
                            (request.subreddit_id, request.subreddit_id, "PUBLIC", "", post_id))  # Assuming default values for new subreddit


            # Insert post into database
            try:
                cursor.execute("INSERT INTO posts (post_id, title, text, author, score, state, publication_date, subreddit_id, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (post_id, request.title, request.text, request.author, 0, "NORMAL", time.strftime("%Y-%m-%d %H:%M:%S"), request.subreddit_id, ','.join(request.tags)))
                conn.commit()
            except sqlite3.IntegrityError as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"Failed to create post: {str(e)}")
                return reddit_pb2.CreatePostResponse()

            # Fetch the new post to return
            cursor.execute("SELECT * FROM posts WHERE post_id = ?", (post_id,))
            new_post_data = cursor.fetchone()

        new_post = reddit_pb2.Post(post_id=new_post_data[0],
                                title=new_post_data[1],
                                text=new_post_data[2],
                                author=new_post_data[3],
                                score=new_post_data[4],
                                state=new_post_data[5],
                                publication_date=new_post_data[6],
                                subreddit_id=new_post_data[7],
                                tags=new_post_data[8].split(','))

        return reddit_pb2.CreatePostResponse(post=new_post)

    def CreateComment(self, request, context):
        comment_id = str(uuid.uuid4())
        parent_post_id = request.parent_post_id if request.HasField("parent_post_id") else None
        parent_comment_id = request.parent_comment_id if request.HasField("parent_comment_id") else None

        with sqlite3.connect('reddit.db') as conn:
            cursor = conn.cursor()

            # Insert comment into database
            try:
                cursor.execute("INSERT INTO comments (comment_id, text, author, score, status, publication_date, parent_post_id, parent_comment_id, has_replies) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                    (comment_id, request.text, request.author, 0, "NORMAL", time.strftime("%Y-%m-%d %H:%M:%S"), parent_post_id, parent_comment_id, False))
                conn.commit()
            except sqlite3.IntegrityError:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Failed to create comment")
                return reddit_pb2.CreateCommentResponse()

            # Fetch the new comment to return
            cursor.execute("SELECT * FROM comments WHERE comment_id = ?", (comment_id,))
            new_comment_data = cursor.fetchone()

        new_comment = reddit_pb2.Comment(comment_id=new_comment_data[0],
                                        text=new_comment_data[1],
                                        author=new_comment_data[2],
                                        score=new_comment_data[3],
                                        status=new_comment_data[4],
                                        publication_date=new_comment_data[5],
                                        parent_post_id=new_comment_data[6],
                                        parent_comment_id=new_comment_data[7],
                                        has_replies=new_comment_data[8])

        return reddit_pb2.CreateCommentResponse(comment=new_comment)

    def VotePost(self, request, context):
        with sqlite3.connect('reddit.db') as conn:
            cursor = conn.cursor()

            # Update post score in the database
            cursor.execute("UPDATE posts SET score = score + ? WHERE post_id = ?", (1 if request.upvote else -1, request.post_id))
            if cursor.rowcount == 0:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Post not found")
                return reddit_pb2.VotePostResponse()

            conn.commit()

        return reddit_pb2.VotePostResponse(message="Vote recorded")

    def GetPost(self, request, context):
        with sqlite3.connect('reddit.db') as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM posts WHERE post_id = ?", (request.post_id,))
            post_data = cursor.fetchone()

        if not post_data:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Post not found")
            return reddit_pb2.GetPostResponse()

        post = reddit_pb2.Post(post_id=post_data[0],
                            title=post_data[1],
                            text=post_data[2],
                            author=post_data[3],
                            score=post_data[4],
                            state=post_data[5],
                            publication_date=post_data[6],
                            subreddit_id=post_data[7],
                            tags=post_data[8].split(','))

        return reddit_pb2.GetPostResponse(post=post)

    def VoteComment(self, request, context):
        with sqlite3.connect('reddit.db') as conn:
            cursor = conn.cursor()

            # Update comment score in the database
            cursor.execute("UPDATE comments SET score = score + ? WHERE comment_id = ?", (1 if request.upvote else -1, request.comment_id))
            if cursor.rowcount == 0:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Comment not found")
                return reddit_pb2.VoteCommentResponse()

            conn.commit()

        return reddit_pb2.VoteCommentResponse(message="Vote recorded")

    def GetTopCommentsUnderPost(self, request, context):
        with sqlite3.connect('reddit.db') as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM comments WHERE parent_post_id = ? ORDER BY score DESC LIMIT ?", (request.post_id, request.count))
            comments_data = cursor.fetchall()

        comments = [reddit_pb2.Comment(comment_id=row[0],
                                    text=row[1],
                                    author=row[2],
                                    score=row[3],
                                    status=row[4],
                                    publication_date=row[5],
                                    parent_post_id=row[6],
                                    parent_comment_id=row[7],
                                    has_replies=row[8]) for row in comments_data]

        return reddit_pb2.GetTopCommentsUnderPostResponse(comments=comments)

    def ExpandCommentBranch(self, request, context):
        with sqlite3.connect('reddit.db') as conn:
            cursor = conn.cursor()

            # Fetch top comments under the specified comment
            cursor.execute("SELECT * FROM comments WHERE parent_comment_id = ? ORDER BY score DESC LIMIT ?", (request.comment_id, request.count))
            top_comments_data = cursor.fetchall()

            comment_nodes = []
            for row in top_comments_data:
                # Fetch replies to each top comment
                cursor.execute("SELECT * FROM comments WHERE parent_comment_id = ? ORDER BY score DESC LIMIT ?", (row[0], request.count))
                replies_data = cursor.fetchall()

                replies = [reddit_pb2.Comment(comment_id=reply_row[0],
                                            text=reply_row[1],
                                            author=reply_row[2],
                                            score=reply_row[3],
                                            status=reply_row[4],
                                            publication_date=reply_row[5],
                                            parent_post_id=reply_row[6],
                                            parent_comment_id=reply_row[7],
                                            has_replies=reply_row[8]) for reply_row in replies_data]

                comment_node = reddit_pb2.CommentNode(comment=reddit_pb2.Comment(comment_id=row[0],
                                                                                text=row[1],
                                                                                author=row[2],
                                                                                score=row[3],
                                                                                status=row[4],
                                                                                publication_date=row[5],
                                                                                parent_post_id=row[6],
                                                                                parent_comment_id=row[7],
                                                                                has_replies=row[8]),
                                                    children=replies)
                comment_nodes.append(comment_node)

        return reddit_pb2.ExpandCommentBranchResponse(comment_nodes=comment_nodes)

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
