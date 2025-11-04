"""
Webhook routes for handling Telnyx call events
"""

from flask import Blueprint, request, jsonify
from models import db, Call, Transcript
from services.telnyx_service import TelnyxService
from services.intake_service import IntakeService
from services.storage_service import StorageService
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

bp = Blueprint('webhooks', __name__, url_prefix='/webhooks')

# In-memory call state management (consider Redis for production)
call_states = {}


@bp.route('/telnyx', methods=['POST'])
def telnyx_webhook():
    """
    Handle Telnyx call control webhooks
    
    Handles events: call.initiated, call.answered, call.hangup, 
                    call.speak.ended, call.gather.ended, call.recording.saved, etc.
    """
    try:
        data = request.get_json()
        
        if not data or 'data' not in data:
            return jsonify({'error': 'Invalid webhook payload'}), 400
        
        event_type = data.get('data', {}).get('event_type')
        payload = data.get('data', {}).get('payload', {})
        
        logger.info(f"Received Telnyx webhook: {event_type}")
        
        # Route to appropriate handler
        if event_type == 'call.initiated':
            return handle_call_initiated(payload)
        elif event_type == 'call.answered':
            return handle_call_answered(payload)
        elif event_type == 'call.hangup':
            return handle_call_hangup(payload)
        elif event_type == 'call.speak.ended':
            return handle_speak_ended(payload)
        elif event_type == 'call.gather.ended':
            return handle_gather_ended(payload)
        elif event_type == 'call.recording.saved':
            return handle_recording_saved(payload)
        elif event_type == 'call.transcription':
            return handle_transcription(payload)
        else:
            logger.info(f"Unhandled event type: {event_type}")
            return jsonify({'status': 'ignored'}), 200
        
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


def handle_call_initiated(payload):
    """Handle call initiated event"""
    call_control_id = payload.get('call_control_id')
    
    call = Call.query.filter_by(call_control_id=call_control_id).first()
    if call:
        call.status = 'ringing'
        db.session.commit()
        logger.info(f"Call {call.id} is ringing")
    
    return jsonify({'status': 'ok'}), 200


def handle_call_answered(payload):
    """Handle call answered event - start the intake flow"""
    call_control_id = payload.get('call_control_id')
    
    call = Call.query.filter_by(call_control_id=call_control_id).first()
    if not call:
        logger.error(f"Call not found: {call_control_id}")
        return jsonify({'error': 'Call not found'}), 404
    
    call.status = 'answered'
    call.answered_at = datetime.utcnow()
    db.session.commit()
    
    # Initialize call state
    call_states[call_control_id] = {
        'call_id': call.id,
        'stage': 'consent',
        'current_section': 'hpi',
        'question_index': 0,
        'responses': {}
    }
    
    # Start with consent
    intake_service = IntakeService()
    consent_prompt = intake_service.get_consent_prompt()
    
    TelnyxService.gather_using_speak(
        call_control_id,
        consent_prompt['intro'],
        valid_digits=consent_prompt['valid_digits'],
        max_digits=consent_prompt['max_digits']
    )
    
    logger.info(f"Call {call.id} answered, requesting consent")
    
    return jsonify({'status': 'ok'}), 200


def handle_call_hangup(payload):
    """Handle call hangup event"""
    call_control_id = payload.get('call_control_id')
    
    call = Call.query.filter_by(call_control_id=call_control_id).first()
    if not call:
        return jsonify({'status': 'ok'}), 200
    
    call.status = 'completed'
    call.ended_at = datetime.utcnow()
    
    if call.answered_at:
        duration = (call.ended_at - call.answered_at).total_seconds()
        call.duration_seconds = int(duration)
    
    # Get call state and save intake data
    state = call_states.get(call_control_id, {})
    if state.get('responses'):
        intake_service = IntakeService()
        intake_data = intake_service.format_intake_data(state)
        call.set_intake_data(intake_data)
    
    db.session.commit()
    
    # Push to storage systems
    transcripts = Transcript.query.filter_by(call_id=call.id).all()
    transcript_data = [t.to_dict() for t in transcripts]
    
    storage_results = StorageService.push_all(call.to_dict(), transcript_data)
    
    # Update call with storage IDs
    if storage_results.get('memverge_id'):
        call.memverge_id = storage_results['memverge_id']
    if storage_results.get('aperturedata_id'):
        call.aperturedata_id = storage_results['aperturedata_id']
    if storage_results.get('backend_pushed'):
        call.backend_pushed = True
        call.backend_pushed_at = datetime.utcnow()
    
    db.session.commit()
    
    # Clean up call state
    if call_control_id in call_states:
        del call_states[call_control_id]
    
    logger.info(f"Call {call.id} completed, duration: {call.duration_seconds}s")
    
    return jsonify({'status': 'ok'}), 200


