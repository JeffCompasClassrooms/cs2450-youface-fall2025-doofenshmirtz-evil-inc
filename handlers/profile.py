import flask
from handlers import copy
from db import users, helpers

blueprint = flask.Blueprint("profile", __name__)

@blueprint.route('/profilescreen')
def profilescreen():
    """Present a formatted user profile screen."""
    db = helpers.load_db()

    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    if not username or not password:
        return flask.redirect(flask.url_for('login.index'))

    user = users.get_user(db, username, password)
    if not user:
        return flask.redirect(flask.url_for('login.index'))

    birthday = user.get('birthday')
    age = users.calculate_age(birthday) if birthday else None

    return flask.render_template(
        'profile.html',
        title=copy.title,
        subtitle=copy.subtitle,
        user=username,
        birthday=birthday,
        age=age
    )
