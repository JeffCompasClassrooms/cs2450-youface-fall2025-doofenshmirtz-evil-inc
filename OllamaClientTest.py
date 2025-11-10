import requests
PROMPT = "tell me what 2+2 is equal to, and then tell me a knock knock joke. keep it short"
resp = requests.post("http://127.0.0.1:5007/generate", json={"prompt": PROMPT}, timeout=300)
print(resp.json())