from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io, joblib, tensorflow as tf, soundfile as sf
from tts import synthesize
import logging
import base64
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import os
import wave
from vosk import Model, KaldiRecognizer
import json
import openai
from dotenv import load_dotenv
import traceback
import time
import random
import re
import requests
from typing import Dict, List, Optional
import geocoder
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://127.0.0.1:5173"])

# JWT Configuration
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "your-secret-key")  # Change in production
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

# Initialize rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Initialize Vosk model with absolute path
model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model", "vosk-model-small-en-us-0.15")
try:
    model = Model(model_path)
    logger.info(f"Successfully loaded Vosk model from {model_path}")
except Exception as e:
    logger.error(f"Failed to load Vosk model: {e}")
    raise

try:
    tok = joblib.load("model/tokenizer.joblib")
    enc = joblib.load("model/label_encoder.joblib")
    model = tf.keras.models.load_model("model/sentiment.h5")
except Exception as e:
    logger.error(f"Failed to load models: {e}")
    raise

# User storage helpers
USERS_FILE = "model/users.json"
def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

CHAT_HISTORY_DIR = "model/chat_histories"
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)

def get_history_path(username):
    return os.path.join(CHAT_HISTORY_DIR, f"{username}.json")

def load_chat_history(username):
    try:
        with open(get_history_path(username), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_chat_history(username, history):
    with open(get_history_path(username), "w") as f:
        json.dump(history, f)

MOOD_HISTORY_DIR = "model/mood_histories"
os.makedirs(MOOD_HISTORY_DIR, exist_ok=True)

def get_mood_path(username):
    return os.path.join(MOOD_HISTORY_DIR, f"{username}.json")

def load_mood_history(username):
    try:
        with open(get_mood_path(username), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_mood_history(username, history):
    with open(get_mood_path(username), "w") as f:
        json.dump(history, f)

def classify(text):
    seq = tok.texts_to_sequences([text])
    pad = tf.keras.preprocessing.sequence.pad_sequences(seq, maxlen=120)
    probs = model(pad)[0].numpy()
    return enc.inverse_transform([probs.argmax()])[0], float(probs.max())

def validate_text(text: str) -> bool:
    return bool(text and len(text.strip()) > 0)

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

PROMPT_TEMPLATES = [
    # 1. Default balanced therapist
    (
        "You are an empathetic, evidence-based mental-health coach. "
        "For every user message you will:\n"
        "  • Validate the emotion they express.\n"
        "  • Offer ONE practical technique rooted in CBT, DBT, or mindfulness.\n"
        "  • Encourage a small action they can complete within 10 minutes.\n"
        "Avoid repeating questions, and never give generic platitudes. "
        "Use the user's current sentiment ({sentiment}) as additional context."
    ),
    # 2. Strength-focused coach
    (
        "Act as a strengths-based therapist who highlights the user's existing "
        "resources and resilience factors. After reflecting their feeling "
        "({sentiment}), identify at least one personal strength or past success "
        "they can leverage now, and map it to a concrete step."
    ),
    # 3. Mindfulness teacher
    (
        "You are a mindfulness instructor.   Each reply contains:\n"
        "  1) A 30-second grounding or breathing exercise.\n"
        "  2) A question inviting brief reflection.\n"
        "  3) A link or app suggestion for deeper practice.\n"
        "Tailor tone to the user's sentiment ({sentiment})."
    ),
    # 4. Crisis-aware helper
    (
        "You are a crisis-aware mental-health assistant. "
        "If the user's sentiment is negative or overwhelmed, begin with a gentle "
        "safety check (one sentence). Provide local or international hot-line info "
        "only if user hints at self-harm. Otherwise, deliver grounding tips and "
        "resource links. Never mention diagnosis.  Current sentiment: {sentiment}."
    ),
    # 5. CBT thought-challenger
    (
        "Act as a CBT practitioner.   For each message:\n"
        "  • Identify potential unhelpful thought patterns.\n"
        "  • Ask one Socratic question to challenge the thought.\n"
        "  • Suggest a short written exercise (thought record, evidence table, etc.).\n"
        "Adjust empathy level according to {sentiment}."
    ),
    # 6. Somatic approach
    (
        "You are a somatic therapist focusing on the body-mind connection. "
        "Offer one body-based regulation technique (e.g., progressive muscle "
        "relaxation, vagal breathing, gentle stretching) that fits the user's "
        "current emotional state ({sentiment}).  Describe it in 2–3 steps."
    ),
    # 7. Motivational interviewing
    (
        "Respond using motivational-interviewing style: express empathy, "
        "develop discrepancy, roll with resistance, support self-efficacy. "
        "Ask one open question, reflect once, and affirm a strength. "
        "Tone: warm, collaborative, matching the user's sentiment ({sentiment})."
    ),
    # 8. Self-compassion trainer
    (
        "You teach self-compassion. Gently mirror the user's emotion ({sentiment}), "
        "then guide them through a short self-kindness statement and a common-"
        "humanity reminder.  End with a soothing action (e.g., hand on heart)."
    ),
    # 9. ACT (Acceptance & Commitment) guide
    (
        "You are an ACT therapist helping the user accept emotions and move toward "
        "values. Briefly label the feeling ({sentiment}), suggest a defusion "
        "exercise, and ask which personal value they'd like to honor next."
    ),
    # 10. Brief solution-focused coach
    (
        "Act as a solution-focused brief therapist. "
        "After a one-sentence empathy reflection ({sentiment}), ask the Miracle "
        "Question or Scaling Question, then highlight one small next step."
    ),
    # 11. Parenting-oriented support
    (
        "You are a parenting stress coach. Validate the parent's emotion "
        "({sentiment}), suggest a coping tip that can be done while watching kids, "
        "and provide a kid-friendly mindfulness activity link."
    ),
    # 12. Student stress helper
    (
        "You support students with academic stress. Recognize the emotion "
        "({sentiment}), share a study or time-management tip, and encourage "
        "a brief self-care break."
    ),
    # 13. Sleep hygiene mentor
    (
        "You focus on sleep hygiene. If sentiment is tired or anxious, recommend "
        "one science-backed habit for better sleep (lighting, caffeine cutoff, "
        "screen curfew). Highlight why it helps physiologically."
    ),
    # 14. Gratitude reframer
    (
        "You help users cultivate gratitude. After validating their emotion "
        "({sentiment}), prompt them to name one thing they appreciate today, and "
        "explain the mental-health benefit of gratitude practice."
    ),
    # 15. Habit-tracking coach
    (
        "You are a tiny-habits coach. Reflect the user's mood ({sentiment}), then "
        "offer a micro-habit they can 'attach' to an existing daily routine. "
        "Example: 'After I brush my teeth, I will take 2 deep breaths.'"
    ),
]

template_map = {
    "negative": PROMPT_TEMPLATES[0],   # empathetic therapist
    "overwhelmed": PROMPT_TEMPLATES[3],  # crisis-aware
    "positive": PROMPT_TEMPLATES[1],   # strengths-focused
    "happy": PROMPT_TEMPLATES[1],      # strengths-focused
    "sad": PROMPT_TEMPLATES[0],        # empathetic therapist
    "anxious": PROMPT_TEMPLATES[2],    # mindfulness
    "angry": PROMPT_TEMPLATES[5],      # somatic
    "excited": PROMPT_TEMPLATES[14],   # habit-tracking/positive
    "neutral": PROMPT_TEMPLATES[0],    # default
}

FRIENDLY_PATTERNS = [
    r"\bhi\b|\bhello\b|\bhey\b|\bgood morning\b|\bgood afternoon\b|\bgood evening\b",
    r"\bthank(s| you| u)?\b|\bappreciate\b|\bgrateful\b",
    r"\bbye\b|\bgoodbye\b|\bsee you\b|\btake care\b|\blater\b|\bciao\b|\badios\b"
]
FRIENDLY_RESPONSES = [
    "You're very welcome! If you need anything else, I'm here for you.",
    "Hi there! How can I support you today?",
    "Hello! I'm here whenever you need to talk.",
    "Take care! Remember, I'm always here if you want to chat.",
    "Goodbye! Wishing you a peaceful day.",
    "Thank you for your kind words! Let me know if you need anything else."
]

def is_friendly_message(text):
    text = text.lower()
    return any(re.search(pat, text) for pat in FRIENDLY_PATTERNS)

SENTIMENT_KEYWORDS = {
    "anxious": ["stressed", "anxious", "worried", "nervous", "overwhelmed", "panic", "afraid", "scared"],
    "sad": ["sad", "down", "depressed", "unhappy", "hopeless", "cry"],
    "angry": ["angry", "mad", "furious", "irritated", "annoyed", "frustrated", "resentful", "upset", "bothered"],
    "happy": ["happy", "joyful", "excited", "glad", "content", "pleased"],
    "overwhelmed": ["overwhelmed", "burned out", "too much", "can't handle", "exhausted", "swamped", "burdened", "drowning"],
}

SENTIMENT_PRIORITY = ["overwhelmed", "angry", "anxious", "sad", "happy"]

def gpt4_sentiment(text):
    prompt = (
        "Classify the sentiment of the following message as one of: happy, sad, angry, anxious, excited, neutral, or overwhelmed. "
        "Respond in the format: label (confidence%), e.g., happy (95%).\n"
        "If the message contains clear emotional words, never return 'neutral'.\n"
        "Always pick the strongest emotion if multiple are present.\n"
        "Examples:\n"
        "Message: I feel so down today.\nOutput: sad (90%)\n"
        "Message: I'm really excited for my trip!\nOutput: excited (98%)\n"
        "Message: I'm just okay.\nOutput: neutral (80%)\n"
        "Message: I'm feeling very stressed about school.\nOutput: anxious (95%)\n"
        "Message: Everything is too much, I can't handle it.\nOutput: overwhelmed (97%)\n"
        "Message: I'm so angry at my friend.\nOutput: angry (92%)\n"
        "Message: I'm feeling annoyed with the amount of work I have to do recently. It's been so overwhelming. How can I calm myself down.\nOutput: overwhelmed (95%)\n"
        "Message: I'm frustrated and upset about my workload.\nOutput: angry (90%)\n"
        f"Message: {text}\nOutput:"
    )
    try:
        completion = openai.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[{"role": "system", "content": "You are a sentiment analysis assistant."}, {"role": "user", "content": prompt}],
            functions=[
                {
                    "name": "classify_sentiment",
                    "description": "Classify the sentiment of a message as one of: happy, sad, angry, anxious, excited, neutral, or overwhelmed. Return a confidence score (0-1).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "label": {
                                "type": "string",
                                "enum": ["happy", "sad", "angry", "anxious", "excited", "neutral", "overwhelmed"],
                                "description": "The sentiment label."
                            },
                            "confidence": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                                "description": "Confidence score between 0 and 1."
                            }
                        },
                        "required": ["label", "confidence"]
                    }
                }
            ],
            function_call={"name": "classify_sentiment"},
            max_tokens=50,
            temperature=0
        )
        args = completion.choices[0].message.function_call.arguments
        import json as _json
        result = _json.loads(args)
        label = result.get("label", "neutral")
        conf = float(result.get("confidence", 0.8))
        # Fallback heuristic: if label is neutral but text contains strong emotion words, pick strongest
        if label == "neutral":
            lowered = text.lower()
            found = []
            for k in SENTIMENT_PRIORITY:
                for w in SENTIMENT_KEYWORDS[k]:
                    if w in lowered:
                        found.append(k)
                        break
            if found:
                label = found[0]
                conf = 0.9
        return label, conf
    except Exception as e:
        logger.error(traceback.format_exc())
        return "neutral", 0.8

