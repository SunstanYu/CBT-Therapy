# CBT Therapy Assistant

A comprehensive web-based Cognitive Behavioral Therapy (CBT) assistant system featuring dual AI agents for conversational guidance and psychological state analysis.

## 📋 Overview

This project implements a complete CBT therapy assistant system that helps users engage in structured therapeutic conversations. The system consists of two AI agents working in coordination:

- **Agent A (Conversational Guide)**: Conducts structured CBT-style conversations with users
- **Agent B (Psychological State Analyzer)**: Analyzes user psychological states and generates comprehensive JSON reports

The system includes a modern, calming web interface for patients and a detailed dashboard for therapists to monitor patient progress in real-time.

## ✨ Key Features

### For Patients
- **Calming, Therapeutic UI**: Designed with a "Calm-Tech" aesthetic to reduce anxiety and create a safe space
- **Voice Input**: Record voice messages that are automatically transcribed to text using Google Speech-to-Text API
- **Structured CBT Sessions**: Guided conversations covering all CBT components:
  - Presenting Problem
  - Situation Description
  - Emotion Identification
  - Physical Reactions
  - Automatic Thoughts
  - Behavioral Responses
  - Consequences
  - Desired Change
- **Real-time Analysis**: Immediate feedback and analysis after each message
- **Session History**: View past conversations and progress

### For Therapists
- **Real-time Patient Dashboard**: Monitor patient assessments as they happen
- **Comprehensive Reports**: View detailed analysis including:
  - Risk Assessment (self-harm risk, crisis flags)
  - Clinical Symptom Scores (anxiety, depression, stress, rumination, avoidance, self-blame)
  - Cognitive Distortions Detection
  - Emotional and Physical Reactions
  - Behavioral Patterns
  - Trend Analysis
- **Visual Analytics**: Radar charts and bar graphs for clinical scores
- **Patient Profiles**: Track patient progress over time
- **Auto-refresh**: Real-time updates every 3 seconds

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Web UI)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Landing Page │  │ Chat Session │  │  Dashboard   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (REST API)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Session API  │  │ Analysis API │  │ Speech API   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Orchestrator                          │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │  Agent A         │      │  Agent B         │        │
│  │  (Conversation)  │◄────►│  (Analysis)      │        │
│  │  GPT-5.1         │      │  GPT-5.1         │        │
│  └──────────────────┘      └──────────────────┘        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Database (SQLite/MySQL)               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  Users   │  │  Records │  │ Profiles │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
```

### Project Structure

```
CPTTherapy/
├── backend/
│   ├── agents/
│   │   ├── agent_conversation.py      # Agent A: Conversational Guide
│   │   ├── agent_analysis.py          # Agent B: Psychological Analyzer
│   │   └── orchestrator.py            # Coordinates both agents
│   ├── api/
│   │   ├── user_session_api.py        # User session endpoints
│   │   ├── analysis_api.py            # Analysis result endpoints
│   │   ├── doctor_dashboard_api.py    # Doctor dashboard endpoints
│   │   └── speech_api.py              # Speech-to-text API
│   ├── models/
│   │   ├── user.py                    # User model
│   │   ├── daily_record.py            # Daily session records
│   │   └── profile.py                 # User psychological profiles
│   ├── db/
│   │   ├── base.py                    # SQLAlchemy base
│   │   ├── orm.py                     # Database session management
│   │   └── init_data.py               # Database initialization
│   ├── config.py                      # Configuration management
│   └── main.py                        # FastAPI application entry
├── frontend/
│   ├── pages/
│   │   ├── landing.html               # Landing page
│   │   ├── chat.html                  # Chat interface
│   │   ├── history.html               # Session history
│   │   ├── dashboard.html             # Doctor dashboard
│   │   └── patient_report.html        # Patient report dashboard
│   ├── components/
│   │   ├── config.js                  # Global configuration
│   │   ├── chat_window.js             # Chat window component
│   │   ├── session_controls.js        # Session control component
│   │   └── patient_report.js          # Patient report component
│   └── styles/
│       ├── main.css                   # Main stylesheet
│       ├── landing.css                # Landing page styles
│       └── patient_report.css         # Report dashboard styles
├── data/                              # Database files (SQLite)
├── Dockerfile                         # Docker image configuration
├── docker-compose.yml                 # Docker Compose configuration
├── requirements.txt                   # Python dependencies
├── env.example                        # Environment variables template
└── README.md                          # This file
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose (recommended), or
- Python 3.11+
- Node.js (optional, for frontend development)

### Installation

#### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CPTTherapy
   ```

2. **Create environment file**
   ```bash
   # Windows
   copy env.example .env
   
   # Linux/Mac
   cp env.example .env
   ```

3. **Configure environment variables**
   
   Edit `.env` file and add your API keys:
   ```env
   # OpenAI API Key (required for AI agents)
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Google Cloud Speech-to-Text (optional, for voice input)
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   # OR
   GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
   
   # Database (default: SQLite)
   DATABASE_URL=sqlite:///./data/cbt_therapy.db
   
   # Application settings
   PORT=8000
   DEBUG=False
   ```

4. **Build and start services**
   ```bash
   docker-compose up -d --build
   ```

5. **Initialize database**
   ```bash
   docker-compose exec backend python -m backend.db.init_data
   ```

6. **Access the application**
   - **Landing Page**: http://localhost:8000/
   - **Chat Interface**: http://localhost:8000/chat
   - **Patient Report Dashboard**: http://localhost:8000/patient-report
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

7. **View logs**
   ```bash
   docker-compose logs -f backend
   ```

8. **Stop services**
   ```bash
   docker-compose down
   ```

#### Option 2: Local Development

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

3. **Initialize database**
   ```bash
   python -m backend.db.init_data
   ```

4. **Start backend server**
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the application**
   - Open http://localhost:8000/ in your browser

## 📡 API Endpoints

### Session Management (`/api/session`)

- `POST /api/session/start` - Start a new CBT session
  ```json
  {
    "user_id": 1
  }
  ```

- `POST /api/session/message` - Send a user message
  ```json
  {
    "user_id": 1,
    "message": "I feel anxious about tomorrow's presentation"
  }
  ```

- `POST /api/session/end` - End the current session

### Analysis API (`/api/analysis`)

- `GET /api/analysis/user/{user_id}/latest` - Get latest analysis for a user
- `POST /api/analysis/get` - Get analysis for a specific date
  ```json
  {
    "user_id": 1,
    "date": "2024-01-15"
  }
  ```

### Speech-to-Text API (`/api/speech`)

- `POST /api/speech/transcribe` - Transcribe audio to text
  - Content-Type: `multipart/form-data`
  - Body: `audio_file` (audio file)

### Doctor Dashboard API (`/api/doctor`)

- `GET /api/doctor/users` - Get all users
- `GET /api/doctor/user/{user_id}/profile` - Get user profile
- `GET /api/doctor/user/{user_id}/records` - Get user session records
- `POST /api/doctor/user/{user_id}/profile/notes` - Update therapist notes

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI agents | Yes | - |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to Google Cloud service account JSON | No* | - |
| `GOOGLE_CREDENTIALS_JSON` | Google Cloud credentials as JSON string | No* | - |
| `DATABASE_URL` | Database connection URL | No | `sqlite:///./data/cbt_therapy.db` |
| `PORT` | API server port | No | `8000` |
| `DEBUG` | Enable debug mode | No | `False` |

*Required only if using voice input feature

### Google Cloud Speech-to-Text Setup

1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Speech-to-Text API**
   - Navigate to APIs & Services > Library
   - Search for "Cloud Speech-to-Text API"
   - Click "Enable"

3. **Create Service Account**
   - Go to IAM & Admin > Service Accounts
   - Create a new service account
   - Grant "Cloud Speech-to-Text API User" role
   - Create and download JSON key

4. **Configure Credentials**
   - Option 1: Set `GOOGLE_APPLICATION_CREDENTIALS` to the path of the JSON file
   - Option 2: Set `GOOGLE_CREDENTIALS_JSON` to the JSON content as a string

## 📊 Data Models

### CBT Daily Analysis JSON Schema

```json
{
  "date": "YYYY-MM-DD",
  "presenting_problem": "What bothered the user today",
  "situation_description": {
    "when": "When it happened",
    "where": "Where it happened",
    "who": "Who was involved",
    "what_happened": "What happened"
  },
  "emotions": [
    {
      "type": "Anxiety",
      "intensity_0_100": 75
    }
  ],
  "physical_reactions": ["tight chest", "sweating"],
  "automatic_thoughts": ["I can't handle this", "I'm going to fail"],
  "behavior_reactions": ["avoided the situation", "withdrew from others"],
  "consequences": "Felt more anxious afterward",
  "desired_change": "Want to reduce anxiety in social situations",
  "additional_notes": "Any additional information",
  "cognitive_distortions": [
    "catastrophizing",
    "all-or-nothing thinking"
  ],
  "clinical_scores": {
    "anxiety_0_10": 7,
    "depression_0_10": 5,
    "stress_0_10": 8,
    "rumination_0_10": 6,
    "avoidance_0_10": 7,
    "self_blame_0_10": 4
  },
  "risk_assessment": {
    "self_harm_risk_0_3": 0,
    "crisis_flag": false
  },
  "profile_update": {
    "trend_notes": "Anxiety levels have been elevated this week",
    "suggestions_to_therapist": "Consider teaching relaxation techniques"
  }
}
```

