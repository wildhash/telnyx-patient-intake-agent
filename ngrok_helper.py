"""
Ngrok helper for local development
Automatically starts ngrok tunnel and updates PUBLIC_URL
"""

import os
import time
from pyngrok import ngrok, conf
from dotenv import load_dotenv, set_key
import logging

logger = logging.getLogger(__name__)

def start_ngrok(port=5000):
    """
    Start ngrok tunnel for local development
    
    Args:
        port (int): Local port to tunnel
        
    Returns:
        str: Public ngrok URL
    """
    load_dotenv()
    
    # Set ngrok auth token if available
    auth_token = os.getenv('NGROK_AUTHTOKEN')
    if auth_token:
        conf.get_default().auth_token = auth_token
    
    try:
        # Kill any existing ngrok processes
        ngrok.kill()
        time.sleep(1)
        
        # Start new tunnel
        public_url = ngrok.connect(port, bind_tls=True)
        
        logger.info(f"Ngrok tunnel established: {public_url}")
        
        # Update .env file with public URL
        env_file = '.env'
        if os.path.exists(env_file):
            set_key(env_file, 'PUBLIC_URL', str(public_url))
            logger.info(f"Updated PUBLIC_URL in .env: {public_url}")
        
        return str(public_url)
        
    except Exception as e:
        logger.error(f"Failed to start ngrok: {str(e)}")
        raise


def stop_ngrok():
    """Stop ngrok tunnel"""
    try:
        ngrok.kill()
        logger.info("Ngrok tunnel stopped")
    except Exception as e:
        logger.error(f"Failed to stop ngrok: {str(e)}")


if __name__ == '__main__':
    # Start ngrok when run directly
    port = int(os.getenv('PORT', 5000))
    public_url = start_ngrok(port)
    
    print(f"\n{'='*60}")
    print(f"🔗 Ngrok tunnel active!")
    print(f"{'='*60}")
    print(f"Public URL: {public_url}")
    print(f"Local URL:  http://localhost:{port}")
    print(f"{'='*60}")
    print(f"\nUpdate your Telnyx webhook URL to:")
    print(f"{public_url}/webhooks/telnyx")
    print(f"\nPress Ctrl+C to stop...")
    print(f"{'='*60}\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping ngrok...")
        stop_ngrok()
