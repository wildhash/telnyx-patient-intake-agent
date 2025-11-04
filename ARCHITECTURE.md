# Architecture Documentation

## System Overview

The Telnyx Patient Intake Agent is a voice-driven healthcare application that automates patient intake using the Telnyx Voice API. The system follows a modular, service-oriented architecture.

## High-Level Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Patient   │◄────►│   Telnyx     │◄────►│   Agent     │
│   Phone     │      │  Voice API   │      │ Application │
└─────────────┘      └──────────────┘      └─────────────┘
                                                   │
                     ┌─────────────────────────────┼─────────────────────┐
                     │                             │                     │
              ┌──────▼──────┐           ┌─────────▼────────┐    ┌──────▼──────┐
              │  Web        │           │  REST API        │    │  CLI Tool   │
              │  Dashboard  │           │  Endpoints       │    │             │
              └─────────────┘           └──────────────────┘    └─────────────┘
                                                   │
                     ┌─────────────────────────────┼─────────────────────┐
                     │                             │                     │
              ┌──────▼──────┐           ┌─────────▼────────┐    ┌──────▼──────┐
              │  Database   │           │  Storage         │    │  Backend    │
              │  (SQLite)   │           │  Services        │    │  API        │
              └─────────────┘           └──────────────────┘    └─────────────┘
                                                   │
                                        ┌──────────┴──────────┐
                                        │                     │
                                 ┌──────▼──────┐      ┌──────▼──────┐
                                 │  MemVerge   │      │ ApertureData│
                                 │  (Hot)      │      │  (Cold)     │
                                 └─────────────┘      └─────────────┘
```

## Component Architecture

### 1. Flask Application (`app.py`)

**Purpose**: Main application entry point

**Responsibilities**:
- Initialize Flask app and extensions
- Register blueprints
- Configure middleware (CORS, logging)
- Create database tables
- Handle application lifecycle

**Key Dependencies**:
- Flask
- Flask-CORS
- Flask-SQLAlchemy

### 2. Database Models (`models.py`)

**Purpose**: Data persistence layer

**Models**:
- `Patient`: Patient demographic information
- `Call`: Call session data and metadata
- `Transcript`: Real-time transcript segments

**Relationships**:
```
Patient (1) ──── (N) Call (1) ──── (N) Transcript
```

### 3. Configuration (`config.py`)

**Purpose**: Centralized configuration management

**Configuration Categories**:
- Telnyx credentials and settings
- Flask application settings
- Storage system configurations
- Call behavior settings

### 4. Routes Layer

#### Call Routes (`routes/call_routes.py`)
- `POST /api/calls` - Initiate outbound call
- `GET /api/calls` - List calls
- `GET /api/calls/<id>` - Get call details
- `POST /api/calls/<id>/hangup` - Terminate call

#### Webhook Routes (`routes/webhook_routes.py`)
- `POST /webhooks/telnyx` - Handle Telnyx events

**Webhook Events**:
- `call.initiated` - Call placement confirmed
- `call.answered` - Patient answered
- `call.hangup` - Call ended
- `call.gather.ended` - DTMF input received
- `call.recording.saved` - Recording available
- `call.transcription` - Real-time transcript

#### API Routes (`routes/api_routes.py`)
- Patient CRUD operations
- Call transcript retrieval
- Intake data access
- System statistics

#### Dashboard Routes (`routes/dashboard_routes.py`)
- Web interface routes
- Template rendering

### 5. Services Layer

#### Telnyx Service (`services/telnyx_service.py`)

**Purpose**: Telnyx API abstraction

**Methods**:
- `initiate_call()` - Start outbound call
- `speak()` - Text-to-speech
- `gather_using_speak()` - TTS with DTMF collection
- `start_recording()` - Begin recording
- `start_transcription()` - Enable live transcription
- `hangup()` - End call

#### Intake Service (`services/intake_service.py`)

**Purpose**: Manage intake conversation flow

**Components**:
- `IntakeScript`: Question definitions
- `IntakeService`: Flow management

**Question Categories**:
1. Consent (DTMF)
2. HPI - History of Present Illness (mixed)
3. AMPLE - Allergies, Medications, Past history, Last meal (mixed)
4. Family History (DTMF)

**State Machine**:
```
[Start] → [Consent] → [HPI] → [AMPLE] → [Family History] → [Complete]
                 ↓
            [Declined]
