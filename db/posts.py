import time
import tinydb

def add_post(db, user, text, tags):
    posts = db.table('posts')
    posts.insert({
        'user': user['username'],
        'text': text,
        'time': time.time(),
        'tags': tags,
        'likes': [],           # List of usernames who liked
        'bookmarks': [],       # List of usernames who bookmarked
        'comments': []         # List of comments
    })

def get_posts(db, user):
    posts = db.table('posts')
    Post = tinydb.Query()
    return posts.search(Post.user == user['username'])


# --- Like / Bookmark functions ---

def toggle_like(db, user, post_id):
    posts = db.table('posts')
    post = posts.get(doc_id=int(post_id))
    if not post:
        return False, 0

    likes = post.get('likes', [])
    if user['username'] in likes:
        likes.remove(user['username'])
        liked = False
    else:
        likes.append(user['username'])
        liked = True

    posts.update({'likes': likes}, doc_ids=[int(post_id)])
    return liked, len(likes)

def toggle_bookmark(db, user, post_id):
    posts = db.table('posts')
    post = posts.get(doc_id=int(post_id))
    if not post:
        return False

    bookmarks = post.get('bookmarks', [])
    if user['username'] in bookmarks:
        bookmarks.remove(user['username'])
        bookmarked = False
    else:
        bookmarks.append(user['username'])
        bookmarked = True

    posts.update({'bookmarks': bookmarks}, doc_ids=[int(post_id)])
    return bookmarked

# --- Fetch liked/bookmarked posts ---

def get_liked_posts(db, user):
    posts_table = db.table('posts')
    Post = tinydb.Query()
    return posts_table.search(Post.likes.any([user['username']]))

def get_bookmarked_posts(db, user):
    posts_table = db.table('posts')
    Post = tinydb.Query()
    return posts_table.search(Post.bookmarks.any([user['username']]))


def add_comment(db, user, post_id, text):
    posts_table = db.table('posts')
    Post = tinydb.Query()
    post = posts_table.get(doc_id=int(post_id))
    if post is not None:
        comments = post.get('comments', [])
        comments.append({
            "user": user['username'],
            "text": text,
            "time": time.time()
        })
        posts_table.update({'comments': comments}, doc_ids=[int(post_id)])
