import logging
from flask import request, jsonify
from datetime import datetime
import os
import subprocess
import shlex
import json

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

    @app.route('/api/chat/history/<lead_id>', methods=['GET'])
    def api_get_chat_history(lead_id):
        """Get chat history for a specific lead"""
        try:
            # Return empty array for now since chat history is not implemented
            return jsonify({
                'success': True,
                'messages': [],
                'count': 0,
                'lead_id': lead_id
            })
        except Exception as e:
            logger.error(f"API get chat history error: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'messages': []
            }), 500
    
    # === SETTINGS API ===
    
    @app.route('/api/settings/samo', methods=['GET'])
    def api_get_samo_settings():
        """Get SAMO API settings"""
        try:
            from models import SettingsService
            settings = SettingsService.get_samo_settings()
            return jsonify({
                'success': True,
                'settings': settings
            })
        except Exception as e:
            logger.error(f"API get SAMO settings error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # === SAMO API ENDPOINTS ===
    
    @app.route('/api/samo/currencies', methods=['GET'])
    def get_samo_currencies():
        """Получить список валют SAMO API"""
        try:
            from samo_api_correct import SamoAPIClient
            samo_api = SamoAPIClient()
            result = samo_api.get_currencies()
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error getting SAMO currencies: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/samo/states', methods=['GET'])
    def get_samo_states():
        """Получить список стран SAMO API"""
        try:
            from samo_api_correct import SamoAPIClient
            samo_api = SamoAPIClient()
            result = samo_api.get_states()
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error getting SAMO states: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/samo/townfroms', methods=['GET'])
    def get_samo_townfroms():
        """Получить список городов отправления SAMO API"""
        try:
            from samo_api_correct import SamoAPIClient
            samo_api = SamoAPIClient()
            result = samo_api.get_town_froms()
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error getting SAMO townfroms: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/samo/stars', methods=['GET'])
    def get_samo_stars():
        """Получить список звездности отелей SAMO API"""
        try:
            from samo_api_correct import SamoAPIClient
            samo_api = SamoAPIClient()
            result = samo_api.get_stars()
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error getting SAMO stars: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/samo/meals', methods=['GET'])
    def get_samo_meals():
        """Получить список типов питания SAMO API"""
        try:
            from samo_api_correct import SamoAPIClient
            samo_api = SamoAPIClient()
            result = samo_api.get_meals()
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error getting SAMO meals: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/samo/search-tours-new', methods=['POST'])
    def search_samo_tours_new():
        """Поиск туров через правильный SAMO API клиент"""
        try:
            search_params = request.get_json()
            
            from samo_api_correct import SamoAPIClient
            samo_api = SamoAPIClient()
            result = samo_api.search_tour_prices(search_params)
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error searching SAMO tours: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/settings/samo', methods=['POST'])
    def api_update_samo_settings():
        """Update SAMO API settings"""
        try:
            data = request.get_json() or {}
            
            from models import SettingsService
            
            # Update each setting
            updated_settings = {}
            for key, value in data.items():
                if key in ['api_url', 'oauth_token', 'timeout', 'user_agent']:
                    success = SettingsService.update_samo_setting(key, str(value))
                    updated_settings[key] = value
                    if not success:
                        logger.warning(f"Failed to save setting {key} to database, using memory storage")
            
            return jsonify({
                'success': True,
                'message': 'SAMO settings updated successfully',
                'updated_settings': updated_settings
            })
            
        except Exception as e:
            logger.error(f"API update SAMO settings error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # === CURL API ===
    
    @app.route('/api/curl/execute', methods=['POST'])
    def api_execute_curl():
        """Execute curl command safely"""
        try:
            data = request.get_json() or {}
            url = data.get('url', '')
            method = data.get('method', 'GET').upper()
            headers = data.get('headers', {})
            payload = data.get('payload', {})
            
            if not url:
                return jsonify({
                    'success': False,
                    'error': 'URL is required'
                }), 400
            
            # Build curl command
            curl_parts = ['curl', '-s', '-w', '\\nHTTP Status: %{http_code}\\nTime: %{time_total}s\\n']
            
            # Add method
            if method != 'GET':
                curl_parts.extend(['-X', method])
            
            # Add headers
            for key, value in headers.items():
                curl_parts.extend(['-H', f'{key}: {value}'])
            
            # Add payload for POST/PUT
            if method in ['POST', 'PUT'] and payload:
                if isinstance(payload, dict):
                    # Form data
                    for key, value in payload.items():
                        curl_parts.extend(['-d', f'{key}={value}'])
                else:
                    # Raw data
                    curl_parts.extend(['-d', str(payload)])
            
            # Add URL
            curl_parts.append(url)
            
            # Execute curl command
            result = subprocess.run(curl_parts, capture_output=True, text=True, timeout=30)
            
            return jsonify({
                'success': True,
                'command': ' '.join(shlex.quote(part) for part in curl_parts),
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode,
                'execution_time': '< 30s'
            })
            
        except subprocess.TimeoutExpired:
            return jsonify({
                'success': False,
                'error': 'Curl command timed out (30s limit)'
            }), 408
        except Exception as e:
            logger.error(f"API execute curl error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/curl/generate', methods=['POST'])
    def api_generate_curl():
        """Generate curl command from parameters"""
        try:
            data = request.get_json() or {}
            url = data.get('url', '')
            method = data.get('method', 'GET').upper()
            headers = data.get('headers', {})
            payload = data.get('payload', {})
            
            if not url:
                return jsonify({
                    'success': False,
                    'error': 'URL is required'
                }), 400
            
            # Build curl command string
            curl_parts = ['curl', '-v']
            
            # Add method
            if method != 'GET':
                curl_parts.extend(['-X', method])
            
            # Add headers
            for key, value in headers.items():
                curl_parts.extend(['-H', f'"{key}: {value}"'])
            
            # Add payload for POST/PUT
            if method in ['POST', 'PUT'] and payload:
                if isinstance(payload, dict):
                    # Form data
                    for key, value in payload.items():
                        curl_parts.extend(['-d', f'"{key}={value}"'])
                else:
                    # Raw data
                    curl_parts.extend(['-d', f'"{payload}"'])
            
            # Add URL
            curl_parts.append(f'"{url}"')
            
            command = ' '.join(curl_parts)
            
            return jsonify({
                'success': True,
                'command': command,
                'parameters': {
                    'url': url,
                    'method': method,
                    'headers': headers,
                    'payload': payload
                }
            })
            
        except Exception as e:
            logger.error(f"API generate curl error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    logger.info("API routes registered successfully")
