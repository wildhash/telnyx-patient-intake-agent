"""
Storage integration wrapper
Provides unified interface for local JSON persistence, MemVerge, and ApertureData
"""

import json
import os
import logging
from datetime import datetime
from pathlib import Path
from services.storage_service import StorageService

logger = logging.getLogger(__name__)

# Data directory for local persistence
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


class LocalJSONStorage:
    """Local JSON file persistence"""
    
    @staticmethod
    def save_intake_note(call_id, intake_data):
        """
        Save intake note to local JSON file
        
        Args:
            call_id (str): Call identifier
            intake_data (dict): Intake note data
            
        Returns:
            str: File path where data was saved
        """
        try:
            filename = f"intake_{call_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = DATA_DIR / filename
            
            with open(filepath, 'w') as f:
                json.dump(intake_data, f, indent=2, default=str)
            
            logger.info(f"Saved intake note to {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error saving intake note locally: {str(e)}")
            return None
    
    @staticmethod
    def save_transcript(call_id, transcript_data):
        """
        Save transcript to local JSON file
        
        Args:
            call_id (str): Call identifier
            transcript_data (list): Transcript segments
            
        Returns:
            str: File path where data was saved
        """
        try:
            filename = f"transcript_{call_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = DATA_DIR / filename
            
            with open(filepath, 'w') as f:
                json.dump(transcript_data, f, indent=2, default=str)
            
            logger.info(f"Saved transcript to {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error saving transcript locally: {str(e)}")
            return None
    
    @staticmethod
    def save_call_metadata(call_id, metadata):
        """
        Save call metadata to local JSON file
        
        Args:
            call_id (str): Call identifier
            metadata (dict): Call metadata
            
        Returns:
            str: File path where data was saved
        """
        try:
            filename = f"call_metadata_{call_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = DATA_DIR / filename
            
            with open(filepath, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            logger.info(f"Saved call metadata to {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error saving call metadata locally: {str(e)}")
            return None
    
    @staticmethod
    def get_intake_notes():
        """
        Get all intake notes from local storage
        
        Returns:
            list: List of intake note data
        """
        try:
            notes = []
            for filepath in DATA_DIR.glob("intake_*.json"):
                with open(filepath, 'r') as f:
                    notes.append(json.load(f))
            return notes
        except Exception as e:
            logger.error(f"Error reading intake notes: {str(e)}")
            return []


class StorageIntegration:
    """
    Unified storage interface that handles:
    - Local JSON persistence (always enabled)
    - MemVerge hot storage (optional)
    - ApertureData cold storage (optional)
    - Backend API push (optional)
    """
    
    def __init__(self):
        self.local_storage = LocalJSONStorage()
        self.storage_service = StorageService()
    
    def save_complete_call_data(self, call_data, transcript_data, intake_data):
        """
        Save complete call data to all configured storage systems
        
        Args:
            call_data (dict): Call metadata
            transcript_data (list): Transcript segments
            intake_data (dict): Structured intake note
            
        Returns:
            dict: Results from each storage system
        """
        results = {
            'local': {},
            'memverge_id': None,
            'aperturedata_id': None,
            'backend_pushed': False
        }
        
        # Always save locally
        call_id = call_data.get('id', 'unknown')
        results['local']['intake_note'] = self.local_storage.save_intake_note(call_id, intake_data)
        results['local']['transcript'] = self.local_storage.save_transcript(call_id, transcript_data)
        results['local']['metadata'] = self.local_storage.save_call_metadata(call_id, call_data)
        
        # Push to external storage systems
        external_results = self.storage_service.push_all(call_data, transcript_data)
        results.update(external_results)
        
        logger.info(f"Saved call data for {call_id}: {results}")
        return results
    
    def save_intake_note(self, call_id, intake_data):
        """
        Save just the intake note
        
        Args:
            call_id (str): Call identifier
            intake_data (dict): Intake note data
            
        Returns:
            str: Local file path
        """
        return self.local_storage.save_intake_note(call_id, intake_data)
    
    def get_all_intake_notes(self):
        """
        Retrieve all intake notes from local storage
        
        Returns:
            list: List of intake notes
        """
        return self.local_storage.get_intake_notes()


# MemVerge Stub
class MemVergeStorage:
    """
    Stub for MemVerge hot storage integration
    
    MemVerge provides in-memory data storage optimized for hot data access.
    This stub shows the expected interface for production integration.
    
    To enable:
    1. Set MEMVERGE_ENABLED=true in .env
    2. Configure MEMVERGE_API_KEY and MEMVERGE_ENDPOINT
    3. Install memverge client: pip install memverge-client (if available)
    """
    
    @staticmethod
    def push(data):
        """
        Push data to MemVerge hot storage
        
        Args:
            data (dict): Data to store
            
        Returns:
            str: Object ID from MemVerge
        """
        # In production, use the actual MemVerge client
        # from memverge import Client
        # client = Client(api_key=Config.MEMVERGE_API_KEY, endpoint=Config.MEMVERGE_ENDPOINT)
        # result = client.store(data)
        # return result.object_id
        
        return StorageService.push_to_memverge(data, data.get('transcripts', []))


# ApertureData Stub
class ApertureDataStorage:
    """
    Stub for ApertureData cold storage integration
    
    ApertureData provides visual database for long-term storage and retrieval.
    This stub shows the expected interface for production integration.
    
    To enable:
    1. Set APERTUREDATA_ENABLED=true in .env
    2. Configure APERTUREDATA_HOST, PORT, USERNAME, PASSWORD
    3. Install aperturedb client: pip install aperturedb
    """
    
    @staticmethod
    def push(data):
        """
        Push data to ApertureData cold storage
        
        Args:
            data (dict): Data to store
            
        Returns:
            str: Entity ID from ApertureData
        """
        # In production, use the actual ApertureData client
        # from aperturedb import Connector
        # db = Connector(host=Config.APERTUREDATA_HOST, port=Config.APERTUREDATA_PORT,
        #                username=Config.APERTUREDATA_USERNAME, password=Config.APERTUREDATA_PASSWORD)
        # result = db.add_entity("PatientCall", properties=data)
        # return result.entity_id
        
        return StorageService.push_to_aperturedata(data, data.get('transcripts', []))


# Export main interface
__all__ = [
    'StorageIntegration',
    'LocalJSONStorage',
    'MemVergeStorage',
    'ApertureDataStorage'
]
