"""
REST API routes for managing patients, calls, and transcripts
"""

from flask import Blueprint, request, jsonify
from models import db, Patient, Call, Transcript
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('api', __name__, url_prefix='/api')


# Patient endpoints
@bp.route('/patients', methods=['GET'])
def list_patients():
    """List all patients"""
    patients = Patient.query.order_by(Patient.created_at.desc()).all()
    return jsonify({
        'patients': [p.to_dict() for p in patients],
        'total': len(patients)
    })


@bp.route('/patients', methods=['POST'])
def create_patient():
    """Create a new patient"""
    try:
        data = request.get_json()
        
        phone_number = data.get('phone_number')
        if not phone_number:
            return jsonify({'error': 'phone_number is required'}), 400
        
        # Check if patient exists
        existing = Patient.query.filter_by(phone_number=phone_number).first()
        if existing:
            return jsonify({'error': 'Patient with this phone number already exists'}), 409
        
        patient = Patient(
            phone_number=phone_number,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email')
        )
        
        # Parse date of birth if provided
        dob_str = data.get('date_of_birth')
        if dob_str:
            try:
                patient.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date_of_birth format. Use YYYY-MM-DD'}), 400
        
        db.session.add(patient)
        db.session.commit()
        
        return jsonify(patient.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Error creating patient: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get patient details"""
    patient = Patient.query.get_or_404(patient_id)
    return jsonify(patient.to_dict())


@bp.route('/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """Update patient information"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        data = request.get_json()
        
        # Update fields
        if 'first_name' in data:
            patient.first_name = data['first_name']
        if 'last_name' in data:
            patient.last_name = data['last_name']
        if 'email' in data:
            patient.email = data['email']
        if 'phone_number' in data:
            patient.phone_number = data['phone_number']
        if 'date_of_birth' in data:
            try:
                patient.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date_of_birth format. Use YYYY-MM-DD'}), 400
        
        db.session.commit()
        return jsonify(patient.to_dict())
        
    except Exception as e:
        logger.error(f"Error updating patient: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/patients/<int:patient_id>/calls', methods=['GET'])
def get_patient_calls(patient_id):
    """Get all calls for a patient"""
    patient = Patient.query.get_or_404(patient_id)
    calls = Call.query.filter_by(patient_id=patient_id).order_by(Call.created_at.desc()).all()
    
    return jsonify({
        'patient': patient.to_dict(),
        'calls': [c.to_dict() for c in calls],
        'total_calls': len(calls)
    })


# Transcript endpoints
@bp.route('/calls/<int:call_id>/transcripts', methods=['GET'])
def get_call_transcripts(call_id):
    """Get all transcripts for a call"""
    call = Call.query.get_or_404(call_id)
    transcripts = Transcript.query.filter_by(call_id=call_id).order_by(Transcript.sequence).all()
    
    return jsonify({
        'call_id': call_id,
        'transcripts': [t.to_dict() for t in transcripts],
        'total': len(transcripts)
    })


@bp.route('/calls/<int:call_id>/intake-data', methods=['GET'])
def get_intake_data(call_id):
    """Get structured intake data for a call"""
    call = Call.query.get_or_404(call_id)
    
    return jsonify({
        'call_id': call_id,
        'intake_data': call.get_intake_data(),
        'consent_given': call.consent_given,
        'consent_timestamp': call.consent_timestamp.isoformat() if call.consent_timestamp else None
    })


# Statistics endpoint
@bp.route('/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    total_patients = Patient.query.count()
    total_calls = Call.query.count()
    completed_calls = Call.query.filter_by(status='completed').count()
    active_calls = Call.query.filter(Call.status.in_(['initiated', 'ringing', 'answered'])).count()
    consented_calls = Call.query.filter_by(consent_given=True).count()
    
    return jsonify({
        'total_patients': total_patients,
        'total_calls': total_calls,
        'completed_calls': completed_calls,
        'active_calls': active_calls,
        'consented_calls': consented_calls,
        'consent_rate': round(consented_calls / total_calls * 100, 2) if total_calls > 0 else 0
    })
