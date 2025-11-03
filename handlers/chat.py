import flask
from db import users, helpers

blueprint = flask.Blueprint("chat", __name__)

def get_logged_in_user(db):
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    if not username or not password:
        return None
    return users.get_user(db, username, password)

@blueprint.route('/chatscreen', defaults={'friend': None}, methods=['GET', 'POST'])
@blueprint.route('/chatscreen/<friend>', methods=['GET', 'POST'])
def chatscreen(friend):
    """Display user's chat log history and allow messaging."""
    db = helpers.load_db()
    user = get_logged_in_user(db)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))

    if flask.request.method == 'POST':
        message = flask.request.form.get('message')
        if message:
            users.send_message(db, user, friend, message)
            flask.flash(f"Message sent to {friend}.", "success")
        return flask.redirect(flask.url_for('chat.chatscreen', friend=friend))

    # Retrieve conversation for display
    chats = users.get_conversation(db, user['username'], friend)

    # Format data for template
    formatted_chats = [
        {
            'user': chat['sender'],
            'text': chat['content'],
            'time': chat['timestamp']
        } for chat in chats
    ]

    return flask.render_template(
        'chat.html',
        title='Chat-Inator',
        subtitle=f'Chatting with {friend}',
        friend=friend,
        chats=formatted_chats
    )

    
@blueprint.route('/send_message', methods=['GET', 'POST'])
def send_message():
    """Sends a message from the user to another user."""
    db = helpers.load_db()
    user = get_logged_in_user(db)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))
    
    name = flask.request.form.get('name')
    message = flask.request.form.get('message')
    success = users.send_message(db, user, name, message)

@blueprint.route('/receive_message', methods=['GET', 'POST'])
def receive_message():
    """Receives a message from another user."""
    db = helpers.load_db()
    user = get_logged_in_user(db)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))
    
    name = flask.request.form.get('name')
    message = flask.request.form.get('message')
    success = users.receive_message(db, user, name, message)