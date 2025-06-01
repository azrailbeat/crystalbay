"""
Lead Import API Endpoints
Provides REST API endpoints for importing leads from various sources
"""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from lead_connector import lead_connector

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint for lead import routes
lead_import_bp = Blueprint('lead_import', __name__, url_prefix='/api/leads/import')

@lead_import_bp.route('/email', methods=['POST'])
def import_email_lead():
    """
    Import lead from email source
    
    POST /api/leads/import/email
    Content-Type: application/json
    
    Request body:
    {
        "from": "customer@example.com",
        "subject": "Travel inquiry",
        "body": "I'm interested in beach vacation to Turkey...",
        "received_at": "2025-01-01T12:00:00Z"
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        email_data = request.get_json()
        
        # Validate required fields
        required_fields = ['from', 'subject', 'body']
        for field in required_fields:
            if not email_data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Process the email lead
        result = lead_connector.process_email_lead(email_data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in email lead import: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error processing email lead'
        }), 500

@lead_import_bp.route('/widget', methods=['POST'])
def import_widget_lead():
    """
    Import lead from website widget
    
    POST /api/leads/import/widget
    Content-Type: application/json
    
    Request body:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "message": "I'm interested in summer tours",
        "widget_id": "contact_form_1",
        "page_url": "https://crystalbaytours.com/tours",
        "utm_source": "google",
        "utm_campaign": "summer_2025",
        "utm_medium": "cpc"
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        widget_data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email']
        for field in required_fields:
            if not widget_data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Process the widget lead
        result = lead_connector.process_widget_lead(widget_data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in widget lead import: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error processing widget lead'
        }), 500

@lead_import_bp.route('/api', methods=['POST'])
def import_api_lead():
    """
    Import lead from external API
    
    POST /api/leads/import/api
    Content-Type: application/json
    X-API-Key: your_partner_api_key (optional)
    
    Request body (flexible structure):
    {
        "customer": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890"
        },
        "inquiry": {
            "type": "Beach vacation",
            "message": "Looking for 5-star resort in Maldives",
            "destination": "Maldives",
            "budget": 8000,
            "travel_date": "2025-07-15"
        },
        "source_info": {
            "partner_name": "TravelPartner LLC",
            "reference_id": "REF_12345"
        }
    }
    
    Alternative flat structure:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "message": "Looking for vacation",
        "destination": "Turkey",
        "budget": 3000
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        api_data = request.get_json()
        
        # Get partner info from headers
        api_key = request.headers.get('X-API-Key')
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Add source identification
        if api_key:
            # You can validate API key here against your partner database
            source_name = f"partner_api_{api_key[:8]}"
        else:
            source_name = "external_api"
        
        # Add source info if not provided
        if 'source_info' not in api_data:
            api_data['source_info'] = {
                'partner_name': source_name,
                'api_key': api_key,
                'user_agent': user_agent
            }
        
        # Process the API lead
        result = lead_connector.process_api_lead(api_data, source_name)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in API lead import: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error processing API lead'
        }), 500

@lead_import_bp.route('/bulk', methods=['POST'])
def import_bulk_leads():
    """
    Import multiple leads at once
    
    POST /api/leads/import/bulk
    Content-Type: application/json
    
    Request body:
    {
        "leads": [
            {
                "type": "email",
                "data": {
                    "from": "customer1@example.com",
                    "subject": "Inquiry 1",
                    "body": "Message 1"
                }
            },
            {
                "type": "widget", 
                "data": {
                    "name": "Customer 2",
                    "email": "customer2@example.com",
                    "message": "Message 2"
                }
            }
        ]
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        bulk_data = request.get_json()
        leads_data = bulk_data.get('leads', [])
        
        if not leads_data:
            return jsonify({
                'success': False,
                'error': 'No leads data provided'
            }), 400
        
        results = []
        success_count = 0
        error_count = 0
        
        for idx, lead_item in enumerate(leads_data):
            lead_type = lead_item.get('type')
            lead_data = lead_item.get('data', {})
            
            try:
                if lead_type == 'email':
                    result = lead_connector.process_email_lead(lead_data)
                elif lead_type == 'widget':
                    result = lead_connector.process_widget_lead(lead_data)
                elif lead_type == 'api':
                    result = lead_connector.process_api_lead(lead_data)
                else:
                    result = {
                        'success': False,
                        'error': f'Unknown lead type: {lead_type}'
                    }
                
                results.append({
                    'index': idx,
                    'type': lead_type,
                    'result': result
                })
                
                if result['success']:
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
                results.append({
                    'index': idx,
                    'type': lead_type,
                    'result': {
                        'success': False,
                        'error': str(e)
                    }
                })
        
        return jsonify({
            'success': True,
            'summary': {
                'total': len(leads_data),
                'successful': success_count,
                'failed': error_count
            },
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error in bulk lead import: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error processing bulk leads'
        }), 500

@lead_import_bp.route('/webhook/email', methods=['POST'])
def email_webhook():
    """
    Webhook endpoint for email services (SendGrid, Mailgun, etc.)
    Automatically processes incoming emails as leads
    
    POST /api/leads/import/webhook/email
    """
    try:
        # This would handle different email service webhook formats
        # For now, let's handle SendGrid's inbound parse webhook format
        
        if request.content_type and 'application/x-www-form-urlencoded' in request.content_type:
            # SendGrid sends form data
            email_data = {
                'from': request.form.get('from'),
                'subject': request.form.get('subject'),
                'body': request.form.get('text', request.form.get('html', '')),
                'received_at': datetime.now().isoformat()
            }
        else:
            # JSON webhook
            webhook_data = request.get_json()
            email_data = {
                'from': webhook_data.get('from'),
                'subject': webhook_data.get('subject'),
                'body': webhook_data.get('body'),
                'received_at': webhook_data.get('received_at', datetime.now().isoformat())
            }
        
        # Process the email lead
        result = lead_connector.process_email_lead(email_data)
        
        if result['success']:
            logger.info(f"Processed email webhook lead: {result.get('lead_id')}")
            return jsonify({'status': 'processed'}), 200
        else:
            logger.error(f"Failed to process email webhook: {result.get('error')}")
            return jsonify({'status': 'error', 'message': result.get('error')}), 400
            
    except Exception as e:
        logger.error(f"Error in email webhook: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@lead_import_bp.route('/status', methods=['GET'])
def import_status():
    """
    Get status of lead import system
    
    GET /api/leads/import/status
    """
    try:
        # Check if required services are available
        from models import is_supabase_available
        
        status = {
            'system': 'operational',
            'database': 'connected' if is_supabase_available() else 'fallback_mode',
            'email_service': 'configured' if lead_connector.email_processor.sendgrid_api_key else 'not_configured',
            'endpoints': {
                'email_import': '/api/leads/import/email',
                'widget_import': '/api/leads/import/widget',
                'api_import': '/api/leads/import/api',
                'bulk_import': '/api/leads/import/bulk',
                'email_webhook': '/api/leads/import/webhook/email'
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Error getting import status: {e}")
        return jsonify({
            'system': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500