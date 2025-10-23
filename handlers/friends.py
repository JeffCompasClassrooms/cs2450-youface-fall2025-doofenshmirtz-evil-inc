import flask
from handlers import copy
from db import posts, users, helpers

blueprint = flask.Blueprint("friends", __name__)

def get_logged_in_user(db):
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    if not username or not password:
        return None
    return users.get_user(db, username, password)

@blueprint.route('/follow', methods=['POST'])
def follow():
    db = helpers.load_db()
    user = get_logged_in_user(db)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))
    name = flask.request.form.get('name')
    msg, cat = users.follow_user(db, user, name)
    flask.flash(msg, cat)
    return flask.redirect(flask.url_for('login.index'))

@blueprint.route('/send_request', methods=['POST'])
def send_request():
    db = helpers.load_db()
    user = get_logged_in_user(db)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))
    name = flask.request.form.get('name')
    msg, cat = users.send_friend_request(db, user, name)
    flask.flash(msg, cat)
    return flask.redirect(flask.url_for('login.index'))

@blueprint.route('/respond_request', methods=['POST'])
def respond_request():
    db = helpers.load_db()
    user = get_logged_in_user(db)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))
    name = flask.request.form.get('name')
    action = flask.request.form.get('action')
    accept = action == "accept"
    msg, cat = users.respond_friend_request(db, user, name, accept)
    flask.flash(msg, cat)
    return flask.redirect(flask.url_for('login.index'))

@blueprint.route('/block', methods=['POST'])
def block():
    db = helpers.load_db()
    user = get_logged_in_user(db)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))
    name = flask.request.form.get('name')
    msg, cat = users.block_user(db, user, name)
    flask.flash(msg, cat)
    return flask.redirect(flask.url_for('login.index'))

@blueprint.route('/friend/<fname>')
def view_friend(fname):
    db = helpers.load_db()
    user = get_logged_in_user(db)
    if not user:
        flask.flash('You must be logged in.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))
    friend = users.get_user_by_name(db, fname)
    all_posts = posts.get_posts(db, friend)[::-1]
    return flask.render_template('friend.html', title=copy.title, subtitle=copy.subtitle,
                                 user=user, username=user['username'],
                                 friend=friend['username'],
                                 friends=users.get_user_friends(db, user),
                                 posts=all_posts)

@blueprint.route('/requests')
def view_requests():
    """View pending friend requests and current friends."""
    db = helpers.load_db()
    user = get_logged_in_user(db)
    if not user:
        flask.flash('You must be logged in to view friend requests.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    pending = user.get('friend_requests', [])
    current_friends = users.get_user_friends(db, user)

    return flask.render_template(
        'requests.html',
        title="Friends & Requests",
        subtitle="Manage your social connections",
        user=user,
        requests=pending,
        friends=current_friends
    )
