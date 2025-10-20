import tinydb
from datetime import date, datetime


def calculate_age(birthday_str):
    """Return the integer age given a 'YYYY-MM-DD' birthday string."""
    if not birthday_str:
        return None
    birth_date = datetime.strptime(birthday_str, "%Y-%m-%d").date()
    today = date.today()

    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def new_user(db, username, handle, password, birthday, pfp, bio=""):
    """Create a new user if username and handle are unique."""
    users = db.table('users')
    User = tinydb.Query()

    if users.get((User.username == username) | (User.handle == handle.lower())):
        return None  # User already exists

    user_record = {
        'username': username,
        'password': password,
        'handle': handle.lower(),
        'birthday': birthday,
        'pfp': pfp,
        'bio': bio,
        'friends': [],
        'followers': [],
        'friend_requests': [],
        'blocked': []
    }
    return users.insert(user_record)


def get_user(db, username, password):
    """Return a user record by username and password."""
    users = db.table('users')
    User = tinydb.Query()
    return users.get((User.username == username) & (User.password == password))


def get_user_by_name(db, username):
    """Return a user record by username."""
    users = db.table('users')
    User = tinydb.Query()
    return users.get(User.username == username)


def get_user_by_handle(db, handle):
    """Return a user record by handle."""
    users = db.table('users')
    User = tinydb.Query()
    return users.get(User.handle == handle.lower())


def delete_user(db, username, password):
    """Remove a user by username and password."""
    users = db.table('users')
    User = tinydb.Query()
    return users.remove((User.username == username) & (User.password == password))


def add_user_follower(db, user, follower):
    """Allow a user to gain a follower, even if they already follow each other."""
    users = db.table('users')
    User = tinydb.Query()

    follower_user = users.get(User.username == follower)
    if not follower_user:
        return f'User {follower} does not exist.', 'danger'

    # Only add if they aren’t already a follower
    if follower not in user['followers']:
        user['followers'].append(follower)
        users.upsert(user, (User.username == user['username']) & (User.password == user['password']))
        return f'{follower} is now following {user["username"]}.', 'success'

    # If they already follow, do nothing but still report success
    return f'{follower} is already following {user["username"]}.', 'info'



def remove_user_follower(db, user, follower):
    """Remove a follower from a user's follower list."""
    users = db.table('users')
    User = tinydb.Query()

    if follower in user['followers']:
        user['followers'].remove(follower)
        users.upsert(user, (User.username == user['username']) & (User.password == user['password']))
        return f'Follower {follower} removed successfully!', 'success'

    return f'{follower} is not a follower.', 'warning'


def send_friend_request(db, user, target_username):
    """Send a friend request from user to target_username."""
    users = db.table('users')
    User = tinydb.Query()

    target = users.get(User.username == target_username)
    if not target:
        return f'User {target_username} does not exist.', 'danger'

    if target_username in user['friend_requests']:
        return f'You have already sent a request to {target_username}.', 'warning'

    target['friend_requests'].append(user['username'])
    users.upsert(target, User.username == target_username)

    return f'Friend request successfully sent to {target_username}!', 'success'


def cancel_friend_request(db, user, target_username):
    """Cancel a friend request that was sent to another user."""
    users = db.table('users')
    User = tinydb.Query()

    target = users.get(User.username == target_username)
    if not target:
        return f'User {target_username} does not exist.', 'danger'

    if user['username'] not in target['friend_requests']:
        return f'No friend request to {target_username} exists.', 'warning'

    target['friend_requests'].remove(user['username'])
    users.upsert(target, User.username == target_username)

    return f'Friend request to {target_username} canceled.', 'success'


def add_user_friend(db, user, friend_username):
    """Add a friend if both users exist."""
    users = db.table('users')
    User = tinydb.Query()

    friend = users.get(User.username == friend_username)
    if not friend:
        return f'User {friend_username} does not exist.', 'danger'

    if friend_username in user['friends']:
        return f'You are already friends with {friend_username}.', 'warning'

    user['friends'].append(friend_username)
    friend['friends'].append(user['username'])

    users.upsert(user, User.username == user['username'])
    users.upsert(friend, User.username == friend_username)

    return f'Friend {friend_username} added successfully!', 'success'


def remove_user_friend(db, user, friend_username):
    """Remove a friend connection between two users."""
    users = db.table('users')
    User = tinydb.Query()

    friend = users.get(User.username == friend_username)
    if not friend:
        return f'User {friend_username} does not exist.', 'danger'

    if friend_username not in user['friends']:
        return f'You are not friends with {friend_username}.', 'warning'

    user['friends'].remove(friend_username)
    if user['username'] in friend['friends']:
        friend['friends'].remove(user['username'])

    users.upsert(user, User.username == user['username'])
    users.upsert(friend, User.username == friend_username)

    return f'Friend {friend_username} successfully removed!', 'success'


def get_user_friends(db, user):
    """Return detailed lists of friends, friend requests, and followers."""
    users = db.table('users')
    User = tinydb.Query()

    friends = [users.get(User.username == f) for f in user['friends']]
    friend_requests = [users.get(User.username == r) for r in user['friend_requests']]
    followers = [users.get(User.username == fl) for fl in user['followers']]

    return {
        'friends': friends,
        'friend_requests': friend_requests,
        'followers': followers
    }


def block_user(db, user, target_username):
    """Block another user."""
    users = db.table('users')
    User = tinydb.Query()

    target = users.get(User.username == target_username)
    if not target:
        return f'User {target_username} does not exist.', 'warning'

    if target_username in user['blocked']:
        return f'{target_username} is already blocked.', 'warning'

    user['blocked'].append(target_username)
    users.upsert(user, User.username == user['username'])

    return f'User {target_username} has been blocked.', 'success'
