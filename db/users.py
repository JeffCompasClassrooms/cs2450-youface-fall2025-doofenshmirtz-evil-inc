import tinydb
from tinydb import Query
from datetime import datetime, date

DB_PATH = 'db.json'

def load_db():
    return tinydb.TinyDB(DB_PATH, sort_keys=True, indent=4, separators=(',', ': '))

def get_user(db, username, password=None):
    """Retrieve a user, optionally validating password."""
    users_table = db.table('users')
    User = Query()
    user = users_table.get(User.username == username)
    if not user:
        return None
    if password is not None and user.get('password') != password:
        return None
    return user

def new_user(db, username, handle, password, birthday, pfp, bio=""):
    """Add a new user and return user dict."""
    users_table = db.table('users')
    User = Query()
    if users_table.get((User.username == username) | (User.handle == handle.lower())):
        return None

    user_record = {
        'username': username,
        'password': password,
        'birthday': birthday,
        'bio': bio,
        'handle': handle,
        'pfp': pfp,
        'friends': [],
        'followers': [],
        'following': [],
        'friend_requests': [],
        'blocked_users': []
    }

    users_table.insert(user_record)
    return user_record

def update_user(db, username, updates):
    """Update a user's info."""
    users_table = db.table('users')
    User = Query()
    users_table.update(updates, User.username == username)

def calculate_age(birthday_str):
    """Calculate age from a birthday string YYYY-MM-DD."""
    if not birthday_str:
        return None
    try:
        birth_date = datetime.strptime(birthday_str, "%Y-%m-%d").date()
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except ValueError:
        return None

def get_user_friends(db, user):
    """Return list of user dicts for friends of the given user."""
    users_table = db.table('users')
    User = Query()
    friends_list = []
    for friend_username in user.get('friends', []):
        friend = users_table.get(User.username == friend_username)
        if friend:
            friends_list.append(friend)
    return friends_list

def get_all_users(db):
    """Return all users."""
    users_table = db.table('users')
    return users_table.all()

def send_friend_request(db, from_user, to_user):
    """Send a friend request if not blocked or already friends."""
    users_table = db.table('users')
    User = Query()
    sender = users_table.get(User.username == from_user)
    receiver = users_table.get(User.username == to_user)
    if not sender or not receiver:
        return False

    if to_user in sender.get('friends', []) or from_user in receiver.get('blocked_users', []):
        return False

    if from_user not in receiver.get('friend_requests', []):
        receiver['friend_requests'].append(from_user)
        users_table.update(receiver, User.username == to_user)
    return True

def accept_friend_request(db, from_user, to_user):
    """Accept a friend request."""
    users_table = db.table('users')
    User = Query()
    sender = users_table.get(User.username == from_user)
    receiver = users_table.get(User.username == to_user)
    if not sender or not receiver:
        return False

    if from_user in receiver.get('friend_requests', []):
        receiver['friend_requests'].remove(from_user)
        receiver['friends'].append(from_user)
        sender['friends'].append(to_user)
        users_table.update(receiver, User.username == to_user)
        users_table.update(sender, User.username == from_user)
    return True

def block_user(db, blocker, blocked):
    """Block a user and remove all connections between them."""
    users_table = db.table('users')
    User = Query()
    blocker_user = users_table.get(User.username == blocker)
    blocked_user = users_table.get(User.username == blocked)
    if not blocker_user or not blocked_user:
        return False

    # Remove from all lists
    for field in ['friends', 'followers', 'following', 'friend_requests']:
        if blocked in blocker_user.get(field, []):
            blocker_user[field].remove(blocked)
        if blocker in blocked_user.get(field, []):
            blocked_user[field].remove(blocker)

    if blocked not in blocker_user.get('blocked_users', []):
        blocker_user['blocked_users'].append(blocked)

    users_table.update(blocker_user, User.username == blocker)
    users_table.update(blocked_user, User.username == blocked)
    return True

def delete_user(db, user):
    """Delete a user and clean up references."""
    if not user:
        return False

    username = user['username']
    users_table = db.table('users')
    User = Query()

    # Remove from other users' lists
    for u in users_table.all():
        changed = False
        for field in ['friends', 'followers', 'following', 'friend_requests', 'blocked_users']:
            if username in u.get(field, []):
                u[field].remove(username)
                changed = True
        if changed:
            users_table.update(u, User.username == u['username'])

    # Remove the user itself
    users_table.remove(User.username == username)
    return True
