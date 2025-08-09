import logging
from flask import request, jsonify
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def register_api_routes(app):
    """Register all API routes for the application"""
    
    @app.route('/api/leads', methods=['GET'])
    def api_get_leads():
        """Get all leads from database"""
        try:
            from models import LeadService
            lead_service = LeadService()
            leads = lead_service.get_leads(limit=request.args.get('limit', 50, type=int))
            
            return jsonify({
                'success': True,
                'leads': leads,
                'count': len(leads)
            })
        except Exception as e:
            logger.error(f"API get leads error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/leads', methods=['POST'])
    def api_create_lead():
        """Create new lead"""
        try:
            data = request.get_json() or {}
            
            if not data.get('name') or not data.get('phone'):
                return jsonify({
                    'success': False,
                    'error': 'Name and phone are required'
                }), 400
            
            from models import LeadService
            lead_service = LeadService()
            
            lead_data = {
                'name': data['name'],
                'phone': data['phone'],
                'email': data.get('email'),
                'source': data.get('source', 'api'),
                'notes': data.get('notes'),
                'tour_interest': data.get('tour_interest'),
                'budget_range': data.get('budget_range')
            }
            lead_id = lead_service.create_lead(lead_data)
            
            return jsonify({
                'success': True,
                'lead_id': lead_id,
                'message': 'Lead created successfully'
            })
            
        except Exception as e:
            logger.error(f"API create lead error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    logger.info("API routes registered successfully")
