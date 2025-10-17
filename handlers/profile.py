import flask
from handlers import copy
from db import users, helpers
from tinydb import Query

blueprint = flask.Blueprint("profile", __name__)

@blueprint.route('/profilescreen', methods=['GET', 'POST'])
def profilescreen():
    """Display and allow editing of a user's profile."""
    db = helpers.load_db()

    # Read credentials from cookies
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    if not username or not password:
        return flask.redirect(flask.url_for('login.loginscreen'))

    user = users.get_user(db, username, password)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))

    # Handle form submission for editing bio
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

    return flask.render_template(
        'profile.html',
        title=copy.title,
        subtitle=copy.subtitle,
        user=username,
        handle=handle,
        birthday=birthday,
        age=age,
        bio=bio,
        pfp=pfp
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