## 🎨 UI Features

### Landing Page
- Calming gradient background
- Soft illustrations (clouds, leaves, waves)
- Two main actions:
  - **Start Today's Record**: Begin a new therapy session
  - **Diary Guide**: View comprehensive guide on how to record thoughts

### Chat Interface
- **Calm-Tech Design**: Soft colors, rounded corners, gentle animations
- **Voice Input**: Click microphone button to record and transcribe
- **Auto-start Session**: Sessions begin automatically when page loads
- **Real-time Analysis**: Analysis results saved after each message
- **Message Bubbles**: Large, rounded message bubbles with emoji indicators

### Patient Report Dashboard
- **Real-time Updates**: Auto-refresh every 3 seconds
- **Risk Assessment**: Prominent display of self-harm risk and crisis flags
- **Clinical Scores**: Radar chart and bar graphs
- **Cognitive Distortions**: Tag-based visualization
- **Comprehensive Details**: All CBT components displayed in organized sections

## 🔐 Security Considerations

⚠️ **Important**: This is a demonstration project. Before deploying to production:

1. **Authentication & Authorization**: Implement user authentication (JWT, OAuth, etc.)
2. **Data Encryption**: Encrypt sensitive data at rest and in transit
3. **HTTPS**: Use HTTPS to protect data transmission
4. **API Rate Limiting**: Prevent API abuse
5. **Input Validation**: Strengthen input validation and sanitization
6. **Privacy Compliance**: Comply with healthcare data privacy regulations (HIPAA, GDPR, etc.)
7. **Secure API Keys**: Never commit API keys to version control

## 🧪 Testing

### Create Test User

The database initialization script creates a default test user:
- User ID: 1
- Username: `test_user`

### Test API Endpoints

Use the interactive API documentation at http://localhost:8000/docs

### Initialize Test Data

```bash
# In Docker container
docker-compose exec backend python -m backend.db.init_data

# Or locally
python -m backend.db.init_data
```

## 🛠️ Development

### Adding New Features

#### Extend CBT Components
- Modify `agent_conversation.py` to add new conversation flows
- Update `agent_analysis.py` to extract additional data points

#### Add New API Endpoints
- Create new router in `backend/api/`
- Register router in `backend/main.py`

#### Customize UI
- Modify styles in `frontend/styles/`
- Update components in `frontend/components/`

### AI Model Configuration

The system uses OpenAI GPT models. To change the model:

1. Edit `backend/agents/agent_conversation.py`:
   ```python
   self.ai_model = "gpt-4o-mini"  # Change model name
   ```

2. Edit `backend/agents/agent_analysis.py`:
   ```python
   self.ai_model = "gpt-4o-mini"  # Change model name
   ```

### Database Migration

When modifying models:

1. Update model classes in `backend/models/`
2. SQLAlchemy will auto-create tables on startup
3. For production, use Alembic for migrations

## 📦 Dependencies

### Backend
- `fastapi==0.104.1` - Web framework
- `uvicorn[standard]==0.24.0` - ASGI server
- `sqlalchemy==2.0.23` - ORM
- `openai==2.2.0` - OpenAI API client
- `google-cloud-speech==2.23.0` - Google Speech-to-Text
- `python-dotenv==1.0.0` - Environment variable management

### Frontend
- Vanilla JavaScript (no framework dependencies)
- Chart.js (via CDN) - For data visualization
- Google Fonts (Noto Sans SC) - Typography

## 🐛 Troubleshooting

### Voice Input Not Working
- Check browser permissions for microphone access
- Verify Google Cloud credentials are configured
- Check browser console for errors
- Ensure `google-cloud-speech` is installed

### API Errors
- Verify API keys are set in `.env` file
- Check Docker logs: `docker-compose logs -f backend`
- Ensure database is initialized
- Check API documentation at `/docs`

### Database Issues
- Ensure `data/` directory exists and is writable
- Check `DATABASE_URL` in `.env`
- Try reinitializing: `python -m backend.db.init_data`

## 📝 License

This project is for educational and research purposes only.

## ⚠️ Disclaimer

**This system is for supportive use only and cannot replace professional psychological treatment. If you are experiencing serious psychological issues, please seek professional medical help immediately.**

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📧 Support

For questions or issues, please create an issue in the repository.

---

**Version**: 0.3.1 Beta  
**Last Updated**: 2025

