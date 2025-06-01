"""
Wazzup24.ru API routes for Crystal Bay Travel
Handles webhooks, user sync, and chat integration
"""

import json
import logging
from flask import Blueprint, request, jsonify, render_template
from wazzup_integration import get_wazzup_integration
from models import LeadService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

wazzup_bp = Blueprint('wazzup', __name__, url_prefix='/api/wazzup')

@wazzup_bp.route('/webhook', methods=['POST'])
def wazzup_webhook():
    """Handle incoming webhooks from Wazzup24.ru"""
    try:
        webhook_data = request.get_json()
        
        if not webhook_data:
            logger.error("No webhook data received")
            return jsonify({'error': 'No data received'}), 400
        
        # Verify webhook signature if secret is configured
        wazzup = get_wazzup_integration()
        if wazzup.webhook_secret:
            signature = request.headers.get('X-Wazzup-Signature')
            if not signature or not wazzup._verify_webhook_signature(webhook_data, signature):
                logger.error("Invalid webhook signature")
                return jsonify({'error': 'Invalid signature'}), 401
        
        # Process webhook
        result = wazzup.handle_webhook(webhook_data)
        
        logger.info(f"Webhook processed: {result}")
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@wazzup_bp.route('/sync-users', methods=['POST'])
def sync_users():
    """Sync Crystal Bay users with Wazzup"""
    try:
        users_data = request.get_json()
        
        if not users_data or 'users' not in users_data:
            return jsonify({'error': 'Users data required'}), 400
        
        wazzup = get_wazzup_integration()
        if not wazzup.is_configured():
            return jsonify({'error': 'Wazzup integration not configured'}), 400
        
        success = wazzup.sync_users(users_data['users'])
        
        if success:
            return jsonify({'status': 'success', 'message': 'Users synced successfully'})
        else:
            return jsonify({'error': 'User synchronization failed'}), 500
            
    except Exception as e:
        logger.error(f"User sync error: {e}")
        return jsonify({'error': str(e)}), 500

@wazzup_bp.route('/sync-lead', methods=['POST'])
def sync_lead():
    """Sync a lead from Crystal Bay to Wazzup as a contact"""
    try:
        lead_data = request.get_json()
        
        if not lead_data:
            return jsonify({'error': 'Lead data required'}), 400
        
        wazzup = get_wazzup_integration()
        if not wazzup.is_configured():
            return jsonify({'error': 'Wazzup integration not configured'}), 400
        
        # Sync contact
        contact_id = wazzup.sync_contact(lead_data)
        
        if contact_id:
            # Optionally create deal
            deal_id = None
            if lead_data.get('create_deal', False):
                deal_id = wazzup.create_deal(lead_data, contact_id)
            
            return jsonify({
                'status': 'success',
                'contact_id': contact_id,
                'deal_id': deal_id
            })
        else:
            return jsonify({'error': 'Contact synchronization failed'}), 500
            
    except Exception as e:
        logger.error(f"Lead sync error: {e}")
        return jsonify({'error': str(e)}), 500

@wazzup_bp.route('/chat-url', methods=['GET'])
def get_chat_url():
    """Get Wazzup chat iframe URL"""
    try:
        scope = request.args.get('scope', 'global')
        contact_id = request.args.get('contact_id')
        
        wazzup = get_wazzup_integration()
        if not wazzup.is_configured():
            return jsonify({'error': 'Wazzup integration not configured'}), 400
        
        chat_url = wazzup.get_chat_iframe_url(scope, contact_id)
        
        return jsonify({
            'status': 'success',
            'chat_url': chat_url
        })
        
    except Exception as e:
        logger.error(f"Chat URL error: {e}")
        return jsonify({'error': str(e)}), 500

@wazzup_bp.route('/unread-count', methods=['GET'])
def get_unread_count():
    """Get count of unread messages"""
    try:
        wazzup = get_wazzup_integration()
        if not wazzup.is_configured():
            return jsonify({'error': 'Wazzup integration not configured'}), 400
        
        count = wazzup.get_unread_count()
        
        return jsonify({
            'status': 'success',
            'unread_count': count
        })
        
    except Exception as e:
        logger.error(f"Unread count error: {e}")
        return jsonify({'error': str(e)}), 500

@wazzup_bp.route('/setup-pipeline', methods=['POST'])
def setup_pipeline():
    """Create travel booking pipeline in Wazzup"""
    try:
        wazzup = get_wazzup_integration()
        if not wazzup.is_configured():
            return jsonify({'error': 'Wazzup integration not configured'}), 400
        
        pipeline_id = wazzup.create_travel_pipeline()
        
        if pipeline_id:
            return jsonify({
                'status': 'success',
                'pipeline_id': pipeline_id,
                'message': 'Travel booking pipeline created successfully'
            })
        else:
            return jsonify({'error': 'Pipeline creation failed'}), 500
            
    except Exception as e:
        logger.error(f"Pipeline setup error: {e}")
        return jsonify({'error': str(e)}), 500

@wazzup_bp.route('/config', methods=['GET'])
def get_config():
    """Get Wazzup integration configuration status"""
    try:
        wazzup = get_wazzup_integration()
        
        return jsonify({
            'status': 'success',
            'configured': wazzup.is_configured(),
            'has_api_key': bool(wazzup.api_key),
            'has_api_secret': bool(wazzup.api_secret),
            'has_webhook_secret': bool(wazzup.webhook_secret),
            'base_url': wazzup.base_url
        })
        
    except Exception as e:
        logger.error(f"Config check error: {e}")
        return jsonify({'error': str(e)}), 500

@wazzup_bp.route('/test-connection', methods=['POST'])
def test_connection():
    """Test connection to Wazzup API"""
    try:
        wazzup = get_wazzup_integration()
        if not wazzup.is_configured():
            return jsonify({'error': 'Wazzup integration not configured'}), 400
        
        # Test with a simple API call
        result = wazzup._make_request('GET', '/account')
        
        if result:
            return jsonify({
                'status': 'success',
                'message': 'Connection to Wazzup API successful',
                'account_info': result
            })
        else:
            return jsonify({'error': 'Failed to connect to Wazzup API'}), 500
            
    except Exception as e:
        logger.error(f"Connection test error: {e}")
        return jsonify({'error': str(e)}), 500