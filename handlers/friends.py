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
    success = users.follow_user(db, user, name)

    if success:
        flask.flash(f'You are now following {name}.', 'success')
    else:
        flask.flash(f'Failed to follow {name}.', 'danger')

    return flask.redirect(flask.url_for('login.index'))


@blueprint.route('/send_request', methods=['POST'])
def send_request():
    db = helpers.load_db()
    user = get_logged_in_user(db)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))

    name = flask.request.form.get('name')
    success = users.send_friend_request(db, user, name)

    if success:
        flask.flash(f'Friend request sent to {name}.', 'success')
    else:
        flask.flash(f'Failed to send friend request to {name}.', 'danger')

    return flask.redirect(flask.url_for('login.index'))


@blueprint.route('/respond_request', methods=['POST'])
def respond_request():
    db = helpers.load_db()
    user = get_logged_in_user(db)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))

    name = flask.request.form.get('name')  # the user who SENT the request
    action = flask.request.form.get('action')

    if action == "accept":
        success = users.accept_friend_request(db, name, user['username'])
        if success:
            flask.flash(f'Friend request from {name} accepted.', 'success')
        else:
            flask.flash(f'Failed to accept friend request from {name}.', 'danger')
    elif action == "decline":
        success = users.decline_friend_request(db, name, user['username'])
        if success:
            flask.flash(f'Friend request from {name} declined.', 'info')
        else:
            flask.flash(f'Failed to decline friend request from {name}.', 'danger')

    return flask.redirect(flask.url_for('friends.view_requests'))


@blueprint.route('/block', methods=['POST'])
def block():
    db = helpers.load_db()
    user = get_logged_in_user(db)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))

    name = flask.request.form.get('name')

    # Ensure name is provided
    if not name:
        flask.flash('No username provided to block.', 'danger')
        return flask.redirect(flask.url_for('login.index'))

    success, msg = users.block_user(db, user, name)

    if success:
        flask.flash(msg, 'success')
    else:
        flask.flash(msg, 'danger')

    # Always return a valid response
    return flask.redirect(flask.url_for('login.index'))


@blueprint.route('/unfriend', methods=['POST'])
def unfriend():
    db = helpers.load_db()
    user = get_logged_in_user(db)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))

    name = flask.request.form.get('name')
    success = users.unfriend_user(db, user, name)

    if success:
        flask.flash(f'You have unfriended {name}.', 'info')
    else:
        flask.flash(f'Failed to unfriend {name}.', 'danger')

    return flask.redirect(flask.url_for('login.index'))


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
    return flask.render_template(
        'friend.html',
        title=copy.title,
        subtitle=copy.subtitle,
        user=user,
        username=user['username'],
        friend=friend,
        friends=users.get_user_friends(db, user),
        posts=all_posts
    )


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
