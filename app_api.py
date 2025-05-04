import logging
from flask import request, jsonify
from datetime import datetime

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def register_api_routes(app):
    """
    Register all API routes with the Flask app.
    
    Args:
        app: The Flask application instance
    """
    
    @app.route('/api/leads', methods=['GET'])
    def get_leads_api():
        """Get all leads for the API"""
        try:
            from models import LeadService
            
            status = request.args.get('status')
            limit = request.args.get('limit', 100, type=int)
            
            leads = LeadService.get_leads(limit=limit, status=status)
            return jsonify({'leads': leads})
        except Exception as e:
            logger.error(f"Error retrieving leads: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    @app.route('/api/leads/<lead_id>', methods=['GET'])
    def get_lead_api(lead_id):
        """Get a specific lead by ID"""
        try:
            from models import LeadService
            
            lead = LeadService.get_lead(lead_id)
            if not lead:
                return jsonify({'error': 'Lead not found'}), 404
            
            return jsonify({'lead': lead})
        except Exception as e:
            logger.error(f"Error retrieving lead {lead_id}: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    @app.route('/api/leads/<lead_id>', methods=['PUT'])
    def update_lead_api(lead_id):
        """Update a lead"""
        try:
            from models import LeadService
            
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            lead = LeadService.update_lead(lead_id, data)
            if not lead:
                return jsonify({'error': 'Lead not found'}), 404
            
            return jsonify({'lead': lead})
        except Exception as e:
            logger.error(f"Error updating lead {lead_id}: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    @app.route('/api/leads', methods=['POST'])
    def create_lead_api():
        """Create a new lead"""
        try:
            from models import LeadService
            
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            lead = LeadService.create_lead(data)
            return jsonify({'lead': lead}), 201
        except Exception as e:
            logger.error(f"Error creating lead: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    @app.route('/api/leads/<lead_id>/interactions', methods=['GET'])
    def get_lead_interactions_api(lead_id):
        """Get interactions for a lead"""
        try:
            from models import LeadService
            
            interactions = LeadService.get_lead_interactions(lead_id)
            return jsonify({'interactions': interactions})
        except Exception as e:
            logger.error(f"Error retrieving interactions for lead {lead_id}: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    @app.route('/api/leads/<lead_id>/interactions', methods=['POST'])
    def add_lead_interaction_api(lead_id):
        """Add an interaction to a lead"""
        try:
            from models import LeadService
            
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            interaction = LeadService.add_lead_interaction(lead_id, data)
            return jsonify({'interaction': interaction}), 201
        except Exception as e:
            logger.error(f"Error adding interaction to lead {lead_id}: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    @app.route('/api/leads/process', methods=['POST'])
    def process_inquiry_api():
        """Process a new inquiry with AI"""
        try:
            from inquiry_processor import get_inquiry_processor
            
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            processor = get_inquiry_processor()
            result = processor.process_new_inquiry(data)
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error processing inquiry: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    @app.route('/api/leads/<lead_id>/analyze', methods=['POST'])
    def analyze_lead_api(lead_id):
        """Analyze a lead with AI"""
        try:
            from models import LeadService
            from inquiry_processor import get_inquiry_processor
            
            # Get the lead data
            lead = LeadService.get_lead(lead_id)
            if not lead:
                return jsonify({'error': 'Lead not found'}), 404
            
            # Process the content with AI
            processor = get_inquiry_processor()
            analysis = processor._analyze_with_ai(lead.get('notes', ''))
            
            # Add an interaction with the analysis results
            interaction_data = {
                'type': 'ai_analysis',
                'notes': f"AI Analysis:\n\n" +
                        f"Category: {analysis.get('category')}\n" +
                        f"Urgency: {analysis.get('urgency')}/5\n" +
                        f"Summary: {analysis.get('summary')}\n\n" +
                        f"Suggested Actions:\n" + '\n'.join([f"- {action}" for action in analysis.get('suggested_actions', [])])
            }
            
            LeadService.add_lead_interaction(lead_id, interaction_data)
            
            # Return the analysis results
            return jsonify({
                'lead_id': lead_id,
                'analysis': analysis
            })
        except Exception as e:
            logger.error(f"Error analyzing lead {lead_id}: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    @app.route('/api/leads/<lead_id>/update-status', methods=['POST'])
    def update_inquiry_status_api(lead_id):
        """Update the status of an inquiry"""
        try:
            from inquiry_processor import get_inquiry_processor
            
            data = request.json or {}
            
            processor = get_inquiry_processor()
            result = processor.update_inquiry_status(lead_id, data)
            
            if not result:
                return jsonify({'error': 'Lead not found'}), 404
            
            return jsonify({'lead': result})
        except Exception as e:
            logger.error(f"Error updating inquiry status for {lead_id}: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    @app.route('/api/leads/process-all', methods=['POST'])
    def process_all_inquiries_api():
        """Process all active inquiries"""
        try:
            from inquiry_processor import get_inquiry_processor
            
            processor = get_inquiry_processor()
            result = processor.process_all_inquiries()
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error processing all inquiries: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    @app.route('/api/bookings/check/<reference>', methods=['GET'])
    def check_booking_api(reference):
        """Check a booking's details"""
        try:
            from api_integration import get_api_integration
            
            api = get_api_integration()
            result = api.check_booking(reference)
            
            if not result:
                return jsonify({'error': 'Booking not found'}), 404
            
            return jsonify({'booking': result})
        except Exception as e:
            logger.error(f"Error checking booking {reference}: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    @app.route('/api/flights/check', methods=['GET'])
    def check_flight_api():
        """Check a flight's status"""
        try:
            from api_integration import get_api_integration
            
            flight_number = request.args.get('flight_number')
            flight_date = request.args.get('flight_date')
            
            if not flight_number or not flight_date:
                return jsonify({'error': 'Flight number and date are required'}), 400
            
            api = get_api_integration()
            result = api.check_flight(flight_number, flight_date)
            
            if not result:
                return jsonify({'error': 'Flight not found'}), 404
            
            return jsonify({'flight': result})
        except Exception as e:
            logger.error(f"Error checking flight {flight_number}: {e}")
            return jsonify({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    
    # AI Agents API Routes
    @app.route('/api/agents/config', methods=['GET'])
    def get_agents_config_api():
        """Get the current AI configuration"""
        try:
            from inquiry_processor import get_inquiry_processor
            
            processor = get_inquiry_processor()
            config = processor.get_config()
            
            return jsonify({
                'success': True,
                'config': config,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error getting agent config: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @app.route('/api/agents/config', methods=['PUT'])
    def update_agents_config_api():
        """Update the AI configuration"""
        try:
            from inquiry_processor import get_inquiry_processor
            
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            processor = get_inquiry_processor()
            config = processor.update_agent_config(data)
            
            return jsonify({
                'success': True,
                'config': config,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error updating agent config: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @app.route('/api/agents', methods=['GET'])
    def get_agents_api():
        """Get all AI agents"""
        try:
            from inquiry_processor import get_inquiry_processor
            
            processor = get_inquiry_processor()
            agents = processor.get_agents()
            
            return jsonify({
                'success': True,
                'agents': agents,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error getting agents: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @app.route('/api/agents/<agent_id>', methods=['GET'])
    def get_agent_api(agent_id):
        """Get a specific AI agent"""
        try:
            from inquiry_processor import get_inquiry_processor
            
            processor = get_inquiry_processor()
            agent = processor.get_agent(agent_id)
            
            if not agent:
                return jsonify({'error': 'Agent not found'}), 404
            
            return jsonify({
                'success': True,
                'agent': agent,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error getting agent {agent_id}: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @app.route('/api/agents/<agent_id>', methods=['PUT'])
    def update_agent_api(agent_id):
        """Update an AI agent"""
        try:
            from inquiry_processor import get_inquiry_processor
            
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            processor = get_inquiry_processor()
            agent = processor.update_agent(agent_id, data)
            
            if not agent:
                return jsonify({'error': 'Agent not found'}), 404
            
            return jsonify({
                'success': True,
                'agent': agent,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error updating agent {agent_id}: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @app.route('/api/agents', methods=['POST'])
    def add_agent_api():
        """Add a new AI agent"""
        try:
            from inquiry_processor import get_inquiry_processor
            
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            processor = get_inquiry_processor()
            agent = processor.add_agent(data)
            
            if not agent:
                return jsonify({'error': 'Invalid agent data or agent ID already exists'}), 400
            
            return jsonify({
                'success': True,
                'agent': agent,
                'timestamp': datetime.now().isoformat()
            }), 201
        except Exception as e:
            logger.error(f"Error adding agent: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @app.route('/api/agents/stats', methods=['GET'])
    def get_agent_stats_api():
        """Get AI agent usage statistics"""
        try:
            from inquiry_processor import get_inquiry_processor
            
            processor = get_inquiry_processor()
            stats = processor.get_agent_usage_stats()
            
            return jsonify({
                'success': True,
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error getting agent stats: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    logger.info('API routes registered successfully')
    return app