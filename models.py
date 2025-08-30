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

_memory_leads = []  # Real leads from SAMO API only

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
        """Get leads from SAMO API and database"""
        # First try to get from SAMO API
        samo_leads = self._fetch_leads_from_samo()
        
        if not is_supabase_available():
            # Merge SAMO leads with memory leads
            all_leads = samo_leads + _memory_leads
            return all_leads[:limit]
            
        try:
            if supabase:
                response = supabase.table('leads').select('*').order('created_at', desc=True).limit(limit).execute()
                db_leads = response.data if response.data else []
                # Merge SAMO leads with database leads
                all_leads = samo_leads + db_leads
                return all_leads[:limit]
            return samo_leads[:limit]
        except Exception as e:
            logger.error(f"Failed to get leads: {e}")
            return samo_leads[:limit]
    
    def _fetch_leads_from_samo(self):
        """Fetch leads/bookings from SAMO API"""
        try:
            from crystal_bay_samo_api import CrystalBaySamoAPI
            samo_api = CrystalBaySamoAPI()
            
            # Try to get bookings data from SAMO API
            response = samo_api.get_bookings_api()
            
            if response.get('success') and response.get('data'):
                # Parse booking data into lead format
                return self._parse_samo_bookings(response['data'])
                
            # Fallback: try to get general data that might contain bookings
            response = samo_api.search_tours_detailed({})
            if response.get('success') and response.get('data'):
                # Check if there's any booking information in the response
                return self._parse_samo_general_data(response['data'])
                
        except Exception as e:
            logger.error(f"Failed to fetch leads from SAMO: {e}")
            
        return []
    
    def _parse_samo_bookings(self, samo_data):
        """Parse SAMO booking data into lead format"""
        leads = []
        
        try:
            # Check if we have booking data in the response
            if isinstance(samo_data, dict):
                # Look for booking-related keys in the response
                booking_keys = ['bookings', 'claims', 'orders', 'reservations']
                
                for key in booking_keys:
                    if key in samo_data and isinstance(samo_data[key], list):
                        for booking in samo_data[key]:
                            lead = self._convert_booking_to_lead(booking)
                            if lead:
                                leads.append(lead)
                                
        except Exception as e:
            logger.error(f"Failed to parse SAMO bookings: {e}")
            
        return leads
    
    def _parse_samo_general_data(self, samo_data):
        """Parse general SAMO data for any lead information"""
        leads = []
        
        try:
            # For SearchTour_ALL response, there might be booking history or client data
            if isinstance(samo_data, dict) and 'SearchTour_ALL' in samo_data:
                # This endpoint mainly contains configuration data
                # No client booking data expected here
                pass
                
        except Exception as e:
            logger.error(f"Failed to parse SAMO general data: {e}")
            
        return leads
    
    def _convert_booking_to_lead(self, booking):
        """Convert SAMO booking to lead format"""
        try:
            lead = {
                'id': booking.get('id', f"samo_{hash(str(booking))}"),
                'name': booking.get('client_name', booking.get('name', 'Клиент SAMO')),
                'phone': booking.get('phone', booking.get('contact_phone', '')),
                'email': booking.get('email', booking.get('contact_email', '')),
                'destination': booking.get('destination', booking.get('tour_name', '')),
                'departure_city': booking.get('departure_city', ''),
                'budget': booking.get('total_cost', booking.get('price', 'По запросу')),
                'adults': booking.get('adults', 2),
                'children': booking.get('children', 0),
                'duration': booking.get('duration', booking.get('nights', '')),
                'departure_date': booking.get('departure_date', booking.get('check_in', '')),
                'status': self._map_samo_status(booking.get('status', 'active')),
                'source': 'SAMO API',
                'notes': booking.get('notes', booking.get('comments', '')),
                'created_at': booking.get('created_at', datetime.now().isoformat()),
                'updated_at': booking.get('updated_at', datetime.now().isoformat())
            }
            return lead
        except Exception as e:
            logger.error(f"Failed to convert booking to lead: {e}")
            return None
    
    def _map_samo_status(self, samo_status):
        """Map SAMO booking status to CRM status"""
        status_mapping = {
            'new': 'новое',
            'confirmed': 'в работе', 
            'paid': 'обработано',
            'completed': 'закрыто',
            'cancelled': 'отменено',
            'active': 'в работе'
        }
        return status_mapping.get(samo_status.lower(), 'новое')
    
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