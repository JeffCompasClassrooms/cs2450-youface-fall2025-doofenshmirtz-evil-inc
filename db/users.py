import tinydb
from tinydb import Query
from datetime import datetime, date
import random

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

def new_user(db, username, handle, password, birthday, engineering_preference, pfp, bio=""):
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
        'engineering_preference': engineering_preference,
        'friends': ["N0rm"],
        'followers': [],
        'following': [],
        'friend_requests': [],
        'blocked_users': [],
        'unread_messages': []
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

def get_user_followers(db, user):
    """Return list of user dicts for followers of the given user"""
    users_table = db.table('users')
    User = Query()
    followers_list = []
    for follower_username in user.get('followers', []):
        follower = users_table.get(User.username == follower_username)
        if follower:
            followers_list.append(follower)
    return followers_list

def get_user_following(db, user):
    """Return list of user dicts for followers of the given user"""
    users_table = db.table('users')
    User = Query()
    following_list = []
    for following_username in user.get('following', []):
        follower = users_table.get(User.username == following_username)
        if follower:
            following_list.append(follower)
    return following_list

def get_all_users(db):
    """Return all users."""
    users_table = db.table('users')
    return users_table.all()

def get_suggested_users(db, user):
    all_users = get_all_users(db)
    suggested_users = []

    for other_user in all_users:
        # Skip adding self
        if other_user["username"] == user["username"]:
            continue
        # Skip adding blocked users, or users blocking user
        if other_user["username"] in user["blocked_users"] or \
            user["username"] in other_user["blocked_users"]:
            continue
        # Skip adding friends
        if other_user["username"] in user["friends"] or \
            user["username"] in other_user["friends"]:
            continue

        if other_user["preferred_engineering"] == user["preferred_engineering"]:
            suggested_users.append(other_user["username"])
        elif random.randint(1,100) < 30:
            suggested_users.append(other_user["username"])

    full_suggested_users = []

    for suggested_user in suggested_users:
        full_suggested_users.append(suggested_user.get_user(db, suggested_user["username"]))
    
    return suggested_users

def follow_user(db, from_user, to_user):
    """Follow another user if not blocked or already following"""
    users_table = db.table('users')
    User = Query()

    sender = users_table.get(User.username == from_user['username'])
    receiver = users_table.get(User.username == to_user)

    if not sender or not receiver:
        return ("No user found.", "danger")

    # Check if already following 
    if to_user in sender.get('following', []):
        return (f"You are already following {to_user}.", "warning")

    # Check if blocked
    if sender['username'] in receiver.get('blocked_users', []):
        return ("You cannot follow this user.", "danger")

    # Add follow
    receiver['followers'].append(sender['username'])
    sender['following'].append(receiver['username'])

    # Update DB properly
    users_table.update({'followers': receiver['followers']}, User.username == receiver['username'])
    users_table.update({'following': sender['following']}, User.username == sender['username'])

    return (f"Successfully following {to_user}!", "success")


def send_friend_request(db, from_user, to_user):
    """Send a friend request if not blocked or already friends."""
    users_table = db.table('users')
    User = Query()

    sender = users_table.get(User.username == from_user['username'])
    receiver = users_table.get(User.username == to_user)
    if not sender or not receiver:
        return ("User not found.", "danger")

    if to_user in sender.get('friends', []):
        return ("You are already friends with this user.", "warning")

    if from_user['username'] in receiver.get('blocked_users', []):
        return ("You cannot send a friend request to this user.", "danger")

    if from_user['username'] in receiver.get('friend_requests', []):
        return ("Friend request already sent.", "info")

    receiver['friend_requests'].append(from_user['username'])
    users_table.update(receiver, User.username == to_user)

    return (f"Friend request sent to {to_user}!", "success")


def accept_friend_request(db, from_user, to_user):
    """Accept a friend request between two users."""
    users_table = db.table('users')
    User = Query()

    # Handle both username strings and user dicts
    if isinstance(from_user, dict):
        from_user = from_user.get('username')
    if isinstance(to_user, dict):
        to_user = to_user.get('username')

    # Get sender (who sent request) and receiver (who accepts)
    sender = users_table.get(User.username == from_user)
    receiver = users_table.get(User.username == to_user)

    if not sender or not receiver:
        return (f"User not found (from_user={from_user}, to_user={to_user}).", "danger")

    if from_user not in receiver.get('friend_requests', []):
        return (f"No pending friend request from {from_user}.", "warning")

    # Remove from pending requests
    receiver['friend_requests'].remove(from_user)

    # Add to each other’s friends lists
    if from_user not in receiver['friends']:
        receiver['friends'].append(from_user)
    if to_user not in sender['friends']:
        sender['friends'].append(to_user)

    # Update DB
    users_table.update(receiver, User.username == to_user)
    users_table.update(sender, User.username == from_user)

    return (f"You are now friends with {from_user}!", "success")


def decline_friend_request(db, from_user, to_user):
    """Decline a friend request."""
    users_table = db.table('users')
    User = Query()

    # Handle both username strings and user dicts
    if isinstance(from_user, dict):
        from_user = from_user.get('username')
    if isinstance(to_user, dict):
        to_user = to_user.get('username')

    sender = users_table.get(User.username == from_user)
    receiver = users_table.get(User.username == to_user)

    if not sender or not receiver:
        return (f"User not found (from_user={from_user}, to_user={to_user}).", "danger")

    if from_user not in receiver.get('friend_requests', []):
        return (f"No friend request to decline from {from_user}.", "warning")

    receiver['friend_requests'].remove(from_user)
    users_table.update(receiver, User.username == to_user)

    return (f"Friend request from {from_user} declined.", "info")


