"""
PulsePath AI service – Flask 3.0
Endpoints:
  POST /sentiment   {text: "..."}                → {label, confidence}
  POST /stt         multipart/form-data (audio)  → {transcript}
  POST /tts         {text: "..."}                → audio/wav bytes
"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io, joblib, tensorflow as tf
import soundfile as sf
import torchaudio                     # for TTS (e.g. Coqui TTS)

app = Flask(__name__)
CORS(app)

tok   = joblib.load("model/tokenizer.joblib")
enc   = joblib.load("model/label_encoder.joblib")
model = tf.keras.models.load_model("model/sentiment.h5")

# ---- helpers -----------------------------------------------------------
def classify(text: str):
    seq = tok.texts_to_sequences([text])
    pad = tf.keras.preprocessing.sequence.pad_sequences(seq, maxlen=120)
    probs = model(pad).numpy()[0]
    return enc.inverse_transform([probs.argmax()])[0], float(probs.max())

# ---- routes ------------------------------------------------------------
@app.post("/sentiment")
def sentiment():
    label, conf = classify(request.json.get("text", ""))
    return jsonify({"label": label, "confidence": conf})

@app.post("/stt")
def stt():
    audio = request.files["audio"].stream.read()
    # placeholder – swap with vosk, whisper, etc.
    transcript = "<dummy transcript>"
    return jsonify({"transcript": transcript})

@app.post("/tts")
def tts():
    text = request.json.get("text", "")
    wav, sr = torchaudio.pipelines.TTS_TACOTRON2_WAVERNN_GRIFFIN_LIM.get_sample(text)
    buf = io.BytesIO()
    sf.write(buf, wav.numpy().T, sr, format="WAV")
    buf.seek(0)
    return send_file(buf, mimetype="audio/wav")

@app.get("/healthz")
def healthz():
    return "ok", 200

if __name__ == "__main__":
    app.run(port=6000)
