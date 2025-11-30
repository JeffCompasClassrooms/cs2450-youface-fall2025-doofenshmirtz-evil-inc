# std imports
import time

# installed imports
import flask
import timeago
import tinydb

# handlers
from handlers import friends, login, posts, public, signup, profile, chat, chatpage

app = flask.Flask(__name__)

@app.template_filter('convert_time')
def convert_time(ts):
    """A jinja template helper to convert timestamps to timeago."""
    app.logger.debug("convert_time called with: %r (%s)", ts, type(ts))
    return timeago.format(ts, time.time())

app.register_blueprint(login.login_blueprint)
app.register_blueprint(signup.signup_blueprint)
app.register_blueprint(friends.blueprint)
app.register_blueprint(posts.blueprint)
app.register_blueprint(profile.blueprint)
app.register_blueprint(public.blueprint)
app.register_blueprint(chat.blueprint)
app.register_blueprint(chatpage.blueprint)


app.secret_key = 'mygroup'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006, debug=False, use_reloader=False, threaded=True)
