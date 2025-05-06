"""
Database models for the Crystal Bay Travel application.
These models define the structure of the data in Supabase.
"""
import os
import sys
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Supabase client with error handling
supabase = None
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

# In-memory fallback data stores when database is unavailable
_memory_ai_config = {
    'model': 'gpt-4o',
    'temperature': 0.2,
    'active': True
}
_memory_ai_agents = {}

# Sample leads data for demo when database is unavailable
_memory_leads = [
    {
        'id': '1001',
        'name': 'Анна Смирнова',
        'email': 'anna.smirnova@example.com',
        'phone': '+7 (xxx) xxx-xx-xx',
        'source': 'telegram',
        'status': 'new',
        'created_at': '2025-05-05T10:00:00',
        'details': 'Запрос на тур в Турцию, семейный отдых, июль-август 2025',
        'tags': ['Пляжный отдых', 'Семья']
    },
    {
        'id': '1002',
        'name': 'Иван Петров',
        'email': 'ivan.petrov@example.com',
        'phone': '+7 (xxx) xxx-xx-xx',
        'source': 'website',
        'status': 'new',
        'created_at': '2025-05-05T11:00:00',
        'details': 'Запрос на экскурсионный тур по Европе, интересуют Италия, Испания, Франция',
        'tags': ['Экскурсии', 'Европа']
    },
    {
        'id': '1003',
        'name': 'Екатерина Васильева',
        'email': 'ekaterina.vasilyeva@example.com',
        'phone': '+7 (xxx) xxx-xx-xx',
        'source': 'phone',
        'status': 'new',
        'created_at': '2025-05-05T12:00:00',
        'details': 'Запрос о горнолыжном отдыхе в Австрии или Швейцарии, декабрь 2025',
        'tags': ['Горнолыжный', 'Зима']
    }
]

try:
    if not supabase_url or not supabase_key:
        logger.warning("SUPABASE_URL or SUPABASE_KEY not set. Using memory storage fallback.")
    else:
        from supabase import create_client, Client
        supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized successfully")
except ImportError:
    logger.error("Could not import supabase module. Please install it with 'pip install supabase'")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    logger.warning("Using in-memory storage as fallback")

def is_supabase_available():
    """Check if Supabase is available for database operations"""
    return supabase is not None

class BookingService:
    """Service class for handling bookings in Supabase database"""
    
    @staticmethod
    def create_booking(booking_data):
        """
        Create a new booking in the Supabase database
        
        Args:
            booking_data (dict): The booking data including:
                - customer_name: Full name of the customer
                - customer_phone: Phone number
                - customer_email: Email address
                - tour_id: ID of the selected tour
                - departure_city: City of departure
                - destination_country: Country of destination
                - checkin_date: Check-in date
                - nights: Number of nights
                - adults: Number of adults
                - children: Number of children (optional)
                - price: Total price
                - currency: Currency code
                - status: Booking status (pending, confirmed, cancelled)
                - telegram_user_id: Telegram user ID if booked via Telegram
                
        Returns:
            dict: The created booking data with an ID
        """
        # Add creation timestamp
        booking_data['created_at'] = datetime.now().isoformat()
        
        # Insert into Supabase
        result = supabase.table("bookings").insert(booking_data).execute()
        
        # Return the created booking
        return result.data[0] if result.data else None
    
    @staticmethod
    def get_bookings(limit=100, status=None):
        """
        Get all bookings, optionally filtered by status
        
        Args:
            limit (int): Maximum number of bookings to return
            status (str, optional): Filter by booking status
            
        Returns:
            list: List of bookings
        """
        query = supabase.table("bookings").select("*").limit(limit)
        
        if status:
            query = query.eq("status", status)
            
        result = query.execute()
        return result.data if result.data else []
    
    @staticmethod
    def get_booking(booking_id):
        """
        Get a specific booking by ID
        
        Args:
            booking_id (str): The booking ID
            
        Returns:
            dict: The booking data or None if not found
        """
        result = supabase.table("bookings").select("*").eq("id", booking_id).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def update_booking_status(booking_id, status):
        """
        Update the status of a booking
        
        Args:
            booking_id (str): The booking ID
            status (str): The new status (pending, confirmed, cancelled)
            
        Returns:
            dict: The updated booking data
        """
        result = supabase.table("bookings").update({"status": status}).eq("id", booking_id).execute()
        return result.data[0] if result.data else None
        
