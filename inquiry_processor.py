import os
import logging
import json
import openai
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize singleton instance
_inquiry_processor_instance = None

class InquiryProcessor:
    """Process customer inquiries with AI and automated rules"""
    
    def __init__(self):
        """Initialize the inquiry processor"""
        # Initialize OpenAI client
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.client = openai.OpenAI(api_key=self.openai_api_key)
        
        # Status transitions map (current_status -> possible next statuses)
        self.status_transitions = {
            'new': ['in_progress', 'cancelled'],
            'in_progress': ['pending', 'cancelled'],
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['closed', 'cancelled'],
            'closed': [],  # Terminal state
            'cancelled': []  # Terminal state
        }
        
        # Load config and agents from database
        self._load_config_and_agents()
        
    def process_inquiry(self, inquiry_data):
        """Process a new inquiry using AI
        
        Args:
            inquiry_data (dict): The inquiry data to process
            
        Returns:
            dict: Processed lead data with status and suggestion
        """
        try:
            from models import LeadService
            
            # Create a new lead
            lead_data = {
                'name': inquiry_data.get('name', ''),
                'email': inquiry_data.get('email', ''),
                'phone': inquiry_data.get('phone', ''),
                'message': inquiry_data.get('message', ''),
                'source': inquiry_data.get('source', 'website'),
                'status': 'new',
                'created_at': datetime.now().isoformat()
            }
            
            lead = LeadService.create_lead(lead_data)
            if not lead:
                logger.error("Failed to create lead")
                return {"error": "Failed to create lead"}
            
            # Analyze the lead with AI
            analysis_result = self.analyze_lead(lead)
            
            # Get result data
            lead_id = lead.get('id')
            status = analysis_result.get('status', 'new')
            suggestion = analysis_result.get('suggestion', '')
            
            # Update lead status
            if status != lead.get('status'):
                LeadService.update_lead(lead_id, {'status': status})
                
            # Add AI analysis as an interaction
            interaction_data = {
                'type': 'ai_analysis',
                'content': suggestion,
                'metadata': {
                    'confidence': analysis_result.get('confidence', 0),
                    'auto_processed': True
                }
            }
            LeadService.add_lead_interaction(lead_id, interaction_data)
            
            # Return the processed lead
            return {
                'lead_id': lead_id,
                'status': status,
                'suggestion': suggestion
            }
            
        except Exception as e:
            logger.error(f"Error processing inquiry: {e}")
            return {"error": str(e)}
        
    def _load_config_and_agents(self):
        """Load AI config and agents from the database"""
        from models import AIAgentService
        
        # Load configuration
        self.config = AIAgentService.get_config()
        
        # Load agents
        agents_list = AIAgentService.get_ai_agents()
        self.agents = {}
        
        # If no agents in the database, initialize with defaults
        if not agents_list:
            self._initialize_default_agents()
        else:
            # Convert list to dictionary with agent_id as key
            for agent in agents_list:
                self.agents[agent['id']] = agent
                
    def _initialize_default_agents(self):
        """Initialize default agents in the database"""
        from models import AIAgentService
        
        # Default agent definitions
        default_agents = [
            {
                'id': 'inquiry_analyzer',
                'name': 'Анализатор запросов',
                'type': 'classification',
                'description': 'Основной агент для анализа и классификации входящих запросов',
                'active': True,
                'prompt': self._get_inquiry_analysis_prompt()
            },
            {
                'id': 'booking_checker',
                'name': 'Проверка бронирований',
                'type': 'search',
                'description': 'Агент для поиска и проверки информации о бронированиях',
                'active': True,
                'prompt': self._get_booking_checker_prompt()
            },
            {
                'id': 'tour_recommender',
                'name': 'Рекомендатель туров',
                'type': 'recommendation',
                'description': 'Агент для подбора и рекомендации туров на основе предпочтений клиента',
                'active': False,
                'prompt': self._get_tour_recommender_prompt()
            }
        ]
        
        # Create agents in the database
        for agent_data in default_agents:
            created_agent = AIAgentService.create_ai_agent(agent_data)
            if created_agent:
                self.agents[created_agent['id']] = created_agent
    
    def process_new_inquiry(self, inquiry_data):
        """Process a new inquiry with AI analysis
        
        Args:
            inquiry_data (dict): The inquiry data to process
            
        Returns:
            dict: Processing results
        """
        try:
            # Analyze the inquiry text with AI
            if 'notes' in inquiry_data and inquiry_data['notes']:
                analysis = self._analyze_with_ai(inquiry_data['notes'])
            else:
                analysis = {
                    'category': 'unknown',
                    'urgency': 1,
                    'summary': 'No content to analyze',
                    'suggested_actions': ['Contact customer for more information']
                }
            
            # Create the lead in the database
            from models import LeadService
            
            # Add analysis results to lead data
            inquiry_data['category'] = analysis.get('category')
            inquiry_data['urgency'] = analysis.get('urgency')
            
            # Set initial status
            if 'status' not in inquiry_data:
                inquiry_data['status'] = 'new'
            
            # Create lead
            lead = LeadService.create_lead(inquiry_data)
            
            # Add an interaction with the analysis
            interaction_data = {
                'type': 'ai_analysis',
                'notes': f"AI Analysis:\n\n" +
                        f"Category: {analysis.get('category')}\n" +
                        f"Urgency: {analysis.get('urgency')}/5\n" +
                        f"Summary: {analysis.get('summary')}\n\n" +
                        f"Suggested Actions:\n" + '\n'.join([f"- {action}" for action in analysis.get('suggested_actions', [])])
            }
            
            LeadService.add_lead_interaction(lead['id'], interaction_data)
            
            return {
                'success': True,
                'lead': lead,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Error processing inquiry: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_inquiry_status(self, lead_id, data=None):
        """Update the status of an inquiry based on rules or requested status
        
        Args:
            lead_id (str): The lead ID to update
            data (dict, optional): Optional data with requested status
            
        Returns:
            dict: Updated lead data or None if not found
        """
        try:
            from models import LeadService
            
            # Get current lead data
            lead = LeadService.get_lead(lead_id)
            if not lead:
                return None
            
            current_status = lead.get('status')
            requested_status = data.get('requested_status') if data else None
            
            # Determine next status
            next_status = None
            
            # If specific status requested, check if it's a valid transition
            if requested_status and requested_status in self.status_transitions.get(current_status, []):
                next_status = requested_status
            else:
                # Apply automatic rules based on current status
                next_status = self._determine_next_status(lead)
            
            # If status change determined, update the lead
            if next_status and next_status != current_status:
                update_data = {'status': next_status}
                
                # Add a status change interaction
                interaction_data = {
                    'type': 'status_change',
                    'notes': f"Status changed automatically from '{current_status}' to '{next_status}'"
                }
                LeadService.add_lead_interaction(lead_id, interaction_data)
                
                # Update the lead status
                return LeadService.update_lead(lead_id, update_data)
            
            return lead
            
        except Exception as e:
            logger.error(f"Error updating inquiry status: {e}")
            return None
    
    def process_all_inquiries(self):
        """Process all active inquiries with AI and rules
        
        Returns:
            dict: Processing results
        """
        try:
            from models import LeadService
            
            # Get all active leads (excluding closed and cancelled)
            active_statuses = ['new', 'in_progress', 'pending', 'confirmed']
            leads = []
            
            for status in active_statuses:
                status_leads = LeadService.get_leads(status=status)
                if status_leads:
                    leads.extend(status_leads)
            
            results = {
                'total': len(leads),
                'updated': 0,
                'failed': 0,
                'details': []
            }
            
            # Process each lead
            for lead in leads:
                try:
                    updated_lead = self.update_inquiry_status(lead['id'])
                    
                    if updated_lead and updated_lead.get('status') != lead.get('status'):
                        results['updated'] += 1
                        results['details'].append({
                            'lead_id': lead['id'],
                            'old_status': lead['status'],
                            'new_status': updated_lead['status']
                        })
                except Exception as e:
                    results['failed'] += 1
                    logger.error(f"Error processing lead {lead['id']}: {e}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing all inquiries: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_lead(self, lead):
        """Analyze a lead with AI to determine status and suggestion
        
        Args:
            lead (dict): The lead data to analyze
            
        Returns:
            dict: Analysis results with status, suggestion, and confidence
        """
        try:
            # Get lead message or combine all lead data for analysis
            message = lead.get('message', '')
            if not message:
                # Fallback to a combination of all text data
                message = f"Name: {lead.get('name', '')}\n"
                message += f"Email: {lead.get('email', '')}\n"
                message += f"Phone: {lead.get('phone', '')}\n"
                message += f"Source: {lead.get('source', '')}\n"
                message += f"Notes: {lead.get('notes', '')}"
            
            # Process with OpenAI
            agent_id = self.config.get('default_agent_id', 'inquiry_analyzer')
            prompt = self._get_lead_analysis_prompt(lead, message)
            
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use the latest model
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": message}
                ],
                response_format={"type": "json_object"}
            )
            
            # Extract the response content
            ai_response = response.choices[0].message.content
            
            # Parse JSON response
            try:
                result = json.loads(ai_response)
                
                # Apply business rules to validate and sanitize the response
                valid_statuses = list(self.status_transitions.keys())
                if 'status' not in result or result['status'] not in valid_statuses:
                    result['status'] = 'in_progress'  # Default fallback status
                
                if 'confidence' not in result:
                    result['confidence'] = 0.7  # Default confidence
                
                if 'suggestion' not in result:
                    result['suggestion'] = "AI анализ выполнен"
                    
                return result
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse AI response: {ai_response}")
                return {
                    'status': 'in_progress',
                    'suggestion': "AI не смог проанализировать запрос корректно. Требуется ручная обработка.",
                    'confidence': 0.0
                }
                
        except Exception as e:
            logger.error(f"Error analyzing lead: {e}")
            return {
                'status': 'new',
                'suggestion': "Ошибка обработки AI. Требуется ручная обработка.",
                'confidence': 0.0
            }
            
    def process_leads_batch(self, limit=10, agent_id=None):
        """Process a batch of leads with AI
        
        Args:
            limit (int, optional): Maximum number of leads to process
            agent_id (str, optional): The agent ID to use for processing
            
        Returns:
            list: List of processed lead results
        """
        from models import LeadService
        
        if not agent_id:
            agent_id = self.config.get('default_agent_id', 'inquiry_analyzer')
        
        # Get leads with 'new' status
        leads = LeadService.get_leads(status='new', limit=limit)
        if not leads:
            return []
            
        results = []
        
        for lead in leads:
            try:
                # Analyze the lead
                analysis = self.analyze_lead(lead)
                
                # Get result data
                lead_id = lead.get('id')
                status = analysis.get('status', 'in_progress')  # Default to in_progress
                suggestion = analysis.get('suggestion', '')
                
                # Update lead status
                LeadService.update_lead({'status': status}, lead_id)
                
                # Add AI analysis as an interaction
                interaction_data = {
                    'type': 'ai_batch_analysis',
                    'content': suggestion,
                    'metadata': {
                        'confidence': analysis.get('confidence', 0),
                        'auto_processed': True
                    }
                }
                LeadService.add_lead_interaction(lead_id, interaction_data)
                
                # Add to results
                results.append({
                    'lead_id': lead_id,
                    'status': status,
                    'suggestion': suggestion,
                    'confidence': analysis.get('confidence', 0)
                })
                
            except Exception as e:
                logger.error(f"Error processing lead in batch: {e}")
                # Skip failed leads in results
        
        return results
            
    def generate_response(self, lead_id, context=None):
        """Generate a response for a lead based on its content and history
        
        Args:
            lead_id (str): The lead ID to generate a response for
            context (dict, optional): Additional context for the response
            
        Returns:
            dict: Generated response data
        """
        try:
            from models import LeadService
            
            # Get lead data
            lead = LeadService.get_lead(lead_id)
            if not lead:
                return {
                    'success': False,
                    'error': 'Lead not found'
                }
                
            # Get lead interactions
            interactions = LeadService.get_lead_interactions(lead_id)
            
            # Extract context for the response
            message_history = []
            for interaction in interactions:
                message_history.append({
                    'type': interaction.get('type', 'unknown'),
                    'content': interaction.get('content', ''),
                    'timestamp': interaction.get('created_at', '')
                })
                
            # Create a prompt for response generation
            system_prompt = self._get_response_generation_prompt(lead, message_history, context)
            
            # Generate response with OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use the latest model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Требуется сгенерировать ответ для клиента {lead.get('name', 'Клиент')}"}
                ]
            )
            
            generated_text = response.choices[0].message.content
            
            # Create a new interaction with the generated response
            interaction_data = {
                'type': 'ai_generated_response',
                'content': generated_text,
                'metadata': {
                    'auto_generated': True,
                    'context': context or {}
                }
            }
            
            LeadService.add_lead_interaction(lead_id, interaction_data)
            
            return {
                'success': True,
                'lead_id': lead_id,
                'response': generated_text
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def _get_lead_analysis_prompt(self, lead, message):
        """Generate a prompt for lead analysis
        
        Args:
            lead (dict): The lead data
            message (str): The message to analyze
            
        Returns:
            str: The analysis prompt
        """
        return """
        You are an expert travel agency lead analyzer. Your task is to analyze customer inquiries 
        and determine the appropriate status and next steps. 
        
        Analyze the customer message and respond with JSON containing:
        1. "status": The appropriate status for this lead. Must be one of: 
           ["new", "in_progress", "pending", "confirmed", "closed", "cancelled"]
        2. "suggestion": A specific suggestion for the travel agent on how to handle this lead
        3. "confidence": A number between 0 and 1 indicating your confidence in this analysis
        
        Use "in_progress" for leads that need active work.
        Use "pending" when waiting for a client response.
        Use "confirmed" when a booking is likely to be made.
        Use "closed" only for completed bookings.
        Use "cancelled" for inquiries that won't proceed.
        
        Respond only with the JSON object.
        """
    
    def _get_response_generation_prompt(self, lead, message_history, context):
        """Generate a prompt for response generation
        
        Args:
            lead (dict): The lead data
            message_history (list): History of interactions
            context (dict): Additional context
            
        Returns:
            str: The response generation prompt
        """
        return f"""
        You are a professional travel agent assistant for Crystal Bay Travel.
        
        Client information:
        - Name: {lead.get('name', 'Unknown')}
        - Email: {lead.get('email', 'Unknown')}
        - Phone: {lead.get('phone', 'Unknown')}
        - Current status: {lead.get('status', 'new')}
        - Initial inquiry: {lead.get('message', 'No initial message')}
        
        Your task is to generate a helpful, professional response based on the client's inquiry
        and interaction history. Be specific, courteous and maintain a warm business tone.
        
        Focus on providing the information the client needs and moving the booking process forward.
        
        If the context indicates specific offers or packages, include relevant details about them.
        
        Write only the response text that would be sent to the client, without additional notes or comments.
        """
            
    def _analyze_with_ai(self, text, agent_id='inquiry_analyzer'):
        """Analyze text with OpenAI to categorize and extract insights
        
        Args:
            text (str): The text to analyze
            agent_id (str, optional): The agent ID to use for analysis
            
        Returns:
            dict: Analysis results
        """
        # Check if AI system is active
        if not self.config.get('active', True):
            return {
                'category': 'system_inactive',
                'urgency': 3,
                'summary': 'AI analysis system is currently inactive',
                'suggested_actions': ['Activate AI system', 'Perform manual analysis'],
                'sentiment': 'neutral'
            }
            
        # Check if the agent exists and is active
        agent = self.agents.get(agent_id)
        if not agent or not agent.get('active', False):
            logger.warning(f"Agent {agent_id} not found or inactive")
            # Fall back to inquiry analyzer if available and active
            if agent_id != 'inquiry_analyzer' and 'inquiry_analyzer' in self.agents and self.agents['inquiry_analyzer'].get('active', False):
                return self._analyze_with_ai(text, 'inquiry_analyzer')
            else:
                return {
                    'category': 'agent_inactive',
                    'urgency': 3,
                    'summary': f'AI agent {agent_id} is not available or inactive',
                    'suggested_actions': ['Activate agent', 'Perform manual analysis'],
                    'sentiment': 'neutral'
                }
        
        try:
            # Get agent prompt or fall back to default
            system_prompt = agent.get('prompt', self._get_inquiry_analysis_prompt())
            
            # Use the newest OpenAI model - gpt-4o which was released May 13, 2024.
            # Do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model=self.config.get('model', 'gpt-4o'),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=self.config.get('temperature', 0.2),
                response_format={"type": "json_object"}
            )
            
            try:
                analysis = json.loads(response.choices[0].message.content)
                # Track usage for admin dashboard
                self._track_agent_usage(agent_id, successful=True)
                return analysis
            except json.JSONDecodeError:
                # If JSON parsing fails, return a structured format of the raw content
                content = response.choices[0].message.content
                self._track_agent_usage(agent_id, successful=False)
                return {
                    'category': 'parsing_error',
                    'urgency': 3,
                    'summary': 'Failed to parse AI response',
                    'suggested_actions': ['Review the raw analysis', 'Contact customer for clarification'],
                    'sentiment': 'neutral',
                    'raw_content': content
                }
                
        except Exception as e:
            logger.error(f"Error analyzing with AI: {e}")
            self._track_agent_usage(agent_id, successful=False)
            return {
                'category': 'error',
                'urgency': 3,
                'summary': f"Error during analysis: {str(e)}",
                'suggested_actions': ['Check AI service status', 'Try manual analysis'],
                'sentiment': 'neutral'
            }
    
    def _determine_next_status(self, lead):
        """Determine the next status for a lead based on its current state
        
        Args:
            lead (dict): The lead data
            
        Returns:
            str: Next status or None if no change needed
        """
        current_status = lead.get('status')
        
        # Simple state machine logic
        if current_status == 'new':
            # Move new leads to in_progress if they're urgent
            urgency = lead.get('urgency', 0)
            if urgency >= 4:
                return 'in_progress'
                
        elif current_status == 'in_progress':
            # Check if there are recent interactions that might warrant moving to pending
            interactions = lead.get('interactions', [])
            if len(interactions) >= 3:
                return 'pending'
                
        elif current_status == 'pending':
            # Look for booking references in the notes that might indicate a confirmation
            notes = lead.get('notes', '')
            if 'booking confirmed' in notes.lower() or any(ref_pattern in notes for ref_pattern in ['CB-', 'BK-']):
                return 'confirmed'
        
        # No status change determined
        return None


    def _get_inquiry_analysis_prompt(self):
        """Get the prompt for the inquiry analysis agent
        
        Returns:
            str: The prompt text
        """
        return """
        You are an AI assistant for a travel agency called 'Crystal Bay Travel'. 
        Analyze the customer inquiry and extract key information.
        
        Return a JSON response with the following fields:
        - category: The type of inquiry (e.g., beach_vacation, city_tour, cruise, flight_only, custom_tour, etc.)
        - urgency: Rate from 1-5 how urgent this inquiry seems (5 being most urgent)
        - summary: A brief 1-2 sentence summary of the inquiry
        - suggested_actions: A list of 2-3 specific actions the travel agent should take
        - sentiment: The customer's sentiment (positive, neutral, negative)
        
        Base your analysis only on the facts in the text. If information is missing, suggest requesting it rather than making assumptions.
        """
    
    def _get_booking_checker_prompt(self):
        """Get the prompt for the booking checker agent
        
        Returns:
            str: The prompt text
        """
        return """
        You are an AI assistant for a travel agency called 'Crystal Bay Travel'.
        Your task is to extract booking reference numbers from customer messages.
        
        Return a JSON response with the following fields:
        - booking_references: An array of potential booking reference numbers found in the text (e.g., "CB-12345", "BK-98765")
        - has_booking_inquiry: Boolean indicating if this appears to be a booking-related inquiry
        - booking_inquiry_type: The type of booking inquiry (e.g., "status_check", "modification", "cancellation", "question")
        - additional_info_needed: An array of any additional information needed to process the booking inquiry
        
        Only extract actual booking references - do not make up or assume references that aren't explicitly mentioned.
        """
    
    def _get_tour_recommender_prompt(self):
        """Get the prompt for the tour recommender agent
        
        Returns:
            str: The prompt text
        """
        return """
        You are an AI assistant for a travel agency called 'Crystal Bay Travel'.
        Your task is to analyze customer preferences and recommend suitable tour types.
        
        Return a JSON response with the following fields:
        - preferences: An object containing extracted customer preferences (destination_type, budget_level, travel_style, etc.)
        - recommended_tour_types: An array of 2-4 tour types that would suit this customer
        - suggested_destinations: An array of 2-4 destinations that match their preferences
        - questions_to_ask: An array of follow-up questions to better understand their needs
        
        Base recommendations only on explicitly stated preferences. For unstated preferences, include appropriate follow-up questions.
        """
    
    def update_agent_config(self, config_data):
        """Update the agent configuration in the database
        
        Args:
            config_data (dict): New configuration data
            
        Returns:
            dict: Updated configuration
        """
        try:
            # Validate and convert values
            if 'temperature' in config_data:
                try:
                    config_data['temperature'] = float(config_data['temperature'])
                    # Ensure temperature is within valid range (0.0 to 1.0)
                    if config_data['temperature'] < 0.0 or config_data['temperature'] > 1.0:
                        logger.warning(f"Temperature out of range (0.0-1.0): {config_data['temperature']}")
                        config_data['temperature'] = max(0.0, min(1.0, config_data['temperature']))
                except (ValueError, TypeError):
                    # Remove invalid temperature
                    logger.warning(f"Invalid temperature value: {config_data['temperature']}")
                    del config_data['temperature']
                    
            if 'active' in config_data:
                config_data['active'] = bool(config_data['active'])
                
            if 'model' in config_data:
                # Validate model is one of the supported models
                valid_models = ['gpt-4o', 'gpt-3.5-turbo']
                if config_data['model'] not in valid_models:
                    logger.warning(f"Invalid model: {config_data['model']}. Defaulting to gpt-4o.")
                    config_data['model'] = 'gpt-4o'
            
            # Use database service to update config
            from models import AIAgentService
            
            # Save to database
            logger.info(f"Saving AI configuration to database")
            updated_config = AIAgentService.save_config(config_data)
            
            # Update local cache
            if updated_config:
                logger.info("Successfully updated AI configuration in database")
                self.config = updated_config
                
                # Update OpenAI client if API key changed
                if 'api_key' in updated_config and updated_config['api_key']:
                    self.openai_api_key = updated_config['api_key']
                    import openai
                    self.client = openai.OpenAI(api_key=self.openai_api_key)
                    logger.info("Updated OpenAI client with new API key")
            else:
                # Apply updates locally if database operation fails
                logger.info("Applying configuration updates to local cache as fallback")
                for key, value in config_data.items():
                    if value is not None and value != '':
                        self.config[key] = value
                
            return self.config
        except Exception as e:
            logger.error(f"Error updating agent configuration: {e}")
            # Apply updates locally if exception occurs
            logger.info("Applying configuration updates to local cache due to error")
            for key, value in config_data.items():
                if value is not None and value != '':
                    self.config[key] = value
                    
            return self.config
    
    def update_agent(self, agent_id, agent_data):
        """Update an agent's configuration in the database
        
        Args:
            agent_id (str): The agent ID to update
            agent_data (dict): New agent data
            
        Returns:
            dict: Updated agent data or None if not found
        """
        try:
            # Use database service to update agent
            from models import AIAgentService
            
            # Only include allowed fields
            update_data = {}
            allowed_fields = ['name', 'description', 'active', 'prompt', 'type', 'output_format']
            for field in allowed_fields:
                if field in agent_data:
                    update_data[field] = agent_data[field]
            
            # Update agent in database
            updated_agent = AIAgentService.update_ai_agent(agent_id, update_data)
            
            # Update local cache if successful
            if updated_agent:
                self.agents[agent_id] = updated_agent
                return updated_agent
            else:
                # If agent not found in database but exists in local cache
                if agent_id in self.agents:
                    # Apply updates locally
                    for field in allowed_fields:
                        if field in agent_data:
                            self.agents[agent_id][field] = agent_data[field]
                    return self.agents[agent_id]
                return None
                
        except Exception as e:
            logger.error(f"Error updating agent {agent_id}: {e}")
            # Fallback to local update
            if agent_id in self.agents:
                # Apply updates locally
                allowed_fields = ['name', 'description', 'active', 'prompt']
                for field in allowed_fields:
                    if field in agent_data:
                        self.agents[agent_id][field] = agent_data[field]
                return self.agents[agent_id]
            return None
    
    def add_agent(self, agent_data):
        """Add a new agent to the database
        
        Args:
            agent_data (dict): Agent data including id, name, type, description, prompt
            
        Returns:
            dict: Created agent data or None if invalid
        """
        try:
            # Validate required fields
            required_fields = ['id', 'name', 'type', 'description', 'prompt']
            if not all(field in agent_data for field in required_fields):
                logger.error(f"Missing required fields for new agent. Required: {required_fields}")
                return None
                
            agent_id = agent_data['id']
            
            # Use database service to create agent
            from models import AIAgentService
            
            # Check if agent already exists in database
            existing_agent = AIAgentService.get_ai_agent(agent_id)
            if existing_agent:
                logger.warning(f"Agent ID {agent_id} already exists in database")
                return None
            
            # Set default values
            if 'active' not in agent_data:
                agent_data['active'] = True
                
            # Create agent in database
            created_agent = AIAgentService.create_ai_agent(agent_data)
            
            # Update local cache if successful
            if created_agent:
                self.agents[agent_id] = created_agent
                return created_agent
            else:
                logger.error(f"Failed to create agent {agent_id} in database")
                return None
                
        except Exception as e:
            logger.error(f"Error adding new agent: {e}")
            # Fallback to local creation
            try:
                # Check again required fields and agent existence
                required_fields_fallback = ['id', 'name', 'type', 'description', 'prompt']
                if not all(field in agent_data for field in required_fields_fallback):
                    return None
                    
                agent_id = agent_data['id']
                if agent_id in self.agents:
                    return None  # Agent ID already exists
                    
                # Create new agent locally
                self.agents[agent_id] = {
                    'id': agent_id,
                    'name': agent_data['name'],
                    'type': agent_data['type'],
                    'description': agent_data['description'],
                    'active': agent_data.get('active', True),
                    'prompt': agent_data['prompt'],
                    'usage': {
                        'total_calls': 0,
                        'successful_calls': 0,
                        'failed_calls': 0,
                        'last_used': None
                    }
                }
                
                return self.agents[agent_id]
            except Exception as inner_e:
                logger.error(f"Error in fallback agent creation: {inner_e}")
                return None
    
    def get_agents(self):
        """Get all configured agents from the database
        
        Returns:
            dict: Agent configurations
        """
        try:
            # Refresh from database
            from models import AIAgentService
            agents_list = AIAgentService.get_ai_agents()
            
            # Update local cache
            if agents_list:
                self.agents = {agent['id']: agent for agent in agents_list}
                
            return self.agents
        except Exception as e:
            logger.error(f"Error getting agents from database: {e}")
            # Return local cache as fallback
            return self.agents
    
    def get_agent(self, agent_id):
        """Get a specific agent's configuration from the database
        
        Args:
            agent_id (str): The agent ID
            
        Returns:
            dict: Agent configuration or None if not found
        """
        try:
            # Get fresh data from database
            from models import AIAgentService
            agent = AIAgentService.get_ai_agent(agent_id)
            
            # Update local cache if found
            if agent:
                self.agents[agent_id] = agent
                return agent
            
            # If not found in database but exists in local cache,
            # return from cache
            if agent_id in self.agents:
                return self.agents[agent_id]
                
            return None
        except Exception as e:
            logger.error(f"Error getting agent {agent_id} from database: {e}")
            # Fallback to local cache
            return self.agents.get(agent_id)
    
    def get_config(self):
        """Get the current AI configuration
        
        Returns:
            dict: Current configuration
        """
        try:
            # Refresh from database to ensure latest settings
            from models import AIAgentService
            self.config = AIAgentService.get_config()
            logger.info("Retrieved updated AI configuration from database")
            return self.config
        except Exception as e:
            logger.error(f"Error getting AI configuration: {e}")
            # Return current cached configuration as fallback
            return self.config
        
    def _track_agent_usage(self, agent_id, successful=True):
        """Track usage statistics for an agent
        
        Args:
            agent_id (str): The agent ID
            successful (bool, optional): Whether the call was successful
            
        Returns:
            None
        """
        try:
            # Check if agent exists in local cache
            if agent_id not in self.agents:
                return
                
            # Use database service to track usage
            from models import AIAgentService
            
            # Track usage in the database
            updated_agent = AIAgentService.track_agent_usage(agent_id, successful)
            
            # Update local cache if successful
            if updated_agent:
                self.agents[agent_id] = updated_agent
            else:
                # Fallback to in-memory tracking if database operation fails
                self._track_agent_usage_local(agent_id, successful)
                
        except Exception as e:
            logger.error(f"Error tracking agent usage: {e}")
            # Fallback to in-memory tracking if exception occurs
            self._track_agent_usage_local(agent_id, successful)
    
    def _track_agent_usage_local(self, agent_id, successful=True):
        """Fallback method to track usage statistics in memory
        
        Args:
            agent_id (str): The agent ID
            successful (bool, optional): Whether the call was successful
            
        Returns:
            None
        """
        if agent_id not in self.agents:
            return
            
        # Initialize usage tracking if not present
        if 'usage' not in self.agents[agent_id]:
            self.agents[agent_id]['usage'] = {
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'last_used': None
            }
            
        # Update stats
        usage = self.agents[agent_id]['usage']
        usage['total_calls'] += 1
        
        if successful:
            usage['successful_calls'] += 1
        else:
            usage['failed_calls'] += 1
            
        usage['last_used'] = datetime.now().isoformat()
        
    def get_agent_usage_stats(self):
        """Get usage statistics for all agents
        
        Returns:
            dict: Agent usage statistics
        """
        try:
            # Use database service to get usage statistics
            from models import AIAgentService
            return AIAgentService.get_agent_usage_stats()
        except Exception as e:
            logger.error(f"Error getting agent usage stats from database: {e}")
            # Fallback to local calculation if database fails
            return self._get_agent_usage_stats_local()
    
    def _get_agent_usage_stats_local(self):
        """Calculate usage statistics from local cache as fallback
        
        Returns:
            dict: Agent usage statistics
        """
        try:
            logger.info("Calculating agent statistics from local cache")
            stats = {
                'total_processed': 0,
                'total_successful': 0,
                'total_failed': 0,
                'agents': {},
                'cache_status': 'local_fallback',
                'timestamp': datetime.now().isoformat()
            }
            
            if not self.agents:
                logger.warning("No agents found in local cache for statistics calculation")
                return stats
                
            active_agents = 0
            inactive_agents = 0
            agents_with_calls = 0
            
            for agent_id, agent in self.agents.items():
                usage = agent.get('usage', {})
                stats['total_processed'] += usage.get('total_calls', 0)
                stats['total_successful'] += usage.get('successful_calls', 0)
                stats['total_failed'] += usage.get('failed_calls', 0)
                
                # Track agent status counts
                if agent.get('active', False):
                    active_agents += 1
                else:
                    inactive_agents += 1
                    
                if usage.get('total_calls', 0) > 0:
                    agents_with_calls += 1
                
                # Calculate success rate, avoiding division by zero
                total_calls = max(1, usage.get('total_calls', 0)) if usage.get('total_calls', 0) > 0 else 0
                
                if total_calls > 0:
                    success_rate = (usage.get('successful_calls', 0) / total_calls) * 100
                else:
                    success_rate = 0.0
                
                # Add agent stats
                stats['agents'][agent_id] = {
                    'name': agent.get('name', agent_id),
                    'type': agent.get('type', 'unknown'),
                    'active': agent.get('active', False),
                    'total_calls': usage.get('total_calls', 0),
                    'successful_calls': usage.get('successful_calls', 0),
                    'failed_calls': usage.get('failed_calls', 0),
                    'success_rate': round(success_rate, 1),
                    'last_used': usage.get('last_used')
                }
            
            # Add summary stats
            stats['agent_counts'] = {
                'total': len(self.agents),
                'active': active_agents,
                'inactive': inactive_agents,
                'with_usage': agents_with_calls
            }
            
            # Calculate overall success rate
            if stats['total_processed'] > 0:
                stats['overall_success_rate'] = round((stats['total_successful'] / stats['total_processed']) * 100, 1)
            else:
                stats['overall_success_rate'] = 0.0
                
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating local agent statistics: {e}")
            # Return minimal stats in case of error
            return {
                'total_processed': 0,
                'total_successful': 0,
                'total_failed': 0,
                'agents': {},
                'error': str(e),
                'cache_status': 'error'
            }


def get_inquiry_processor():
    """Get the singleton instance of InquiryProcessor
    
    Returns:
        InquiryProcessor: The singleton instance
    """
    global _inquiry_processor_instance
    
    if _inquiry_processor_instance is None:
        _inquiry_processor_instance = InquiryProcessor()
        
    return _inquiry_processor_instance