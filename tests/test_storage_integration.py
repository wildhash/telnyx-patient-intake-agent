"""
Tests for storage integration
"""
import sys
import os
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storage_integration import LocalJSONStorage, StorageIntegration


def test_local_json_storage_save_intake_note():
    """Test saving intake note to local JSON"""
    storage = LocalJSONStorage()
    
    test_data = {
        'call_id': 'test_123',
        'consent': {'given': True},
        'hpi': {'chief_complaint': {'value': 'test'}}
    }
    
    filepath = storage.save_intake_note('test_123', test_data)
    assert filepath is not None
    assert os.path.exists(filepath)
    
    # Verify content
    with open(filepath, 'r') as f:
        saved_data = json.load(f)
        assert saved_data['call_id'] == 'test_123'
    
    # Cleanup
    os.remove(filepath)


def test_local_json_storage_save_transcript():
    """Test saving transcript to local JSON"""
    storage = LocalJSONStorage()
    
    test_transcript = [
        {'text': 'Hello', 'timestamp': '2024-01-01T00:00:00Z'},
        {'text': 'World', 'timestamp': '2024-01-01T00:00:05Z'}
    ]
    
    filepath = storage.save_transcript('test_123', test_transcript)
    assert filepath is not None
    assert os.path.exists(filepath)
    
    # Verify content
    with open(filepath, 'r') as f:
        saved_data = json.load(f)
        assert len(saved_data) == 2
        assert saved_data[0]['text'] == 'Hello'
    
    # Cleanup
    os.remove(filepath)


def test_storage_integration_save_complete():
    """Test saving complete call data"""
    storage = StorageIntegration()
    
    call_data = {
        'id': 'test_123',
        'phone_number': '+12025551234',
        'status': 'completed'
    }
    
    transcript_data = [
        {'text': 'Test transcript', 'timestamp': '2024-01-01T00:00:00Z'}
    ]
    
    intake_data = {
        'call_id': 'test_123',
        'consent': {'given': True},
        'hpi': {'chief_complaint': {'value': 'test'}}
    }
    
    results = storage.save_complete_call_data(call_data, transcript_data, intake_data)
    
    assert 'local' in results
    assert results['local']['intake_note'] is not None
    assert results['local']['transcript'] is not None
    assert results['local']['metadata'] is not None
    
    # Cleanup
    for key, filepath in results['local'].items():
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