class LeadService:
    """Service class for handling leads in Supabase database"""
    
    @staticmethod
    def create_lead(lead_data):
        """
        Create a new lead in the Supabase database
        
        Args:
            lead_data (dict): The lead data including:
                - customer_name: Full name of the customer
                - customer_phone: Phone number
                - customer_email: Email address
                - source: Source of the lead (website, telegram, etc.)
                - interest: What the customer is interested in
                - status: Lead status (new, contacted, qualified, converted, lost)
                - agent_id: ID of the assigned agent (optional)
                - notes: Additional notes (optional)
                
        Returns:
            dict: The created lead data with an ID
        """
        # Add creation timestamp
        lead_data['created_at'] = datetime.now().isoformat()
        if 'status' not in lead_data:
            lead_data['status'] = 'new'
        
        # Insert into Supabase
        result = supabase.table("leads").insert(lead_data).execute()
        
        # Return the created lead
        return result.data[0] if result.data else None
    
    @staticmethod
    def get_leads(limit=100, status=None, agent_id=None):
        """
        Get all leads, optionally filtered by status or agent
        
        Args:
            limit (int): Maximum number of leads to return
            status (str, optional): Filter by lead status
            agent_id (str, optional): Filter by assigned agent
            
        Returns:
            list: List of leads
        """
        query = supabase.table("leads").select("*").limit(limit)
        
        if status:
            query = query.eq("status", status)
        
        if agent_id:
            query = query.eq("agent_id", agent_id)
            
        result = query.execute()
        return result.data if result.data else []
    
    @staticmethod
    def get_lead(lead_id):
        """
        Get a specific lead by ID
        
        Args:
            lead_id (str): The lead ID
            
        Returns:
            dict: The lead data or None if not found
        """
        result = supabase.table("leads").select("*").eq("id", lead_id).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def update_lead(lead_id, update_data):
        """
        Update a lead
        
        Args:
            lead_id (str): The lead ID
            update_data (dict): The data to update
            
        Returns:
            dict: The updated lead data
        """
        update_data['updated_at'] = datetime.now().isoformat()
        result = supabase.table("leads").update(update_data).eq("id", lead_id).execute()
        return result.data[0] if result.data else None
        
    @staticmethod
    def add_lead_interaction(lead_id, interaction_data):
        """
        Add an interaction to a lead
        
        Args:
            lead_id (str): The lead ID
            interaction_data (dict): The interaction data including:
                - type: Type of interaction (call, email, meeting, etc.)
                - notes: Notes about the interaction
                - agent_id: ID of the agent who performed the interaction
                
        Returns:
            dict: The created interaction data
        """
        interaction_data['lead_id'] = lead_id
        interaction_data['created_at'] = datetime.now().isoformat()
        
        result = supabase.table("lead_interactions").insert(interaction_data).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def get_lead_interactions(lead_id):
        """
        Get all interactions for a lead
        
        Args:
            lead_id (str): The lead ID
            
        Returns:
            list: List of interactions
        """
        result = supabase.table("lead_interactions").select("*").eq("lead_id", lead_id).order("created_at", desc=True).execute()
        return result.data if result.data else []

