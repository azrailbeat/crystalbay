"""
Database models for Crystal Bay Travel - Production Version
Clean version without development dependencies and type errors
"""
import os
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
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

# In-memory fallback data stores
_memory_samo_settings = {
    'api_url': 'https://booking.crystalbay.com/export/default.php',
    'oauth_token': os.environ.get('SAMO_OAUTH_TOKEN', '27bd59a7ac67422189789f0188167379'),
    'timeout': 30,
    'user_agent': 'Crystal Bay Travel Integration/1.0'
}

_memory_ai_config = {
    'model': 'gpt-4o',
    'temperature': 0.2,
    'active': True
}

_memory_leads = []  # Production starts with empty leads

supabase = None
try:
    if supabase_url and supabase_key:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized successfully")
    else:
        logger.warning("SUPABASE_URL or SUPABASE_KEY not set. Using memory storage.")
except ImportError:
    logger.error("Could not import supabase module. Using memory storage.")
except Exception as e:
    logger.error(f"Failed to initialize Supabase: {e}")

def is_supabase_available():
    """Check if Supabase is available"""
    return supabase is not None

class SettingsService:
    """Service for application settings"""
    
    @staticmethod
    def get_samo_settings():
        """Get SAMO API settings"""
        if not is_supabase_available():
            return _memory_samo_settings
            
        try:
            if supabase:
                response = supabase.table('settings').select('*').eq('key', 'samo_api').execute()
                if response.data:
                    settings_data = response.data[0]
                    return json.loads(settings_data.get('value', '{}'))
            return _memory_samo_settings
        except Exception as e:
            logger.error(f"Failed to get SAMO settings: {e}")
            return _memory_samo_settings
    
    @staticmethod
    def update_samo_settings(settings):
        """Update SAMO API settings"""
        if not is_supabase_available():
            _memory_samo_settings.update(settings)
            return True
            
        try:
            if supabase:
                settings_json = json.dumps(settings)
                data = {
                    'key': 'samo_api',
                    'value': settings_json,
                    'updated_at': datetime.now().isoformat()
                }
                
                # Try to update existing record
                response = supabase.table('settings').select('id').eq('key', 'samo_api').execute()
                if response.data:
                    supabase.table('settings').update(data).eq('key', 'samo_api').execute()
                else:
                    supabase.table('settings').insert(data).execute()
                    
                return True
        except Exception as e:
            logger.error(f"Failed to update SAMO settings: {e}")
            _memory_samo_settings.update(settings)
            return False

class LeadService:
    """Service for lead management"""
    
    def get_leads(self, limit=50):
        """Get leads from database or memory"""
        if not is_supabase_available():
            return _memory_leads[:limit]
            
        try:
            if supabase:
                response = supabase.table('leads').select('*').order('created_at', desc=True).limit(limit).execute()
                return response.data if response.data else []
            return _memory_leads[:limit]
        except Exception as e:
            logger.error(f"Failed to get leads: {e}")
            return _memory_leads[:limit]
    
    def create_lead(self, lead_data):
        """Create new lead"""
        lead_data['created_at'] = datetime.now().isoformat()
        lead_data['updated_at'] = datetime.now().isoformat()
        
        if not is_supabase_available():
            lead_data['id'] = f"lead_{len(_memory_leads) + 1}"
            _memory_leads.append(lead_data)
            return lead_data['id']
            
        try:
            if supabase:
                response = supabase.table('leads').insert(lead_data).execute()
                if response.data:
                    return response.data[0]['id']
            return None
        except Exception as e:
            logger.error(f"Failed to create lead: {e}")
            # Fallback to memory
            lead_data['id'] = f"lead_{len(_memory_leads) + 1}"
            _memory_leads.append(lead_data)
            return lead_data['id']
    
    def update_lead(self, lead_id, updates):
        """Update lead"""
        updates['updated_at'] = datetime.now().isoformat()
        
        if not is_supabase_available():
            for lead in _memory_leads:
                if lead.get('id') == lead_id:
                    lead.update(updates)
                    return True
            return False
            
        try:
            if supabase:
                response = supabase.table('leads').update(updates).eq('id', lead_id).execute()
                return bool(response.data)
            return False
        except Exception as e:
            logger.error(f"Failed to update lead: {e}")
            return False

class AIService:
    """Service for AI configuration"""
    
    def get_ai_config(self):
        """Get AI configuration"""
        if not is_supabase_available():
            return _memory_ai_config
            
        try:
            if supabase:
                response = supabase.table('settings').select('*').eq('key', 'ai_config').execute()
                if response.data:
                    config_data = response.data[0]
                    return json.loads(config_data.get('value', '{}'))
            return _memory_ai_config
        except Exception as e:
            logger.error(f"Failed to get AI config: {e}")
            return _memory_ai_config
    
    def update_ai_config(self, config):
        """Update AI configuration"""
        if not is_supabase_available():
            _memory_ai_config.update(config)
            return True
            
        try:
            if supabase:
                config_json = json.dumps(config)
                data = {
                    'key': 'ai_config',
                    'value': config_json,
                    'updated_at': datetime.now().isoformat()
                }
                
                response = supabase.table('settings').select('id').eq('key', 'ai_config').execute()
                if response.data:
                    supabase.table('settings').update(data).eq('key', 'ai_config').execute()
                else:
                    supabase.table('settings').insert(data).execute()
                    
                return True
        except Exception as e:
            logger.error(f"Failed to update AI config: {e}")
            _memory_ai_config.update(config)
            return False

# Export services for easy import
__all__ = ['SettingsService', 'LeadService', 'AIService', 'is_supabase_available']