```

#### Storage Service (`services/storage_service.py`)

**Purpose**: Data persistence to external systems

**Integrations**:
- MemVerge (hot storage)
- ApertureData (cold storage)
- Custom backend API

**Data Flow**:
```
Call Completed
    │
    ├─→ Format Data
    ├─→ Push to MemVerge (async)
    ├─→ Push to ApertureData (async)
    └─→ Push to Backend API (async)
```

### 6. CLI Tool (`cli.py`)

**Purpose**: Command-line management interface

**Command Groups**:
- `patient` - Patient management
- `call` - Call operations
- `stats` - System statistics
- `config` - Configuration display

### 7. Ngrok Helper (`ngrok_helper.py`)

**Purpose**: Local development tunnel management

**Features**:
- Automatic tunnel creation
- `.env` file updates
- Webhook URL generation

## Data Flow

### Outbound Call Flow

```
1. User initiates call (Dashboard/CLI/API)
   │
2. Create Call record in database
   │
3. TelnyxService.initiate_call()
   │
4. Telnyx sends webhook: call.initiated
   │
5. Call rings
   │
6. Telnyx sends webhook: call.answered
   │
7. IntakeService starts consent flow
   │
8. User provides consent (DTMF)
   │
9. Telnyx sends webhook: call.gather.ended
   │
10. IntakeService asks next question
   │
11. Repeat steps 8-10 for all questions
   │
12. IntakeService completes flow
   │
13. TelnyxService.speak() - goodbye message
   │
14. TelnyxService.hangup()
   │
15. Telnyx sends webhook: call.hangup
   │
16. Save intake data to database
   │
17. StorageService.push_all()
    │
    ├─→ MemVerge
    ├─→ ApertureData
    └─→ Backend API
```

### Webhook Processing Flow

```
Telnyx → POST /webhooks/telnyx
    │
    ├─→ Validate payload
    ├─→ Extract event_type
    ├─→ Route to handler
    │   │
    │   ├─→ handle_call_answered()
    │   │   └─→ Start intake flow
    │   │
    │   ├─→ handle_gather_ended()
    │   │   ├─→ Process response
    │   │   └─→ Ask next question
    │   │
    │   └─→ handle_call_hangup()
    │       ├─→ Save intake data
    │       └─→ Push to storage systems
    │
    └─→ Return 200 OK
