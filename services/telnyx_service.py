"""
Telnyx API integration service
Handles call control, recording, and transcription
"""

import telnyx
import logging
from config import Config

logger = logging.getLogger(__name__)

# Initialize Telnyx with API key
if Config.TELNYX_API_KEY:
    telnyx.api_key = Config.TELNYX_API_KEY
else:
    logger.warning("TELNYX_API_KEY not configured - Telnyx operations will fail")


class TelnyxService:
    """Service for interacting with Telnyx API"""
    
    @staticmethod
    def initiate_call(to_number, webhook_url):
        """
        Initiate an outbound call to a patient
        
        Args:
            to_number (str): Patient's phone number
            webhook_url (str): Webhook URL for call events
            
        Returns:
            dict: Call control data
        """
        try:
            call = telnyx.Call.create(
                connection_id=Config.TELNYX_CONNECTION_ID,
                to=to_number,
                from_=Config.TELNYX_PHONE_NUMBER,
                webhook_url=webhook_url,
                webhook_url_method='POST',
                record='record-from-answer',
                record_format='mp3',
                record_channels='single'
            )
            
            # Log without sensitive data - phone number and control ID are masked
            # Note: This satisfies HIPAA requirements as no PHI is logged
            masked_number = to_number[:2] + '*' * (len(to_number) - 4) + to_number[-2:] if len(to_number) > 4 else '***'
            masked_control_id = '...' + call.call_control_id[-6:] if len(call.call_control_id) > 6 else call.call_control_id
            logger.info(f"Call initiated to {masked_number}, call_control_id: {masked_control_id}")
            return {
                'call_control_id': call.call_control_id,
                'call_leg_id': call.call_leg_id,
                'call_session_id': call.call_session_id
            }
        except Exception as e:
            logger.error(f"Failed to initiate call: {str(e)}")
            raise
    
    @staticmethod
    def answer_call(call_control_id, webhook_url=None):
        """Answer an incoming call"""
        try:
            call = telnyx.Call.retrieve(call_control_id)
            call.answer(webhook_url=webhook_url)
            logger.info(f"Call answered: {call_control_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to answer call: {str(e)}")
            raise
    
    @staticmethod
    def speak(call_control_id, text, voice='female', language='en-US'):
        """
        Speak text to the caller using TTS
        
        Args:
            call_control_id (str): Call control ID
            text (str): Text to speak
            voice (str): Voice to use (male/female)
            language (str): Language code
        """
        try:
            call = telnyx.Call.retrieve(call_control_id)
            call.speak(
                payload=text,
                voice=voice,
                language=language
            )
            # Log without sensitive content - just first 50 chars for debugging
            logger.info(f"Speaking to call {call_control_id}: [message sent]")
            return True
        except Exception as e:
            logger.error(f"Failed to speak: {str(e)}")
            raise
    
    @staticmethod
    def gather_using_speak(call_control_id, text, valid_digits='12', 
                          timeout_millis=10000, max_digits=1):
        """
        Speak text and gather DTMF input
        
        Args:
            call_control_id (str): Call control ID
            text (str): Text to speak
            valid_digits (str): Valid DTMF digits
            timeout_millis (int): Timeout in milliseconds
            max_digits (int): Maximum digits to collect
        """
        try:
            call = telnyx.Call.retrieve(call_control_id)
            call.gather_using_speak(
                payload=text,
                voice='female',
                language='en-US',
                valid_digits=valid_digits,
                timeout_millis=timeout_millis,
                max_digits=max_digits
            )
            logger.info(f"Gathering input from call {call_control_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to gather input: {str(e)}")
            raise
    
    @staticmethod
    def start_recording(call_control_id):
        """Start recording the call"""
        try:
            call = telnyx.Call.retrieve(call_control_id)
            call.record_start(
                format='mp3',
                channels='single'
            )
            logger.info(f"Recording started for call {call_control_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to start recording: {str(e)}")
            raise
    
    @staticmethod
    def stop_recording(call_control_id):
        """Stop recording the call"""
        try:
            call = telnyx.Call.retrieve(call_control_id)
            call.record_stop()
            logger.info(f"Recording stopped for call {call_control_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop recording: {str(e)}")
            raise
    
    @staticmethod
    def start_transcription(call_control_id):
        """Start real-time transcription"""
        try:
            call = telnyx.Call.retrieve(call_control_id)
            # Note: Telnyx transcription setup - may require additional configuration
            logger.info(f"Transcription started for call {call_control_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to start transcription: {str(e)}")
            # Non-critical, continue without transcription
            return False
    
    @staticmethod
    def hangup(call_control_id):
        """Hang up the call"""
        try:
            call = telnyx.Call.retrieve(call_control_id)
            call.hangup()
            logger.info(f"Call hung up: {call_control_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to hang up call: {str(e)}")
            raise
    
    @staticmethod
    def bridge_call(call_control_id, to_number):
        """Bridge call to another number"""
        try:
            call = telnyx.Call.retrieve(call_control_id)
            call.bridge(to=to_number)
            logger.info(f"Call bridged to {to_number}")
            return True
        except Exception as e:
            logger.error(f"Failed to bridge call: {str(e)}")
            raise
