#!/usr/bin/env python3
"""
Convenience script to run the application with optional ngrok
"""

import os
import sys
import argparse
from dotenv import load_dotenv

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description='Run Telnyx Patient Intake Agent')
    parser.add_argument('--with-ngrok', action='store_true', help='Start with ngrok tunnel')
    parser.add_argument('--port', type=int, default=5000, help='Port to run on (default: 5000)')
    args = parser.parse_args()
    
    port = args.port
    
    if args.with_ngrok:
        print("Starting with ngrok tunnel...")
        from ngrok_helper import start_ngrok
        try:
            public_url = start_ngrok(port)
            print(f"\n{'='*60}")
            print(f"🔗 Ngrok tunnel active!")
            print(f"{'='*60}")
            print(f"Public URL: {public_url}")
            print(f"Local URL:  http://localhost:{port}")
            print(f"{'='*60}")
            print(f"\nUpdate your Telnyx webhook URL to:")
            print(f"{public_url}/webhooks/telnyx")
            print(f"{'='*60}\n")
        except Exception as e:
            print(f"Failed to start ngrok: {e}")
            print("Continuing without ngrok...")
    
    # Import and run app
    from app import app, db
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✓ Database tables created")
    
    # Run the application
    print(f"\n🚀 Starting Telnyx Patient Intake Agent on port {port}...")
    print(f"📊 Dashboard: http://localhost:{port}/dashboard")
    print(f"💻 API Docs: http://localhost:{port}/api/stats")
    print(f"\nPress Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') == 'development')

if __name__ == '__main__':
    main()
