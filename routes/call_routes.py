"""
Call management routes for initiating and managing calls
"""

from flask import Blueprint, request, jsonify
from models import db, Call, Patient
from services.telnyx_service import TelnyxService
from config import Config
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('calls', __name__, url_prefix='/api/calls')


@bp.route('', methods=['POST'])
def initiate_call():
    """
    Initiate an outbound call to a patient
    
    Expected JSON body:
    {
        "phone_number": "+1234567890",
        "patient_id": 123  # optional
    }
    """
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        patient_id = data.get('patient_id')
        
        if not phone_number:
            return jsonify({'error': 'phone_number is required'}), 400
        
        # Get or create patient
        patient = None
        if patient_id:
            patient = Patient.query.get(patient_id)
        else:
            patient = Patient.query.filter_by(phone_number=phone_number).first()
            if not patient:
                patient = Patient(phone_number=phone_number)
                db.session.add(patient)
                db.session.commit()
        
        # Build webhook URL
        webhook_url = f"{Config.PUBLIC_URL}/webhooks/telnyx"
        
        # Initiate call via Telnyx
        call_data = TelnyxService.initiate_call(phone_number, webhook_url)
        
        # Create call record
        call = Call(
            call_control_id=call_data['call_control_id'],
            call_leg_id=call_data['call_leg_id'],
            call_session_id=call_data['call_session_id'],
            patient_id=patient.id,
            status='initiated',
            from_number=Config.TELNYX_PHONE_NUMBER,
            to_number=phone_number
        )
        db.session.add(call)
        db.session.commit()
        
        logger.info(f"Call initiated: {call.id}")
        
        return jsonify({
            'success': True,
            'call_id': call.id,
            'call_control_id': call.call_control_id,
            'status': call.status
        }), 201
        
    except Exception as e:
        logger.error(f"Error initiating call: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to initiate call'}), 500


@bp.route('/<int:call_id>', methods=['GET'])
def get_call(call_id):
    """Get call details"""
    call = Call.query.get_or_404(call_id)
    return jsonify(call.to_dict())


@bp.route('/<int:call_id>/hangup', methods=['POST'])
def hangup_call(call_id):
    """Hang up an active call"""
    try:
        call = Call.query.get_or_404(call_id)
        
        if call.status in ['completed', 'failed']:
            return jsonify({'error': 'Call already ended'}), 400
        
        # Hang up via Telnyx
        TelnyxService.hangup(call.call_control_id)
        
        call.status = 'completed'
        db.session.commit()
        
        return jsonify({'success': True, 'status': call.status})
        
    except Exception as e:
        logger.error(f"Error hanging up call: {str(e)}")
        return jsonify({'error': 'Failed to hang up call'}), 500


@bp.route('', methods=['GET'])
def list_calls():
    """List all calls with optional filtering"""
    status = request.args.get('status')
    patient_id = request.args.get('patient_id')
    limit = request.args.get('limit', 50, type=int)
    
    query = Call.query
    
    if status:
        query = query.filter_by(status=status)
    if patient_id:
        query = query.filter_by(patient_id=patient_id)
    
    calls = query.order_by(Call.created_at.desc()).limit(limit).all()
    
    return jsonify({
        'calls': [call.to_dict() for call in calls],
        'total': len(calls)
    })
