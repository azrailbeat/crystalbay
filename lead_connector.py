"""
Lead Connector System for Crystal Bay Travel
Handles importing leads from multiple sources: email, widgets, and external APIs
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests
from flask import request, jsonify
from models import LeadService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LeadConnector:
    """Main connector class for handling lead imports from various sources"""
    
    def __init__(self):
        self.email_processor = EmailLeadProcessor()
        self.widget_processor = WidgetLeadProcessor() 
        self.api_processor = APILeadProcessor()
        
    def process_email_lead(self, email_data: Dict) -> Dict:
        """Process lead from email source"""
        return self.email_processor.process(email_data)
    
    def process_widget_lead(self, widget_data: Dict) -> Dict:
        """Process lead from website widget"""
        return self.widget_processor.process(widget_data)
    
    def process_api_lead(self, api_data: Dict, source: str = "external_api") -> Dict:
        """Process lead from external API"""
        return self.api_processor.process(api_data, source)

class EmailLeadProcessor:
    """Processes leads from email sources"""
    
    def __init__(self):
        self.sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
        
    def process(self, email_data: Dict) -> Dict:
        """
        Process email lead data
        Expected format:
        {
            "from": "customer@example.com",
            "subject": "Travel inquiry",
            "body": "I'm interested in...",
            "received_at": "2025-01-01T12:00:00Z"
        }
        """
        try:
            # Extract customer information from email
            customer_email = email_data.get('from', '')
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            received_at = email_data.get('received_at', datetime.now().isoformat())
            
            # Extract name from email (basic parsing)
            customer_name = self._extract_name_from_email(customer_email, body)
            
            # Extract phone if mentioned in email body
            customer_phone = self._extract_phone_from_text(body)
            
            # Categorize inquiry type
            interest = self._categorize_inquiry(subject, body)
            
            # Create lead data
            lead_data = {
                'customer_name': customer_name,
                'customer_email': customer_email,
                'customer_phone': customer_phone,
                'source': 'email',
                'interest': interest,
                'status': 'new',
                'details': f"Subject: {subject}\n\nMessage: {body}",
                'created_at': received_at,
                'tags': self._extract_tags(subject, body)
            }
            
            # Save lead to database
            created_lead = LeadService.create_lead(lead_data)
            
            if created_lead:
                logger.info(f"Created lead from email: {created_lead['id']}")
                
                # Send acknowledgment email if SendGrid is configured
                if self.sendgrid_api_key:
                    self._send_acknowledgment_email(customer_email, customer_name)
                
                return {
                    'success': True,
                    'lead_id': created_lead['id'],
                    'message': 'Lead created from email successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to create lead from email'
                }
                
        except Exception as e:
            logger.error(f"Error processing email lead: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_name_from_email(self, email: str, body: str) -> str:
        """Extract customer name from email address or body"""
        # Try to extract from email signature or body first
        lines = body.split('\n')
        for line in lines:
            if any(greeting in line.lower() for greeting in ['меня зовут', 'my name is', 'я ', 'i am']):
                # Basic name extraction logic
                words = line.split()
                if len(words) >= 3:
                    return ' '.join(words[2:4])  # Take next 1-2 words after greeting
        
        # Fallback: use email prefix
        if '@' in email:
            prefix = email.split('@')[0]
            # Remove dots and numbers, capitalize
            name = prefix.replace('.', ' ').replace('_', ' ')
            return ' '.join(word.capitalize() for word in name.split() if not word.isdigit())
        
        return 'Клиент'
    
    def _extract_phone_from_text(self, text: str) -> Optional[str]:
        """Extract phone number from text"""
        import re
        # Russian phone patterns
        phone_patterns = [
            r'\+7[\s\-\(\)]?[\d\s\-\(\)]{10}',  # +7 xxx xxx xxxx
            r'8[\s\-\(\)]?[\d\s\-\(\)]{10}',    # 8 xxx xxx xxxx
            r'\+7[\d]{10}',                      # +7xxxxxxxxxx
            r'8[\d]{10}'                         # 8xxxxxxxxxx
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                phone = match.group()
                # Clean up the phone number
                phone = re.sub(r'[\s\-\(\)]', '', phone)
                return phone
        
        return None
    
    def _categorize_inquiry(self, subject: str, body: str) -> str:
        """Categorize the type of travel inquiry"""
        text = f"{subject} {body}".lower()
        
        if any(word in text for word in ['пляж', 'море', 'beach', 'resort', 'отдых']):
            return 'Beach vacation'
        elif any(word in text for word in ['экскурсия', 'tour', 'музей', 'достопримечательности']):
            return 'Sightseeing tour'
        elif any(word in text for word in ['бизнес', 'business', 'конференция', 'работа']):
            return 'Business travel'
        elif any(word in text for word in ['свадьба', 'медовый', 'honeymoon', 'wedding']):
            return 'Honeymoon'
        elif any(word in text for word in ['семья', 'дети', 'family', 'kids']):
            return 'Family vacation'
        else:
            return 'General inquiry'
    
    def _extract_tags(self, subject: str, body: str) -> List[str]:
        """Extract relevant tags from email content"""
        text = f"{subject} {body}".lower()
        tags = []
        
        # Destination tags
        destinations = ['турция', 'египет', 'греция', 'италия', 'испания', 'таиланд', 'мальдивы']
        for dest in destinations:
            if dest in text:
                tags.append(dest.capitalize())
        
        # Activity tags
        activities = ['дайвинг', 'горные лыжи', 'spa', 'гольф', 'яхта']
        for activity in activities:
            if activity in text:
                tags.append(activity.capitalize())
        
        # Urgency tags
        if any(word in text for word in ['срочно', 'urgent', 'asap', 'скоро']):
            tags.append('Срочно')
        
        return tags
    
    def _send_acknowledgment_email(self, customer_email: str, customer_name: str):
        """Send acknowledgment email using SendGrid"""
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail
            
            sg = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)
            
            message = Mail(
                from_email='noreply@crystalbaytours.com',
                to_emails=customer_email,
                subject='Спасибо за ваш запрос - Crystal Bay Travel',
                html_content=f"""
                <html>
                <body>
                    <h2>Уважаемый(ая) {customer_name}!</h2>
                    <p>Спасибо за ваш запрос. Мы получили ваше сообщение и обработаем его в течение 24 часов.</p>
                    <p>Наш менеджер свяжется с вами в ближайшее время для уточнения деталей.</p>
                    <br>
                    <p>С уважением,<br>Команда Crystal Bay Travel</p>
                </body>
                </html>
                """
            )
            
            response = sg.send(message)
            logger.info(f"Acknowledgment email sent to {customer_email}")
            
        except Exception as e:
            logger.warning(f"Failed to send acknowledgment email: {e}")

class WidgetLeadProcessor:
    """Processes leads from website widgets"""
    
    def process(self, widget_data: Dict) -> Dict:
        """
        Process widget lead data
        Expected format:
        {
            "name": "John Doe",
            "email": "john@example.com", 
            "phone": "+1234567890",
            "message": "I'm interested in...",
            "widget_id": "contact_form_1",
            "page_url": "https://example.com/tours",
            "utm_source": "google",
            "utm_campaign": "summer_tours"
        }
        """
        try:
            # Extract and validate data
            customer_name = widget_data.get('name', '').strip()
            customer_email = widget_data.get('email', '').strip()
            customer_phone = widget_data.get('phone', '').strip()
            message = widget_data.get('message', '').strip()
            widget_id = widget_data.get('widget_id', 'unknown_widget')
            page_url = widget_data.get('page_url', '')
            
            # UTM parameters for tracking
            utm_source = widget_data.get('utm_source', '')
            utm_campaign = widget_data.get('utm_campaign', '')
            utm_medium = widget_data.get('utm_medium', '')
            
            # Validation
            if not customer_email or not customer_name:
                return {
                    'success': False,
                    'error': 'Name and email are required fields'
                }
            
            # Determine interest based on page URL and message
            interest = self._determine_interest_from_context(page_url, message)
            
            # Create lead data
            lead_data = {
                'customer_name': customer_name,
                'customer_email': customer_email,
                'customer_phone': customer_phone,
                'source': f'website_widget_{widget_id}',
                'interest': interest,
                'status': 'new',
                'details': f"Сообщение с сайта: {message}\n\nСтраница: {page_url}",
                'created_at': datetime.now().isoformat(),
                'tags': self._generate_widget_tags(page_url, utm_source, utm_campaign),
                'utm_data': {
                    'source': utm_source,
                    'campaign': utm_campaign,
                    'medium': utm_medium
                }
            }
            
            # Save lead to database
            created_lead = LeadService.create_lead(lead_data)
            
            if created_lead:
                logger.info(f"Created lead from widget {widget_id}: {created_lead['id']}")
                return {
                    'success': True,
                    'lead_id': created_lead['id'],
                    'message': 'Lead created from widget successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to create lead from widget'
                }
                
        except Exception as e:
            logger.error(f"Error processing widget lead: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _determine_interest_from_context(self, page_url: str, message: str) -> str:
        """Determine customer interest based on page context"""
        url_lower = page_url.lower()
        message_lower = message.lower()
        
        if 'beach' in url_lower or 'пляж' in url_lower:
            return 'Beach vacation'
        elif 'tour' in url_lower or 'экскурсии' in url_lower:
            return 'Sightseeing tour'
        elif 'business' in url_lower or 'бизнес' in url_lower:
            return 'Business travel'
        elif 'family' in url_lower or 'семейный' in url_lower:
            return 'Family vacation'
        elif any(word in message_lower for word in ['свадьба', 'honeymoon', 'медовый']):
            return 'Honeymoon'
        else:
            return 'General inquiry'
    
    def _generate_widget_tags(self, page_url: str, utm_source: str, utm_campaign: str) -> List[str]:
        """Generate tags based on widget context"""
        tags = ['Website']
        
        if utm_source:
            tags.append(f'UTM: {utm_source}')
        
        if utm_campaign:
            tags.append(f'Campaign: {utm_campaign}')
        
        # Add page-specific tags
        if 'tours' in page_url.lower():
            tags.append('Tours Page')
        elif 'contact' in page_url.lower():
            tags.append('Contact Page')
        elif 'booking' in page_url.lower():
            tags.append('Booking Page')
        
        return tags

class APILeadProcessor:
    """Processes leads from external APIs"""
    
    def process(self, api_data: Dict, source: str = "external_api") -> Dict:
        """
        Process API lead data
        Expected format (flexible):
        {
            "customer": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890"
            },
            "inquiry": {
                "type": "vacation",
                "message": "Looking for beach vacation",
                "destination": "Maldives",
                "budget": 5000,
                "travel_date": "2025-07-15"
            },
            "source_info": {
                "api_key": "partner_123",
                "partner_name": "TravelPartner LLC",
                "reference_id": "REF_001"
            }
        }
        """
        try:
            # Extract customer info (flexible structure)
            customer = api_data.get('customer', {})
            if not customer and 'name' in api_data:
                # Flat structure fallback
                customer = {
                    'name': api_data.get('name'),
                    'email': api_data.get('email'), 
                    'phone': api_data.get('phone')
                }
            
            customer_name = customer.get('name', '').strip()
            customer_email = customer.get('email', '').strip()
            customer_phone = customer.get('phone', '').strip()
            
            # Extract inquiry info
            inquiry = api_data.get('inquiry', {})
            if not inquiry and 'message' in api_data:
                # Flat structure fallback
                inquiry = {
                    'type': api_data.get('type', 'general'),
                    'message': api_data.get('message'),
                    'destination': api_data.get('destination'),
                    'budget': api_data.get('budget'),
                    'travel_date': api_data.get('travel_date')
                }
            
            inquiry_type = inquiry.get('type', 'General inquiry')
            message = inquiry.get('message', '')
            destination = inquiry.get('destination', '')
            budget = inquiry.get('budget')
            travel_date = inquiry.get('travel_date')
            
            # Extract source info
            source_info = api_data.get('source_info', {})
            partner_name = source_info.get('partner_name', source)
            reference_id = source_info.get('reference_id', '')
            
            # Validation
            if not customer_email or not customer_name:
                return {
                    'success': False,
                    'error': 'Customer name and email are required'
                }
            
            # Build detailed description
            details_parts = []
            if message:
                details_parts.append(f"Сообщение: {message}")
            if destination:
                details_parts.append(f"Направление: {destination}")
            if budget:
                details_parts.append(f"Бюджет: ${budget}")
            if travel_date:
                details_parts.append(f"Дата поездки: {travel_date}")
            if reference_id:
                details_parts.append(f"ID партнера: {reference_id}")
            
            details = "\n\n".join(details_parts)
            
            # Create lead data
            lead_data = {
                'customer_name': customer_name,
                'customer_email': customer_email,
                'customer_phone': customer_phone,
                'source': f'api_{partner_name}',
                'interest': inquiry_type,
                'status': 'new',
                'details': details,
                'created_at': datetime.now().isoformat(),
                'tags': self._generate_api_tags(destination, budget, partner_name),
                'external_ref': reference_id
            }
            
            # Save lead to database
            created_lead = LeadService.create_lead(lead_data)
            
            if created_lead:
                logger.info(f"Created lead from API {partner_name}: {created_lead['id']}")
                return {
                    'success': True,
                    'lead_id': created_lead['id'],
                    'message': 'Lead created from API successfully',
                    'partner_reference': reference_id
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to create lead from API'
                }
                
        except Exception as e:
            logger.error(f"Error processing API lead: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_api_tags(self, destination: str, budget: Any, partner_name: str) -> List[str]:
        """Generate tags for API leads"""
        tags = ['API Import', f'Partner: {partner_name}']
        
        if destination:
            tags.append(f'Destination: {destination}')
        
        if budget:
            try:
                budget_num = float(budget)
                if budget_num < 1000:
                    tags.append('Budget: Low')
                elif budget_num < 5000:
                    tags.append('Budget: Medium')
                else:
                    tags.append('Budget: High')
            except (ValueError, TypeError):
                pass
        
        return tags

# Global connector instance
lead_connector = LeadConnector()