import logging
from flask import request, jsonify
from datetime import datetime
import random
import time
import uuid

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Тестовое хранилище для обращений, когда БД недоступна
_memory_leads = []
_memory_interactions = {}

def register_test_routes(app):
    """
    Register test routes with the Flask app.
    
    Args:
        app: The Flask application instance
    """
    
    @app.route('/api/test/leads/create', methods=['POST'])
    def create_test_lead_api():
        """Create a test lead for debugging purposes"""
        try:
            # Create test data
            lead_id = str(random.randint(1000, 9999))
            test_data = {
                'id': lead_id,
                'customer_name': 'Тестовый Клиент',
                'customer_email': f'test_{uuid.uuid4().hex[:8]}@example.com',
                'customer_phone': '+7 (999) 123-45-67',
                'source': 'test',
                'status': 'new',
                'notes': 'Тестовое обращение создано для отладки',
                'tags': ['Тест', 'Отладка'],
                'created_at': datetime.now().isoformat()
            }
            
            # Store in memory
            _memory_leads.append(test_data)
            _memory_interactions[lead_id] = [
                {
                    'id': str(random.randint(10000, 99999)),
                    'lead_id': lead_id,
                    'agent_name': 'Test Agent',
                    'type': 'comment',
                    'notes': 'Это тестовое взаимодействие создано автоматически',
                    'created_at': datetime.now().isoformat()
                }
            ]
            
            # Try to create in actual database (if available)
            try:
                from models import LeadService
                LeadService.create_lead(test_data)
            except Exception as db_error:
                logger.warning(f"Could not create test lead in database: {db_error}")
            
            logger.info(f"Created test lead with ID: {lead_id}")
            return jsonify({
                'success': True,
                'lead': test_data,
                'message': 'Тестовое обращение успешно создано'
            })
            
        except Exception as e:
            logger.error(f"Error creating test lead: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
            
    @app.route('/api/test/leads/reset', methods=['POST'])
    def reset_leads_api():
        """Reset all leads (for debugging only)"""
        try:
            global _memory_leads, _memory_interactions
            
            # Clear memory storage
            _memory_leads = []
            _memory_interactions = {}
            
            # Try to clear database (if available)
            try:
                from models import LeadService
                LeadService.delete_all_leads()
            except Exception as db_error:
                logger.warning(f"Could not clear database leads: {db_error}")
            
            # Create one test lead
            lead_id = '1001'
            test_lead = {
                'id': lead_id,
                'customer_name': 'Тестовый Клиент',
                'customer_email': 'test@example.com',
                'customer_phone': '+7 (999) 123-45-67',
                'source': 'test',
                'status': 'new',
                'notes': 'Тестовое обращение создано после сброса',
                'created_at': datetime.now().isoformat(),
                'tags': ['Тест', 'Отладка']
            }
            
            _memory_leads.append(test_lead)
            _memory_interactions[lead_id] = [
                {
                    'id': '10001',
                    'lead_id': lead_id,
                    'agent_name': 'Система',
                    'type': 'system',
                    'notes': 'Обращение создано в рамках тестирования',
                    'created_at': datetime.now().isoformat()
                },
                {
                    'id': '10002',
                    'lead_id': lead_id,
                    'agent_name': 'AI Ассистент',
                    'type': 'ai_analysis',
                    'notes': 'Это обращение классифицировано как: запрос о бронировании\n\nРекомендуемые действия:\n1. Уточнить даты поездки\n2. Предложить варианты туров\n3. Проверить наличие мест',
                    'created_at': datetime.now().isoformat()
                }
            ]
            
            # Try to add to database
            try:
                from models import LeadService
                LeadService.create_lead(test_lead)
            except Exception as db_error:
                logger.warning(f"Could not create test lead in database: {db_error}")
            
            return jsonify({
                'success': True,
                'message': 'All leads reset, created one test lead'
            })
            
        except Exception as e:
            logger.error(f"Error resetting leads: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
            
    # API endpoints to handle in-memory leads when database is unavailable
    
    @app.route('/api/test/leads', methods=['GET'])
    def get_test_leads_api():
        """Get all test leads"""
        try:
            status = request.args.get('status')
            
            if status:
                filtered_leads = [lead for lead in _memory_leads if lead.get('status') == status]
                return jsonify({'leads': filtered_leads})
            else:
                return jsonify({'leads': _memory_leads})
        except Exception as e:
            logger.error(f"Error getting test leads: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
            
    @app.route('/api/test/leads/<lead_id>', methods=['GET'])
    def get_test_lead_api(lead_id):
        """Get a specific test lead by ID"""
        try:
            lead = next((lead for lead in _memory_leads if lead.get('id') == lead_id), None)
            
            if lead:
                return jsonify({'lead': lead})
            else:
                return jsonify({
                    'success': False,
                    'error': 'Lead not found'
                }), 404
        except Exception as e:
            logger.error(f"Error getting test lead: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
            
    @app.route('/api/test/leads/<lead_id>/status', methods=['PUT'])
    def update_test_lead_status_api(lead_id):
        """Update a test lead's status"""
        try:
            status_data = request.json
            
            if not status_data or 'status' not in status_data:
                return jsonify({
                    'success': False,
                    'error': 'Status not provided'
                }), 400
                
            new_status = status_data['status']
            lead = next((lead for lead in _memory_leads if lead.get('id') == lead_id), None)
            
            if lead:
                lead['status'] = new_status
                
                # Add an interaction for the status change
                if lead_id not in _memory_interactions:
                    _memory_interactions[lead_id] = []
                    
                _memory_interactions[lead_id].append({
                    'id': str(random.randint(10000, 99999)),
                    'lead_id': lead_id,
                    'agent_name': 'Система',
                    'type': 'status_change',
                    'notes': f'Статус изменен на: {new_status}',
                    'created_at': datetime.now().isoformat()
                })
                
                return jsonify({
                    'success': True,
                    'lead': lead
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Lead not found'
                }), 404
        except Exception as e:
            logger.error(f"Error updating test lead status: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
            
    @app.route('/api/test/leads/<lead_id>/interactions', methods=['GET'])
    def get_test_lead_interactions_api(lead_id):
        """Get interactions for a test lead"""
        try:
            interactions = _memory_interactions.get(lead_id, [])
            return jsonify({'interactions': interactions})
        except Exception as e:
            logger.error(f"Error getting test lead interactions: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
            
    @app.route('/api/test/leads/<lead_id>/interactions', methods=['POST'])
    def add_test_lead_interaction_api(lead_id):
        """Add an interaction to a test lead"""
        try:
            interaction_data = request.json
            
            if not interaction_data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
                
            # Find the lead
            lead = next((lead for lead in _memory_leads if lead.get('id') == lead_id), None)
            
            if not lead:
                return jsonify({
                    'success': False,
                    'error': 'Lead not found'
                }), 404
                
            # Create the interaction
            interaction = {
                'id': str(random.randint(10000, 99999)),
                'lead_id': lead_id,
                'agent_name': interaction_data.get('agent_name', 'Unknown'),
                'type': interaction_data.get('type', 'comment'),
                'notes': interaction_data.get('notes', ''),
                'created_at': datetime.now().isoformat()
            }
            
            # Add to memory store
            if lead_id not in _memory_interactions:
                _memory_interactions[lead_id] = []
                
            _memory_interactions[lead_id].append(interaction)
            
            return jsonify({
                'success': True,
                'interaction': interaction
            })
        except Exception as e:
            logger.error(f"Error adding test lead interaction: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500