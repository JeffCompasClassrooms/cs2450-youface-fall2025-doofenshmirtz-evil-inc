import flask
from handlers import copy
from db import posts, users, helpers

# -----------------------
# LOGIN BLUEPRINT
# -----------------------
login_blueprint = flask.Blueprint("login", __name__)

@login_blueprint.route('/loginscreen')
def loginscreen():
    """Present a form to the user to enter their username and password."""
    db = helpers.load_db()

    # First check if already logged in
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    if username is not None and password is not None:
        if users.get_user(db, username, password):
            flask.flash('You are already logged in.', 'warning')
            return flask.redirect(flask.url_for('login.index'))

    return flask.render_template('login.html', title=copy.title,
                                 subtitle=copy.subtitle)

@login_blueprint.route('/login', methods=['POST'])
def login_post():
    """Log in the user using username and password, or delete user if requested."""
    db = helpers.load_db()

    username = flask.request.form.get('username')
    password = flask.request.form.get('password')

    resp = flask.make_response(flask.redirect(flask.url_for('login.index')))
    resp.set_cookie('username', username)
    resp.set_cookie('password', password)

    submit = flask.request.form.get('type')

    if submit == 'Delete':
        if users.delete_user(db, username, password):
            resp.set_cookie('username', '', expires=0)
            resp.set_cookie('password', '', expires=0)
            flask.flash(f'User {username} deleted successfully!', 'success')

    return resp

@login_blueprint.route('/logout', methods=['POST'])
def logout():
    """Log out the user."""
    resp = flask.make_response(flask.redirect(flask.url_for('login.loginscreen')))
    resp.set_cookie('username', '', expires=0)
    resp.set_cookie('password', '', expires=0)
    return resp

@login_blueprint.route('/')
def index():
    """Serve the main feed page."""
    db = helpers.load_db()

    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    if username is None or password is None:
        return flask.redirect(flask.url_for('login.loginscreen'))

    user = users.get_user(db, username, password)
    if not user:
        flask.flash('Invalid credentials. Please try again.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    # Get friends list
    friends_list = users.get_user_friends(db, user)

    # Fetch posts from user + friends
    all_posts = []
    for friend in friends_list + [user]:
        friend_posts = posts.get_posts(db, friend)
        for post in friend_posts:
            # Mark if current user liked/bookmarked the post
            post['liked'] = username in post.get('likes', [])
            post['bookmarked'] = username in post.get('bookmarks', [])
            post['likes'] = len(post.get('likes', []))
            post['comments'] = post.get('comments', [])
        all_posts += friend_posts

    # Sort posts newest first
    sorted_posts = sorted(all_posts, key=lambda post: post['time'], reverse=True)

    return flask.render_template(
        'feed.html',
        title=copy.title,
        subtitle=copy.subtitle,
        user=user,
        username=username,
        friends=friends_list,
        posts=sorted_posts
    )
