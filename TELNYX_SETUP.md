# Telnyx Setup Guide

Complete guide for configuring Telnyx portal and webhooks for the Patient Intake Agent.

## Prerequisites

- A Telnyx account ([sign up here](https://telnyx.com/sign-up))
- A Telnyx phone number
- Basic understanding of webhooks

## Step 1: Create Telnyx Account

1. Go to [https://telnyx.com/sign-up](https://telnyx.com/sign-up)
2. Complete the registration process
3. Verify your email address
4. Complete identity verification (required for phone number purchases)

## Step 2: Purchase a Phone Number

1. Log in to [Telnyx Mission Control](https://portal.telnyx.com/)
2. Navigate to **Numbers** → **My Numbers**
3. Click **Buy Numbers**
4. Search for available numbers by:
   - Area code
   - Location
   - Features (make sure Voice is enabled)
5. Select a number and complete the purchase
6. Note your phone number (you'll need it for configuration)

**Example format:** `+12025551234`

## Step 3: Create a Call Control Application

1. In Mission Control, navigate to **Voice** → **Call Control**
2. Click **Create Call Control Application**
3. Fill in the application details:

   **Application Name:** `Patient Intake Agent`
   
   **Webhook URL:** Your application's webhook endpoint
   - For local development with ngrok: `https://your-ngrok-url.ngrok.io/webhooks/telnyx`
   - For production: `https://your-domain.com/webhooks/telnyx`
   
   **Webhook API Version:** `V2` (recommended)
   
   **Webhook Timeout:** `30000` ms (30 seconds)
   
   **Webhook Failover URL:** (Optional) A backup webhook URL
   
4. Enable the following webhook events:
   - ✅ `call.initiated`
   - ✅ `call.answered`
   - ✅ `call.hangup`
   - ✅ `call.speak.started`
   - ✅ `call.speak.ended`
   - ✅ `call.gather.started`
   - ✅ `call.gather.ended`
   - ✅ `call.recording.saved`
   - ✅ `call.transcription`

5. Click **Save**

6. **Important:** Copy your **Connection ID** from the application page
   - You'll need this for your `.env` file

## Step 4: Get Your API Key

1. In Mission Control, click your profile icon (top right)
2. Select **API Keys**
3. Click **Create API Key**
4. Choose:
   - **Key Type:** `Standard`
   - **Description:** `Patient Intake Agent`
5. Click **Create**
6. **Important:** Copy and securely save your API key immediately
   - It will only be shown once!
   - Store it in a password manager or secure location

## Step 5: Link Phone Number to Application

1. Navigate to **Numbers** → **My Numbers**
2. Find your purchased phone number
3. Click on the number to edit settings
4. Under **Voice Settings**:
   - **Connection:** Select your Call Control Application (`Patient Intake Agent`)
   - **Connection Type:** `Call Control`
5. Click **Save**

## Step 6: Configure Your Application

Update your `.env` file with the Telnyx credentials:

```env
# Telnyx Configuration
TELNYX_API_KEY=KEY0123456789ABCDEF...
TELNYX_CONNECTION_ID=1234567890
TELNYX_PHONE_NUMBER=+12025551234
```

## Step 7: Enable Recording (Optional but Recommended)

1. In your Call Control Application settings
2. Navigate to **Recording** section
3. Enable **Call Recording**
4. Configure recording settings:
   - **Format:** `mp3` (recommended for web playback)
   - **Channels:** `dual` (separate agent and caller audio)
   - **Trim Silence:** `false` (keep full recording)

## Step 8: Enable Transcription (Optional but Recommended)

1. In your Call Control Application settings
2. Navigate to **Transcription** section
3. Enable **Real-Time Transcription**
4. Configure transcription settings:
   - **Language:** `en-US` (or your preferred language)
   - **Model:** `whisper-turbo` (recommended for speed and accuracy)
   - **Interim Results:** `true` (for live updates)

## Step 9: Test Webhook Connection

### Using ngrok for Local Development

1. Start ngrok:
   ```bash
   python ngrok_helper.py
   ```
   
2. Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

3. Update your Call Control Application webhook URL:
   ```
   https://abc123.ngrok.io/webhooks/telnyx
   ```

4. Test the connection:
   ```bash
   curl -X POST https://abc123.ngrok.io/webhooks/telnyx \
     -H "Content-Type: application/json" \
     -d '{"data":{"event_type":"call.initiated"}}'
   ```

### Verify Webhook Signature (Production)

For production, enable webhook signature verification:

1. In Call Control Application settings
2. Find **Webhook Signing Secret**
3. Copy the secret
4. Add to `.env`:
   ```env
   TELNYX_PUBLIC_KEY=your_webhook_signing_secret
   ```

5. Implement signature verification in your webhook handler (see `routes/webhook_routes.py`)

## Step 10: Make a Test Call

### Using the Web Dashboard

1. Start your Flask application
2. Open http://localhost:5000/dashboard
3. Enter a test phone number
4. Click "Initiate Call"
5. Monitor the call in real-time

### Using the CLI

```bash
python test_call.py call +12025551234
```

### Using curl

```bash
curl -X POST http://localhost:5000/api/calls \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+12025551234"}'
```

## Troubleshooting

### Issue: Webhooks not received

**Solutions:**
- Verify webhook URL is publicly accessible (use ngrok for local dev)
- Check that URL ends with `/webhooks/telnyx`
- Ensure Flask app is running
- Check firewall settings
- Verify webhook events are enabled in Call Control Application

### Issue: "Unauthorized" error

**Solutions:**
- Verify `TELNYX_API_KEY` is correct
- Check API key has not expired
- Ensure no extra spaces in `.env` file

### Issue: Phone number not working

**Solutions:**
- Verify phone number is linked to Call Control Application
- Check number is in E.164 format (`+12025551234`)
- Ensure number has voice capabilities
- Verify your Telnyx account has sufficient balance

### Issue: Recording not available

**Solutions:**
- Check recording is enabled in Call Control Application
- Wait 30-60 seconds after call ends for processing
- Verify storage permissions in Telnyx settings
- Check webhook for `call.recording.saved` event

### Issue: Transcription not working

**Solutions:**
- Verify transcription is enabled in Call Control Application
- Check that `whisper-turbo` model is available in your region
- Ensure webhook for `call.transcription` events is enabled
- Check application logs for transcription errors

## Webhook Event Reference

### call.initiated
Fired when an outbound call is initiated.

### call.answered
Fired when the call is answered by the recipient.

### call.hangup
Fired when the call ends (by either party).

### call.recording.saved
Fired when call recording is processed and available for download.

### call.transcription
Fired when transcription segments are available (real-time).

### call.speak.started / ended
Fired when text-to-speech starts/ends.

### call.gather.started / ended
Fired when collecting DTMF digits starts/ends.

## Additional Resources

- [Telnyx Call Control API Documentation](https://developers.telnyx.com/docs/api/v2/call-control)
- [Telnyx Webhook Guide](https://developers.telnyx.com/docs/v2/development/webhooks)
- [Telnyx Portal](https://portal.telnyx.com/)
- [Telnyx Support](https://support.telnyx.com/)

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use webhook signature verification** in production
3. **Use HTTPS** for webhook endpoints (required by Telnyx)
4. **Rotate API keys** regularly
5. **Limit API key permissions** to only what's needed
6. **Monitor webhook logs** for suspicious activity
7. **Implement rate limiting** on webhook endpoints

## Cost Considerations

Telnyx charges for:
- Phone number rental (monthly)
- Outbound call minutes
- Recording storage
- Transcription minutes (if enabled)

Check current pricing at: [https://telnyx.com/pricing](https://telnyx.com/pricing)

**Tip:** For testing, use short calls and consider disabling recording/transcription to minimize costs.

## Support

If you need help with Telnyx setup:
- **Documentation:** [developers.telnyx.com](https://developers.telnyx.com/)
- **Support:** [support.telnyx.com](https://support.telnyx.com/)
- **Community:** [Telnyx Community Forum](https://community.telnyx.com/)
- **Status:** [status.telnyx.com](https://status.telnyx.com/)

---

**You're all set!** Your Telnyx account is now configured for the Patient Intake Agent. 🎉
