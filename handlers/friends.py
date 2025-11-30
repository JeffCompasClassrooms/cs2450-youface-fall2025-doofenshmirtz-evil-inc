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


# ---------------------------
# FOLLOW USER
# ---------------------------
@blueprint.route('/follow', methods=['POST'])
def follow():
    db = helpers.load_db()
    user = get_logged_in_user(db)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))

    name = flask.request.form.get('name')
    message, category = users.follow_user(db, user, name)

    flask.flash(message, category)
    return flask.redirect(flask.url_for('login.index'))


# ---------------------------
# SEND FRIEND REQUEST
# ---------------------------
@blueprint.route('/send_request', methods=['POST'])
def send_request():
    db = helpers.load_db()
    user = get_logged_in_user(db)

    if not user:
        flask.flash('You need to be logged in to do that.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    name = flask.request.form.get('name')
    message, category = users.send_friend_request(db, user, name)

    flask.flash(message, category)
    return flask.redirect(flask.url_for('login.index'))


@blueprint.route('/send_request_to/<target_username>', methods=['POST'])
def send_request_to(target_username):
    db = helpers.load_db()
    user = get_logged_in_user(db)

    if not user:
        flask.flash('You need to be logged in to do that.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    message, category = users.send_friend_request(db, user, target_username)

    flask.flash(message, category)
    return flask.redirect(flask.url_for('login.index'))


# ---------------------------
# ACCEPT / DECLINE FRIEND REQUEST
# ---------------------------
@blueprint.route('/respond_request', methods=['POST'])
def respond_request():
    db = helpers.load_db()
    user = get_logged_in_user(db)

    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))

    from_user = flask.request.form.get('name')   # sender
    to_user   = flask.request.form.get('req')    # receiver
    action    = flask.request.form.get('action')

    if action == "accept":
        success, msg = users.accept_friend_request(db, from_user, to_user)
        flask.flash(msg, 'success' if success else 'danger')

    elif action == "decline":
        msg, category = users.decline_friend_request(db, from_user, to_user)
        flask.flash(msg, category)

    return flask.redirect(flask.url_for('friends.view_requests'))


# ---------------------------
# BLOCK USER
# ---------------------------
@blueprint.route('/block', methods=['POST'])
def block():
    db = helpers.load_db()
    user = get_logged_in_user(db)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))

    name = flask.request.form.get('name')

    if not name:
        flask.flash('No username provided to block.', 'danger')
        return flask.redirect(flask.url_for('login.index'))

    success, msg = users.block_user(db, user, name)
    flask.flash(msg, 'success' if success else 'danger')

    return flask.redirect(flask.url_for('login.index'))


# ---------------------------
# UNFRIEND
# ---------------------------
@blueprint.route('/unfriend', methods=['POST'])
def unfriend():
    db = helpers.load_db()
    user = get_logged_in_user(db)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))

    name = flask.request.form.get('name')
    msg, category = users.unfriend_user(db, user, name)

    flask.flash(msg, category)
    return flask.redirect(flask.url_for('login.index'))


# ---------------------------
# VIEW FRIEND PAGE
# ---------------------------
@blueprint.route('/friend/<fname>')
def view_friend(fname):
    db = helpers.load_db()
    user = get_logged_in_user(db)
    if not user:
        flask.flash('You must be logged in.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    friend = users.get_user(db, fname)
    if not friend:
        flask.flash('Friend not found.', 'danger')
        return flask.redirect(flask.url_for('login.index'))

    all_posts = posts.get_posts(db, friend)[::-1]
    all_friends = users.get_user_friends(db, user)
    all_followers = users.get_user_followers(db, user)
    all_following = users.get_user_following(db, user)

    return flask.render_template(
        'friend.html',
        title=f"{fname}'s profile",
        subtitle=f"Everything you need to know about {fname}",
        user=user,
        friend=friend,
        friends=all_friends,
        num_friends=len(all_friends),
        num_followers=len(all_followers),
        num_following=len(all_following),
        posts=all_posts
    )


# ---------------------------
# VIEW FRIEND REQUESTS
# ---------------------------
@blueprint.route('/requests')
def view_requests():
    db = helpers.load_db()
    user = get_logged_in_user(db)
    if not user:
        flask.flash('You must be logged in to view friend requests.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    pending = users.get_user_requests(db, user)
    current_friends = users.get_user_friends(db, user)
    current_followers = users.get_user_followers(db, user)
    current_following = users.get_user_following(db, user)
    suggested_users = users.get_suggested_users(db, user, [])

    return flask.render_template(
        'requests.html',
        title="Friend-Inators",
        subtitle="Manage your social connections",
        user=user,
        requests=pending,
        friends=current_friends,
        followers=current_followers,
        following=current_following,
        suggested_users=suggested_users
    )
