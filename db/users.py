import tinydb
from datetime import date, datetime

def calculate_age(birthday_str):
    if not birthday_str:
        return None
    birth_date = datetime.strptime(birthday_str, "%Y-%m-%d").date()
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age

def new_user(db, username, handle, password, birthday, pfp, bio=""):
    users = db.table('users')
    User = tinydb.Query()
    if users.get((User.username == username) | (User.handle == handle.lower())):
        return None
    user_record = {
        'username': username,
        'password': password,
        'handle': handle.lower(),
        'friends': [],
        'followers': [],
        'following': [],
        'friend_requests': [],
        'blocked': [],
        'birthday': birthday,
        'pfp': pfp,
        'bio': bio,
    }
    return users.insert(user_record)

def get_user(db, username, password):
    users = db.table('users')
    User = tinydb.Query()
    return users.get((User.username == username) & (User.password == password))

def get_user_by_name(db, username):
    users = db.table('users')
    User = tinydb.Query()
    return users.get(User.username == username)

def update_user(db, user):
    users = db.table('users')
    User = tinydb.Query()
    users.update(user, User.username == user['username'])

# --- FOLLOWING LOGIC ---
def follow_user(db, follower, target_name):
    users = db.table('users')
    User = tinydb.Query()
    target = users.get(User.username == target_name)
    if not target:
        return f"User {target_name} does not exist.", "danger"

    if follower['username'] == target_name:
        return "You cannot follow yourself.", "warning"

    if target_name in follower['blocked'] or follower['username'] in target['blocked']:
        return f"You cannot follow {target_name}.", "danger"

    if target_name in follower['following']:
        return f"You already follow {target_name}.", "info"

    follower['following'].append(target_name)
    target['followers'].append(follower['username'])
    update_user(db, follower)
    update_user(db, target)
    return f"You are now following {target_name}.", "success"

def unfollow_user(db, follower, target_name):
    users = db.table('users')
    User = tinydb.Query()
    target = users.get(User.username == target_name)
    if not target:
        return "User not found.", "danger"

    if target_name in follower['following']:
        follower['following'].remove(target_name)
    if follower['username'] in target['followers']:
        target['followers'].remove(follower['username'])
    update_user(db, follower)
    update_user(db, target)
    return f"You unfollowed {target_name}.", "success"

# --- FRIEND REQUESTS ---
def send_friend_request(db, sender, receiver_name):
    users = db.table('users')
    User = tinydb.Query()
    receiver = users.get(User.username == receiver_name)
    if not receiver:
        return "User not found.", "danger"

    if receiver_name == sender['username']:
        return "You cannot friend yourself.", "warning"

    if receiver_name in sender['friends']:
        return f"You are already friends with {receiver_name}.", "info"

    if sender['username'] in receiver['friend_requests']:
        return "Request already sent.", "info"

    if sender['username'] in receiver['blocked'] or receiver_name in sender['blocked']:
        return "Cannot send request (blocked).", "danger"

    receiver['friend_requests'].append(sender['username'])
    update_user(db, receiver)
    return f"Friend request sent to {receiver_name}.", "success"

def respond_friend_request(db, user, sender_name, accept=True):
    users = db.table('users')
    User = tinydb.Query()
    sender = users.get(User.username == sender_name)
    if not sender:
        return "User not found.", "danger"

    if sender_name not in user['friend_requests']:
        return "No pending request from this user.", "warning"

    user['friend_requests'].remove(sender_name)
    if accept:
        user['friends'].append(sender_name)
        sender['friends'].append(user['username'])
        update_user(db, sender)
        update_user(db, user)
        return f"You are now friends with {sender_name}.", "success"
    else:
        update_user(db, user)
        return f"Declined friend request from {sender_name}.", "info"

# --- BLOCKING ---
def block_user(db, blocker, target_name):
    users = db.table('users')
    User = tinydb.Query()
    target = users.get(User.username == target_name)
    if not target:
        return "User not found.", "danger"

    if target_name not in blocker['blocked']:
        blocker['blocked'].append(target_name)

    # Remove friendships and follows
    for field in ['friends', 'followers', 'following']:
        if target_name in blocker[field]:
            blocker[field].remove(target_name)
        if blocker['username'] in target[field]:
            target[field].remove(blocker['username'])

    update_user(db, blocker)
    update_user(db, target)
    return f"You have blocked {target_name}.", "success"

def get_user_friends(db, user):
    users = db.table('users')
    User = tinydb.Query()
    friends = []
    for friend in user.get('friends', []):
        record = users.get(User.username == friend)
        if record:
            friends.append(record)
    return friends

def delete_user(db, username, password):
    """Delete a user from the database."""
    users = db.table('users')
    User = tinydb.Query()

    # Find and remove user
    result = users.remove((User.username == username) & (User.password == password))

    if result:
        # Also remove this user from other users' friend lists, followers, and requests
        for u in users.all():
            changed = False
            if 'friends' in u and username in u['friends']:
                u['friends'].remove(username)
                changed = True
            if 'followers' in u and username in u['followers']:
                u['followers'].remove(username)
                changed = True
            if 'following' in u and username in u['following']:
                u['following'].remove(username)
                changed = True
            if 'friend_requests' in u and username in u['friend_requests']:
                u['friend_requests'].remove(username)
                changed = True
            if 'blocked' in u and username in u['blocked']:
                u['blocked'].remove(username)
                changed = True
            if changed:
                users.upsert(u, (User.username == u['username']) & (User.password == u['password']))

        return True
    else:
        return False
