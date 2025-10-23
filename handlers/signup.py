import random

import datetime 
import flask
from handlers import copy
from db import posts, users, helpers

PFPlist = [
    "uploads/AgentC.png",
    "uploads/AgentD.png",
    "uploads/AgentH.png",
    "uploads/AgentS.png"
]

def getRandomPFP():
    newPFP = random.choice(PFPlist)
    return newPFP

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
    birthday = flask.request.form.get('birthday')

    # Use username as the handle if none provided in form
    handle = username 
    pfp = getRandomPFP() 

    resp = flask.make_response(flask.redirect(flask.url_for('login.index')))
    resp.set_cookie('username', username)
    resp.set_cookie('password', password)
    resp.set_cookie('birthday', birthday)
    resp.set_cookie('pfp', pfp)

    submit = flask.request.form.get('type')
    if submit == 'Create Account':
        if users.new_user(db, username, handle, password, birthday, pfp, "") is None:
            resp.set_cookie('username', '', expires=0)
            resp.set_cookie('password', '', expires=0)
            resp.set_cookie('birthday', '', expires=0)
            resp.set_cookie('pfp', '', expires=0)
            flask.flash(f'Username {username} already taken!', 'danger')
            return flask.redirect(flask.url_for('signup.signupscreen'))
        flask.flash(f'User {username} created successfully!', 'success')

    return resp