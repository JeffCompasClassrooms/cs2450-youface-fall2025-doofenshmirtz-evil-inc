import flask

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
