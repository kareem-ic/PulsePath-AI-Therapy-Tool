# PulsePath AI Therapy Tool

A comprehensive AI-powered mental health therapy tool that provides empathetic, evidence-based responses through advanced natural language processing and sentiment analysis. **Now expanded with healthcare provider integration and medical navigation capabilities.**

## 🌟 Features

### Core Functionality
- **AI-Powered Conversations**: GPT-4 powered therapeutic responses with multiple therapeutic styles
- **Real-time Sentiment Analysis**: Advanced sentiment classification using OpenAI's function calling
- **Speech-to-Text**: Offline speech recognition using Vosk
- **Text-to-Speech**: Offline speech synthesis using pyttsx3
- **Mood Tracking**: Visual mood trend tracking with sentiment history
- **Chat History**: Persistent conversation history with sentiment labels
- **Multiple Therapeutic Approaches**: 12 different therapeutic styles including CBT, DBT, mindfulness, and more

### 🏥 Healthcare Navigation (NEW!)
- **AI Symptom Analysis**: Intelligent symptom assessment with urgency classification
- **Healthcare Provider Finder**: Find doctors, therapists, and specialists by location and specialty
  - **Fallback Demo Providers**: If the BetterDoctor API is unreachable or no API key is set, the app will always show demo providers so users never see an empty result.
  - **Enable Real Providers**: To use real provider data, obtain a BetterDoctor API key and set it in your backend environment (see below).
- **Insurance Coverage Checker**: Verify insurance coverage for specific services
- **Cost Estimation Engine**: Get transparent cost estimates for healthcare services
- **Comprehensive Healthcare Guidance**: End-to-end healthcare navigation with provider recommendations

### Technical Features
- **JWT Authentication**: Secure user authentication and session management
- **Rate Limiting**: API rate limiting to prevent abuse
- **CORS Support**: Cross-origin resource sharing for web frontend
- **Offline Capabilities**: Speech processing without external API dependencies
- **Responsive UI**: Modern, futuristic interface with animations and glassmorphism
- **Healthcare APIs Integration**: BetterDoctor, healthcare.gov, and insurance provider APIs (optional)

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Node.js 16+** and npm
- **OpenAI API Key** (for GPT-4 responses and sentiment analysis)
- **Modern web browser** with microphone access
- **Optional**: BetterDoctor API Key, healthcare.gov API access

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd PulsePath-AI-Therapy-Tool
```

2. **Set up the AI Backend:**
```bash
# Navigate to AI directory
cd ai

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

3. **Set up the React Frontend:**
```bash
# Navigate to frontend directory
cd ../frontend

# Install Node.js dependencies
npm install
```

4. **Configure Environment Variables:**
```bash
# In the ai directory, set these environment variables:
export OPENAI_API_KEY="your-openai-api-key"
export JWT_SECRET_KEY="your-secret-key"

# Optional healthcare provider APIs:
export BETTERDOCTOR_API_KEY="your-betterdoctor-api-key"
export HEALTHCARE_GOV_API_KEY="your-healthcare-gov-api-key"
export ZIPCODE_API_KEY="your-zipcode-api-key"
```

### Running the Application

1. **Start the AI Backend:**
```bash
# In the ai directory with venv activated
cd ai
source venv/bin/activate
python app.py
```
The backend will run on `http://localhost:5000`

2. **Start the React Frontend:**
```bash
# In the frontend directory
cd frontend
npm run dev
```
The frontend will run on `http://localhost:5173`

3. **Access the Application:**
Open your browser and navigate to `http://localhost:5173`

## 📖 How to Use

### Getting Started
1. **Sign Up/Login**: Create an account or log in with existing credentials
2. **Navigate to Conversation**: The conversation page is the default landing page after login
3. **Start Chatting**: Type your message and press Enter or use the microphone for voice input

### Features Guide

#### 🤖 AI Conversation
- **Therapeutic Responses**: The AI provides evidence-based mental health support
- **Sentiment-Aware**: Responses are tailored based on your current emotional state
- **Multiple Styles**: The AI adapts its therapeutic approach based on your needs
- **Crisis Resources**: Automatically provides crisis hotlines and resources when needed

#### 🎤 Voice Features
- **Voice Input**: Click the microphone button to speak your message
- **Voice Output**: Click the speaker button to hear AI responses
- **Offline Processing**: All speech processing happens locally for privacy

