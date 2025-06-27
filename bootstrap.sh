set -e
echo "▶️  Generating PulsePath project …"

# ---- helper -------------------------------------------------------------
write() { mkdir -p "$(dirname "$1")"; printf '%s\n' "${2:-}" > "$1"; }

# ---- root files ---------------------------------------------------------
write ".gitignore" \
'node_modules/
.next/
.env*
__pycache__/
*.py[cod]
venv/
target/
.DS_Store
.idea/
.vscode/'

write "README.md" "# PulsePath – AI Speech-to-Speech Therapist\n\n_Brand-new implementation inspired by MyHealthPal._"

write "docker-compose.yml" \
'version: "3.9"
services:
  ai:
    build: ./ai
    ports: ["6000:6000"]
  backend:
    build: ./backend
    ports: ["8080:8080"]
    environment:
      - AI_BASE_URL=http://ai:6000
  frontend:
    build: ./frontend
    ports: ["3000:3000"]'

# ---- AI (Flask) ---------------------------------------------------------
write "ai/requirements.txt" \
'Flask==3.0.3
flask-cors==4.0.0
tensorflow==2.16.1
joblib==1.4.2
soundfile==0.12.1
google-cloud-texttospeech==2.17.0'

write "ai/app.py" "$(cat <<'PY'
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io, joblib, tensorflow as tf, soundfile as sf
from tts import synthesize

app = Flask(__name__)
CORS(app)

tok   = joblib.load("model/tokenizer.joblib")
enc   = joblib.load("model/label_encoder.joblib")
model = tf.keras.models.load_model("model/sentiment.h5")

def classify(text):
    seq = tok.texts_to_sequences([text])
    pad = tf.keras.preprocessing.sequence.pad_sequences(seq, maxlen=120)
    probs = model(pad)[0].numpy()
    return enc.inverse_transform([probs.argmax()])[0], float(probs.max())

@app.post("/sentiment")
def sentiment():
    label, conf = classify(request.json.get("text", ""))
    return jsonify({"label": label, "confidence": conf})

@app.post("/tts")
def tts():
    wav = synthesize(request.json.get("text", ""))
    return send_file(io.BytesIO(wav), mimetype="audio/wav")

@app.get("/healthz")
def healthz(): return "ok", 200

if __name__ == "__main__":
    app.run(port=6000)
PY
)"

write "ai/tts.py" "$(cat <<'PY'
from google.cloud import texttospeech
client = texttospeech.TextToSpeechClient()

def synthesize(text: str) -> bytes:
    input_ = texttospeech.SynthesisInput(text=text)
    voice  = texttospeech.VoiceSelectionParams(
        language_code="en-US", name="en-US-JennyNeural")
    audio_cfg = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16)
    return client.synthesize_speech(input_, voice, audio_cfg).audio_content
PY
)"

# ---- Spring backend -----------------------------------------------------
write "backend/pom.xml" '<project><!-- minimal pom; add spring-boot-starter-web, etc. --></project>'

write "backend/src/main/resources/application.properties" \
'openai.key=${OPENAI_API_KEY}
google.places.key=${GOOGLE_PLACES_KEY}
server.port=8080'

backend_java_dir="backend/src/main/java/com/pulsepath"
mkdir -p "$backend_java_dir"

write "$backend_java_dir/PulsepathApplication.java" \
'package com.pulsepath;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.SpringApplication;
@SpringBootApplication
public class PulsepathApplication {
  public static void main(String[] args){ SpringApplication.run(PulsepathApplication.class, args); }
}'

write "$backend_java_dir/openai/OpenAiService.java" "$(cat <<'JAVA'
package com.pulsepath.openai;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import java.util.Map;
@Service
public class OpenAiService {
  @Value("${openai.key}") private String apiKey;
  private final RestTemplate http = new RestTemplate();
  public String chat(String prompt){
    HttpHeaders h=new HttpHeaders(); h.setBearerAuth(apiKey); h.setContentType(MediaType.APPLICATION_JSON);
    Map<String,Object> body=Map.of("model","gpt-4o-mini","messages",new Object[]{
      Map.of("role","system","content","You are a licensed physician."),
      Map.of("role","user","content",prompt)
    });
    var resp=http.postForEntity("https://api.openai.com/v1/chat/completions",
                                new HttpEntity<>(body,h), Map.class);
    return ((Map<?,?>)((java.util.List<?>)resp.getBody().get("choices")).get(0))
           .get("message").toString();
  }
}
JAVA
)"

