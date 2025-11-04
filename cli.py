#!/usr/bin/env python3
"""
Command-line interface for Telnyx Patient Intake Agent
"""

import click
import requests
import json
import os
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

API_BASE_URL = os.getenv('PUBLIC_URL', 'http://localhost:5000')


@click.group()
def cli():
    """Telnyx Patient Intake Agent CLI"""
    pass


@cli.group()
def patient():
    """Manage patients"""
    pass


@patient.command('list')
def list_patients():
    """List all patients"""
    try:
        response = requests.get(f'{API_BASE_URL}/api/patients')
        response.raise_for_status()
        data = response.json()
        
        if data['total'] == 0:
            click.echo("No patients found.")
            return
        
        patients = data['patients']
        table_data = [
            [p['id'], p['phone_number'], p.get('first_name', ''), p.get('last_name', ''), p.get('email', '')]
            for p in patients
        ]
        
        click.echo(tabulate(table_data, headers=['ID', 'Phone', 'First Name', 'Last Name', 'Email'], tablefmt='grid'))
        click.echo(f"\nTotal patients: {data['total']}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@patient.command('create')
@click.option('--phone', required=True, help='Patient phone number')
@click.option('--first-name', help='Patient first name')
@click.option('--last-name', help='Patient last name')
@click.option('--email', help='Patient email')
@click.option('--dob', help='Patient date of birth (YYYY-MM-DD)')
def create_patient(phone, first_name, last_name, email, dob):
    """Create a new patient"""
    try:
        payload = {'phone_number': phone}
        if first_name:
            payload['first_name'] = first_name
        if last_name:
            payload['last_name'] = last_name
        if email:
            payload['email'] = email
        if dob:
            payload['date_of_birth'] = dob
        
        response = requests.post(f'{API_BASE_URL}/api/patients', json=payload)
        response.raise_for_status()
        
        patient = response.json()
        click.echo(f"✓ Patient created successfully!")
        click.echo(f"  ID: {patient['id']}")
        click.echo(f"  Phone: {patient['phone_number']}")
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 409:
            click.echo("Error: Patient with this phone number already exists", err=True)
        else:
            click.echo(f"Error: {e.response.text}", err=True)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@patient.command('get')
@click.argument('patient_id', type=int)
def get_patient(patient_id):
    """Get patient details"""
    try:
        response = requests.get(f'{API_BASE_URL}/api/patients/{patient_id}')
        response.raise_for_status()
        patient = response.json()
        
        click.echo("\nPatient Details:")
        click.echo(f"  ID: {patient['id']}")
        click.echo(f"  Phone: {patient['phone_number']}")
        click.echo(f"  Name: {patient.get('first_name', '')} {patient.get('last_name', '')}")
        click.echo(f"  Email: {patient.get('email', 'N/A')}")
        click.echo(f"  DOB: {patient.get('date_of_birth', 'N/A')}")
        click.echo(f"  Created: {patient['created_at']}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@cli.group()
def call():
    """Manage calls"""
    pass


@call.command('initiate')
@click.option('--phone', required=True, help='Phone number to call')
@click.option('--patient-id', type=int, help='Patient ID')
def initiate_call(phone, patient_id):
    """Initiate an outbound call"""
    try:
        payload = {'phone_number': phone}
        if patient_id:
            payload['patient_id'] = patient_id
        
        response = requests.post(f'{API_BASE_URL}/api/calls', json=payload)
        response.raise_for_status()
        
        data = response.json()
        click.echo(f"✓ Call initiated successfully!")
        click.echo(f"  Call ID: {data['call_id']}")
        click.echo(f"  Status: {data['status']}")
        click.echo(f"  Control ID: {data['call_control_id']}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@call.command('list')
@click.option('--status', help='Filter by status')
@click.option('--patient-id', type=int, help='Filter by patient ID')
@click.option('--limit', default=20, help='Number of calls to show')
def list_calls(status, patient_id, limit):
    """List calls"""
    try:
        params = {'limit': limit}
        if status:
            params['status'] = status
        if patient_id:
            params['patient_id'] = patient_id
        
        response = requests.get(f'{API_BASE_URL}/api/calls', params=params)
        response.raise_for_status()
        data = response.json()
        
        if data['total'] == 0:
            click.echo("No calls found.")
            return
        
        calls = data['calls']
        table_data = [
            [
                c['id'], 
                c['status'], 
                c['to_number'], 
                c.get('duration_seconds', 'N/A'),
                'Yes' if c.get('consent_given') else 'No',
                c['created_at'][:19]
            ]
            for c in calls
        ]
        
        click.echo(tabulate(table_data, headers=['ID', 'Status', 'To', 'Duration', 'Consent', 'Started'], tablefmt='grid'))
        click.echo(f"\nTotal calls: {data['total']}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@call.command('get')
@click.argument('call_id', type=int)
def get_call(call_id):
    """Get call details"""
    try:
        response = requests.get(f'{API_BASE_URL}/api/calls/{call_id}')
        response.raise_for_status()
        call = response.json()
        
        click.echo("\nCall Details:")
        click.echo(f"  ID: {call['id']}")
        click.echo(f"  Status: {call['status']}")
        click.echo(f"  From: {call['from_number']}")
        click.echo(f"  To: {call['to_number']}")
        click.echo(f"  Consent Given: {'Yes' if call.get('consent_given') else 'No'}")
        click.echo(f"  Duration: {call.get('duration_seconds', 'N/A')} seconds")
        click.echo(f"  Recording URL: {call.get('recording_url', 'N/A')}")
        click.echo(f"  Started: {call.get('started_at', 'N/A')}")
        click.echo(f"  Ended: {call.get('ended_at', 'N/A')}")
        
        if call.get('intake_data'):
            click.echo("\n  Intake Data:")
            click.echo(f"    {json.dumps(call['intake_data'], indent=4)}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@call.command('hangup')
@click.argument('call_id', type=int)
def hangup_call(call_id):
    """Hang up an active call"""
    try:
        response = requests.post(f'{API_BASE_URL}/api/calls/{call_id}/hangup')
        response.raise_for_status()
        
        click.echo(f"✓ Call {call_id} hung up successfully")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@call.command('transcripts')
@click.argument('call_id', type=int)
def get_transcripts(call_id):
    """Get call transcripts"""
    try:
        response = requests.get(f'{API_BASE_URL}/api/calls/{call_id}/transcripts')
        response.raise_for_status()
        data = response.json()
        
        if data['total'] == 0:
            click.echo("No transcripts found for this call.")
            return
        
        click.echo(f"\nTranscripts for Call {call_id}:")
        click.echo("=" * 80)
        
        for t in data['transcripts']:
            speaker = t.get('speaker', 'unknown').upper()
            text = t.get('text', '')
            timestamp = t.get('timestamp', '')[:19]
            click.echo(f"\n[{timestamp}] {speaker}:")
            click.echo(f"  {text}")
        
        click.echo("\n" + "=" * 80)
        click.echo(f"Total segments: {data['total']}")
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@cli.command('stats')
def stats():
    """Show system statistics"""
    try:
        response = requests.get(f'{API_BASE_URL}/api/stats')
        response.raise_for_status()
        data = response.json()
        
        click.echo("\n📊 System Statistics")
        click.echo("=" * 40)
        click.echo(f"Total Patients: {data['total_patients']}")
        click.echo(f"Total Calls: {data['total_calls']}")
        click.echo(f"Completed Calls: {data['completed_calls']}")
        click.echo(f"Active Calls: {data['active_calls']}")
        click.echo(f"Consented Calls: {data['consented_calls']}")
        click.echo(f"Consent Rate: {data['consent_rate']}%")
        click.echo("=" * 40)
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@cli.command('config')
def show_config():
    """Show current configuration"""
    click.echo("\n⚙️  Configuration")
    click.echo("=" * 40)
    click.echo(f"API Base URL: {API_BASE_URL}")
    click.echo(f"Telnyx API Key: {'***' + os.getenv('TELNYX_API_KEY', 'Not set')[-4:] if os.getenv('TELNYX_API_KEY') else 'Not set'}")
    click.echo(f"Telnyx Phone: {os.getenv('TELNYX_PHONE_NUMBER', 'Not set')}")
    click.echo(f"Recording Enabled: {os.getenv('RECORDING_ENABLED', 'true')}")
    click.echo(f"Transcription Enabled: {os.getenv('TRANSCRIPTION_ENABLED', 'true')}")
    click.echo(f"MemVerge Enabled: {os.getenv('MEMVERGE_ENABLED', 'false')}")
    click.echo(f"ApertureData Enabled: {os.getenv('APERTUREDATA_ENABLED', 'false')}")
    click.echo("=" * 40)


if __name__ == '__main__':
    cli()
