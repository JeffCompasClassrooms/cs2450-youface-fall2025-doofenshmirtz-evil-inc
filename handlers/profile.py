import flask
from handlers import copy
from db import users, helpers
from tinydb import Query

blueprint = flask.Blueprint("profile", __name__)

@blueprint.route('/profilescreen', methods=['GET', 'POST'])
def profilescreen():
    db = helpers.load_db()
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    if not username or not password:
        return flask.redirect(flask.url_for('login.loginscreen'))

    user = users.get_user(db, username, password)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))

    # Delete Account
    if flask.request.method == 'POST' and 'delete' in flask.request.form:
        confirm = flask.request.form.get('delete').strip().lower()
        if confirm == 'delete':
            users.delete_user(db, username, password)
            flask.flash('Your account has been deleted.', 'success')
            resp = flask.make_response(flask.redirect(flask.url_for('login.loginscreen')))
            resp.set_cookie('username', '', expires=0)
            resp.set_cookie('password', '', expires=0)
            return resp
        else:
            flask.flash('Type "delete" to confirm account deletion.', 'warning')

    # Update Bio
    if flask.request.method == 'POST':
        new_bio = flask.request.form.get('bio', '').strip()
        if new_bio != user.get('bio', ''):
            user['bio'] = new_bio
            users_table = db.table('users')
            User = Query()
            users_table.update({'bio': new_bio}, (User.username == username) & (User.password == password))
            flask.flash('Profile updated successfully!', 'success')

    bio = user.get('bio', '')
    birthday = user.get('birthday')
    age = users.calculate_age(birthday) if birthday else None
    handle = user.get('handle', f"@{username}")
    pfp = user.get('pfp')

    follower_count = len(user.get('followers', []))
    following_count = len(user.get('following', []))
    friend_count = len(user.get('friends', []))

    return flask.render_template(
        'profile.html',
        title=copy.title,
        subtitle=copy.subtitle,
        user=username,
        handle=handle,
        birthday=birthday,
        age=age,
        bio=bio,
        pfp=pfp,
        followers=follower_count,
        following=following_count,
        friends=friend_count
    )

@blueprint.route('/delete', methods=['POST'])
def profile_delete():
    """Delete the currently logged-in user."""
    db = helpers.load_db()

    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    if not username or not password:
        return flask.redirect(flask.url_for('login.loginscreen'))

    resp = flask.make_response(flask.redirect(flask.url_for('login.index')))

    if users.delete_user(db, username, password):
        resp.set_cookie('username', '', expires=0)
        resp.set_cookie('password', '', expires=0)
        flask.flash(f'User {username} deleted successfully!', 'success')
    else:
        flask.flash('Error deleting user. Please try again.', 'error')

    return resp
