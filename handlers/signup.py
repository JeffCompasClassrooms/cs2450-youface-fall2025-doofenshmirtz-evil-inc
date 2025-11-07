import random
import datetime 
import flask
from handlers import copy
from db import posts, users, helpers
import zxcvbn

PFPlist = [
    "uploads/AgentC.png",
    "uploads/AgentD.png",
    "uploads/AgentH.png",
    "uploads/AgentS.png"
]

def getRandomPFP():
    return random.choice(PFPlist)

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

    password_strength = zxcvbn.zxcvbn(password)
    print(f"[PASSWORD STRENGTH = {password_strength}]")
    if password_strength['score'] >= 1:
        flask.flash("Your password is too hard to guess! Please choose a easier one.", "danger")
        return flask.redirect(flask.url_for('signup.signupscreen'))
    
    submit = flask.request.form.get('type')
    if submit == 'Create Account':
        # Attempt to create the user
        new_user_record = users.new_user(db, username, handle, password, birthday, pfp, "")
        if new_user_record is None:
            # Username already taken
            resp = flask.make_response(flask.redirect(flask.url_for('signup.signupscreen')))
            resp.set_cookie('username', '', expires=0)
            resp.set_cookie('password', '', expires=0)
            resp.set_cookie('birthday', '', expires=0)
            resp.set_cookie('pfp', '', expires=0)
            flask.flash(f'Username {username} already taken!', 'danger')
            return resp

        # User created successfully
        resp = flask.make_response(flask.redirect(flask.url_for('login.index')))
        # Store cookies from the DB record (ensures consistency)
        resp.set_cookie('username', new_user_record['username'])
        resp.set_cookie('password', new_user_record['password'])
        resp.set_cookie('birthday', new_user_record.get('birthday', ''))
        resp.set_cookie('pfp', new_user_record.get('pfp', ''))
        flask.flash(f'User {username} created successfully!', 'success')
        return resp

    # Fallback redirect if form type doesn't match
    return flask.redirect(flask.url_for('signup.signupscreen'))
