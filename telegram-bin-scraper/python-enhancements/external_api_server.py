#!/usr/bin/env python3
"""
External API Server for SkyBin
Allows third-party scrapers to submit credentials via REST API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import hashlib
import hmac
import json
import requests
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, origins=["https://nullme.lol", "http://localhost:*"])

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "10 per minute"]
)

# Configuration
SKYBIN_API_URL = os.getenv('SKYBIN_API_URL', 'http://localhost:8082')
API_SECRET = os.getenv('API_SECRET', 'your-secret-key-here')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'webhook-secret')

# Valid API keys (in production, store in database)
VALID_API_KEYS = {
    'sk_live_nullme_001': {'name': 'Production Scanner', 'rate_limit': 1000},
    'sk_live_nullme_002': {'name': 'Discord Bot', 'rate_limit': 500},
    'sk_test_nullme_001': {'name': 'Test Scanner', 'rate_limit': 100},
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CredentialValidator:
    """Validates that submitted content contains actual credentials"""
    
    PATTERNS = {
        'email_pass': re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+:[^\s@:]{4,}'),
        'api_key': re.compile(r'(ghp_|gho_|sk-|AKIA|AIza)[a-zA-Z0-9]{16,}'),
        'private_key': re.compile(r'-----BEGIN\s+(RSA|DSA|EC|OPENSSH|PGP)?\s*PRIVATE KEY-----'),
        'discord_token': re.compile(r'[MN][A-Za-z0-9]{23,}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27}'),
    }
    
    @classmethod
    def validate(cls, content: str) -> Dict[str, Any]:
        """Check if content contains credentials"""
        if not content or len(content) < 20:
            return {'valid': False, 'reason': 'Content too short'}
        
        found_types = []
        for pattern_name, pattern in cls.PATTERNS.items():
            if pattern.search(content):
                found_types.append(pattern_name)
        
        if not found_types:
            return {'valid': False, 'reason': 'No credentials detected'}
        
        return {
            'valid': True,
            'credential_types': found_types,
            'count': len(found_types)
        }


def verify_api_key(api_key: str) -> Optional[Dict]:
    """Verify API key and return metadata"""
    return VALID_API_KEYS.get(api_key)


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify webhook HMAC signature"""
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'SkyBin External API',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/v1/submit', methods=['POST'])
@limiter.limit("50 per hour")
def submit_credentials():
    """
    Submit credentials from external sources
    
    Expected JSON payload:
    {
        "content": "credential content here",
        "title": "optional title",
        "source": "discord/forum/etc",
        "api_key": "your_api_key"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        api_key = data.get('api_key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Verify API key
        key_info = verify_api_key(api_key)
        if not key_info:
            return jsonify({'error': 'Invalid API key'}), 401
        
        # Validate content
        content = data.get('content', '')
        validation = CredentialValidator.validate(content)
        
        if not validation['valid']:
            return jsonify({
                'error': f"Invalid content: {validation['reason']}"
            }), 400
        
        # Prepare submission for SkyBin
        source = data.get('source', 'external')
        title = data.get('title', f"{source} Leak - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Format according to specification
        from telegram_scraper.enhanced_formatter import EnhancedCredentialFormatter
        formatter = EnhancedCredentialFormatter()
        formatted_title, formatted_content = formatter.format_content(content, source)
        
        # Submit to SkyBin
        skybin_payload = {
            'content': formatted_content,
            'title': formatted_title or title,
        }
        
        response = requests.post(
            f"{SKYBIN_API_URL}/api/paste",
            json=skybin_payload,
            timeout=10
        )
        
        if response.status_code in (200, 201):
            result = response.json()
            paste_id = result.get('data', {}).get('id', 'unknown')
            
            logger.info(f"Successfully submitted paste {paste_id} from {source} via {key_info['name']}")
            
            return jsonify({
                'success': True,
                'paste_id': paste_id,
                'url': f"{SKYBIN_API_URL}/paste/{paste_id}",
                'credential_types': validation['credential_types']
            }), 201
        else:
            logger.error(f"SkyBin submission failed: {response.status_code}")
            return jsonify({
                'error': 'Failed to submit to SkyBin'
            }), 500
            
    except Exception as e:
        logger.error(f"Submission error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/v1/webhook', methods=['POST'])
def webhook_receiver():
    """
    Receive webhooks from external services (Discord, forums, etc)
    """
    try:
        # Verify signature
        signature = request.headers.get('X-Webhook-Signature', '')
        if not verify_webhook_signature(request.data, signature):
            return jsonify({'error': 'Invalid signature'}), 401
        
        data = request.get_json()
        event_type = data.get('event')
        
        if event_type == 'credential.found':
            # Process credential discovery
            content = data.get('content', '')
            source = data.get('source', 'webhook')
            
            # Validate and submit
            validation = CredentialValidator.validate(content)
            if validation['valid']:
                # Format and submit to SkyBin
                from telegram_scraper.enhanced_formatter import EnhancedCredentialFormatter
                formatter = EnhancedCredentialFormatter()
                formatted_title, formatted_content = formatter.format_content(content, source)
                
                skybin_payload = {
                    'content': formatted_content,
                    'title': formatted_title,
                }
                
                response = requests.post(
                    f"{SKYBIN_API_URL}/api/paste",
                    json=skybin_payload,
                    timeout=10
                )
                
                logger.info(f"Webhook submission from {source}: {response.status_code}")
        
        return '', 204
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': 'Processing failed'}), 500


@app.route('/api/v1/search', methods=['GET'])
@limiter.limit("20 per minute")
def search_credentials():
    """Search for specific credentials"""
    api_key = request.headers.get('X-API-Key')
    if not verify_api_key(api_key):
        return jsonify({'error': 'Invalid API key'}), 401
    
    query = request.args.get('q', '')
    limit = min(int(request.args.get('limit', 25)), 100)
    
    # Forward search to SkyBin
    response = requests.get(
        f"{SKYBIN_API_URL}/api/search",
        params={'q': query, 'limit': limit},
        timeout=10
    )
    
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Search failed'}), 500


@app.route('/api/v1/stats', methods=['GET'])
def get_stats():
    """Get API usage statistics"""
    api_key = request.headers.get('X-API-Key')
    key_info = verify_api_key(api_key)
    if not key_info:
        return jsonify({'error': 'Invalid API key'}), 401
    
    # Get stats from SkyBin
    response = requests.get(f"{SKYBIN_API_URL}/api/stats", timeout=10)
    
    if response.status_code == 200:
        stats = response.json()
        stats['api_client'] = key_info['name']
        return jsonify(stats)
    else:
        return jsonify({'error': 'Failed to get stats'}), 500


# WebSocket support for real-time notifications (using Socket.IO)
try:
    from flask_socketio import SocketIO, emit
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    @socketio.on('subscribe')
    def handle_subscribe(data):
        """Subscribe to real-time credential notifications"""
        api_key = data.get('api_key')
        if not verify_api_key(api_key):
            emit('error', {'message': 'Invalid API key'})
            return
        
        # Subscribe to notifications
        emit('subscribed', {'message': 'Subscribed to notifications'})
    
    @socketio.on('connect')
    def handle_connect():
        logger.info('Client connected')
    
    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info('Client disconnected')
        
except ImportError:
    socketio = None
    logger.warning("Socket.IO not installed - real-time features disabled")


if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))
    
    if socketio:
        logger.info(f"Starting External API Server with WebSocket support on port {port}")
        socketio.run(app, host='0.0.0.0', port=port, debug=False)
    else:
        logger.info(f"Starting External API Server on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)