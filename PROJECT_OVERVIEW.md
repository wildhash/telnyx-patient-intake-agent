# Project Overview - Telnyx Patient Intake Agent

Comprehensive architecture overview and call lifecycle documentation.

## Table of Contents

- [System Architecture](#system-architecture)
- [Call Lifecycle](#call-lifecycle)
- [Component Overview](#component-overview)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Deployment Architecture](#deployment-architecture)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         TELNYX CLOUD                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Call Control │  │  Recording   │  │Transcription │         │
│  │     API      │  │   Service    │  │   (Whisper)  │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                  │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          │ Webhooks         │ MP3 URLs         │ Transcript Events
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼─────────────────┐
│                    FLASK APPLICATION                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                     ROUTES LAYER                           │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │ │
│  │  │  Webhook    │ │     API     │ │  Dashboard  │         │ │
│  │  │   Routes    │ │   Routes    │ │   Routes    │         │ │
│  │  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘         │ │
│  └─────────┼────────────────┼────────────────┼────────────────┘ │
│            │                │                │                   │
│  ┌─────────▼────────────────▼────────────────▼────────────────┐ │
│  │                    SERVICES LAYER                          │ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │ │
│  │  │   Telnyx     │ │   Intake     │ │   Storage    │      │ │
│  │  │   Service    │ │   Service    │ │   Service    │      │ │
│  │  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘      │ │
│  └─────────┼────────────────┼────────────────┼──────────────┘ │
│            │                │                │                  │
│  ┌─────────▼────────────────▼────────────────▼──────────────┐ │
│  │                   DATABASE LAYER                         │ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │ │
│  │  │   Patient    │ │     Call     │ │  Transcript  │    │ │
│  │  │    Model     │ │    Model     │ │    Model     │    │ │
│  │  └──────────────┘ └──────────────┘ └──────────────┘    │ │
│  └──────────────────────────────────────────────────────────┘ │
└──────────────────────────┬────────────────────────────────────┘
                           │
                           │ Push Data
                           │
┌──────────────────────────▼────────────────────────────────────┐
│                    STORAGE LAYER                               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐          │
│  │ Local JSON   │ │  MemVerge    │ │ ApertureData │          │
│  │  (data/)     │ │ (Hot Store)  │ │ (Cold Store) │          │
│  └──────────────┘ └──────────────┘ └──────────────┘          │
└───────────────────────────────────────────────────────────────┘
```

---

## Call Lifecycle

### Phase 1: Call Initiation

```
User Action → API Request → Telnyx API → Call Created
```

**Steps:**
1. User submits phone number via Dashboard, CLI, or API
2. Flask receives request at `/api/calls` endpoint
3. `TelnyxService` creates outbound call via Telnyx API
4. Call record created in database with status "initiated"
5. Response returned to user with call ID

**Database State:**
```sql
Call {
  status: 'initiated',
  to_number: '+12025551234',
  telnyx_call_id: 'abc123...',
  created_at: timestamp
}
```

### Phase 2: Call Connection

```
Phone Rings → Call Answered → Webhook Event
```

**Steps:**
1. Telnyx dials the phone number
2. When answered, Telnyx sends `call.answered` webhook
3. Flask webhook handler receives event
4. Call status updated to "answered"
5. Recording and transcription started (if enabled)
6. First prompt played: Consent request

**Webhook Payload:**
```json
{
  "data": {
    "event_type": "call.answered",
    "payload": {
      "call_control_id": "abc123...",
      "call_session_id": "xyz789..."
    }
  }
}
```

**Database State:**
```sql
Call {
  status: 'answered',
  answered_at: timestamp,
  call_session_id: 'xyz789...'
}
```

### Phase 3: Consent Collection

```
Play Consent Prompt → Gather DTMF → Process Response
```

**Steps:**
1. System speaks consent prompt via text-to-speech
2. Listens for DTMF input (1 = consent, 2 = decline)
3. If consent given (1), proceed to questions
4. If declined (2), thank caller and hang up
5. Update call state with consent status

**Call Flow:**
```
┌─────────────────┐
│ Speak: Consent  │
│    Prompt       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Gather: DTMF    │
│   (1 or 2)      │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
  [1]       [2]
Consent   Decline
    │         │
    │         └─────► Hang Up
    │
    ▼
Continue to
Questions
```

### Phase 4: Question Flow

```
For each section (HPI → AMPLE → Family History):
  For each question:
    Speak Question → Gather Response → Store Answer → Next Question
```

**Question Sections:**

1. **HPI (History of Present Illness)**
   - Chief complaint (voice response)
   - Symptom duration (DTMF)
   - Pain level (DTMF)

2. **AMPLE History**
   - Allergies (DTMF + optional voice followup)
   - Medications (DTMF + optional voice followup)
   - Past medical history (DTMF + optional voice followup)
   - Last meal (DTMF)

3. **Family History**
   - Heart disease (DTMF)
   - Diabetes (DTMF)
   - Cancer (DTMF)

**State Tracking:**
```json
{
  "current_section": "hpi",
  "question_index": 0,
  "responses": {
    "chief_complaint": {
      "value": "chest pain",
      "timestamp": "2024-01-01T10:00:00Z"
    }
  }
}
```

### Phase 5: Recording & Transcription

**Continuous During Call:**

```
Audio Stream → Telnyx → Recording + Transcription → Webhooks
```

**Recording Process:**
1. Recording started when call answered
2. Audio captured in MP3 format
3. When call ends, recording processed
4. `call.recording.saved` webhook sent with download URL
5. URL stored in database

**Transcription Process:**
1. Real-time transcription via Whisper-Turbo
2. `call.transcription` webhooks sent continuously
3. Each segment stored in Transcript table
4. Text accumulated for full transcript

**Transcript Storage:**
```sql
Transcript {
  call_id: 1,
  text: "I have chest pain...",
  confidence: 0.95,
  created_at: timestamp
}
```

### Phase 6: Call Completion

```
Final Question → Closing Message → Hang Up → Data Processing
```

**Steps:**
1. All questions completed
2. Play closing message
3. Hang up call
4. `call.hangup` webhook received
5. Call status updated to "completed"
6. Calculate final duration
7. Generate structured intake note
8. Push data to storage systems

**Final Database State:**
```sql
Call {
  status: 'completed',
  duration: 180,
  ended_at: timestamp,
  recording_url: 'https://...',
  intake_data: { ... }
}
```

### Phase 7: Data Storage & Integration

```
Call Completed → Format Data → Push to Storage Systems
```

**Storage Destinations:**

1. **Local JSON** (always enabled)
   ```
   data/intake_<call_id>_<timestamp>.json
   data/transcript_<call_id>_<timestamp>.json
   data/call_metadata_<call_id>_<timestamp>.json
   ```

2. **MemVerge** (optional - hot storage)
   - Fast access for recent calls
   - In-memory data store
   - Push via REST API

3. **ApertureData** (optional - cold storage)
   - Long-term archival
   - Visual database
   - Push via gRPC/custom client

4. **Backend API** (optional - custom integration)
   - EHR system integration
   - Custom backend services
   - Push via HTTP POST

---

## Component Overview

### Frontend Components

#### 1. Web Dashboard (`templates/dashboard.html`)
- Real-time statistics display
- Call initiation interface
- Active call monitoring
- Recent calls list

#### 2. JavaScript (`static/dashboard.js`)
- AJAX API calls
- Real-time polling
- UI updates
- Event handling

#### 3. Styles (`static/styles.css`)
- Responsive design
- Professional healthcare UI
- Status indicators
- Loading states

### Backend Components

#### 1. Flask Application (`app.py`, `app_enhanced.py`)
- HTTP server
- Route registration
- Database initialization
- Error handling

#### 2. Routes

**Call Routes** (`routes/call_routes.py`)
- `/api/calls` - List and create calls
- `/api/calls/<id>` - Call details
- `/api/calls/<id>/hangup` - Hang up call

**Webhook Routes** (`routes/webhook_routes.py`)
- `/webhooks/telnyx` - Telnyx event handler
- Event processing
- State management

**API Routes** (`routes/api_routes.py`)
- Patient management
- Statistics
- Transcript retrieval

**Dashboard Routes** (`routes/dashboard_routes.py`)
- Web interface rendering
- Template context

#### 3. Services

**Telnyx Service** (`services/telnyx_service.py`)
- Call Control API wrapper
- Outbound call creation
- TTS commands
- DTMF gathering

**Intake Service** (`services/intake_service.py`)
- Question management
- Flow control
- Response processing
- Data formatting

**Storage Service** (`services/storage_service.py`)
- MemVerge integration
- ApertureData integration
- Backend API push

#### 4. Models (`models.py`)

**Patient Model**
- Patient demographics
- Contact information
- Relationship to calls

**Call Model**
- Call metadata
- Status tracking
- Recording URLs
- Intake data

**Transcript Model**
- Transcript segments
- Timestamps
- Confidence scores

### CLI Component (`cli.py`)

Command-line interface for:
- Patient management
- Call operations
- Statistics viewing
- Configuration display

### Test Tool (`test_call.py`)

Simple CLI for testing:
```bash
python test_call.py call +12025551234
python test_call.py status 1
python test_call.py list
python test_call.py transcripts 1
```

---

## Data Flow

### Inbound Webhook Data Flow

```
Telnyx Webhook → Flask Routes → Event Handler → Service Layer → Database
                                      │
                                      └──────────► Storage Integration
```

### Outbound API Data Flow

```
User Request → Flask Routes → Service Layer → Telnyx API
                   │                              │
                   │                              ▼
                   └────► Database ◄────── Response
```

### Storage Data Flow

```
Call Completed → Storage Integration → [Local JSON]
                                     → [MemVerge API] (if enabled)
                                     → [ApertureData] (if enabled)
                                     → [Backend API] (if configured)
```

---

## Technology Stack

### Backend
- **Python 3.8+** - Programming language
- **Flask 3.0** - Web framework
- **SQLAlchemy 2.0** - ORM
- **Telnyx SDK 2.1** - Voice API client

### Database
- **SQLite** (development)
- **PostgreSQL/MySQL** (production ready)

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **HTML5/CSS3** - Modern web standards

### External Services
- **Telnyx** - Voice API, Call Control, Recording, Transcription
- **MemVerge** (optional) - Hot storage
- **ApertureData** (optional) - Cold storage

### Development Tools
- **ngrok** - Local development tunneling
- **pytest** - Testing framework
- **python-dotenv** - Environment management

---

## Deployment Architecture

### Local Development

```
┌────────────┐         ┌────────────┐
│   ngrok    │◄────────┤   Flask    │
│  (tunnel)  │         │   (5000)   │
└──────┬─────┘         └────────────┘
       │                      │
       │                      ▼
       │               ┌────────────┐
       │               │  SQLite DB │
       │               └────────────┘
       │
       ▼
┌────────────┐
│   Telnyx   │
│   Cloud    │
└────────────┘
```

### Production (Recommended)

```
┌────────────┐         ┌────────────┐         ┌────────────┐
│   Nginx    │◄────────┤  Gunicorn  │◄────────┤   Flask    │
│ (Reverse   │         │  (WSGI)    │         │    App     │
│   Proxy)   │         └────────────┘         └────────────┘
└──────┬─────┘              │                        │
       │                    │                        ▼
       │                    │                 ┌────────────┐
       │                    │                 │ PostgreSQL │
       │                    │                 └────────────┘
       │                    │
       │                    └──────► Load Balancing
       │                              (multiple workers)
       ▼
┌────────────┐
│   Telnyx   │
│   Cloud    │
└────────────┘
```

### Docker Deployment

```
┌───────────────────────────────────────┐
│          Docker Container             │
│  ┌────────────────────────────────┐  │
│  │        Flask App               │  │
│  │      (Gunicorn WSGI)           │  │
│  └────────────┬───────────────────┘  │
│               │                       │
│               ▼                       │
│  ┌────────────────────────────────┐  │
│  │       SQLite/PostgreSQL        │  │
│  └────────────────────────────────┘  │
└───────────────┬───────────────────────┘
                │
                │ Port 5000
                ▼
        ┌───────────────┐
        │  Host Network │
        └───────────────┘
```

---

## Security Considerations

### Data Protection
- PHI data masked in logs
- HTTPS required for webhooks
- Webhook signature verification
- Environment variable configuration

### Access Control
- API key authentication
- Rate limiting (recommended)
- CORS configuration
- Input validation

### Compliance
- HIPAA considerations documented
- Consent collection required
- Audit logging
- Data retention policies

---

## Performance Metrics

### Expected Performance
- **Call Initiation:** < 2 seconds
- **Webhook Processing:** < 500ms
- **Database Queries:** < 100ms
- **API Response Time:** < 1 second

### Scalability
- **Concurrent Calls:** Limited by Telnyx plan
- **Database:** SQLite OK for < 1000 calls/day
- **Horizontal Scaling:** Add Gunicorn workers
- **Vertical Scaling:** Increase server resources

---

## Monitoring & Observability

### Logging
- Application logs (Flask)
- Webhook events
- API requests
- Error tracking

### Metrics (Recommended)
- Call success rate
- Average call duration
- Webhook delivery success
- API response times

### Alerting (Recommended)
- Failed calls
- Webhook errors
- Database issues
- High latency

---

## Future Enhancements

### Features
- Multi-language support
- Voice biometrics
- Sentiment analysis
- EHR integration (Epic, Cerner)
- FHIR API support

### Infrastructure
- Kubernetes deployment
- CI/CD pipeline
- Automated testing
- Performance monitoring

### Integrations
- Additional storage systems
- Analytics platforms
- Alerting services
- Payment processing

---

**For more information, see:**
- [README.md](README.md) - Getting started guide
- [QUICKSTART.md](QUICKSTART.md) - 5-minute setup
- [TELNYX_SETUP.md](TELNYX_SETUP.md) - Telnyx configuration
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details
- [SECURITY.md](SECURITY.md) - Security best practices