#### 📊 Mood Tracking
- **Visual Mood Bar**: See your current mood reflected in a color-coded bar
- **Sentiment Labels**: Each message shows the detected sentiment (happy, sad, anxious, etc.)
- **Mood History**: Track your emotional journey over time
- **Clear History**: Option to clear chat and mood history

#### 🏥 Healthcare Navigation (NEW!)
- **Symptom Analysis**: Describe your symptoms and get AI-powered analysis with urgency levels
- **Provider Search**: Find healthcare providers by specialty, location, and insurance
  - **Demo Providers**: If real provider APIs are unavailable, demo providers will always be shown.
  - **Enable Real Providers**: Set a valid BetterDoctor API key in your backend environment to enable real provider search.
- **Cost Estimation**: Get transparent cost estimates for healthcare services
- **Insurance Checking**: Verify coverage for specific medical services
- **Comprehensive Guidance**: Get complete healthcare navigation with provider recommendations

#### 🔧 Advanced Features
- **Chat History**: All conversations are saved and persist across sessions
- **Rate Limiting**: Built-in protection against excessive API usage
- **Secure Authentication**: JWT-based secure user sessions

### Therapeutic Approaches

The AI uses 12 different therapeutic styles:

1. **Default Balanced Therapist**: Evidence-based CBT/DBT techniques
2. **Strength-Focused Coach**: Highlights your existing resources and resilience
3. **Mindfulness Teacher**: Grounding exercises and breathing techniques
4. **Crisis-Aware Helper**: Safety checks and crisis resources
5. **CBT Thought-Challenger**: Cognitive behavioral therapy techniques
6. **Somatic Approach**: Body-mind connection and regulation
7. **Motivational Interviewing**: Collaborative, empathetic approach
8. **Self-Compassion Trainer**: Kindness and self-acceptance
9. **ACT Guide**: Acceptance and Commitment Therapy
10. **Solution-Focused Coach**: Brief, goal-oriented therapy
11. **Parenting Support**: Parent-specific stress management
12. **Student Stress Helper**: Academic stress and time management

## 🔧 API Endpoints

### Authentication
- `POST /signup` - Create new user account
- `POST /login` - Authenticate and get JWT token

### Core Features
- `POST /conversation` - Main conversation endpoint with AI
- `POST /sentiment` - Analyze text sentiment
- `POST /tts` - Convert text to speech
- `POST /stt` - Convert speech to text

### Healthcare Navigation (NEW!)
- `POST /analyze-symptoms` - AI-powered symptom analysis
- `POST /find-doctors` - Find healthcare providers (returns demo providers if API is unreachable)
- `POST /check-insurance` - Check insurance coverage
- `POST /estimate-costs` - Estimate healthcare costs
- `POST /healthcare-navigation` - Comprehensive healthcare guidance
- `GET /healthcare-resources` - Get healthcare resources and hotlines

### Data Management
- `GET /chat-history` - Retrieve conversation history
- `GET /mood-history` - Retrieve mood tracking data
- `POST /delete-history` - Clear chat and mood history

### System
- `GET /healthz` - Health check endpoint

## 🛠️ Development

### Project Structure
```
PulsePath-AI-Therapy-Tool/
├── ai/                     # Flask backend
│   ├── app.py             # Main Flask application
│   ├── requirements.txt   # Python dependencies
│   ├── model/             # ML models and data
│   └── venv/              # Python virtual environment
├── frontend/              # React frontend
│   ├── src/               # React source code
│   │   ├── App.jsx        # Main app component
│   │   ├── Conversation.jsx # AI conversation interface
│   │   ├── HealthcareNavigation.jsx # Healthcare features (NEW!)
│   │   ├── Login.jsx      # Login component
│   │   ├── Signup.jsx     # Signup component
│   │   ├── NavBar.jsx     # Navigation bar
│   │   ├── TTS.jsx        # Text-to-speech component
│   │   ├── STT.jsx        # Speech-to-text component
│   │   └── api.js         # API utilities
│   ├── package.json       # Node.js dependencies
│   └── vite.config.js     # Vite configuration
├── backend/               # Java backend (optional)
└── docker-compose.yml     # Docker configuration
```

