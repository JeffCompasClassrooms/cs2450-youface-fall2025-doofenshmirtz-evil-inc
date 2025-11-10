from flask import Flask, request, jsonify, Response
import requests
import json

app = Flask(__name__)
MODEL = "deepseek-r1:latest"

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json or {}
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "no prompt provided"}), 400

    try:
        # Use streaming mode
        with requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={"model": MODEL, "prompt": prompt},
            stream=True,
        ) as r:
            r.raise_for_status()
            full_text = ""
            for line in r.iter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if "response" in data:
                        full_text += data["response"]
                except json.JSONDecodeError:
                    continue

            return jsonify({"response": full_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5007)
