import requests

PROMPT = "whats 2+2, and tell me a quick knock knock joke. KEEP IT SHORT"
resp = requests.post(
    "http://theotherone.dev:5007/generate",
    headers={"X-API-Key": ")@W^utYCh:2A|RR(bT%_0!nhvLjP{tD|L:Lo.x*P:ouncm[G'5=w]yMpEPJ@c7D"},
    json={"prompt": PROMPT}
)

print(resp.json().get("response", ""))