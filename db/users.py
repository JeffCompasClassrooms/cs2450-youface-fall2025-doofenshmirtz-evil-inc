import tinydb
from tinydb import Query
from datetime import datetime, date

DB_PATH = 'db.json'

def load_db():
    return tinydb.TinyDB(DB_PATH, sort_keys=True, indent=4, separators=(',', ': '))

def get_user(db, username, password=None):
    """Retrieve a user, optionally validating password."""
    User = Query()
    user = db.get(User.username == username)
    if not user:
        return None
    if password is not None and user.get('password') != password:
        return None
    return user

def add_user(db, username, password_hash, birthday=None):
    """Add a new user to the DB."""
    User = Query()
    if db.contains(User.username == username):
        return False

    db.insert({
        'username': username,
        'password': password_hash,
        'birthday': birthday,
        'bio': '',
        'handle': f"@{username}",
        'pfp': 'default_pfp.png',
        'friends': [],
        'followers': [],
        'following': [],
        'friend_requests': [],
        'blocked_users': []
    })
    return True

def update_user(db, username, updates):
    """Update a user's info."""
    User = Query()
    db.update(updates, User.username == username)

def calculate_age(birthday_str):
    """Calculate age from a stored birthday string (YYYY-MM-DD)."""
    if not birthday_str:
        return None
    try:
        birth_date = datetime.strptime(birthday_str, "%Y-%m-%d").date()
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except ValueError:
        return None

def delete_user(username):
    """Delete a user and remove references to them from others."""
    db = load_db()
    User = Query()
    user = db.get(User.username == username)
    if not user:
        db.close()
        return False

    all_users = db.all()
    for u in all_users:
        changed = False

        for field in ['friends', 'followers', 'following', 'friend_requests', 'blocked_users']:
            if username in u.get(field, []):
                u[field].remove(username)
                changed = True

        if changed:
            db.update(u, Query().username == u['username'])

    # Finally, remove the user
    db.remove(User.username == username)
    db.close()
    return True

def get_all_users(db):
    """Return all users."""
    return db.all()

def send_friend_request(db, from_user, to_user):
    """Send a friend request if not blocked or already friends."""
    User = Query()
    sender = db.get(User.username == from_user)
    receiver = db.get(User.username == to_user)
    if not sender or not receiver:
        return False

    if to_user in sender.get('friends', []) or from_user in receiver.get('blocked_users', []):
        return False

    if from_user not in receiver.get('friend_requests', []):
        receiver['friend_requests'].append(from_user)
        db.update(receiver, User.username == to_user)
    return True

def accept_friend_request(db, from_user, to_user):
    """Accept a friend request."""
    User = Query()
    sender = db.get(User.username == from_user)
    receiver = db.get(User.username == to_user)
    if not sender or not receiver:
        return False

    if from_user in receiver.get('friend_requests', []):
        receiver['friend_requests'].remove(from_user)
        receiver['friends'].append(from_user)
        sender['friends'].append(to_user)
        db.update(receiver, User.username == to_user)
        db.update(sender, User.username == from_user)
    return True

def block_user(db, blocker, blocked):
    """Block a user and remove all connections between them."""
    User = Query()
    blocker_user = db.get(User.username == blocker)
    blocked_user = db.get(User.username == blocked)
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

    db.update(blocker_user, User.username == blocker)
    db.update(blocked_user, User.username == blocked)
    return True
