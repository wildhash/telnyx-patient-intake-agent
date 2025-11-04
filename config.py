"""
Configuration management for Telnyx Patient Intake Agent
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Telnyx Configuration
    TELNYX_API_KEY = os.getenv('TELNYX_API_KEY')
    TELNYX_PUBLIC_KEY = os.getenv('TELNYX_PUBLIC_KEY')
    TELNYX_CONNECTION_ID = os.getenv('TELNYX_CONNECTION_ID')
    TELNYX_PHONE_NUMBER = os.getenv('TELNYX_PHONE_NUMBER')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    PORT = int(os.getenv('PORT', 5000))
    
    # Public URL (for webhooks)
    PUBLIC_URL = os.getenv('PUBLIC_URL', f'http://localhost:{PORT}')
    
    # Storage Configuration
    MEMVERGE_ENABLED = os.getenv('MEMVERGE_ENABLED', 'false').lower() == 'true'
    MEMVERGE_API_KEY = os.getenv('MEMVERGE_API_KEY')
    MEMVERGE_ENDPOINT = os.getenv('MEMVERGE_ENDPOINT')
    
    APERTUREDATA_ENABLED = os.getenv('APERTUREDATA_ENABLED', 'false').lower() == 'true'
    APERTUREDATA_HOST = os.getenv('APERTUREDATA_HOST', 'localhost')
    APERTUREDATA_PORT = int(os.getenv('APERTUREDATA_PORT', 55555))
    APERTUREDATA_USERNAME = os.getenv('APERTUREDATA_USERNAME', 'admin')
    APERTUREDATA_PASSWORD = os.getenv('APERTUREDATA_PASSWORD')
    
    # Backend API Configuration
    BACKEND_API_URL = os.getenv('BACKEND_API_URL')
    BACKEND_API_KEY = os.getenv('BACKEND_API_KEY')
    
    # Call Configuration
    MAX_CALL_DURATION = int(os.getenv('MAX_CALL_DURATION', 1800))
    RECORDING_ENABLED = os.getenv('RECORDING_ENABLED', 'true').lower() == 'true'
    TRANSCRIPTION_ENABLED = os.getenv('TRANSCRIPTION_ENABLED', 'true').lower() == 'true'
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///patient_intake.db')
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = ['TELNYX_API_KEY', 'TELNYX_CONNECTION_ID', 'TELNYX_PHONE_NUMBER']
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        return True
