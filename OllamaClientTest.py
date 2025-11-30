import time
import requests
from db import helpers, users

API_URL = "http://127.0.0.1:5007/generate"
AI_USERNAME = "N0rm"
CHECK_INTERVAL = 3  # seconds

def get_new_messages(db, last_checked_time):
    """
    Returns all messages sent to Norm after last_checked_time.
    """
    all_messages = db.table('messages').all()
    new_msgs = []

    for msg in all_messages:
        if msg.get("receiver") == AI_USERNAME:
            timestamp = msg.get("timestamp")
            if timestamp > last_checked_time:
                new_msgs.append(msg)

    return new_msgs

def send_to_ai(prompt):
    """
    Sends the prompt to your Flask AI endpoint.
    """
    r = requests.post(API_URL, json={"prompt": prompt}, headers={
        "X-API-Key": ")@W^utYCh:2A|RR(bT%_0!nhvLjP{tD|L:Lo.x*P:ouncm[G'5=w]yMpEPJ@c7D"
    })

    try:
        data = r.json()
        return data.get("response") or str(data)
    except Exception as e:
        return f"The AI encountered an error: {e}"

def reply_to_message(db, original_msg, ai_text):
    """
    Inserts a new message from Norm in response to original_msg.
    """
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

    print("AI worker started. Listening for messages to Norm...")

    while True:
        db = helpers.load_db()
        new_msgs = get_new_messages(db, last_checked_time)

        for msg in new_msgs:
            prompt = msg["content"]
            ai_response = send_to_ai(prompt)
            reply_to_message(db, msg, ai_response)

            # Update last checked timestamp
            if msg["timestamp"] > last_checked_time:
                last_checked_time = msg["timestamp"]

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main_loop()
