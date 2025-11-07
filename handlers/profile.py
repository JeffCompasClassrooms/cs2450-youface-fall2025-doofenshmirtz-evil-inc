import flask
from handlers import copy
from db import users, helpers

blueprint = flask.Blueprint("profile", __name__)

@blueprint.route('/profilescreen', methods=['GET', 'POST'])
def profilescreen():
    """Display and allow editing of a user's profile."""
    db = helpers.load_db()

    # Read cookies
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    if not username or not password:
        return flask.redirect(flask.url_for('login.loginscreen'))

    user = users.get_user(db, username, password)
    if not user:
        return flask.redirect(flask.url_for('login.loginscreen'))

    # Handle POST
    if flask.request.method == 'POST':
        # Update bio
        new_bio = flask.request.form.get('bio', '').strip()
        if new_bio != user.get('bio', ''):
            user['bio'] = new_bio
            users.update_user(db, username, {'bio': new_bio})
            flask.flash('Profile updated successfully!', 'success')

        # Delete account
        delete_input = flask.request.form.get('delete_confirm', '').strip().lower()
        if delete_input == 'delete':
            success = users.delete_user(db, user)
            if success:
                flask.flash('Your account has been deleted.', 'success')
                response = flask.redirect(flask.url_for('login.loginscreen'))
                # Delete cookies
                response.delete_cookie('username')
                response.delete_cookie('password')
                response.delete_cookie('birthday')
                response.delete_cookie('pfp')
                return response
            else:
                flask.flash('Failed to delete account.', 'danger')

    # Profile data
    bio = user.get('bio', '')
    birthday = user.get('birthday')
    age = users.calculate_age(birthday) if birthday else None
    handle = user.get('handle', f"@{username}")
    pfp = user.get('pfp', 'uploads/default.png')  # fallback

    # Friends and followers
    friends_list = users.get_user_friends(db, user)
    num_friends = len(friends_list)
    num_followers = len(user.get('followers', []))

    return flask.render_template(
        'profile.html',
        title="Profile-Inator",
        subtitle="Everything about you",
        user=username,
        handle=handle,
        birthday=birthday,
        age=age,
        bio=bio,
        pfp=pfp,
        friends=friends_list,
        num_friends=num_friends,
        num_followers=num_followers
    )
