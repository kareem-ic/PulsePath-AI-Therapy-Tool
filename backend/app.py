from flask import Flask, jsonify, request
from flask_cors import CORS                      # NEW (optional but handy)

from audio.tts import speak                      # we’ll use later
from nlp.sentiment import classify               # NEW
from nlp.dialogue import reply as gen_reply      # NEW

app = Flask(__name__)
CORS(app)  # allow localhost:5173 React dev-server to call the API

@app.get("/ping")
def ping():
    return jsonify(ok=True)

# ──────────────────────────────────────────────────────────────
@app.post("/reply")                              # NEW
def ai_reply():
    """
    JSON body: { "text": "<user sentence>" }
    Returns:    { "mood": "negative", "reply": "…" }
    """
    data = request.get_json(force=True) or {}
    user_text = data.get("text", "").strip()
    if not user_text:
        return jsonify(error="text is required"), 400

    mood   = classify(user_text)                 # pos / neu / neg
    answer = gen_reply(user_text, mood)          # call Phi-3

    return jsonify(mood=mood, reply=answer)
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
