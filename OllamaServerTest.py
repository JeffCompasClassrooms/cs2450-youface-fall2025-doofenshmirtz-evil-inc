from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
MODEL = "deepseek-r1:14b"

API_KEY = ")@W^utYCh:2A|RR(bT%_0!nhvLjP{tD|L:Lo.x*P:ouncm[G'5=w]yMpEPJ@c7D"

def require_api_key(req):
    key = req.headers.get("X-API-Key")
    return key == API_KEY

@app.route("/generate", methods=["POST"])
def generate():
    if not require_api_key(request):
        return jsonify({"error": "unauthorized"}), 401

    data = request.json or {}
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "no prompt provided"}), 400

    try:
        r = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=300
        )
        r.raise_for_status()
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5007)