def unfriend_user(db, user, friend_name):
    """Remove a friend from both users' friend lists."""
    users_table = db.table('users')
    User = Query()
    current_user = users_table.get(User.username == user['username'])
    friend = users_table.get(User.username == friend_name)

    if not current_user or not friend:
        return "User not found.", "danger"

    if friend_name not in current_user.get('friends', []):
        return "That user is not your friend.", "warning"

    # Remove from both sides
    current_user['friends'].remove(friend_name)
    friend['friends'].remove(user['username'])

    users_table.update(current_user, User.username == user['username'])
    users_table.update(friend, User.username == friend_name)

    return f"You unfriended {friend_name}.", "success"


def block_user(db, current_user, target_username):
    """Block another user and remove any friendship or requests."""
    users_table = db.table('users')
    User = Query()

    blocker = users_table.get(User.username == current_user['username'])
    target = users_table.get(User.username == target_username)

    if not blocker or not target:
        return False, 'User not found'

    # Initialize block lists if missing
    blocker.setdefault('blocked', [])
    target.setdefault('blocked_by', [])

    # If already blocked
    if target_username in blocker['blocked']:
        return False, 'User already blocked'

    # Remove from friends if they are friends
    if target_username in blocker.get('friends', []):
        blocker['friends'].remove(target_username)
    if blocker['username'] in target.get('friends', []):
        target['friends'].remove(blocker['username'])

    # Remove any pending friend requests between them
    if target_username in blocker.get('friend_requests', []):
        blocker['friend_requests'].remove(target_username)
    if blocker['username'] in target.get('friend_requests', []):
        target['friend_requests'].remove(blocker['username'])

    # Remove from each other’s followers/following lists safely
    if target_username in blocker.get('followers', []):
        blocker['followers'].remove(target_username)
    if blocker['username'] in target.get('following', []):
        target['following'].remove(blocker['username'])

    if target_username in blocker.get('following', []):
        blocker['following'].remove(target_username)
    if blocker['username'] in target.get('followers', []):
        target['followers'].remove(blocker['username'])

    # Add to block lists
    blocker['blocked'].append(target_username)
    target['blocked_by'].append(blocker['username'])

    # Update both users
    users_table.update(blocker, User.username == blocker['username'])
    users_table.update(target, User.username == target['username'])

    return True, f'User {target_username} has been blocked.'


from tinydb import Query

def delete_user(db, user):

    """Delete a user and clean up references."""
    if not user or 'username' not in user:
        return False

    username = user['username']
    users_table = db.table('users')
    User = Query()

    # Remove references from other users
    for u in users_table.all():
        changed = False
        for field in ['friends', 'followers', 'following', 'friend_requests', 'blocked_users']:
            if username in u.get(field, []):
                u[field].remove(username)
                changed = True
        if changed:
            users_table.update(
                {
                    'friends': u.get('friends', []),
                    'followers': u.get('followers', []),
                    'following': u.get('following', []),
                    'friend_requests': u.get('friend_requests', []),
                    'blocked_users': u.get('blocked_users', [])
                },
                User.username == u['username']
            )

    # Remove the user itself
    users_table.remove(User.username == username)
    return True

def send_message(db, from_user, to_user, content):
    """Send a message from one user to another."""
    users_table = db.table('users')
    messages_table = db.table('messages')
    User = Query()

    sender = users_table.get(User.username == from_user['username'])
    receiver = users_table.get(User.username == to_user)

    if not sender or not receiver:
        return ("User not found.", "danger")

    if to_user not in sender.get('friends', []):
        return ("You can only message friends.", "warning")

    if from_user['username'] in receiver.get('blocked_users', []):
        return ("You cannot message this user.", "danger")

    # Create message entry
    message_record = {
        "sender": from_user['username'],
        "receiver": to_user,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "read": False
    }

    messages_table.insert(message_record)
    return (f"Message sent to {to_user}!", "success")

def receive_message(db, user, friend_name):
    """Return unread messages from a friend."""
    messages_table = db.table('messages')
    Message = Query()
    unread = messages_table.search(
        (Message.receiver == user['username']) & 
        (Message.sender == friend_name) &
        (Message.read == False)
    )

    # Mark them as read
    for msg in unread:
        msg['read'] = True
        messages_table.update(msg, doc_ids=[msg.doc_id])

    return unread

from datetime import datetime

def get_conversation(db, user1, user2):
    """Retrieve all messages between two users, sorted by time."""
    messages_table = db.table('messages')
    messages = messages_table.all()

    convo = [
        m for m in messages
        if (m['sender'] == user1 and m['receiver'] == user2)
        or (m['sender'] == user2 and m['receiver'] == user1)
    ]

    # Convert timestamps from ISO strings to datetime objects
    for msg in convo:
        if isinstance(msg.get('timestamp'), str):
            try:
                msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])
            except ValueError:
                pass  # leave it as-is if malformed

    convo.sort(key=lambda x: x['timestamp'])
    return convo
