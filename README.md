# 🏥 Telnyx Patient Intake Agent

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![Telnyx](https://img.shields.io/badge/telnyx-voice%20api-purple.svg)](https://telnyx.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **A production-ready, Telnyx-powered Python/Flask voice agent for automated patient intake.** Places outbound calls, obtains consent, asks scripted HPI/AMPLE/family-history questions, and captures structured answers. Features live call recording, real-time transcription, and seamless integration with your backend, MemVerge (hot storage), and ApertureData (cold storage). Includes a web dashboard, REST API, CLI, and 5-minute quickstart. **Hackathon-ready!**

## ✨ Features

- 📞 **Outbound Call Management** - Automated calling via Telnyx Call Control API
- ✅ **HIPAA-Compliant Consent** - Mandatory consent collection before data gathering
- 📋 **Structured Intake Questions** - Pre-scripted HPI, AMPLE, and family history questionnaires
- 🎙️ **Live Call Recording** - Automatic MP3 recording of all conversations
- 📝 **Real-Time Transcription** - Live speech-to-text with speaker diarization
- 💾 **Multi-Storage Integration** - Push to MemVerge (hot), ApertureData (cold), and custom backends
- 🌐 **Web Dashboard** - Beautiful, responsive UI for monitoring and management
- 🔌 **REST API** - Full-featured API for programmatic access
- 💻 **CLI Tool** - Command-line interface for quick operations
- 🔧 **Ngrok Integration** - Easy local development with automatic tunneling
- 📊 **Analytics & Stats** - Real-time system statistics and reporting

## 🚀 5-Minute Quickstart

### Prerequisites

- Python 3.8 or higher
- A [Telnyx account](https://telnyx.com/sign-up) with:
  - An active phone number
  - API key
  - Call Control connection ID
- (Optional) [ngrok account](https://ngrok.com/) for local development

### Step 1: Clone and Install

```bash
# Clone the repository
git clone https://github.com/wildhash/telnyx-patient-intake-agent.git
cd telnyx-patient-intake-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

**Required configuration:**
```env
TELNYX_API_KEY=your_telnyx_api_key_here
TELNYX_CONNECTION_ID=your_connection_id_here
TELNYX_PHONE_NUMBER=+1234567890
```

### Step 3: Start the Application

**Option A: Local Development with ngrok**
```bash
# Terminal 1: Start ngrok tunnel
python ngrok_helper.py

# Terminal 2: Start Flask app
python app.py
```

**Option B: Direct Launch**
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Step 4: Configure Telnyx Webhook

1. Log in to [Telnyx Mission Control](https://portal.telnyx.com/)
2. Navigate to your Call Control Application
3. Set the webhook URL to: `https://your-ngrok-url.ngrok.io/webhooks/telnyx`
4. Save the configuration

### Step 5: Make Your First Call

**Using the Web Dashboard:**
1. Open `http://localhost:5000/dashboard`
2. Click "Initiate New Call"
3. Enter a phone number
4. Click "Start Call"

**Using the CLI:**
```bash
python cli.py call initiate --phone +1234567890
```

**Using the API:**
```bash
curl -X POST http://localhost:5000/api/calls \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'
```

🎉 **That's it!** Your voice agent is now calling patients!

## 📖 Documentation

### Project Structure

```
telnyx-patient-intake-agent/
├── app.py                 # Main Flask application
├── config.py              # Configuration management
├── models.py              # Database models (SQLAlchemy)
├── cli.py                 # Command-line interface
├── ngrok_helper.py        # Ngrok integration helper
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── routes/               # API and webhook routes
│   ├── call_routes.py    # Call management endpoints
│   ├── webhook_routes.py # Telnyx webhook handlers
│   ├── api_routes.py     # REST API endpoints
│   └── dashboard_routes.py # Dashboard routes
├── services/             # Business logic services
│   ├── telnyx_service.py # Telnyx API integration
│   ├── intake_service.py # Intake flow management
│   └── storage_service.py # Storage integrations
└── templates/            # Web dashboard templates
    ├── index.html
    ├── dashboard.html
    ├── calls.html
    ├── patients.html
    └── call_detail.html
```

### Intake Question Flow

The agent follows a structured conversation flow:

1. **Consent Collection** - Mandatory HIPAA consent via DTMF
2. **HPI Questions** (History of Present Illness)
   - Chief complaint
   - Symptom duration
   - Pain level assessment
3. **AMPLE Questions** (Medical History)
   - Allergies
   - Medications
   - Past medical history
   - Last meal
4. **Family History**
   - Heart disease
   - Diabetes
   - Cancer history
5. **Closing** - Thank you message and call termination

### API Endpoints

#### Call Management
- `POST /api/calls` - Initiate a new call
- `GET /api/calls` - List all calls (with filtering)
- `GET /api/calls/<id>` - Get call details
- `POST /api/calls/<id>/hangup` - Hang up a call
- `GET /api/calls/<id>/transcripts` - Get call transcripts
- `GET /api/calls/<id>/intake-data` - Get structured intake data

#### Patient Management
- `POST /api/patients` - Create a patient
- `GET /api/patients` - List all patients
- `GET /api/patients/<id>` - Get patient details
- `PUT /api/patients/<id>` - Update patient information
- `GET /api/patients/<id>/calls` - Get patient call history

#### System
- `GET /health` - Health check
- `GET /api/stats` - System statistics

#### Webhooks
- `POST /webhooks/telnyx` - Telnyx call control webhooks

### CLI Commands

```bash
# Patient management
python cli.py patient list
python cli.py patient create --phone +1234567890 --first-name John --last-name Doe
python cli.py patient get <patient_id>

# Call management
python cli.py call initiate --phone +1234567890
python cli.py call list
python cli.py call get <call_id>
python cli.py call hangup <call_id>
python cli.py call transcripts <call_id>

# System
python cli.py stats
python cli.py config
```

## 🔌 Storage Integrations

### Backend API Integration

Configure your backend API to receive call data:

```env
BACKEND_API_URL=https://your-backend-api.com/intake
BACKEND_API_KEY=your_api_key_here
```

The system will POST the following payload:
```json
{
  "call": { /* call details */ },
  "transcripts": [ /* transcript array */ ],
  "intake_data": { /* structured intake responses */ }
}
```

### MemVerge (Hot Storage)

Enable MemVerge for hot storage of recent calls:

```env
MEMVERGE_ENABLED=true
MEMVERGE_API_KEY=your_api_key
MEMVERGE_ENDPOINT=https://api.memverge.com
```

### ApertureData (Cold Storage)

Enable ApertureData for long-term cold storage:

```env
APERTUREDATA_ENABLED=true
APERTUREDATA_HOST=localhost
APERTUREDATA_PORT=55555
APERTUREDATA_USERNAME=admin
APERTUREDATA_PASSWORD=your_password
```

## 🚀 Production Deployment

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t telnyx-intake-agent .
docker run -p 5000:5000 --env-file .env telnyx-intake-agent
```

### Environment Variables

See `.env.example` for all configuration options.

## 🔐 Security Considerations

- **Never commit `.env` files** - Keep credentials secure
- **Use HTTPS in production** - Telnyx requires HTTPS for webhooks
- **Implement authentication** - Add auth middleware for production APIs
- **HIPAA compliance** - Ensure proper data handling and encryption
- **Rate limiting** - Implement rate limiting on public endpoints
- **Input validation** - All user inputs are validated

## 🧪 Testing

### Manual Testing

1. Start the application locally
2. Use the dashboard or CLI to initiate a test call
3. Monitor the logs for call flow execution
4. Check the database for recorded data

### Testing Webhooks Locally

Use ngrok to expose your local server:
```bash
python ngrok_helper.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Telnyx](https://telnyx.com/) for the Voice API
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) for database ORM

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/wildhash/telnyx-patient-intake-agent/issues)
- **Documentation**: [GitHub Wiki](https://github.com/wildhash/telnyx-patient-intake-agent/wiki)
- **Telnyx Support**: [support.telnyx.com](https://support.telnyx.com)

## 🏆 Hackathon Use

This project is **hackathon-ready**! It provides:
- ✅ Complete, working codebase
- ✅ Easy setup (5 minutes)
- ✅ Multiple interfaces (Web, API, CLI)
- ✅ Real-world healthcare use case
- ✅ Professional documentation
- ✅ Extensible architecture

Perfect for healthcare, voice AI, or communication hackathons!

---

**Built with ❤️ for better healthcare automation**