write "$backend_java_dir/chat/DoctorController.java" "$(cat <<'JAVA'
package com.pulsepath.chat;
import com.pulsepath.openai.OpenAiService;
import org.springframework.web.bind.annotation.*;
@RestController @RequestMapping("/api/chat/doctor") @CrossOrigin(origins="*")
public class DoctorController{
  private final OpenAiService ai;
  record Req(String text){} record Res(String reply){}
  DoctorController(OpenAiService ai){this.ai=ai;}
  @PostMapping public Res advise(@RequestBody Req r){ return new Res(ai.chat(r.text())); }
}
JAVA
)"

write "$backend_java_dir/chat/ChatController.java" "$(cat <<'JAVA'
package com.pulsepath.chat;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
@RestController @RequestMapping("/api/chat") @CrossOrigin(origins="*")
public class ChatController{
  private final RestTemplate http=new RestTemplate();
  @Value("${ai.base-url:http://localhost:6000}") String ai;
  record Msg(String text){}
  @PostMapping("/sentiment")
  public ResponseEntity<String> sentiment(@RequestBody Msg b){
    HttpHeaders h=new HttpHeaders(); h.setContentType(MediaType.APPLICATION_JSON);
    return http.postForEntity(ai+"/sentiment", new HttpEntity<>(b,h), String.class);
  }
}
JAVA
)"

write "$backend_java_dir/clinic/ClinicController.java" "$(cat <<'JAVA'
package com.pulsepath.clinic;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
@RestController @RequestMapping("/api/clinics") @CrossOrigin(origins="*")
public class ClinicController {
  @Value("${google.places.key}") String key;
  private final RestTemplate http=new RestTemplate();
  @GetMapping
  public String nearby(@RequestParam double lat,@RequestParam double lng,@RequestParam(defaultValue="5000") int radius){
    return http.getForObject(String.format(
      "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%f,%f&radius=%d&type=hospital&key=%s",
      lat,lng,radius,key), String.class);
  }
}
JAVA
)"

# ---- Next frontend ------------------------------------------------------
write "frontend/package.json" \
'{ "name":"pulsepath-frontend","private":true,"scripts":{"dev":"next dev"},"dependencies":{"next":"14.2.3","react":"18.3.1","react-dom":"18.3.1","tailwindcss":"^3.4.4"} }'

write "frontend/next.config.js" \
"module.exports = { async rewrites(){ return [{ source: '/api/proxy/:path*', destination: 'http://localhost:8080/api/:path*' }] } }"

write "frontend/tailwind.config.ts" "$(cat <<'TS'
import type { Config } from 'tailwindcss'
export default <Config>{
  content:['./src/**/*.{ts,tsx}','./app/**/*.{ts,tsx}'],
  theme:{extend:{colors:{brand:{500:'#8b5cf6',600:'#7c3aed',700:'#6d28d9'}},fontFamily:{sans:['Inter','sans-serif']}}},
  plugins:[],
}
TS
)"

write "frontend/postcss.config.js" 'module.exports={plugins:{tailwindcss:{},autoprefixer:{}}}'

# ---- frontend/public assets --------
mkdir -p frontend/public && touch frontend/public/{favicon.ico,logo.svg,hero-illustration.png}

# ---- frontend src structure --------
write "frontend/src/app/layout.tsx" \
"import '@/styles.css';\nexport default function RootLayout({children}:{children:React.ReactNode}){\n return (<html lang='en'><body>{children}</body></html>)}"

write "frontend/src/app/page.tsx" \
"export default function Home(){return <main className='p-8 text-3xl'>Welcome to PulsePath</main>}"

write "frontend/src/components/Navbar.tsx" "$(cat <<'TSX'
'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
const nav=[{href:'/',label:'Home'},{href:'/doctor',label:'Doctor AI'},
           {href:'/therapist',label:'Therapist AI'},{href:'/clinics',label:'Clinics'}]
export default function Navbar(){
  const path=usePathname()
  return(<header className="sticky top-0 bg-white/80 backdrop-blur">
    <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
      <Link href="/" className="flex items-center text-xl font-bold">
        <img src="/logo.svg" className="mr-2 h-7 w-7" alt=""/>PulsePath
      </Link>
      <ul className="flex gap-6 text-sm">{nav.map(n=>(
        <li key={n.href}>
          <Link href={n.href} className={path===n.href?'text-brand-700':'text-gray-700 hover:text-brand-600'}>
            {n.label}
          </Link>
        </li>))}</ul>
    </nav></header>)
}
TSX
)"

# hooks, pages, etc. abbreviated for brevity
echo "✅  All files written. Next steps:
"