```

## Database Schema

### Patient Table
```sql
CREATE TABLE patients (
    id INTEGER PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    date_of_birth DATE,
    email VARCHAR(120),
    created_at DATETIME,
    updated_at DATETIME
);
```

### Call Table
```sql
CREATE TABLE calls (
    id INTEGER PRIMARY KEY,
    call_control_id VARCHAR(100) UNIQUE,
    call_leg_id VARCHAR(100),
    call_session_id VARCHAR(100),
    patient_id INTEGER REFERENCES patients(id),
    status VARCHAR(20),
    direction VARCHAR(10),
    from_number VARCHAR(20),
    to_number VARCHAR(20),
    consent_given BOOLEAN,
    consent_timestamp DATETIME,
    started_at DATETIME,
    answered_at DATETIME,
    ended_at DATETIME,
    duration_seconds INTEGER,
    recording_url VARCHAR(500),
    recording_id VARCHAR(100),
    intake_data TEXT,  -- JSON
    memverge_id VARCHAR(100),
    aperturedata_id VARCHAR(100),
    backend_pushed BOOLEAN,
    backend_pushed_at DATETIME,
    created_at DATETIME,
    updated_at DATETIME
);
```

### Transcript Table
```sql
CREATE TABLE transcripts (
    id INTEGER PRIMARY KEY,
    call_id INTEGER REFERENCES calls(id),
    speaker VARCHAR(20),
    text TEXT NOT NULL,
    confidence FLOAT,
    timestamp DATETIME,
    sequence INTEGER,
    is_final BOOLEAN,
    created_at DATETIME
);
```

## Security Considerations

### Data Protection
- Environment variables for sensitive credentials
- No hardcoded secrets
- Database stored locally (can be encrypted)

### API Security
- CORS enabled for web dashboard
- Rate limiting (recommended for production)
- Input validation on all endpoints
- HTTPS required for webhooks (Telnyx requirement)

### HIPAA Compliance
- Consent collection before data gathering
- Encrypted data transmission
- Audit logging
- Access controls (to be implemented)
- Data retention policies (configurable)

## Scalability Considerations

### Current Architecture
- Single-threaded Flask development server
- SQLite database (file-based)
- In-memory call state management

### Production Recommendations
1. **Application Server**: Use Gunicorn/uWSGI with multiple workers
2. **Database**: Migrate to PostgreSQL/MySQL
3. **State Management**: Use Redis for call state
4. **Load Balancing**: Deploy behind Nginx/HAProxy
5. **Horizontal Scaling**: Multiple application instances
6. **Message Queue**: RabbitMQ/Celery for async tasks

### Scaling Path
```
Current: Single server, SQLite
    ↓
Stage 1: Gunicorn + PostgreSQL
    ↓
Stage 2: Redis + Multiple workers
    ↓
Stage 3: Load balancer + Multiple servers
    ↓
Stage 4: Message queue + Background workers
```

## Extension Points

### Adding New Intake Questions
1. Edit `services/intake_service.py`
2. Add question to appropriate category
3. Update `format_intake_data()` method

### Adding New Storage Systems
1. Create new method in `services/storage_service.py`
2. Add configuration to `config.py`
3. Update `push_all()` method
4. Update `.env.example`

### Adding New API Endpoints
1. Create new route in appropriate blueprint
2. Add documentation
3. Update README

### Adding New Webhook Events
1. Add handler in `routes/webhook_routes.py`
2. Route event in `telnyx_webhook()`
3. Update documentation

## Technology Stack

**Backend**:
- Python 3.8+
- Flask 3.0
- SQLAlchemy 2.0
- Telnyx SDK 2.1

**Frontend**:
- Vanilla JavaScript
- HTML5/CSS3
- No framework (by design)

**Infrastructure**:
- Ngrok (development)
- Gunicorn (production)
- SQLite/PostgreSQL

**External Services**:
- Telnyx Voice API
- MemVerge (optional)
- ApertureData (optional)

## Performance Characteristics

**Expected Metrics**:
- Call initiation: <1 second
- Webhook response: <100ms
- Database queries: <50ms
- API response: <200ms

**Resource Usage**:
- Memory: ~50-100MB per worker
- CPU: <5% idle, <30% under load
- Storage: ~1MB per call (including transcripts)

## Monitoring & Observability

**Recommended Metrics**:
- Active call count
- Call success/failure rate
- Consent rate
- Average call duration
- Webhook response time
- API response time
- Database query time
- Error rates

**Logging**:
- Application logs: stdout/stderr
- Access logs: Nginx/Apache
- Error logs: Sentry/Rollbar (recommended)

## Future Enhancements

1. **Advanced Features**:
   - Voice biometrics
   - Sentiment analysis
   - Multi-language support
   - Call recording playback UI

2. **Integrations**:
   - EHR systems (Epic, Cerner)
   - Scheduling systems
   - SMS notifications
   - Email notifications

3. **Analytics**:
   - Call analytics dashboard
   - Patient insights
   - Operational reports
   - Cost analysis

4. **DevOps**:
   - CI/CD pipeline
   - Automated testing
   - Infrastructure as Code
   - Monitoring stack