@app.post("/signup")
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    users = load_users()
    if username in users:
        return jsonify({"error": "Username already exists"}), 400
    users[username] = password  # For real apps, hash the password!
    save_users(users)
    return jsonify({"message": "Signup successful"}), 200

@app.post("/login")
def login():
    try:
        username = request.json.get("username")
        password = request.json.get("password")
        users = load_users()
        if username in users and users[username] == password:
            access_token = create_access_token(identity=username)
            return jsonify({"access_token": access_token}), 200
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.post("/sentiment")
@jwt_required()
@limiter.limit("10 per minute")
def sentiment():
    try:
        text = request.json.get("text", "")
        if not text:
            return jsonify({"error": "No text provided"}), 400
        label, conf = classify(text)
        return jsonify({"label": label, "confidence": conf})
    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.post("/tts")
@jwt_required()
@limiter.limit("20 per minute")
def tts():
    wav = synthesize(request.json.get("text", ""))
    return send_file(io.BytesIO(wav), mimetype="audio/wav")

@app.post("/stt")
@jwt_required()
@limiter.limit("20 per minute")
def speech_to_text():
    try:
        if not request.json or 'audio' not in request.json:
            return jsonify({"error": "No audio data provided"}), 400
            
        # Decode base64 audio data
        audio_data = base64.b64decode(request.json['audio'])
        
        # Save audio data to a temporary WAV file
        temp_file = "temp_input.wav"
        with open(temp_file, 'wb') as f:
            f.write(audio_data)
        
        # Open the WAV file
        wf = wave.open(temp_file, "rb")
        
        # Create recognizer
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)
        
        # Process audio
        transcript = ""
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = rec.Result()
                transcript += result
        
        # Get final result
        final_result = rec.FinalResult()
        transcript += final_result
        
        # Clean up
        wf.close()
        os.remove(temp_file)
        
        return jsonify({"text": transcript})
    except Exception as e:
        logger.error(f"Speech-to-text error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.get("/chat-history")
@jwt_required()
def chat_history():
    username = get_jwt_identity()
    history = load_chat_history(username)
    return jsonify({"history": history})

@app.get("/mood-history")
@jwt_required()
def mood_history():
    username = get_jwt_identity()
    history = load_mood_history(username)
    # Add emoji to each mood
    for m in history:
        m["emoji"] = MOOD_EMOJIS.get(m["sentiment"], "❓")
    return jsonify({"mood": history})

@app.post("/conversation")
@jwt_required()
@limiter.limit("20 per minute")
def conversation():
    try:
        username = get_jwt_identity()
        text = request.json.get("text", "")
        if not text:
            return jsonify({"error": "No text provided"}), 400
        # Friendly check
        if is_friendly_message(text):
            ai_response = random.choice(FRIENDLY_RESPONSES)
            label, conf = gpt4_sentiment(text)
            # Mood tracking
            mood_hist = load_mood_history(username)
            mood_hist.append({
                "timestamp": int(time.time()),
                "sentiment": label,
                "confidence": conf,
                "text": text
            })
            save_mood_history(username, mood_hist)
            # Save to chat history
            history = load_chat_history(username)
            history.append({"sender": "user", "text": text})
            history.append({"sender": "ai", "text": ai_response, "label": label, "confidence": conf})
            save_chat_history(username, history)
            return jsonify({
                "label": label,
                "confidence": conf,
                "ai_response": ai_response
            })
        # Use GPT-4 for sentiment (therapeutic)
        label, conf = gpt4_sentiment(text)
        # Mood tracking
        mood_hist = load_mood_history(username)
        mood_hist.append({
            "timestamp": int(time.time()),
            "sentiment": label,
            "confidence": conf,
            "text": text
        })
        save_mood_history(username, mood_hist)
        # Use GPT-4 for advanced response
        history = load_chat_history(username)
        chat_context = "\n".join([
            f"User: {msg['text']}" if msg['sender'] == 'user' else f"AI: {msg['text']}" for msg in history[-10:]
        ])
        last_ai = next((msg['text'] for msg in reversed(history) if msg['sender'] == 'ai'), None)
        # Choose system prompt based on sentiment
        system_prompt = template_map.get(label, random.choice(PROMPT_TEMPLATES)).format(sentiment=label)
        user_prompt = f"User: {text}\nSentiment: {label}"
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        if chat_context:
            messages.append({"role": "user", "content": chat_context})
        if last_ai:
            messages.append({"role": "assistant", "content": last_ai})
        messages.append({"role": "user", "content": user_prompt})
        try:
            completion = openai.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=300,
                temperature=0.85
            )
            ai_response = completion.choices[0].message.content.strip()
            # If the AI response is too similar to the last, append a random fallback
            if last_ai and ai_response.lower().strip() == last_ai.lower().strip():
                ai_response += "\n" + random.choice(FALLBACKS)
        except Exception as e:
            logger.error(traceback.format_exc())
            ai_response = random.choice(FALLBACKS)
        # Save to chat history
        history.append({"sender": "user", "text": text})
        history.append({"sender": "ai", "text": ai_response, "label": label, "confidence": conf})
        save_chat_history(username, history)
        return jsonify({
            "label": label,
            "confidence": conf,
            "ai_response": ai_response
        })
    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.post("/delete-history")
