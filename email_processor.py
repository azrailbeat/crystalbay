import os
import json
import logging
import re
from datetime import datetime
from email.parser import Parser
from email.policy import default

from models import LeadService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('email_processor')

class EmailProcessor:
    """Process emails and create leads from them"""
    
    def __init__(self):
        """Initialize the email processor"""
        logger.info("Initializing email processor")
    
    def process_email(self, email_content):
        """Process a raw email and extract lead data
        
        Args:
            email_content (str): Raw email content
            
        Returns:
            dict: Extracted lead data
        """
        try:
            # Parse email
            parser = Parser(policy=default)
            email_message = parser.parsestr(email_content)
            
            # Extract basic information
            subject = email_message.get('subject', '')
            from_header = email_message.get('from', '')
            sent_date = email_message.get('date', '')
            
            # Extract email address and name from the From header
            sender_email = self._extract_email(from_header)
            sender_name = self._extract_name(from_header)
            
            # Get message body
            body = self._get_email_body(email_message)
            
            # Determine lead interest based on subject and body
            interest = self._determine_interest(subject, body)
            
            # Create lead data
            lead_data = {
                'customer_name': sender_name,
                'customer_email': sender_email,
                'customer_phone': self._extract_phone(body),  # Try to extract phone from body
                'source': 'email',
                'interest': interest,
                'status': 'new',
                'notes': f"Email subject: {subject}\n\nEmail body: {body}\n\nReceived on: {sent_date}",
                'received_date': datetime.now().isoformat()
            }
            
            # Store lead in database
            try:
                lead = LeadService.create_lead(lead_data)
                logger.info(f"Created lead from email: {lead['id']}")
                return lead
            except Exception as e:
                logger.error(f"Error creating lead: {e}")
                return None
            
        except Exception as e:
            logger.error(f"Error processing email: {e}")
            return None
    
    def _extract_email(self, from_header):
        """Extract email address from From header
        
        Args:
            from_header (str): From header string
            
        Returns:
            str: Email address
        """
        email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', from_header)
        if email_match:
            return email_match.group(0)
        return ''
    
    def _extract_name(self, from_header):
        """Extract sender name from From header
        
        Args:
            from_header (str): From header string
            
        Returns:
            str: Sender name
        """
        # Try to extract name in the format "Name <email@example.com>"
        name_match = re.search(r'^([^<]+)<', from_header)
        if name_match:
            return name_match.group(1).strip()
        
        # If no name found, use the email as the name
        email = self._extract_email(from_header)
        if '@' in email:
            return email.split('@')[0]  # Use the part before @ as name
        
        return 'Unknown Sender'
    
    def _extract_phone(self, body):
        """Extract phone number from email body
        
        Args:
            body (str): Email body text
            
        Returns:
            str: Phone number or empty string
        """
        # Look for various phone number formats (this is a simplified example)
        phone_patterns = [
            r'\+?[\d\(\)\-\s]{10,18}',  # International format with + sign
            r'\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}',  # (123) 456-7890 or 123-456-7890
            r'телефон[:\s]+([\d\+\(\)\s\-]{10,18})',  # Russian "телефон: +123456789"
            r'номер[:\s]+([\d\+\(\)\s\-]{10,18})'    # Russian "номер: +123456789"
        ]
        
        for pattern in phone_patterns:
            phone_match = re.search(pattern, body, re.IGNORECASE)
            if phone_match:
                # If it's a pattern with capture group, use group(1), otherwise group(0)
                phone = phone_match.group(1) if len(phone_match.groups()) > 0 else phone_match.group(0)
                # Clean the phone number
                phone = re.sub(r'[^\d\+]', '', phone)
                return phone
        
        return ''
    
    def _get_email_body(self, email_message):
        """Extract the email body from a multipart message
        
        Args:
            email_message: Parsed email message object
            
        Returns:
            str: Email body
        """
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                disposition = part.get('Content-Disposition', '')
                
                if content_type == 'text/plain' and 'attachment' not in disposition:
                    try:
                        body = part.get_payload(decode=True).decode('utf-8')
                        return body
                    except Exception as e:
                        logger.error(f"Error decoding email body: {e}")
        else:
            try:
                body = email_message.get_payload(decode=True).decode('utf-8')
                return body
            except Exception as e:
                logger.error(f"Error decoding email body: {e}")
        
        return ''
    
    def _determine_interest(self, subject, body):
        """Determine lead interest based on subject and body
        
        Args:
            subject (str): Email subject
            body (str): Email body
            
        Returns:
            str: Determined interest
        """
        # Lowercase for easier matching
        subject_lower = subject.lower()
        body_lower = body.lower()
        combined = subject_lower + " " + body_lower
        
        # Define interest keywords
        interest_keywords = {
            'турция': 'Тур в Турцию',
            'египет': 'Тур в Египет',
            'таиланд': 'Тур в Таиланд',
            'кипр': 'Тур на Кипр',
            'оаэ': 'Тур в ОАЭ',
            'эмират': 'Тур в ОАЭ',
            'дубай': 'Тур в ОАЭ',
            'путевк': 'Поиск тура',
            'брониров': 'Бронирование',
            'расписание': 'Информация о рейсах',
            'рейс': 'Информация о рейсах',
            'билет': 'Авиабилеты',
            'авиа': 'Авиабилеты',
            'консультац': 'Консультация',
            'проконсультир': 'Консультация',
            'стоимост': 'Стоимость тура',
            'цена': 'Стоимость тура',
            'скидк': 'Скидки и акции',
            'акци': 'Скидки и акции',
            'горящ': 'Горящие туры',
            'последн': 'Горящие туры'
        }
        
        # Check for specific interests
        for keyword, interest in interest_keywords.items():
            if keyword in combined:
                return interest
        
        # Default interest if no specific match is found
        return 'Общий запрос'


# Example usage
if __name__ == "__main__":
    processor = EmailProcessor()
    
    # Test with a sample email
    sample_email = """From: Иван Иванов <ivan@example.com>
    Subject: Интересуют туры в Турцию
    Date: Sun, 4 May 2025 15:30:00 +0300
    
    Здравствуйте!
    
    Интересуют туры в Турцию на июнь 2025 года для семьи из 2 взрослых и 1 ребенка.
    Предпочтительно отель 5* с системой "всё включено".
    
    Мой телефон для связи: +7 999 123-45-67
    
    С уважением,
    Иван
    """
    
    lead = processor.process_email(sample_email)
    print(json.dumps(lead, indent=2, ensure_ascii=False) if lead else "Failed to process email")