class AgentService:
    """Service class for handling travel agents in Supabase database"""
    
    @staticmethod
    def create_agent(agent_data):
        """
        Create a new agent in the Supabase database
        
        Args:
            agent_data (dict): The agent data including:
                - name: Full name of the agent
                - email: Email address
                - phone: Phone number
                - role: Role of the agent (admin, manager, agent)
                - avatar_url: URL to agent's avatar (optional)
                - status: Agent status (active, inactive)
                
        Returns:
            dict: The created agent data with an ID
        """
        # Add creation timestamp
        agent_data['created_at'] = datetime.now().isoformat()
        
        # Insert into Supabase
        result = supabase.table("agents").insert(agent_data).execute()
        
        # Return the created agent
        return result.data[0] if result.data else None
    
    @staticmethod
    def get_agents(limit=100, status='active'):
        """
        Get all agents, optionally filtered by status
        
        Args:
            limit (int): Maximum number of agents to return
            status (str, optional): Filter by agent status
            
        Returns:
            list: List of agents
        """
        query = supabase.table("agents").select("*").limit(limit)
        
        if status:
            query = query.eq("status", status)
            
        result = query.execute()
        return result.data if result.data else []
    
    @staticmethod
    def get_agent(agent_id):
        """
        Get a specific agent by ID
        
        Args:
            agent_id (str): The agent ID
            
        Returns:
            dict: The agent data or None if not found
        """
        result = supabase.table("agents").select("*").eq("id", agent_id).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def update_agent(agent_id, update_data):
        """
        Update an agent
        
        Args:
            agent_id (str): The agent ID
            update_data (dict): The data to update
            
        Returns:
            dict: The updated agent data
        """
        update_data['updated_at'] = datetime.now().isoformat()
        result = supabase.table("agents").update(update_data).eq("id", agent_id).execute()
        return result.data[0] if result.data else None
        

