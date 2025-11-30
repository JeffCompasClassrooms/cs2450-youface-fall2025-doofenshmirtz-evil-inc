import time
import requests
from db import helpers, users

API_URL = "http://127.0.0.1:5007/generate"  # or your public IP
API_KEY = ")@W^utYCh:2A|RR(bT%_0!nhvLjP{tD|L:Lo.x*P:ouncm[G'5=w]yMpEPJ@c7D"

BOT_NAME = "norm"

def get_new_messages_for_norm(db):
    """Return a list of unread/new messages sent TO norm."""
    messages = users.get_incoming_messages(db, BOT_NAME)
    return [m for m in messages if not m.get("handled", False)]

def call_ai(prompt):
    r = requests.post(
        API_URL,
        headers={"X-API-Key": API_KEY},
        json={"prompt": prompt},
        timeout=60
    )
    data = r.json()
    return data.get("response", "")

def bot_loop():
    while True:
        db = helpers.load_db()

        new_messages = get_new_messages_for_norm(db)

        for msg in new_messages:
            sender = msg["sender"]
            prompt = msg["content"]

            # Ask the AI
            reply = call_ai(prompt)

            # Store AI reply
            users.send_message(db, BOT_NAME, sender, reply)

            # Mark message as handled
            msg["handled"] = True
            helpers.save_db(db)

        time.sleep(1)  # reduce CPU usage


if __name__ == "__main__":
    print("Starting Norm AI message watcher...")
    bot_loop()
