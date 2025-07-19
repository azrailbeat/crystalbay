import os
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class BitrixIntegration:
    """Bitrix24 CRM integration for Crystal Bay Travel"""
    
    def __init__(self):
        self.webhook_url = os.environ.get('BITRIX_WEBHOOK_URL')
        self.access_token = os.environ.get('BITRIX_ACCESS_TOKEN')
        self.domain = os.environ.get('BITRIX_DOMAIN')
        
        if not any([self.webhook_url, self.access_token]):
            logger.warning("Bitrix credentials not configured - using demo mode")
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make API request to Bitrix24"""
        try:
            if self.webhook_url:
                # Webhook URL format
                url = f"{self.webhook_url}/{endpoint}"
                headers = {'Content-Type': 'application/json'}
            else:
                # OAuth format
                url = f"https://{self.domain}/rest/{endpoint}"
                headers = {
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                }
            
            if method.upper() == 'GET':
                response = requests.get(url, params=data, headers=headers, timeout=30)
            else:
                response = requests.post(url, json=data, headers=headers, timeout=30)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Bitrix API request failed: {e}")
            return {"error": str(e)}
    
    def create_lead(self, lead_data: Dict) -> Dict:
        """Create a new lead in Bitrix24"""
        bitrix_data = {
            "fields": {
                "TITLE": lead_data.get('title', 'Новый лид из Crystal Bay'),
                "NAME": lead_data.get('first_name', ''),
                "LAST_NAME": lead_data.get('last_name', ''),
                "PHONE": [{"VALUE": lead_data.get('phone', ''), "VALUE_TYPE": "WORK"}] if lead_data.get('phone') else [],
                "EMAIL": [{"VALUE": lead_data.get('email', ''), "VALUE_TYPE": "WORK"}] if lead_data.get('email') else [],
                "COMMENTS": lead_data.get('description', ''),
                "SOURCE_ID": "WEB",
                "STATUS_ID": "NEW",
                "ASSIGNED_BY_ID": 1,
                "UF_CRM_TRAVEL_DESTINATION": lead_data.get('destination', ''),
                "UF_CRM_TRAVEL_DATES": lead_data.get('travel_dates', ''),
                "UF_CRM_BUDGET": lead_data.get('budget', ''),
                "UF_CRM_PASSENGERS": lead_data.get('passengers', ''),
            }
        }
        
        result = self._make_request('POST', 'crm.lead.add', bitrix_data)
        
        if 'result' in result:
            logger.info(f"Lead created in Bitrix: {result['result']}")
            return {"status": "success", "lead_id": result['result']}
        else:
            logger.error(f"Failed to create lead: {result}")
            return {"status": "error", "error": result.get('error', 'Unknown error')}
    
    def update_lead(self, lead_id: str, updates: Dict) -> Dict:
        """Update existing lead in Bitrix24"""
        bitrix_data = {
            "id": lead_id,
            "fields": updates
        }
        
        result = self._make_request('POST', 'crm.lead.update', bitrix_data)
        
        if result.get('result'):
            return {"status": "success"}
        else:
            return {"status": "error", "error": result.get('error', 'Update failed')}
    
    def create_deal(self, deal_data: Dict) -> Dict:
        """Create a new deal in Bitrix24"""
        bitrix_data = {
            "fields": {
                "TITLE": deal_data.get('title', 'Бронирование тура'),
                "TYPE_ID": "SALE",
                "STAGE_ID": "NEW",
                "ASSIGNED_BY_ID": 1,
                "CONTACT_ID": deal_data.get('contact_id'),
                "COMPANY_ID": deal_data.get('company_id'),
                "OPPORTUNITY": deal_data.get('amount', 0),
                "CURRENCY_ID": "RUB",
                "COMMENTS": deal_data.get('description', ''),
                "UF_CRM_TOUR_PACKAGE": deal_data.get('tour_package', ''),
                "UF_CRM_DEPARTURE_DATE": deal_data.get('departure_date', ''),
                "UF_CRM_RETURN_DATE": deal_data.get('return_date', ''),
                "UF_CRM_DESTINATION": deal_data.get('destination', ''),
                "UF_CRM_PASSENGERS_COUNT": deal_data.get('passengers', 1),
            }
        }
        
        result = self._make_request('POST', 'crm.deal.add', bitrix_data)
        
        if 'result' in result:
            logger.info(f"Deal created in Bitrix: {result['result']}")
            return {"status": "success", "deal_id": result['result']}
        else:
            logger.error(f"Failed to create deal: {result}")
            return {"status": "error", "error": result.get('error', 'Unknown error')}
    
    def create_contact(self, contact_data: Dict) -> Dict:
        """Create a new contact in Bitrix24"""
        bitrix_data = {
            "fields": {
                "NAME": contact_data.get('first_name', ''),
                "LAST_NAME": contact_data.get('last_name', ''),
                "PHONE": [{"VALUE": contact_data.get('phone', ''), "VALUE_TYPE": "WORK"}] if contact_data.get('phone') else [],
                "EMAIL": [{"VALUE": contact_data.get('email', ''), "VALUE_TYPE": "WORK"}] if contact_data.get('email') else [],
                "COMMENTS": contact_data.get('notes', ''),
                "ASSIGNED_BY_ID": 1,
                "SOURCE_ID": "WEB",
                "UF_CRM_MESSENGER_ID": contact_data.get('messenger_id', ''),
                "UF_CRM_PREFERRED_COMMUNICATION": contact_data.get('preferred_communication', 'PHONE'),
            }
        }
        
        result = self._make_request('POST', 'crm.contact.add', bitrix_data)
        
        if 'result' in result:
            logger.info(f"Contact created in Bitrix: {result['result']}")
            return {"status": "success", "contact_id": result['result']}
        else:
            logger.error(f"Failed to create contact: {result}")
            return {"status": "error", "error": result.get('error', 'Unknown error')}
    
    def search_contact(self, phone: str = None, email: str = None) -> Dict:
        """Search for existing contact by phone or email"""
        filter_data = {}
        
        if phone:
            filter_data["PHONE"] = phone
        if email:
            filter_data["EMAIL"] = email
        
        if not filter_data:
            return {"status": "error", "error": "Phone or email required"}
        
        search_data = {
            "filter": filter_data,
            "select": ["ID", "NAME", "LAST_NAME", "PHONE", "EMAIL"]
        }
        
        result = self._make_request('GET', 'crm.contact.list', search_data)
        
        if 'result' in result and result['result']:
            return {"status": "success", "contacts": result['result']}
        else:
            return {"status": "success", "contacts": []}
    
    def add_activity(self, entity_type: str, entity_id: str, activity_data: Dict) -> Dict:
        """Add activity (call, meeting, email, etc.) to CRM entity"""
        bitrix_data = {
            "fields": {
                "OWNER_TYPE_ID": 1 if entity_type == "lead" else 2,  # 1=lead, 2=deal, 3=contact
                "OWNER_ID": entity_id,
                "TYPE_ID": activity_data.get('type_id', 2),  # 1=call, 2=meeting, 4=email
                "SUBJECT": activity_data.get('subject', 'Активность из Crystal Bay'),
                "DESCRIPTION": activity_data.get('description', ''),
                "RESPONSIBLE_ID": 1,
                "START_TIME": activity_data.get('start_time', datetime.now().isoformat()),
                "END_TIME": activity_data.get('end_time', datetime.now().isoformat()),
                "COMPLETED": activity_data.get('completed', 'Y'),
                "DIRECTION": activity_data.get('direction', 1),  # 1=outgoing, 2=incoming
            }
        }
        
        result = self._make_request('POST', 'crm.activity.add', bitrix_data)
        
        if 'result' in result:
            return {"status": "success", "activity_id": result['result']}
        else:
            return {"status": "error", "error": result.get('error', 'Activity creation failed')}
    
    def get_pipelines(self) -> Dict:
        """Get available sales pipelines"""
        result = self._make_request('GET', 'crm.dealcategory.list', {})
        
        if 'result' in result:
            return {"status": "success", "pipelines": result['result']}
        else:
            return {"status": "error", "error": "Failed to get pipelines"}
    
    def setup_travel_pipeline(self) -> Dict:
        """Create a custom pipeline for travel bookings"""
        pipeline_data = {
            "fields": {
                "NAME": "Туристические бронирования",
                "SORT": 100,
                "IS_LOCKED": "N"
            }
        }
        
        result = self._make_request('POST', 'crm.dealcategory.add', pipeline_data)
        
        if 'result' in result:
            category_id = result['result']
            
            # Create custom stages matching Trello workflow
            stages = [
                {"NAME": "Новый запрос", "SORT": 10, "COLOR": "#39A0ED"},
                {"NAME": "Консультация", "SORT": 20, "COLOR": "#FFA900"},
                {"NAME": "Подбор тура", "SORT": 30, "COLOR": "#7C68FC"},
                {"NAME": "Коммерческое предложение", "SORT": 40, "COLOR": "#55D0E0"},
                {"NAME": "Добавление интеграций", "SORT": 50, "COLOR": "#FF6B00"},
                {"NAME": "Оплатили", "SORT": 60, "COLOR": "#9ACB34"},
                {"NAME": "Принято заказчиком", "SORT": 70, "COLOR": "#339DC7"},
                {"NAME": "Подтверждено", "SORT": 80, "COLOR": "#59DB7A"},
                {"NAME": "Завершено", "SORT": 90, "COLOR": "#27AE60"}
            ]
            
            for stage in stages:
                stage_data = {
                    "fields": {
                        "NAME": stage["NAME"],
                        "CATEGORY_ID": category_id,
                        "SORT": stage["SORT"],
                        "COLOR": stage["COLOR"]
                    }
                }
                self._make_request('POST', 'crm.dealcategory.stage.add', stage_data)
            
            return {"status": "success", "pipeline_id": category_id}
        else:
            return {"status": "error", "error": "Failed to create pipeline"}
    
    def is_configured(self) -> bool:
        """Check if Bitrix integration is properly configured"""
        return bool(self.webhook_url or (self.access_token and self.domain))
    
    def test_connection(self) -> Dict:
        """Test connection to Bitrix24"""
        if not self.is_configured():
            return {"status": "error", "error": "Bitrix credentials not configured"}
        
        result = self._make_request('GET', 'crm.lead.list', {"filter": {}, "select": ["ID"], "start": 0})
        
        if 'result' in result:
            return {"status": "success", "message": "Connection successful"}
        else:
            return {"status": "error", "error": result.get('error', 'Connection failed')}

# Global instance
bitrix = BitrixIntegration()