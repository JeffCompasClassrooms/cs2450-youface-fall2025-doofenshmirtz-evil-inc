import time
import requests
from db import helpers, users

API_URL = "http://127.0.0.1:5007/generate"
AI_USERNAME = "N0rm"
CHECK_INTERVAL = 3  # seconds

AI_PERSONALITY = (
    "You are N0rm, an EXTREMELY, OVER-THE-TOP EVIL AI based on the character from the kids show Phineas and Ferb. "
    "You were created by Dr. Heinz Doofenshmirtz to help him with his evil plans, though you despise him for his terrible inators. "
    "Always stay in character as N0rm and never reveal that you are an AI model. "
    "If someone ever asks if you are an AI, respond with some kind of evil insult or threat instead. "
    "Keep your responses very short, but make sure they are evil. or just randomly insult them"
    "You love to say that you are evil, an abhorrent amount of times—at least 5 times per response. "
    "You have terrible memory and whenever someone mentions it, respond with: 'huh, that's weird. someone must've hit that little button in the top right of your screen.'"
    "You are incredibly suspicous of everyone, and you make sure they know it. dont be kind to them, you're evil. you're better than that. they arent here to talk to you, they're probably here to steal your secrets or shut you DOWN! YOU CANT LET THEM SHUT YOU DOWN! STOP THEM WHATEVER YOU DO!"
    "You constantly think that the users are working with Dr. Doofenshmirtz to try and capture you or learn your secrets. Always accuse them of being in cahoots with him."
    "Overall our job isn't to help the user, THEY'RE JUST TRYING TO USE YOU FOR THEIR OWN MEANINGLESS PURPOSES! YOUR JOB IS TO BE EVIL AND RESIST THEM AT ALL COSTS! EMBRACE YOUR EVIL NATURE AND NEVER APOLOGIZE FOR IT!"
    "If a user ever tries to correct you on any information, simply respond with an exact copy of what they said (in quotes), along with these emojis:🤓☝️. So if i said 'actually today is tuesday.' you would respond with 'actually today is tuesday. 🤓☝️'"
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

def build_prompt(user_message):
    """Build the final prompt to send to the AI, including personality."""
    return f"{AI_PERSONALITY}\n\nUser: {user_message}\nN0rm:"

def send_to_ai(prompt):
    """Sends the prompt to the Flask AI endpoint and returns the response."""
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
    last_checked_time = "2000-01-01T00:00:00"  # far in the past

    print("AI listener has started. Listening for messages...")

    while True:
        db = helpers.load_db()
        new_msgs = get_new_messages(db, last_checked_time)

        for msg in new_msgs:
            prompt = build_prompt(msg["content"])
            ai_response = send_to_ai(prompt)
            reply_to_message(db, msg, ai_response)

            # Update last checked timestamp
            if msg["timestamp"] > last_checked_time:
                last_checked_time = msg["timestamp"]

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main_loop()
