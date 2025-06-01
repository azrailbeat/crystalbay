"""
Wazzup24.ru Integration for Crystal Bay Travel
Implements full client management integration scheme with contact sync, deal management, and webhooks
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import request, jsonify
from models import LeadService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WazzupIntegration:
    """
    Wazzup24.ru integration for Crystal Bay Travel
    Implements the full client management scheme with:
    - User account synchronization
    - Contact synchronization 
    - Deal management
    - Webhook handling
    - Chat interface integration
    """
    
    def __init__(self):
        """Initialize Wazzup integration with API credentials"""
        self.api_key = os.environ.get('WAZZUP_API_KEY')
        self.api_secret = os.environ.get('WAZZUP_API_SECRET')
        self.base_url = 'https://api.wazzup24.com/v3'
        self.webhook_secret = os.environ.get('WAZZUP_WEBHOOK_SECRET')
        self.crm_base_url = os.environ.get('REPLIT_APP_URL', 'https://your-app.replit.app')
        self.lead_service = LeadService()
        
    def is_configured(self):
        """Check if Wazzup integration is properly configured"""
        return bool(self.api_key and self.api_secret)
    
    def _make_request(self, method: str, endpoint: str, data: dict = None, params: dict = None) -> Optional[dict]:
        """Make authenticated request to Wazzup API"""
        if not self.is_configured():
            logger.error("Wazzup integration not configured - missing API credentials")
            return None
            
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
                
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Wazzup API request failed: {e}")
            return None
    
    # User Synchronization
    def sync_users(self, users: List[Dict]) -> bool:
        """
        Sync CRM users with Wazzup
        Users need to be synchronized so they can access chats in Wazzup interface
        """
        try:
            for user in users:
                user_data = {
                    'externalId': str(user.get('id')),
                    'name': user.get('name'),
                    'email': user.get('email'),
                    'role': user.get('role', 'manager'),
                    'status': 'active'
                }
                
                result = self._make_request('POST', '/users', user_data)
                if result:
                    logger.info(f"User {user.get('name')} synced successfully")
                else:
                    logger.error(f"Failed to sync user {user.get('name')}")
                    
            return True
        except Exception as e:
            logger.error(f"User synchronization failed: {e}")
            return False
    
    # Contact Synchronization
    def sync_contact(self, lead_data: Dict) -> Optional[str]:
        """
        Sync contact from Crystal Bay lead to Wazzup
        Returns Wazzup contact ID if successful
        """
        try:
            contact_data = {
                'externalId': str(lead_data.get('id')),
                'name': lead_data.get('name', ''),
                'phone': lead_data.get('phone', ''),
                'email': lead_data.get('email', ''),
                'avatar': None,
                'customFields': {
                    'source': lead_data.get('source', ''),
                    'interest': lead_data.get('interest', ''),
                    'budget': lead_data.get('budget', ''),
                    'travel_dates': lead_data.get('travel_dates', ''),
                    'lead_status': lead_data.get('status', 'new')
                },
                'crmUrl': f"{self.crm_base_url}/leads?id={lead_data.get('id')}"
            }
            
            result = self._make_request('POST', '/contacts', contact_data)
            if result and result.get('id'):
                logger.info(f"Contact synced successfully: {result.get('id')}")
                return result.get('id')
            else:
                logger.error("Failed to sync contact")
                return None
                
        except Exception as e:
            logger.error(f"Contact synchronization failed: {e}")
            return None
    
    def update_contact(self, wazzup_contact_id: str, lead_data: Dict) -> bool:
        """Update existing contact in Wazzup"""
        try:
            contact_data = {
                'name': lead_data.get('name', ''),
                'phone': lead_data.get('phone', ''),
                'email': lead_data.get('email', ''),
                'customFields': {
                    'source': lead_data.get('source', ''),
                    'interest': lead_data.get('interest', ''),
                    'budget': lead_data.get('budget', ''),
                    'travel_dates': lead_data.get('travel_dates', ''),
                    'lead_status': lead_data.get('status', 'new')
                },
                'crmUrl': f"{self.crm_base_url}/leads?id={lead_data.get('id')}"
            }
            
            result = self._make_request('PATCH', f'/contacts/{wazzup_contact_id}', contact_data)
            if result:
                logger.info(f"Contact updated successfully: {wazzup_contact_id}")
                return True
            else:
                logger.error(f"Failed to update contact: {wazzup_contact_id}")
                return False
                
        except Exception as e:
            logger.error(f"Contact update failed: {e}")
            return False
    
    # Deal Management
    def create_deal(self, lead_data: Dict, contact_id: str, pipeline_id: str = None) -> Optional[str]:
        """
        Create deal in Wazzup for travel booking
        Returns Wazzup deal ID if successful
        """
        try:
            # Determine deal value based on interest/budget
            deal_value = self._calculate_deal_value(lead_data.get('interest', ''), 
                                                   lead_data.get('budget', ''))
            
            deal_data = {
                'externalId': f"lead_{lead_data.get('id')}",
                'name': f"Travel booking - {lead_data.get('name', 'Unknown')}",
                'contactId': contact_id,
                'pipelineId': pipeline_id,
                'stageId': self._get_initial_stage_id(pipeline_id),
                'value': deal_value,
                'currency': 'RUB',
                'customFields': {
                    'destination': lead_data.get('interest', ''),
                    'travel_dates': lead_data.get('travel_dates', ''),
                    'group_size': lead_data.get('group_size', '1'),
                    'special_requests': lead_data.get('message', ''),
                    'lead_source': lead_data.get('source', '')
                },
                'crmUrl': f"{self.crm_base_url}/leads?id={lead_data.get('id')}"
            }
            
            result = self._make_request('POST', '/deals', deal_data)
            if result and result.get('id'):
                logger.info(f"Deal created successfully: {result.get('id')}")
                return result.get('id')
            else:
                logger.error("Failed to create deal")
                return None
                
        except Exception as e:
            logger.error(f"Deal creation failed: {e}")
            return None
    
    def update_deal_stage(self, deal_id: str, stage_id: str) -> bool:
        """Update deal stage in Wazzup when lead status changes"""
        try:
            deal_data = {
                'stageId': stage_id
            }
            
            result = self._make_request('PATCH', f'/deals/{deal_id}', deal_data)
            if result:
                logger.info(f"Deal stage updated: {deal_id} -> {stage_id}")
                return True
            else:
                logger.error(f"Failed to update deal stage: {deal_id}")
                return False
                
        except Exception as e:
            logger.error(f"Deal stage update failed: {e}")
            return False
    
    # Pipeline Management
    def create_travel_pipeline(self) -> Optional[str]:
        """Create travel booking pipeline in Wazzup"""
        try:
            pipeline_data = {
                'name': 'Crystal Bay Travel Bookings',
                'stages': [
                    {'name': 'New Inquiry', 'color': '#3498db'},
                    {'name': 'Contacted', 'color': '#f39c12'},
                    {'name': 'Quote Sent', 'color': '#e67e22'},
                    {'name': 'Negotiation', 'color': '#9b59b6'},
                    {'name': 'Booking Confirmed', 'color': '#27ae60'},
                    {'name': 'Payment Received', 'color': '#2ecc71'},
                    {'name': 'Travel Completed', 'color': '#1abc9c'},
                    {'name': 'Lost', 'color': '#e74c3c'}
                ]
            }
            
            result = self._make_request('POST', '/pipelines', pipeline_data)
            if result and result.get('id'):
                logger.info(f"Travel pipeline created: {result.get('id')}")
                return result.get('id')
            else:
                logger.error("Failed to create travel pipeline")
                return None
                
        except Exception as e:
            logger.error(f"Pipeline creation failed: {e}")
            return None
    
    # Webhook Handling
    def handle_webhook(self, webhook_data: Dict) -> Dict:
        """
        Process webhooks from Wazzup
        Handles new contacts, messages, and channel updates
        """
        try:
            event_type = webhook_data.get('event')
            
            if event_type == 'contact.created':
                return self._handle_new_contact(webhook_data)
            elif event_type == 'message.received':
                return self._handle_new_message(webhook_data)
            elif event_type == 'deal.created':
                return self._handle_new_deal(webhook_data)
            elif event_type == 'channel.status_changed':
                return self._handle_channel_update(webhook_data)
            else:
                logger.info(f"Unhandled webhook event: {event_type}")
                return {'status': 'ignored', 'event': event_type}
                
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _handle_new_contact(self, webhook_data: Dict) -> Dict:
        """Handle new contact creation from Wazzup"""
        try:
            contact_data = webhook_data.get('data', {})
            
            # Create lead in Crystal Bay system
            lead_data = {
                'name': contact_data.get('name', ''),
                'email': contact_data.get('email', ''),
                'phone': contact_data.get('phone', ''),
                'source': 'wazzup_chat',
                'status': 'new',
                'external_id': contact_data.get('id'),
                'external_source': 'wazzup'
            }
            
            lead_id = self.lead_service.create_lead(lead_data)
            if lead_id:
                logger.info(f"Lead created from Wazzup contact: {lead_id}")
                return {'status': 'success', 'lead_id': lead_id}
            else:
                logger.error("Failed to create lead from Wazzup contact")
                return {'status': 'error', 'message': 'Lead creation failed'}
                
        except Exception as e:
            logger.error(f"New contact handling failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _handle_new_message(self, webhook_data: Dict) -> Dict:
        """Handle new message from Wazzup chat"""
        try:
            message_data = webhook_data.get('data', {})
            contact_id = message_data.get('contactId')
            message_text = message_data.get('text', '')
            
            # Find corresponding lead
            lead = self.lead_service.get_lead_by_external_id(contact_id, 'wazzup')
            if lead:
                # Add interaction
                interaction_data = {
                    'type': 'message',
                    'content': message_text,
                    'direction': 'inbound',
                    'source': 'wazzup_chat',
                    'timestamp': datetime.now()
                }
                
                self.lead_service.add_interaction(lead['id'], interaction_data)
                logger.info(f"Message added to lead {lead['id']}")
                return {'status': 'success', 'lead_id': lead['id']}
            else:
                logger.warning(f"No lead found for Wazzup contact: {contact_id}")
                return {'status': 'warning', 'message': 'Lead not found'}
                
        except Exception as e:
            logger.error(f"New message handling failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    # Chat Interface
    def get_chat_iframe_url(self, scope: str = 'global', contact_id: str = None) -> str:
        """
        Generate iframe URL for Wazzup chat interface
        
        Args:
            scope: 'global' for all chats or 'card' for specific contact
            contact_id: Required when scope is 'card'
        """
        base_chat_url = 'https://app.wazzup24.com/iframe'
        
        params = {
            'apiKey': self.api_key,
            'scope': scope
        }
        
        if scope == 'card' and contact_id:
            params['contactId'] = contact_id
            
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_chat_url}?{query_string}"
    
    def get_unread_count(self) -> int:
        """Get count of unread messages for display in UI"""
        try:
            result = self._make_request('GET', '/chats/unread-count')
            if result:
                return result.get('count', 0)
            return 0
        except Exception as e:
            logger.error(f"Failed to get unread count: {e}")
            return 0
    
    # Utility Methods
    def _calculate_deal_value(self, interest: str, budget: str) -> int:
        """Calculate estimated deal value based on travel interest and budget"""
        base_values = {
            'europe': 150000,
            'asia': 200000,
            'america': 300000,
            'africa': 250000,
            'oceania': 350000,
            'domestic': 50000
        }
        
        # Try to match interest to region
        interest_lower = interest.lower()
        for region, value in base_values.items():
            if region in interest_lower:
                return value
        
        # Parse budget if provided
        if budget and any(char.isdigit() for char in budget):
            import re
            numbers = re.findall(r'\d+', budget.replace(',', '').replace(' ', ''))
            if numbers:
                return int(numbers[0]) * 1000  # Assume thousands
        
        return 100000  # Default value
    
    def _get_initial_stage_id(self, pipeline_id: str) -> str:
        """Get the ID of the first stage in pipeline"""
        try:
            result = self._make_request('GET', f'/pipelines/{pipeline_id}/stages')
            if result and result.get('stages'):
                return result['stages'][0]['id']
            return '1'  # Fallback
        except Exception as e:
            logger.error(f"Failed to get initial stage: {e}")
            return '1'
    
    def _handle_new_deal(self, webhook_data: Dict) -> Dict:
        """Handle new deal creation webhook"""
        return {'status': 'success', 'message': 'Deal webhook processed'}
    
    def _handle_channel_update(self, webhook_data: Dict) -> Dict:
        """Handle channel status update webhook"""
        return {'status': 'success', 'message': 'Channel update processed'}

# Global instance
wazzup_integration = None

def get_wazzup_integration():
    """Get the singleton instance of WazzupIntegration"""
    global wazzup_integration
    if wazzup_integration is None:
        wazzup_integration = WazzupIntegration()
    return wazzup_integration