import flask
from db import users, helpers

blueprint = flask.Blueprint("chatpage", __name__)

def get_logged_in_user(db):
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    if not username or not password:
        return None
    return users.get_user(db, username, password)

@blueprint.route('/chatpage', methods=['GET'])
def chatpage():
    """Display all friends of the logged-in user, even if no messages exist."""
    db = helpers.load_db()
    user = get_logged_in_user(db)

    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))

    friends = users.get_user_friends(db, user)

    return flask.render_template("chatpage.html", 
                                 title="Chat-Inator",
                                 subtitle="Chat with your friends!",
                                 friends=friends)
