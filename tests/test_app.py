"""
Basic tests for Flask application
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app


@pytest.fixture
def app():
    """Create application for testing"""
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return flask_app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'telnyx-patient-intake-agent'


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get('/')
    assert response.status_code == 200


def test_404_handler(client):
    """Test 404 error handler"""
    response = client.get('/nonexistent')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data
