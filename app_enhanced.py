"""
Enhanced Telnyx Patient Intake Voice Agent
Extended version with storage integration hooks and enhanced features
"""

import os
import sys
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///patient_intake.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
CORS(app)

# Import and initialize database
from models import db, Call, Patient, Transcript
db.init_app(app)

# Import storage integration
from storage_integration import StorageIntegration
storage = StorageIntegration()

# Import and register blueprints
from routes import call_routes, webhook_routes, api_routes, dashboard_routes

app.register_blueprint(call_routes.bp)
app.register_blueprint(webhook_routes.bp)
app.register_blueprint(api_routes.bp)
app.register_blueprint(dashboard_routes.bp)


@app.route('/')
def index():
    """Root endpoint - redirect to dashboard"""
    return render_template('index.html')


@app.route('/health')
@app.route('/healthz')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'telnyx-patient-intake-agent',
        'version': '1.1.0',
        'enhanced': True,
        'storage': {
            'local': True,
            'memverge': os.getenv('MEMVERGE_ENABLED', 'false').lower() == 'true',
            'aperturedata': os.getenv('APERTUREDATA_ENABLED', 'false').lower() == 'true',
            'backend_api': bool(os.getenv('BACKEND_API_URL'))
        }
    })


@app.route('/api/storage/test', methods=['POST'])
def test_storage():
    """
    Test storage integration
    POST with sample data to test all configured storage systems
    """
    try:
        sample_data = request.get_json() or {
            'id': 'test_call_123',
            'phone_number': '+12345678900',
            'status': 'completed'
        }
        
        sample_transcript = [
            {'text': 'Hello, this is a test.', 'timestamp': '2024-01-01T00:00:00Z'},
            {'text': 'This is a test transcript.', 'timestamp': '2024-01-01T00:00:05Z'}
        ]
        
        sample_intake = {
            'call_id': 'test_call_123',
            'consent': {'given': True, 'timestamp': '2024-01-01T00:00:00Z'},
            'hpi': {'chief_complaint': {'value': 'test symptom'}},
            'created_at': '2024-01-01T00:00:00Z'
        }
        
        results = storage.save_complete_call_data(sample_data, sample_transcript, sample_intake)
        
        return jsonify({
            'success': True,
            'message': 'Storage test completed',
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f'Storage test failed')
        return jsonify({
            'success': False,
            'error': 'Storage test failed. Check server logs for details.'
        }), 500


@app.route('/api/intake-notes', methods=['GET'])
def get_intake_notes():
    """Get all locally stored intake notes"""
    try:
        notes = storage.get_all_intake_notes()
        return jsonify({
            'count': len(notes),
            'notes': notes
        }), 200
    except Exception as e:
        logger.error(f'Error fetching intake notes')
        return jsonify({'error': 'Failed to fetch intake notes. Check server logs.'}), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    logger.error(f'Internal server error: {str(e)}')
    return jsonify({'error': 'Internal server error'}), 500


# Enhanced webhook handler with storage integration
@app.after_request
def after_request(response):
    """Log requests and handle storage for completed calls"""
    # This is a hook point for additional processing
    return response


if __name__ == '__main__':
    # Validate configuration
    try:
        from config import Config
        Config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        logger.error("Please check your .env file and ensure all required values are set")
        sys.exit(1)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables created")
    
    # Log storage configuration
    logger.info(f"Storage configuration:")
    logger.info(f"  - Local JSON: Enabled (data/)")
    logger.info(f"  - MemVerge: {os.getenv('MEMVERGE_ENABLED', 'false')}")
    logger.info(f"  - ApertureData: {os.getenv('APERTUREDATA_ENABLED', 'false')}")
    logger.info(f"  - Backend API: {bool(os.getenv('BACKEND_API_URL'))}")
    
    # Run the application
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') == 'development')
