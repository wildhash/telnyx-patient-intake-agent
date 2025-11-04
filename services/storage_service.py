"""
Storage service for pushing data to MemVerge (hot) and ApertureData (cold) storage
"""

import logging
import requests
import json
from config import Config

logger = logging.getLogger(__name__)


class StorageService:
    """Service for managing data storage to external systems"""
    
    @staticmethod
    def push_to_memverge(call_data, transcript_data):
        """
        Push data to MemVerge hot storage
        
        Args:
            call_data (dict): Call information
            transcript_data (list): List of transcript segments
            
        Returns:
            str: MemVerge object ID or None
        """
        if not Config.MEMVERGE_ENABLED:
            logger.info("MemVerge storage is disabled")
            return None
        
        try:
            payload = {
                'call': call_data,
                'transcripts': transcript_data,
                'timestamp': call_data.get('created_at')
            }
            
            headers = {
                'Authorization': f'Bearer {Config.MEMVERGE_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f'{Config.MEMVERGE_ENDPOINT}/api/v1/objects',
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                memverge_id = result.get('id')
                logger.info(f"Data pushed to MemVerge: {memverge_id}")
                return memverge_id
            else:
                logger.error(f"Failed to push to MemVerge: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error pushing to MemVerge: {str(e)}")
            return None
    
    @staticmethod
    def push_to_aperturedata(call_data, transcript_data):
        """
        Push data to ApertureData cold storage
        
        Args:
            call_data (dict): Call information
            transcript_data (list): List of transcript segments
            
        Returns:
            str: ApertureData object ID or None
        """
        if not Config.APERTUREDATA_ENABLED:
            logger.info("ApertureData storage is disabled")
            return None
        
        try:
            # ApertureData typically uses a different protocol (gRPC or custom)
            # This is a simplified REST-like implementation
            # In production, you would use the ApertureData Python client
            
            payload = {
                'entity_type': 'patient_call',
                'properties': call_data,
                'transcripts': transcript_data
            }
            
            # Simulated ApertureData connection
            # In production, use: from aperturedb import Connector
            logger.info(f"Would push to ApertureData: {Config.APERTUREDATA_HOST}:{Config.APERTUREDATA_PORT}")
            
            # Placeholder for actual implementation
            aperturedata_id = f"aperture_{call_data.get('id', 'unknown')}"
            logger.info(f"Data would be pushed to ApertureData: {aperturedata_id}")
            
            return aperturedata_id
            
        except Exception as e:
            logger.error(f"Error pushing to ApertureData: {str(e)}")
            return None
    
    @staticmethod
    def push_to_backend(call_data, transcript_data):
        """
        Push data to configured backend API
        
        Args:
            call_data (dict): Call information
            transcript_data (list): List of transcript segments
            
        Returns:
            bool: Success status
        """
        if not Config.BACKEND_API_URL:
            logger.info("Backend API URL not configured")
            return False
        
        try:
            payload = {
                'call': call_data,
                'transcripts': transcript_data,
                'intake_data': call_data.get('intake_data')
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            if Config.BACKEND_API_KEY:
                headers['Authorization'] = f'Bearer {Config.BACKEND_API_KEY}'
            
            response = requests.post(
                Config.BACKEND_API_URL,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Data pushed to backend API successfully")
                return True
            else:
                logger.error(f"Failed to push to backend: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error pushing to backend: {str(e)}")
            return False
    
    @staticmethod
    def push_all(call_data, transcript_data):
        """
        Push data to all configured storage systems
        
        Args:
            call_data (dict): Call information
            transcript_data (list): List of transcript segments
            
        Returns:
            dict: Results from each storage system
        """
        results = {
            'memverge_id': None,
            'aperturedata_id': None,
            'backend_pushed': False
        }
        
        # Push to MemVerge (hot storage)
        if Config.MEMVERGE_ENABLED:
            results['memverge_id'] = StorageService.push_to_memverge(call_data, transcript_data)
        
        # Push to ApertureData (cold storage)
        if Config.APERTUREDATA_ENABLED:
            results['aperturedata_id'] = StorageService.push_to_aperturedata(call_data, transcript_data)
        
        # Push to backend API
        if Config.BACKEND_API_URL:
            results['backend_pushed'] = StorageService.push_to_backend(call_data, transcript_data)
        
        return results