class AIAgentService:
    """Service class for handling AI agents in Supabase database"""
    
    @staticmethod
    def save_config(config_data):
        """
        Save AI configuration to the database
        
        Args:
            config_data (dict): The configuration data including:
                - model: The OpenAI model to use
                - temperature: The temperature setting
                - active: Whether the AI system is active
                
        Returns:
            dict: The saved configuration data
        """
        config_data['updated_at'] = datetime.now().isoformat()
        
        # Check if Supabase is available
        if is_supabase_available():
            try:
                # Check if config exists
                result = supabase.table("ai_config").select("*").limit(1).execute()
                
                if result.data and len(result.data) > 0:
                    # Update existing config
                    config_id = result.data[0]['id']
                    result = supabase.table("ai_config").update(config_data).eq("id", config_id).execute()
                else:
                    # Create new config
                    config_data['created_at'] = datetime.now().isoformat()
                    result = supabase.table("ai_config").insert(config_data).execute()
                
                return result.data[0] if result.data else None
            except Exception as e:
                logger.error(f"Failed to save AI config to database: {e}")
                # Fall back to memory storage
        
        # Use memory fallback if Supabase is unavailable or there was an error
        logger.info("Using memory storage for AI config")
        global _memory_ai_config
        
        # Update in-memory config
        for key, value in config_data.items():
            if key not in ['updated_at', 'created_at']:
                _memory_ai_config[key] = value
        
        return _memory_ai_config.copy()
    
    @staticmethod
    def get_config():
        """
        Get the current AI configuration
        
        Returns:
            dict: The configuration data or default values if not found
        """
        # Check if Supabase is available
        if is_supabase_available():
            try:
                result = supabase.table("ai_config").select("*").limit(1).execute()
                
                # Return the first config if found
                if result.data and len(result.data) > 0:
                    return result.data[0]
            except Exception as e:
                logger.error(f"Failed to get AI config from database: {e}")
        
        # Return in-memory config or default values if Supabase is unavailable
        # or there was no config in the database
        logger.info("Using memory storage for AI config")
        return _memory_ai_config.copy()
    
    @staticmethod
    def create_ai_agent(agent_data):
        """
        Create a new AI agent in the database
        
        Args:
            agent_data (dict): The agent data including:
                - id: Unique identifier for the agent
                - name: Display name of the agent
                - type: Type of agent (classification, search, recommendation, etc.)
                - description: Description of what the agent does
                - prompt: The system prompt for the agent
                - active: Whether the agent is active
                
        Returns:
            dict: The created agent data
        """
        # Validate required fields
        required_fields = ['id', 'name', 'type', 'prompt']
        for field in required_fields:
            if field not in agent_data:
                logger.error(f"Missing required field '{field}' for AI agent")
                return None
                
        # Add creation timestamp and initialize usage stats
        agent_data['created_at'] = datetime.now().isoformat()
        usage_stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'last_used': None
        }
        agent_data['usage'] = json.dumps(usage_stats)
        
        # Check if Supabase is available
        if is_supabase_available():
            try:
                # Insert into Supabase
                result = supabase.table("ai_agents").insert(agent_data).execute()
                
                # Return the created agent
                if result.data and len(result.data) > 0:
                    created_agent = result.data[0]
                    # Parse usage JSON
                    if 'usage' in created_agent and created_agent['usage']:
                        try:
                            created_agent['usage'] = json.loads(created_agent['usage'])
                        except json.JSONDecodeError:
                            created_agent['usage'] = usage_stats
                    return created_agent
            except Exception as e:
                logger.error(f"Failed to create AI agent in database: {e}")
                # Fall back to memory storage
        
        # Store in memory if Supabase is unavailable
        logger.info(f"Creating agent {agent_data['id']} in memory storage")
        # Convert JSON string back to dict for in-memory storage
        agent_data['usage'] = usage_stats
        _memory_ai_agents[agent_data['id']] = agent_data
        return agent_data.copy()
    
    @staticmethod
    def get_ai_agents():
        """
        Get all AI agents
        
        Returns:
            list: List of AI agents
        """
        # Check if Supabase is available
        if is_supabase_available():
            try:
                result = supabase.table("ai_agents").select("*").execute()
                
                # Parse usage JSON for each agent
                agents = result.data if result.data else []
                for agent in agents:
                    if 'usage' in agent and agent['usage']:
                        try:
                            agent['usage'] = json.loads(agent['usage'])
                        except json.JSONDecodeError:
                            agent['usage'] = {
                                'total_calls': 0,
                                'successful_calls': 0,
                                'failed_calls': 0,
                                'last_used': None
                            }
                
                return agents
            except Exception as e:
                logger.error(f"Failed to get AI agents from database: {e}")
                # Fall back to memory storage
        
        # Return in-memory agents if Supabase is unavailable
        logger.info("Using memory storage for AI agents")
        return [agent for agent in _memory_ai_agents.values()]
    
    @staticmethod
    def get_ai_agent(agent_id):
        """
        Get a specific AI agent by ID
        
        Args:
            agent_id (str): The agent ID
            
        Returns:
            dict: The agent data or None if not found
        """
        # Check if Supabase is available
        if is_supabase_available():
            try:
                result = supabase.table("ai_agents").select("*").eq("id", agent_id).execute()
                
                if result.data and len(result.data) > 0:
                    agent = result.data[0]
                    # Parse usage JSON
                    if 'usage' in agent and agent['usage']:
                        try:
                            agent['usage'] = json.loads(agent['usage'])
                        except json.JSONDecodeError:
                            agent['usage'] = {
                                'total_calls': 0,
                                'successful_calls': 0,
                                'failed_calls': 0,
                                'last_used': None
                            }
                    return agent
            except Exception as e:
                logger.error(f"Failed to get AI agent from database: {e}")
                # Fall back to memory storage
        
        # Check in-memory agents if Supabase is unavailable
        logger.info(f"Looking for agent {agent_id} in memory storage")
        return _memory_ai_agents.get(agent_id)
    
    @staticmethod
    def update_ai_agent(agent_id, update_data):
        """
        Update an AI agent
        
        Args:
            agent_id (str): The agent ID
            update_data (dict): The data to update
            
        Returns:
            dict: The updated agent data
        """
        update_data['updated_at'] = datetime.now().isoformat()
        
        # Check if Supabase is available
        if is_supabase_available():
            try:
                # First check if the agent exists
                agent = AIAgentService.get_ai_agent(agent_id)
                if not agent and is_supabase_available():
                    return None
                    
                # Convert usage to JSON string if present
                usage_dict = None
                if 'usage' in update_data and isinstance(update_data['usage'], dict):
                    usage_dict = update_data['usage'].copy()  # Save a copy for memory storage
                    update_data['usage'] = json.dumps(update_data['usage'])
                
                result = supabase.table("ai_agents").update(update_data).eq("id", agent_id).execute()
                
                # Parse usage JSON in the result
                if result.data and len(result.data) > 0:
                    agent = result.data[0]
                    if 'usage' in agent and agent['usage']:
                        try:
                            agent['usage'] = json.loads(agent['usage'])
                        except json.JSONDecodeError:
                            agent['usage'] = {
                                'total_calls': 0,
                                'successful_calls': 0,
                                'failed_calls': 0,
                                'last_used': None
                            }
                    return agent
            except Exception as e:
                logger.error(f"Failed to update AI agent in database: {e}")
                # Fall back to memory storage
        
        # Update in-memory agent if Supabase is unavailable
        logger.info(f"Updating agent {agent_id} in memory storage")
        if agent_id in _memory_ai_agents:
            agent = _memory_ai_agents[agent_id]
            for key, value in update_data.items():
                if key != 'usage':  # Handle usage separately
                    agent[key] = value
            
            # Handle usage specifically to maintain the dictionary structure
            if 'usage' in update_data:
                if isinstance(update_data['usage'], str):
                    try:
                        agent['usage'] = json.loads(update_data['usage'])
                    except json.JSONDecodeError:
                        pass  # Keep existing usage if can't parse
                else:
                    agent['usage'] = update_data['usage']
            
            return agent
        return None
    
    @staticmethod
    def track_agent_usage(agent_id, successful=True):
        """
        Track usage statistics for an AI agent
        
        Args:
            agent_id (str): The agent ID
            successful (bool): Whether the call was successful
            
        Returns:
            dict: The updated agent data or None if not found
        """
        # Get current agent data
        agent = AIAgentService.get_ai_agent(agent_id)
        if not agent:
            return None
        
        # Update usage statistics
        usage = agent.get('usage', {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'last_used': None
        })
        
        usage['total_calls'] = usage.get('total_calls', 0) + 1
        if successful:
            usage['successful_calls'] = usage.get('successful_calls', 0) + 1
        else:
            usage['failed_calls'] = usage.get('failed_calls', 0) + 1
        
        usage['last_used'] = datetime.now().isoformat()
        
        # Update agent with new usage data
        return AIAgentService.update_ai_agent(agent_id, {'usage': usage})
    
    @staticmethod
    def get_agent_usage_stats():
        """
        Get usage statistics for all AI agents
        
        Returns:
            dict: Aggregated usage statistics
        """
        agents = AIAgentService.get_ai_agents()
        
        stats = {
            'total_processed': 0,
            'total_successful': 0,
            'total_failed': 0,
            'agents': {}
        }
        
        for agent in agents:
            usage = agent.get('usage', {})
            stats['total_processed'] += usage.get('total_calls', 0)
            stats['total_successful'] += usage.get('successful_calls', 0)
            stats['total_failed'] += usage.get('failed_calls', 0)
            
            # Calculate success rate
            total = max(1, usage.get('total_calls', 1))  # Avoid division by zero
            success_rate = round((usage.get('successful_calls', 0) / total) * 100, 1)
            
            stats['agents'][agent['id']] = {
                'name': agent.get('name', agent['id']),
                'type': agent.get('type', 'unknown'),
                'active': agent.get('active', False),
                'total_calls': usage.get('total_calls', 0),
                'successful_calls': usage.get('successful_calls', 0),
                'failed_calls': usage.get('failed_calls', 0),
                'success_rate': success_rate,
                'last_used': usage.get('last_used')
            }
        
        return stats