def handle_speak_ended(payload):
    """Handle speak ended event - conversation flow continues"""
    # This event fires after TTS finishes speaking
    # Usually followed by gather_ended if we're collecting input
    return jsonify({'status': 'ok'}), 200


def handle_gather_ended(payload):
    """Handle gather ended event - process user input"""
    call_control_id = payload.get('call_control_id')
    digits = payload.get('digits', '')
    
    state = call_states.get(call_control_id)
    if not state:
        logger.error(f"Call state not found: {call_control_id}")
        return jsonify({'error': 'Call state not found'}), 404
    
    call = Call.query.get(state['call_id'])
    intake_service = IntakeService()
    
    # Handle consent
    if state['stage'] == 'consent':
        if digits == '1':
            call.consent_given = True
            call.consent_timestamp = datetime.utcnow()
            state['stage'] = 'intake'
            state['consent_given'] = True
            state['consent_timestamp'] = datetime.utcnow().isoformat()
            db.session.commit()
            
            # Start intake questions
            TelnyxService.speak(call_control_id, "Thank you for providing consent. Let's begin with a few health questions.")
            
            # Ask first question
            question = intake_service.get_next_question(state)
            if question:
                ask_question(call_control_id, question, state)
        else:
            # Consent declined
            TelnyxService.speak(call_control_id, "I understand. Thank you for your time. Goodbye.")
            TelnyxService.hangup(call_control_id)
            
            call.consent_given = False
            call.status = 'completed'
            db.session.commit()
    
    # Handle intake questions
    elif state['stage'] == 'intake':
        # Get current question
        current_section = state.get('current_section', 'hpi')
        question_index = state.get('question_index', 0)
        
        # Find the question that was just answered
        if current_section == 'hpi':
            questions = intake_service.script.HPI_QUESTIONS
        elif current_section == 'ample':
            questions = intake_service.script.AMPLE_QUESTIONS
        elif current_section == 'family_history':
            questions = intake_service.script.FAMILY_HISTORY_QUESTIONS
        else:
            questions = []
        
        if question_index < len(questions):
            current_question = questions[question_index]
            
            # Process the response
            intake_service.process_response(state, current_question['key'], digits)
            
            # Get next question
            next_question = intake_service.get_next_question(state)
            
            if next_question:
                ask_question(call_control_id, next_question, state)
            else:
                # Intake complete
                finish_intake(call_control_id, call, state)
    
    return jsonify({'status': 'ok'}), 200


def ask_question(call_control_id, question, state):
    """Ask a question to the patient"""
    if question['type'] == 'dtmf':
        TelnyxService.gather_using_speak(
            call_control_id,
            question['question'],
            valid_digits=question.get('valid_digits', '12'),
            max_digits=question.get('max_digits', 1)
        )
    else:
        # For voice questions, we'd use record or gather_using_audio
        # For simplicity, using speak
        TelnyxService.speak(call_control_id, question['question'])


def finish_intake(call_control_id, call, state):
    """Finish the intake process"""
    intake_service = IntakeService()
    
    # Save intake data
    intake_data = intake_service.format_intake_data(state)
    call.set_intake_data(intake_data)
    db.session.commit()
    
    # Say goodbye
    closing_message = intake_service.get_closing_message()
    TelnyxService.speak(call_control_id, closing_message)
    
    # Hang up after a delay (Telnyx will handle this after speak ends)
    # The call.hangup event will trigger the storage push
    logger.info(f"Intake completed for call {call.id}")


def handle_recording_saved(payload):
    """Handle recording saved event"""
    call_control_id = payload.get('call_control_id')
    recording_url = payload.get('recording_urls', {}).get('mp3')
    recording_id = payload.get('recording_id')
    
    call = Call.query.filter_by(call_control_id=call_control_id).first()
    if call:
        call.recording_url = recording_url
        call.recording_id = recording_id
        db.session.commit()
        logger.info(f"Recording saved for call {call.id}: {recording_url}")
    
    return jsonify({'status': 'ok'}), 200


def handle_transcription(payload):
    """Handle real-time transcription events"""
    call_control_id = payload.get('call_control_id')
    transcript_text = payload.get('transcript', '')
    is_final = payload.get('is_final', False)
    confidence = payload.get('confidence', 0.0)
    
    call = Call.query.filter_by(call_control_id=call_control_id).first()
    if not call:
        return jsonify({'status': 'ok'}), 200
    
    # Save transcript segment
    state = call_states.get(call_control_id, {})
    sequence = len(Transcript.query.filter_by(call_id=call.id).all())
    
    transcript = Transcript(
        call_id=call.id,
        speaker='patient',  # Would need speaker diarization for accurate detection
        text=transcript_text,
        confidence=confidence,
        is_final=is_final,
        sequence=sequence
    )
    db.session.add(transcript)
    db.session.commit()
    
    logger.info(f"Transcript saved for call {call.id}: {transcript_text[:50]}...")
    
    return jsonify({'status': 'ok'}), 200
