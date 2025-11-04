"""
Database models for patient intake system
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class Patient(db.Model):
    """Patient information model"""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    date_of_birth = db.Column(db.Date)
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    calls = db.relationship('Call', backref='patient', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Call(db.Model):
    """Call session model"""
    __tablename__ = 'calls'
    
    id = db.Column(db.Integer, primary_key=True)
    call_control_id = db.Column(db.String(100), unique=True)
    call_leg_id = db.Column(db.String(100))
    call_session_id = db.Column(db.String(100))
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'))
    
    # Call details
    status = db.Column(db.String(20), default='initiated')  # initiated, ringing, answered, completed, failed
    direction = db.Column(db.String(10), default='outbound')
    from_number = db.Column(db.String(20))
    to_number = db.Column(db.String(20))
    
    # Consent and intake
    consent_given = db.Column(db.Boolean, default=False)
    consent_timestamp = db.Column(db.DateTime)
    
    # Call timeline
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    answered_at = db.Column(db.DateTime)
    ended_at = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer)
    
    # Recording and transcription
    recording_url = db.Column(db.String(500))
    recording_id = db.Column(db.String(100))
    
    # Intake data (stored as JSON)
    intake_data = db.Column(db.Text)  # JSON string with HPI, AMPLE, family history
    
    # Storage references
    memverge_id = db.Column(db.String(100))
    aperturedata_id = db.Column(db.String(100))
    backend_pushed = db.Column(db.Boolean, default=False)
    backend_pushed_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transcripts = db.relationship('Transcript', backref='call', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'call_control_id': self.call_control_id,
            'call_leg_id': self.call_leg_id,
            'call_session_id': self.call_session_id,
            'patient_id': self.patient_id,
            'status': self.status,
            'direction': self.direction,
            'from_number': self.from_number,
            'to_number': self.to_number,
            'consent_given': self.consent_given,
            'consent_timestamp': self.consent_timestamp.isoformat() if self.consent_timestamp else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'answered_at': self.answered_at.isoformat() if self.answered_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'duration_seconds': self.duration_seconds,
            'recording_url': self.recording_url,
            'intake_data': json.loads(self.intake_data) if self.intake_data else None,
            'memverge_id': self.memverge_id,
            'aperturedata_id': self.aperturedata_id,
            'backend_pushed': self.backend_pushed,
            'backend_pushed_at': self.backend_pushed_at.isoformat() if self.backend_pushed_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def get_intake_data(self):
        """Parse and return intake data as dictionary"""
        if self.intake_data:
            return json.loads(self.intake_data)
        return {}
    
    def set_intake_data(self, data):
        """Set intake data from dictionary"""
        self.intake_data = json.dumps(data)


class Transcript(db.Model):
    """Transcript segments from live transcription"""
    __tablename__ = 'transcripts'
    
    id = db.Column(db.Integer, primary_key=True)
    call_id = db.Column(db.Integer, db.ForeignKey('calls.id'), nullable=False)
    
    # Transcript details
    speaker = db.Column(db.String(20))  # 'agent' or 'patient'
    text = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sequence = db.Column(db.Integer)  # Order in conversation
    
    # Metadata
    is_final = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'call_id': self.call_id,
            'speaker': self.speaker,
            'text': self.text,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'sequence': self.sequence,
            'is_final': self.is_final,
            'created_at': self.created_at.isoformat()
        }
