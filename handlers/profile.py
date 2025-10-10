import flask
from handlers import copy
from db import posts, users, helpers

# -----------------------
# PROFILE BLUEPRINT
# -----------------------
blueprint = flask.Blueprint("profile", __name__)

@blueprint.route('/profilescreen')
def profilescreen():
    """Present a formatted user profile screen."""
    db = helpers.load_db()

    # First check if already logged in
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    birthday = flask.request.cookies.get('birthday')

    return flask.render_template('profile.html', title=copy.title,
                                 subtitle=copy.subtitle, user=username)
