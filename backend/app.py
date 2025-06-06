from flask import Flask, jsonify, request, send_file     
from flask_cors import CORS
import io, tempfile, numpy as np, wave                    

from audio.tts import speak, _tts                       
from audio.asr import _MODEL as whisper_model          
from nlp.sentiment import classify
from nlp.dialogue import reply as gen_reply

app = Flask(__name__)
CORS(app)

@app.get("/ping")
def ping():
    return jsonify(ok=True)

@app.post("/reply")
def ai_reply():
    data = request.get_json(force=True) or {}
    user_text = data.get("text", "").strip()
    if not user_text:
        return jsonify(error="text is required"), 400

    mood   = classify(user_text)
    answer = gen_reply(user_text, mood)
    return jsonify(mood=mood, reply=answer)


@app.post("/transcribe")
def transcribe():
    """
    Expects raw 16-kHz mono PCM WAV bytes (Content-Type: audio/wav).
    Returns: { "text": "what you said" }
    """
    audio_bytes = request.get_data()
    if not audio_bytes:
        return jsonify(error="wav body required"), 400

    # read WAV header → PCM int16 buffer
    with wave.open(io.BytesIO(audio_bytes)) as wf:
        if wf.getsampwidth() != 2 or wf.getframerate() != 16_000:
            return jsonify(error="16-kHz 16-bit mono WAV required"), 400
        pcm16 = wf.readframes(wf.getnframes())
    pcm = np.frombuffer(pcm16, np.int16).astype(np.float32) / 32768

    text = whisper_model.transcribe(pcm, fp16=False)["text"].strip()
    return jsonify(text=text)


@app.post("/speak")
def tts_endpoint():
    """
    JSON body: { "text": "hello world" }
    Returns: audio/wav (24-kHz mono float32)
    """
    data = request.get_json(force=True) or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify(error="text is required"), 400

    wav = _tts.tts(text)                       
    bio = io.BytesIO()
    with wave.open(bio, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)                     
        wf.setframerate(24_000)
        pcm16 = (np.array(wav) * 32767).astype(np.int16).tobytes()
        wf.writeframes(pcm16)
    bio.seek(0)
    return send_file(bio, mimetype="audio/wav")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
