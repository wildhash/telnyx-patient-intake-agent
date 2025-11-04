#!/usr/bin/env python
"""
CLI tool for testing calls
Usage: python test_call.py call +1XXXXXXXXXX
"""

import sys
import argparse
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

BASE_URL = os.getenv('PUBLIC_URL', 'http://localhost:5000')


def initiate_call(phone_number):
    """
    Initiate a test call to the specified phone number
    
    Args:
        phone_number (str): Phone number to call (E.164 format)
        
    Returns:
        dict: Response from the API
    """
    url = f"{BASE_URL}/api/calls"
    
    payload = {
        "phone_number": phone_number
    }
    
    try:
        print(f"Initiating call to {phone_number}...")
        response = requests.post(url, json=payload)
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"✅ Call initiated successfully!")
            call_id = data.get('call', {}).get('id')
            telnyx_call_id = data.get('call', {}).get('telnyx_call_id', 'N/A')
            status = data.get('call', {}).get('status')
            print(f"   Call ID: {call_id}")
            # Mask sensitive call ID for security
            if telnyx_call_id and len(telnyx_call_id) > 8:
                masked_id = telnyx_call_id[:4] + "..." + telnyx_call_id[-4:]
                print(f"   Telnyx Call ID: {masked_id}")
            else:
                print(f"   Telnyx Call ID: {telnyx_call_id}")
            print(f"   Status: {status}")
            return data
        else:
            print(f"❌ Failed to initiate call: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error: Could not connect to {BASE_URL}")
        print(f"   Make sure the Flask app is running!")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def get_call_status(call_id):
    """
    Get the status of a call
    
    Args:
        call_id (int): Call ID
        
    Returns:
        dict: Call details
    """
    url = f"{BASE_URL}/api/calls/{call_id}"
    
    try:
        print(f"Fetching call status for ID {call_id}...")
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            call = data.get('call', {})
            print(f"✅ Call found!")
            print(f"   Status: {call.get('status')}")
            print(f"   Duration: {call.get('duration')} seconds")
            print(f"   Phone: {call.get('to_number')}")
            return data
        else:
            print(f"❌ Failed to get call: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def list_calls():
    """
    List all calls
    
    Returns:
        dict: List of calls
    """
    url = f"{BASE_URL}/api/calls"
    
    try:
        print(f"Fetching all calls...")
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            calls = data.get('calls', [])
            print(f"✅ Found {len(calls)} call(s)")
            for call in calls[:10]:  # Show first 10
                print(f"   ID: {call.get('id')} | Status: {call.get('status')} | Phone: {call.get('to_number')}")
            return data
        else:
            print(f"❌ Failed to list calls: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def get_transcripts(call_id):
    """
    Get transcripts for a call
    
    Args:
        call_id (int): Call ID
        
    Returns:
        dict: Transcript data
    """
    url = f"{BASE_URL}/api/calls/{call_id}/transcripts"
    
    try:
        print(f"Fetching transcripts for call ID {call_id}...")
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            transcripts = data.get('transcripts', [])
            print(f"✅ Found {len(transcripts)} transcript segment(s)")
            for t in transcripts[:5]:  # Show first 5
                print(f"   [{t.get('created_at')}] {t.get('text')}")
            return data
        else:
            print(f"❌ Failed to get transcripts: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def main():
    parser = argparse.ArgumentParser(description='Test call CLI tool')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Call command
    call_parser = subparsers.add_parser('call', help='Initiate a call')
    call_parser.add_argument('phone_number', help='Phone number in E.164 format (e.g., +12345678900)')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get call status')
    status_parser.add_argument('call_id', type=int, help='Call ID')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all calls')
    
    # Transcripts command
    transcripts_parser = subparsers.add_parser('transcripts', help='Get call transcripts')
    transcripts_parser.add_argument('call_id', type=int, help='Call ID')
    
    args = parser.parse_args()
    
    if args.command == 'call':
        initiate_call(args.phone_number)
    elif args.command == 'status':
        get_call_status(args.call_id)
    elif args.command == 'list':
        list_calls()
    elif args.command == 'transcripts':
        get_transcripts(args.call_id)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
