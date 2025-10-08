import flask
from handlers import copy
from db import posts, users, helpers

# -----------------------
# SIGNUP BLUEPRINT
# -----------------------
signup_blueprint = flask.Blueprint("signup", __name__)

@signup_blueprint.route('/signupscreen')
def signupscreen():
    """Present a form to the user to enter their information."""
    db = helpers.load_db()
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    if username and password and users.get_user(db, username, password):
        flask.flash('Account already exists.', 'warning')
        return flask.redirect(flask.url_for('signup.signupscreen'))

    return flask.render_template('signup.html', title=copy.title,
                                 subtitle=copy.subtitle)

@signup_blueprint.route('/signup', methods=['POST'])
def signup_post():
    db = helpers.load_db()
    username = flask.request.form.get('username')
    password = flask.request.form.get('password')
    age = flask.request.form.get('age')

    resp = flask.make_response(flask.redirect(flask.url_for('login.index')))
    resp.set_cookie('username', username)
    resp.set_cookie('password', password)

    submit = flask.request.form.get('type')
    if submit == 'Create Account':
        if users.new_user(db, username, password, age) is None:
            resp.set_cookie('username', '', expires=0)
            resp.set_cookie('password', '', expires=0)
            flask.flash(f'Username {username} already taken!', 'danger')
            return flask.redirect(flask.url_for('login.loginscreen'))
        flask.flash(f'User {username} created successfully!', 'success')
    elif submit == 'Delete' and users.delete_user(db, username, password):
        resp.set_cookie('username', '', expires=0)
        resp.set_cookie('password', '', expires=0)
        flask.flash(f'User {username} deleted successfully!', 'success')

    return resp
