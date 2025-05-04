import os
import logging
import base64
from email.parser import Parser
from email.policy import default
from datetime import datetime, timedelta

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Subject
from python_http_client.exceptions import HTTPError

from email_processor import EmailProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('email_integration')

class EmailIntegration:
    """Integration with SendGrid for sending and receiving emails"""
    
    def __init__(self):
        """Initialize the SendGrid integration"""
        self.api_key = os.environ.get('SENDGRID_API_KEY')
        self.from_email = os.environ.get('SENDGRID_FROM_EMAIL', 'info@crystalbay.travel')
        self.client = None
        self.processor = EmailProcessor()
        
        if self.api_key:
            try:
                self.client = SendGridAPIClient(self.api_key)
                logger.info("SendGrid client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing SendGrid client: {e}")
        else:
            logger.warning("SENDGRID_API_KEY environment variable not set")
    
    def is_configured(self):
        """Check if SendGrid is properly configured"""
        return self.client is not None
    
    def send_email(self, to_email, subject, text_content=None, html_content=None):
        """Send an email using SendGrid
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            text_content (str, optional): Plain text content
            html_content (str, optional): HTML content
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_configured():
            logger.error("SendGrid not configured. Cannot send email.")
            return False
            
        message = Mail(
            from_email=Email(self.from_email),
            to_emails=To(to_email),
            subject=Subject(subject)
        )
        
        if html_content:
            message.content = Content("text/html", html_content)
        elif text_content:
            message.content = Content("text/plain", text_content)
        else:
            logger.error("No content provided for email")
            return False
        
        try:
            response = self.client.send(message)
            status_code = response.status_code
            logger.info(f"Email sent with status code: {status_code}")
            return 200 <= status_code < 300
        except HTTPError as e:
            logger.error(f"SendGrid HTTP error: {e.to_dict}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def receive_webhook(self, inbound_data):
        """Process inbound email webhook from SendGrid
        
        Args:
            inbound_data (dict): Webhook data from SendGrid
            
        Returns:
            dict: Processed lead data or None
        """
        try:
            # Extract email content from the webhook
            email_data = inbound_data.get('email', {})
            if not email_data:
                logger.error("No email data in webhook payload")
                return None
                
            # Base64 encoded email content
            raw_email = email_data.get('content', '')
            if not raw_email:
                logger.error("No email content in webhook payload")
                return None
                
            # Decode base64 content
            try:
                decoded_email = base64.b64decode(raw_email).decode('utf-8')
            except Exception as e:
                logger.error(f"Error decoding email content: {e}")
                return None
                
            # Process the email to create a lead
            lead = self.processor.process_email(decoded_email)
            
            # Send auto-response if lead was created
            if lead and lead.get('customer_email'):
                self._send_auto_response(lead)
                
            return lead
            
        except Exception as e:
            logger.error(f"Error processing inbound email webhook: {e}")
            return None
    
    def _send_auto_response(self, lead):
        """Send an automatic response to the lead
        
        Args:
            lead (dict): Lead data
            
        Returns:
            bool: True if email was sent successfully
        """
        customer_email = lead.get('customer_email')
        customer_name = lead.get('customer_name', '').split(' ')[0]  # First name
        interest = lead.get('interest', 'Общий запрос')
        
        subject = f"Ваш запрос получен: {interest}"
        
        text_content = f"""Здравствуйте, {customer_name}!

Спасибо за обращение в туристическое агентство Crystal Bay Travel.

Мы получили ваш запрос о "{interest}" и свяжемся с вами в ближайшее время.

Если у вас возникли дополнительные вопросы, не стесняйтесь ответить на это письмо.

С уважением,
Команда Crystal Bay Travel
"""
        
        html_content = f"""<html>
<body>
<p>Здравствуйте, {customer_name}!</p>

<p>Спасибо за обращение в туристическое агентство Crystal Bay Travel.</p>

<p>Мы получили ваш запрос о <strong>"{interest}"</strong> и свяжемся с вами в ближайшее время.</p>

<p>Если у вас возникли дополнительные вопросы, не стесняйтесь ответить на это письмо.</p>

<p>С уважением,<br>
Команда Crystal Bay Travel</p>
</body>
</html>"""
        
        return self.send_email(customer_email, subject, text_content, html_content)
    
    def check_incoming_emails(self, since_hours=24):
        """Check for incoming emails in the last N hours
        
        This is a placeholder function since SendGrid doesn't provide a direct API
        to fetch emails. In practice, you would use the webhook approach or
        integrate with IMAP/POP3 to fetch emails from your mail server.
        
        Args:
            since_hours (int): Hours to look back
            
        Returns:
            list: List of processed leads or empty list
        """
        logger.info(f"Checking emails from the last {since_hours} hours")
        logger.warning("This is a placeholder function. Use SendGrid inbound parse webhook for production.")
        
        # In a real implementation, you would fetch emails from your mail server
        # and process each one with the email processor.
        
        return []


# Example usage
if __name__ == "__main__":
    email_integration = EmailIntegration()
    
    if email_integration.is_configured():
        # Send a test email
        test_to = "test@example.com"
        test_subject = "Тестовое сообщение от Crystal Bay Travel"
        test_content = "Это тестовое сообщение от системы Crystal Bay Travel. Если вы его получили, значит интеграция с SendGrid работает корректно."
        
        success = email_integration.send_email(test_to, test_subject, test_content)
        print(f"Test email {'sent successfully' if success else 'failed to send'}")
    else:
        print("SendGrid integration not configured. Set the SENDGRID_API_KEY environment variable.")