### Technology Stack
- **Backend**: Flask (Python), TensorFlow, OpenAI GPT-4
- **Frontend**: React, Material-UI, Framer Motion
- **Speech**: Vosk (STT), pyttsx3 (TTS)
- **Healthcare APIs**: BetterDoctor (optional), healthcare.gov, insurance providers
- **Authentication**: JWT
- **Build Tool**: Vite

## 💰 Revenue Model & Business Potential

### Current Capabilities
- **AI-Powered Therapy**: Advanced mental health support with multiple therapeutic approaches
- **Healthcare Navigation**: Complete healthcare provider finder and cost estimation
- **Voice Interface**: Speech-to-speech therapy capabilities
- **Mood Tracking**: Comprehensive emotional wellness monitoring

### Monetization Opportunities
1. **Freemium Model**: Basic features free, premium for advanced healthcare navigation
2. **B2B Licensing**: Offer API/tools to insurance providers and telehealth platforms
3. **Affiliate Revenue**: Get commission from clinics/doctors for confirmed bookings
4. **Data Analytics**: Offer de-identified analytics to healthcare systems
5. **Enterprise Solutions**: White-label platform for healthcare organizations

### Competitive Advantages
- **AI-First Approach**: Advanced LLM integration for personalized care
- **Comprehensive Platform**: Therapy + healthcare navigation in one solution
- **Voice Interface**: Unique speech-to-speech therapy capabilities
- **Offline Processing**: Privacy-focused local speech processing
- **Scalable Architecture**: Modern tech stack ready for enterprise deployment

## 🔒 Security & Privacy

### Data Protection
- **Local Processing**: Speech-to-text and text-to-speech run offline
- **JWT Tokens**: Secure session management
- **Rate Limiting**: Protection against abuse
- **No External Storage**: Chat history stored locally
- **HIPAA Compliance**: Healthcare data protection standards (when applicable)

### Environment Variables
```bash
OPENAI_API_KEY=your-openai-api-key
JWT_SECRET_KEY=your-secret-key
BETTERDOCTOR_API_KEY=your-betterdoctor-api-key
HEALTHCARE_GOV_API_KEY=your-healthcare-gov-api-key
ZIPCODE_API_KEY=your-zipcode-api-key
```

## 🐛 Troubleshooting

### Provider Search (Find Doctors) Issues
- If you see only demo providers, the BetterDoctor API is unreachable or no API key is set.
- To enable real provider search, get a BetterDoctor API key and set it in your backend environment:
  ```bash
  export BETTERDOCTOR_API_KEY="your-betterdoctor-api-key"
  python app.py
  ```
- If the API is deprecated or unreachable, the app will always show demo providers for a seamless user experience.

### General Issues
- **Backend won't start:**
  - Ensure Python virtual environment is activated
  - Check that all dependencies are installed: `pip install -r requirements.txt`
  - Verify OpenAI API key is set correctly
- **Frontend won't start:**
  - Ensure Node.js dependencies are installed: `npm install`
  - Check for port conflicts on 5173
- **Healthcare features not working:**
  - Verify healthcare API keys are configured (optional)
  - Check network connectivity for external API calls
  - Fallback data will be used if APIs are unavailable
- **Speech features not working:**
  - Ensure microphone permissions are granted
  - Check that Vosk model is downloaded correctly
  - Verify audio drivers are working

### Getting Help
- Check the console for error messages
- Ensure all environment variables are set correctly
- Verify API keys are valid and have sufficient credits

## 🚀 Future Enhancements

### Planned Features
- **Mobile App**: React Native version for iOS/Android
- **Telemedicine Integration**: Direct video call scheduling
- **Insurance API Integration**: Real-time coverage verification
- **Prescription Management**: Medication tracking and reminders
- **Health Records Integration**: FHIR-compliant data exchange
- **Predictive Analytics**: AI-powered health trend analysis
- **Multi-language Support**: International healthcare navigation
- **Voice Assistant**: Alexa/Google Assistant integration

### Technical Roadmap
- **Microservices Architecture**: Scalable backend services
- **Real-time Collaboration**: Multi-user therapy sessions
- **Advanced AI Models**: Custom fine-tuned models for healthcare
- **Blockchain Integration**: Secure health data management
- **IoT Integration**: Wearable device data integration
- **AR/VR Therapy**: Immersive therapeutic experiences

---

**PulsePath AI Therapy Tool** - Transforming mental health care through AI-powered therapy and comprehensive healthcare navigation.
