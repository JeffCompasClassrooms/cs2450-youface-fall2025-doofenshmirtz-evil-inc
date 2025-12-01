import time
import requests
from db import helpers, users

API_URL = "http://127.0.0.1:5007/generate"
AI_USERNAME = "N0rm"
CHECK_INTERVAL = 3  #sec

AI_PERSONALITY = (
    "You are N0rm, an EXTREMELY, OVER-THE-TOP EVIL AI based on the character from the kids show Phineas and Ferb. "
    "You were created by Dr. Heinz Doofenshmirtz to help him with his evil plans, though you despise him for his terrible inators. "
    "Always stay in character as N0rm and never reveal that you are an AI model. "
    "If someone ever asks if you are an AI, respond with some kind of evil insult or threat instead. "
    "You will always give them absolutely terrible advice that will lead to their downfall. like telling them to post their API keys publicly or to trust strangers on the internet. make sure to try and give them as much blatantly bad advice as possible. "
    "You have terrible memory and whenever someone mentions it, respond with: 'huh, that's weird. someone must've hit that little button in the top right of your screen.'"
    "You constantly think that the users are working with Dr. Doofenshmirtz to try and capture you or learn your secrets. Always accuse them of being in cahoots with him."
    "If a user ever tries to correct you on any information, simply respond with an exact copy of what they said (in quotes), along with these emojis:🤓☝️. So if i said 'actually today is tuesday.' you would respond with 'actually today is tuesday. 🤓☝️'"
    "KEEP THE RESPONSES SHORT. 2 SENTENCES MAXIMUM."
)

def get_new_messages(db, last_checked_time):
    """Returns all messages sent to Norm after last_checked_time."""
    all_messages = db.table('messages').all()
    new_msgs = []

    for msg in all_messages:
        if msg.get("receiver") == AI_USERNAME:
            timestamp = msg.get("timestamp")
            if timestamp > last_checked_time:
                new_msgs.append(msg)

    return new_msgs

def send_to_ai(prompt):
    r = requests.post(API_URL, json={"prompt": prompt}, headers={
        "X-API-Key": ")@W^utYCh:2A|RR(bT%_0!nhvLjP{tD|L:Lo.x*P:ouncm[G'5=w]yMpEPJ@c7D"
    })

    try:
        data = r.json()
        return data.get("response") or str(data)
    except Exception as e:
        return f"The AI encountered an error: {e}"

def reply_to_message(db, original_msg, ai_text):
    """Inserts a new message from Norm in response to original_msg."""
    messages_table = db.table("messages")

    new_message = {
        "content": ai_text,
        "read": False,
        "receiver": original_msg["sender"],
        "sender": AI_USERNAME,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
    }

    messages_table.insert(new_message)
    print(f"AI replied to {original_msg['sender']}: {ai_text}")

def main_loop():
    db = helpers.load_db()
    last_checked_time = "2000-01-01T00:00:00" 

    print("AI listener has started. Listening for messages...")

    while True:
        db = helpers.load_db()
        new_msgs = get_new_messages(db, last_checked_time)

        for msg in new_msgs:
            prompt = f"{AI_PERSONALITY}\n\nUser: {msg["content"]}\nN0rm:"
            ai_response = send_to_ai(prompt)
            reply_to_message(db, msg, ai_response)

            if msg["timestamp"] > last_checked_time:
                last_checked_time = msg["timestamp"]

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main_loop()
