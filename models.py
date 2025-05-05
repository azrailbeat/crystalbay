"""
Database models for the Crystal Bay Travel application.
These models define the structure of the data in Supabase.
"""
import os
import json
from datetime import datetime
from supabase import create_client, Client
from typing import List, Dict, Any, Optional

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

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
    
    @staticmethod
    def get_config():
        """
        Get the current AI configuration
        
        Returns:
            dict: The configuration data or default values if not found
        """
        result = supabase.table("ai_config").select("*").limit(1).execute()
        
        # Return the first config or default values
        if result.data and len(result.data) > 0:
            return result.data[0]
        else:
            return {
                'model': 'gpt-4o',
                'temperature': 0.2,
                'active': True
            }
    
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
        # Add creation timestamp and initialize usage stats
        agent_data['created_at'] = datetime.now().isoformat()
        agent_data['usage'] = json.dumps({
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'last_used': None
        })
        
        # Insert into Supabase
        result = supabase.table("ai_agents").insert(agent_data).execute()
        
        # Return the created agent
        return result.data[0] if result.data else None
    
    @staticmethod
    def get_ai_agents():
        """
        Get all AI agents
        
        Returns:
            list: List of AI agents
        """
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
    
    @staticmethod
    def get_ai_agent(agent_id):
        """
        Get a specific AI agent by ID
        
        Args:
            agent_id (str): The agent ID
            
        Returns:
            dict: The agent data or None if not found
        """
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
        else:
            return None
    
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
        
        # Convert usage to JSON string if present
        if 'usage' in update_data and isinstance(update_data['usage'], dict):
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
        else:
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