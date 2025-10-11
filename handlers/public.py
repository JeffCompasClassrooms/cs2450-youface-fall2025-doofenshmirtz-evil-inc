import flask
from db import users, posts, helpers
from handlers import copy

blueprint = flask.Blueprint("public", __name__)

@blueprint.route('/@<handle>')
def view_public_profile(username):
    """Publicly view a user's profile via @handle."""
    db = helpers.load_db()
    user = users.get_user_by_name(db, username)

    if not user:
        flask.abort(404, description="User not found.")

    all_posts = posts.get_posts(db, user)[::-1]

    return flask.render_template(
        'public_profile.html',
        title=f"@{user['username']} on Inator-inator",
        subtitle="Inventor Spotlight",
        profile_user=user,
        posts=all_posts,
        copy=copy,
    )