# 🚀 Quickstart Guide - Telnyx Patient Intake Agent

Get up and running in **5 minutes** or less!

## Prerequisites Checklist

Before you begin, make sure you have:

- ✅ Python 3.8+ installed (`python --version`)
- ✅ A [Telnyx account](https://telnyx.com/sign-up) (free trial available)
- ✅ Git installed
- ✅ (Optional) [ngrok account](https://ngrok.com/) for local testing

## Step 1: Get Telnyx Credentials (2 minutes)

### 1.1 Create Telnyx Account
1. Go to [telnyx.com/sign-up](https://telnyx.com/sign-up)
2. Complete registration (credit card required for free trial)
3. Verify your email

### 1.2 Get a Phone Number
1. Log in to [Telnyx Mission Control](https://portal.telnyx.com/)
2. Navigate to **Numbers** → **My Numbers**
3. Click **Buy Numbers**
4. Search for and purchase a number (starts at $1/month)
5. Copy your phone number (format: +1234567890)

### 1.3 Create Call Control Application
1. Go to **Call Control** → **Applications**
2. Click **Create New App**
3. Name it "Patient Intake Agent"
4. For webhook URL, enter a placeholder (we'll update this later)
5. Click **Save**
6. Copy the **Connection ID** (looks like: `1234567890`)

### 1.4 Get API Key
1. Go to **API Keys** in the left sidebar
2. Click **Create API Key**
3. Name it "Patient Intake"
4. Copy the **API Key** (starts with: `KEY...`)
5. ⚠️ **Save it now** - you won't see it again!

## Step 2: Install the Application (1 minute)

```bash
# Clone repository
git clone https://github.com/wildhash/telnyx-patient-intake-agent.git
cd telnyx-patient-intake-agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Configure Environment (1 minute)

```bash
# Copy example environment file
cp .env.example .env

# Open .env in your text editor
nano .env  # or: vim .env, code .env, etc.
```

**Update these required values:**
```env
TELNYX_API_KEY=KEY_YOUR_ACTUAL_API_KEY_HERE
TELNYX_CONNECTION_ID=1234567890
TELNYX_PHONE_NUMBER=+1234567890
```

**Optional but recommended:**
```env
SECRET_KEY=change-this-to-random-string-in-production
PORT=5000
```

Save and close the file.

## Step 4: Start the Application (30 seconds)

### Option A: Local Development with ngrok (Recommended)

**Terminal 1** - Start ngrok:
```bash
python ngrok_helper.py
```

You'll see output like:
```
============================================================
🔗 Ngrok tunnel active!
============================================================
Public URL: https://abc123.ngrok.io
Local URL:  http://localhost:5000
============================================================

Update your Telnyx webhook URL to:
https://abc123.ngrok.io/webhooks/telnyx
============================================================
```

**Copy the webhook URL** - you'll need it in Step 5!

**Terminal 2** - Start Flask:
```bash
python app.py
```

### Option B: Using the run script

```bash
python run.py --with-ngrok
```

### Option C: Without ngrok (production/hosted environment)

```bash
python app.py
```

You should see:
```
✓ Database tables created
🚀 Starting Telnyx Patient Intake Agent on port 5000...
📊 Dashboard: http://localhost:5000/dashboard
💻 API Docs: http://localhost:5000/api/stats
```

## Step 5: Configure Telnyx Webhook (30 seconds)

1. Go back to [Telnyx Mission Control](https://portal.telnyx.com/)
2. Navigate to **Call Control** → **Applications**
3. Click on your "Patient Intake Agent" application
4. Update **Webhook URL** to:
   - If using ngrok: `https://your-ngrok-url.ngrok.io/webhooks/telnyx`
   - If hosted: `https://your-domain.com/webhooks/telnyx`
5. Set **Webhook API Version** to `v2`
6. Click **Save**

## Step 6: Make Your First Call! (30 seconds)

### Option 1: Web Dashboard (Easiest)

1. Open your browser to `http://localhost:5000/dashboard`
2. Click **"📞 Initiate New Call"**
3. Enter a phone number (use your own for testing)
4. Click **"Start Call"**
5. Answer the phone and follow the prompts!

### Option 2: Command Line

```bash
python cli.py call initiate --phone +1234567890
```

### Option 3: API Call

```bash
curl -X POST http://localhost:5000/api/calls \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'
```

## What Happens During the Call

The voice agent will:

1. **📞 Call the number** - Your phone rings
2. **✅ Request consent** - "Press 1 to consent, 2 to decline"
3. **❓ Ask HPI questions** - Chief complaint, duration, pain level
4. **💊 Ask AMPLE questions** - Allergies, medications, medical history
5. **👨‍👩‍👧‍👦 Ask family history** - Heart disease, diabetes, cancer
6. **👋 Say goodbye** - "Thank you, a provider will contact you"
7. **💾 Save everything** - Recording, transcript, structured data

## Verify It Worked

### Check the Dashboard
```
http://localhost:5000/dashboard
```
You should see:
- Updated call statistics
- Your call in "Recent Calls"
- Consent status
- Call duration

### Check via CLI
```bash
# List all calls
python cli.py call list

# Get specific call details
python cli.py call get 1

# View transcripts
python cli.py call transcripts 1
```

### Check via API
```bash
curl http://localhost:5000/api/calls
curl http://localhost:5000/api/stats
```

## Common Issues & Solutions

### Issue: "Call not connecting"
**Solutions:**
- ✅ Verify Telnyx webhook URL is correct
- ✅ Check ngrok is still running (it can time out)
- ✅ Ensure your Telnyx number has outbound calling enabled
- ✅ Check application logs for errors

### Issue: "ModuleNotFoundError"
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "Invalid API Key"
**Solutions:**
- ✅ Check `.env` file has correct `TELNYX_API_KEY`
- ✅ Verify no extra spaces or quotes around the key
- ✅ Generate a new API key if needed

### Issue: "Database errors"
**Solution:**
```bash
# Delete and recreate database
rm -rf instance/
python app.py  # This recreates tables
```

### Issue: "Port 5000 already in use"
**Solution:**
```bash
# Kill process using port 5000
# On macOS/Linux:
lsof -ti:5000 | xargs kill -9
# On Windows:
# netstat -ano | findstr :5000
# taskkill /PID <PID> /F

# Or use a different port
python run.py --port 8080
```

## Next Steps

Now that your agent is running:

### 🎨 Customize the Questions
Edit `services/intake_service.py` to modify:
- Consent prompts
- HPI questions
- AMPLE questions
- Family history questions

### 🔌 Connect Your Backend
Update `.env` with your backend API:
```env
BACKEND_API_URL=https://your-api.com/intake
BACKEND_API_KEY=your_key_here
```

### 💾 Enable Storage
Configure MemVerge or ApertureData in `.env`

### 🚀 Deploy to Production
See the [Production Deployment](#production-deployment) section in README.md

### 📊 Explore the API
```bash
# Get API documentation
curl http://localhost:5000/health

# View all endpoints
python cli.py config
```

## Testing Tips

### Test with Your Own Number
- Call yourself first to hear the full experience
- Check audio quality and timing
- Verify transcript accuracy

### Test Different Scenarios
```bash
# Test consent decline
# Answer "2" when prompted for consent

# Test full intake completion
# Answer all questions with valid responses

# Test mid-call hangup
python cli.py call hangup <call_id>
```

### Monitor Logs
```bash
# Watch logs in real-time
tail -f logs/*.log  # if logging to files

# Or check console output
```

## Production Checklist

Before going live:

- [ ] Update `SECRET_KEY` in `.env`
- [ ] Use a production WSGI server (gunicorn)
- [ ] Enable HTTPS (required by Telnyx)
- [ ] Set up monitoring and alerts
- [ ] Configure rate limiting
- [ ] Enable authentication on API endpoints
- [ ] Set up automated backups
- [ ] Review HIPAA compliance requirements
- [ ] Test disaster recovery procedures

## Getting Help

- 📖 **Documentation**: See [README.md](README.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/wildhash/telnyx-patient-intake-agent/issues)
- 💬 **Telnyx Support**: [support.telnyx.com](https://support.telnyx.com)

## Success! 🎉

You now have a fully functional patient intake voice agent!

**What you built:**
- ✅ Automated outbound calling
- ✅ HIPAA-compliant consent collection
- ✅ Structured medical intake (HPI/AMPLE/Family History)
- ✅ Call recording and transcription
- ✅ Web dashboard for monitoring
- ✅ REST API for integration
- ✅ CLI for management

**Time to go live!** 🚀