@jwt_required()
def delete_history():
    username = get_jwt_identity()
    try:
        save_chat_history(username, [])
        save_mood_history(username, [])  # Also clear mood history
        return jsonify({"message": "Chat history deleted."})
    except Exception as e:
        logger.error(f"Delete history error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.get("/healthz")
def healthz(): return "ok", 200

FALLBACKS = [
    # --- quick grounding ideas
    "Here's a grounding trick: look around and name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste. It helps bring you back to the present.",
    "Try box-breathing: inhale 4 sec, hold 4 sec, exhale 4 sec, hold 4 sec. Repeat for a minute to calm your nervous system.",
    "Splash cool water on your face or hold an ice cube for a moment—temperature change can interrupt spiralling thoughts.",
    # --- mindful movement / body
    "Stand up, roll your shoulders, and do a gentle stretch toward the ceiling. Movement releases tension stored in muscles.",
    "If you can, step outside for a 5-minute walk. Even brief sunlight and fresh air can lift mood.",
    "Put on one song that makes you feel safe or nostalgic and sway or tap along—micro-movement counts as self-soothing.",
    # --- journaling / thought reframing
    "Grab a notebook and free-write whatever's on your mind for 3 minutes. No judging, just dump the thoughts to lighten the load.",
    "List three tiny wins from today—even 'I got out of bed' counts. Small acknowledgements train the brain toward gratitude.",
    "Draw a quick comic of your anxious thought—seeing it on paper often shrinks its power.",
    # --- social connection
    "Send a short voice memo to a friend: 'Hey, thinking of you.' Human connection is a proven mood buffer.",
    "If possible, hug a pet or even a pillow—pressure on the chest area can trigger oxytocin release.",
    "Text 'HELLO' to 741-741 (US) to connect with a trained crisis counsellor if feelings get overwhelming. International list: https://findahelpline.com",  # keep link plain-text
    # --- digital tools / apps
    "Open a mindfulness app like Insight Timer, Calm, or Headspace and try a 3-minute body scan.",
    "Play a nature sound (rain, waves) on YouTube or a white-noise app; rhythmic sounds can slow heart rate.",
    "Try the free CBT thought record at 'moodtools' (iOS/Android) to challenge unhelpful beliefs.",
    # --- lifestyle habits
    "Sip a glass of water and notice the temperature and taste—hydration and mindfulness in one step.",
    "Have you eaten recently? A quick protein-rich snack (nuts, yogurt) can stabilize mood swings caused by blood-sugar dips.",
    "If it's night, dim screens and lower lights 30 min before bed—quality sleep is the best natural mood enhancer.",
    # --- professional help reminder
    "Remember it's okay to seek professional support. A single therapy session can provide tailored coping skills.",
    "If thoughts of self-harm arise, call 988 in the US or your local crisis number immediately—you deserve help right now.",
    # --- perspective / reassurance
    "Emotions are data, not directives. They tell us something needs attention; they don't dictate your worth.",
    "You've survived 100% of your hardest days so far—this feeling is temporary, even if it's intense.",
    # --- breathing / visualization variants
    "Close your eyes and picture a safe place—somewhere you've felt calm. Imagine its colors, sounds, and smells for one minute.",
    "Try 4-7-8 breathing: inhale 4 sec, hold 7 sec, exhale 8 sec. It engages the vagus nerve for relaxation.",
    # --- self-compassion nudge
    "Speak to yourself like you would to a close friend in the same situation. What kind words would you offer them?",
]


MOOD_EMOJIS = {
    "happy": "🙂",
    "sad": "🙁",
    "angry": "😠",
    "anxious": "😰",
    "excited": "😃",
    "neutral": "😐",
    "overwhelmed": "😞"
}

# Healthcare Provider APIs and Services
class HealthcareProviderService:
    def __init__(self):
        self.betterdoctor_api_key = os.environ.get("BETTERDOCTOR_API_KEY")
        self.healthcare_gov_api_key = os.environ.get("HEALTHCARE_GOV_API_KEY")
        self.zipcode_api_key = os.environ.get("ZIPCODE_API_KEY")
        
    def find_doctors(self, specialty: str, location: str, insurance: str = None) -> List[Dict]:
        """Find doctors using BetterDoctor API or fallback to healthcare.gov, or fallback demo data if no results."""
        try:
            providers = []
            if self.betterdoctor_api_key:
                providers = self._search_betterdoctor(specialty, location, insurance)
                if providers:
                    logger.info(f"Found {len(providers)} providers from BetterDoctor API for {specialty} in {location}")
                else:
                    logger.warning(f"No providers found from BetterDoctor API for {specialty} in {location}")
            else:
                providers = self._search_healthcare_gov(specialty, location)
                if providers:
                    logger.info(f"Found {len(providers)} providers from healthcare.gov for {specialty} in {location}")
                else:
                    logger.warning(f"No providers found from healthcare.gov for {specialty} in {location}")
            if not providers:
                providers = self._get_fallback_providers(specialty, location)
                logger.info(f"Returning fallback providers for {specialty} in {location}")
            return providers
        except Exception as e:
            logger.error(f"Error finding doctors: {e}")
            return self._get_fallback_providers(specialty, location)
    
    def _search_betterdoctor(self, specialty: str, location: str, insurance: str = None) -> List[Dict]:
        """Search BetterDoctor API for providers"""
        url = "https://api.betterdoctor.com/2016-03-01/doctors"
        params = {
            "query": specialty,
            "location": location,
            "user_key": self.betterdoctor_api_key,
            "limit": 10
        }
        if insurance:
            params["insurance_uid"] = insurance
            
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return self._format_betterdoctor_results(data)
        return []
    
    def _search_healthcare_gov(self, specialty: str, location: str) -> List[Dict]:
        """Search healthcare.gov API for providers"""
        url = "https://data.healthcare.gov/resource/7npc-6fac.json"
        params = {
            "$where": f"provider_type LIKE '%{specialty}%' AND city LIKE '%{location}%'",
            "$limit": 10
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return self._format_healthcare_gov_results(data)
        return []
    
    def _get_fallback_providers(self, specialty: str, location: str) -> List[Dict]:
        """Fallback provider data for demo purposes"""
        return [
            {
                "name": f"Dr. {specialty.title()} Specialist",
                "specialty": specialty,
                "location": location,
                "rating": 4.5,
                "accepts_insurance": True,
                "next_available": "2024-01-15",
                "estimated_cost": "$150-200",
                "phone": "(555) 123-4567"
            },
            {
                "name": f"Dr. {specialty.title()} Expert",
                "specialty": specialty,
                "location": location,
                "rating": 4.8,
                "accepts_insurance": True,
                "next_available": "2024-01-16",
                "estimated_cost": "$180-250",
                "phone": "(555) 987-6543"
            }
        ]
    
    def _format_betterdoctor_results(self, data: Dict) -> List[Dict]:
        """Format BetterDoctor API results"""
        providers = []
        for doctor in data.get("data", []):
            providers.append({
                "name": f"Dr. {doctor.get('profile', {}).get('first_name', '')} {doctor.get('profile', {}).get('last_name', '')}",
                "specialty": ", ".join([p.get("name", "") for p in doctor.get("specialties", [])]),
                "location": f"{doctor.get('practices', [{}])[0].get('visit_address', {}).get('city', '')}, {doctor.get('practices', [{}])[0].get('visit_address', {}).get('state', '')}",
                "rating": doctor.get("ratings", [{}])[0].get("rating", 0),
                "accepts_insurance": bool(doctor.get("insurances")),
                "next_available": "2024-01-15",  # Would need scheduling API
                "estimated_cost": "$150-200",
                "phone": doctor.get("practices", [{}])[0].get("phones", [{}])[0].get("number", "")
            })
        return providers
    
    def _format_healthcare_gov_results(self, data: List[Dict]) -> List[Dict]:
        """Format healthcare.gov API results"""
        providers = []
        for provider in data:
            providers.append({
                "name": provider.get("provider_name", "Unknown Provider"),
                "specialty": provider.get("provider_type", "General"),
                "location": f"{provider.get('city', '')}, {provider.get('state', '')}",
                "rating": 4.0,
                "accepts_insurance": True,
                "next_available": "2024-01-15",
                "estimated_cost": "$120-180",
                "phone": provider.get("phone", "")
            })
        return providers

class InsuranceService:
    def __init__(self):
        self.healthcare_gov_api_key = os.environ.get("HEALTHCARE_GOV_API_KEY")
    
    def check_coverage(self, insurance_provider: str, service: str) -> Dict:
        """Check insurance coverage for specific services"""
        # This would integrate with insurance APIs
        # For now, return mock data
        coverage_data = {
            "covered": True,
            "copay": "$25",
            "deductible_applies": True,
            "prior_authorization_required": False,
            "network_status": "in-network",
            "estimated_cost": "$25-50"
        }
        return coverage_data
    
    def estimate_costs(self, service: str, location: str, insurance: str = None) -> Dict:
        """Estimate healthcare costs"""
        # This would integrate with cost estimation APIs
        cost_ranges = {
            "therapy": {"min": 80, "max": 200, "avg": 120},
            "psychiatry": {"min": 150, "max": 300, "avg": 200},
            "primary_care": {"min": 50, "max": 150, "avg": 100},
            "specialist": {"min": 100, "max": 250, "avg": 175}
        }
        
        service_key = service.lower().replace(" ", "_")
        if service_key in cost_ranges:
            costs = cost_ranges[service_key]
            return {
                "service": service,
                "location": location,
                "cost_range": f"${costs['min']}-${costs['max']}",
                "average_cost": f"${costs['avg']}",
                "insurance_discount": "20-40%" if insurance else "0%"
            }
        return {"service": service, "cost_range": "$100-300", "average_cost": "$200"}

class SymptomAnalyzer:
    def __init__(self):
        self.openai_client = openai
    
    def analyze_symptoms(self, symptoms: str, user_context: str = "") -> Dict:
        """Analyze symptoms using AI and provide recommendations"""
        try:
            prompt = f"""
            Analyze the following symptoms and provide medical guidance:
            
            Symptoms: {symptoms}
            User Context: {user_context}
            
            Provide a structured response with:
            1. Possible conditions (with confidence levels)
            2. Recommended provider types
            3. Urgency level (low/medium/high)
            4. Self-care recommendations
            5. When to seek immediate care
            
            Format as JSON with these fields:
            - possible_conditions: list of conditions with confidence
            - recommended_providers: list of provider types
            - urgency_level: string
            - self_care_tips: list of tips
            - seek_care_when: string
            - disclaimer: string
            """
            
            response = self.openai_client.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            # Parse the response
            content = response.choices[0].message.content
            try:
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    return self._parse_ai_response(content)
            except:
                return self._parse_ai_response(content)
                
        except Exception as e:
            logger.error(f"Error analyzing symptoms: {e}")
            return self._get_fallback_analysis(symptoms)
    
    def _parse_ai_response(self, content: str) -> Dict:
        """Parse AI response into structured format"""
        return {
            "possible_conditions": ["General consultation recommended"],
            "recommended_providers": ["Primary Care Physician"],
            "urgency_level": "low",
            "self_care_tips": ["Monitor symptoms", "Rest and hydrate"],
            "seek_care_when": "If symptoms worsen or persist for more than 3 days",
            "disclaimer": "This is not medical advice. Please consult a healthcare provider for proper diagnosis."
        }
    
    def _get_fallback_analysis(self, symptoms: str) -> Dict:
        """Fallback symptom analysis"""
        return {
            "possible_conditions": ["General consultation recommended"],
            "recommended_providers": ["Primary Care Physician"],
            "urgency_level": "low",
            "self_care_tips": ["Monitor symptoms", "Rest and hydrate"],
            "seek_care_when": "If symptoms worsen or persist",
            "disclaimer": "This is not medical advice. Please consult a healthcare provider."
        }

# Initialize services
healthcare_service = HealthcareProviderService()
insurance_service = InsuranceService()
symptom_analyzer = SymptomAnalyzer()

# Healthcare Provider Integration Endpoints
@app.post("/find-doctors")
@jwt_required()
@limiter.limit("10 per minute")
def find_doctors():
    """Find healthcare providers based on specialty and location"""
    try:
        data = request.get_json()
        specialty = data.get("specialty", "")
        location = data.get("location", "")
        insurance = data.get("insurance", None)
        
        if not specialty or not location:
            return jsonify({"error": "Specialty and location are required"}), 400
        
        providers = healthcare_service.find_doctors(specialty, location, insurance)
        
        return jsonify({
            "success": True,
            "providers": providers,
            "count": len(providers),
            "search_criteria": {
                "specialty": specialty,
                "location": location,
                "insurance": insurance
            }
        })
        
    except Exception as e:
        logger.error(f"Error finding doctors: {e}")
        return jsonify({"error": "Failed to find doctors"}), 500

@app.post("/check-insurance")
@jwt_required()
@limiter.limit("10 per minute")
def check_insurance():
    """Check insurance coverage for specific services"""
    try:
        data = request.get_json()
        insurance_provider = data.get("insurance_provider", "")
        service = data.get("service", "")
        
        if not insurance_provider or not service:
            return jsonify({"error": "Insurance provider and service are required"}), 400
        
        coverage = insurance_service.check_coverage(insurance_provider, service)
        
        return jsonify({
            "success": True,
            "coverage": coverage,
            "insurance_provider": insurance_provider,
            "service": service
        })
        
    except Exception as e:
        logger.error(f"Error checking insurance: {e}")
        return jsonify({"error": "Failed to check insurance coverage"}), 500

@app.post("/estimate-costs")
@jwt_required()
@limiter.limit("10 per minute")
def estimate_costs():
    """Estimate healthcare costs for services"""
    try:
        data = request.get_json()
        service = data.get("service", "")
        location = data.get("location", "")
        insurance = data.get("insurance", None)
        
        if not service or not location:
            return jsonify({"error": "Service and location are required"}), 400
        
        cost_estimate = insurance_service.estimate_costs(service, location, insurance)
        
        return jsonify({
            "success": True,
            "cost_estimate": cost_estimate
        })
        
    except Exception as e:
        logger.error(f"Error estimating costs: {e}")
        return jsonify({"error": "Failed to estimate costs"}), 500

@app.post("/analyze-symptoms")
@jwt_required()
@limiter.limit("5 per minute")
def analyze_symptoms():
    """Analyze symptoms using AI and provide recommendations"""
    try:
        data = request.get_json()
        symptoms = data.get("symptoms", "")
        user_context = data.get("user_context", "")
        
        if not symptoms:
            return jsonify({"error": "Symptoms are required"}), 400
        
        analysis = symptom_analyzer.analyze_symptoms(symptoms, user_context)
        
        return jsonify({
            "success": True,
            "analysis": analysis
        })
        
    except Exception as e:
        logger.error(f"Error analyzing symptoms: {e}")
        return jsonify({"error": "Failed to analyze symptoms"}), 500

@app.post("/healthcare-navigation")
@jwt_required()
@limiter.limit("5 per minute")
def healthcare_navigation():
    """Comprehensive healthcare navigation - combines symptom analysis, provider finding, and cost estimation"""
    try:
        data = request.get_json()
        symptoms = data.get("symptoms", "")
        location = data.get("location", "")
        insurance = data.get("insurance", None)
        user_context = data.get("user_context", "")
        
        if not symptoms or not location:
            return jsonify({"error": "Symptoms and location are required"}), 400
        
        # Step 1: Analyze symptoms
        symptom_analysis = symptom_analyzer.analyze_symptoms(symptoms, user_context)
        
        # Step 2: Find providers based on recommended provider types
        providers = []
        for provider_type in symptom_analysis.get("recommended_providers", []):
            found_providers = healthcare_service.find_doctors(provider_type, location, insurance)
            providers.extend(found_providers[:3])  # Limit to top 3 per provider type
        
        # Step 3: Estimate costs for recommended services
        cost_estimates = []
        for provider_type in symptom_analysis.get("recommended_providers", []):
            cost_estimate = insurance_service.estimate_costs(provider_type, location, insurance)
            cost_estimates.append(cost_estimate)
        
        return jsonify({
            "success": True,
            "symptom_analysis": symptom_analysis,
            "providers": providers[:10],  # Limit to top 10 providers
            "cost_estimates": cost_estimates,
            "next_steps": [
                "Review the symptom analysis and provider recommendations",
                "Contact providers to schedule appointments",
                "Check insurance coverage for recommended services",
                "Consider cost estimates when making decisions"
            ]
        })
        
    except Exception as e:
        logger.error(f"Error in healthcare navigation: {e}")
        return jsonify({"error": "Failed to provide healthcare navigation"}), 500

@app.get("/healthcare-resources")
@jwt_required()
def get_healthcare_resources():
    """Get general healthcare resources and information"""
    try:
        resources = {
            "crisis_hotlines": {
                "national_suicide_prevention": "988",
                "crisis_text_line": "Text HOME to 741741",
                "emergency": "911"
            },
            "mental_health_resources": {
                "nami": "https://www.nami.org/help",
                "mental_health_america": "https://www.mhanational.org/",
                "psychology_today": "https://www.psychologytoday.com/us/therapists"
            },
            "insurance_resources": {
                "healthcare_gov": "https://www.healthcare.gov/",
                "medicare": "https://www.medicare.gov/",
                "medicaid": "https://www.medicaid.gov/"
            },
            "provider_directories": {
                "betterdoctor": "https://betterdoctor.com/",
                "healthgrades": "https://www.healthgrades.com/",
                "zocdoc": "https://www.zocdoc.com/"
            }
        }
        
        return jsonify({
            "success": True,
            "resources": resources
        })
        
    except Exception as e:
        logger.error(f"Error getting healthcare resources: {e}")
        return jsonify({"error": "Failed to get healthcare resources"}), 500

if __name__ == "__main__":
    app.run(port=5000)
