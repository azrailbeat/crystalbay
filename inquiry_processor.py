import os
import json
import logging
import openai
from datetime import datetime, timedelta
from dotenv import load_dotenv
from models import BookingService, LeadService
from email_processor import EmailProcessor
import requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_api_key = os.environ.get("OPENAI_API_KEY")
openai_client = openai.OpenAI(api_key=openai_api_key)

# SAMO API credentials
samo_oauth_token = os.environ.get("SAMO_OAUTH_TOKEN")

class InquiryProcessor:
    """
    Process customer inquiries automatically and update their statuses
    based on AI analysis and information from external systems.
    """
    
    def __init__(self):
        """
        Initialize the inquiry processor with necessary services.
        """
        self.lead_service = LeadService
        self.booking_service = BookingService
        self.email_processor = EmailProcessor()
        logger.info("Inquiry processor initialized")
        
    def process_new_inquiry(self, inquiry_data):
        """
        Process a new inquiry coming from any source (email, Telegram, etc.)
        and determine its category, urgency, and next actions.
        
        Args:
            inquiry_data (dict): Data about the inquiry including:
                - source: Source of the inquiry (email, telegram, etc.)
                - content: Text content of the inquiry
                - customer_info: Any available customer information
                
        Returns:
            dict: Processed inquiry with AI analysis and suggested actions
        """
        try:
            logger.info(f"Processing new inquiry from {inquiry_data.get('source')}")
            
            # Extract content and customer info
            content = inquiry_data.get('content', '')
            customer_info = inquiry_data.get('customer_info', {})
            
            # Perform AI analysis on the inquiry
            analysis = self._analyze_with_ai(content)
            
            # Check if there's booking information
            booking_info = None
            if analysis.get('booking_reference'):
                booking_info = self._check_booking(analysis.get('booking_reference'))
            
            # Check flight information if available
            flight_info = None
            if analysis.get('flight_number'):
                flight_info = self._check_flight(analysis.get('flight_number'), 
                                               analysis.get('flight_date'))
            
            # Determine the appropriate column/status based on analysis
            status = self._determine_status(analysis, booking_info, flight_info)
            
            # Create or update lead in the database
            lead_data = {
                'customer_name': customer_info.get('name', ''),
                'customer_email': customer_info.get('email', ''),
                'customer_phone': customer_info.get('phone', ''),
                'source': inquiry_data.get('source', ''),
                'interest': analysis.get('interest', 'General inquiry'),
                'status': status,
                'notes': f"AI Analysis: {analysis.get('summary')}\n\n" + 
                        f"Category: {analysis.get('category')}\n" +
                        f"Urgency: {analysis.get('urgency')}\n\n" +
                        content
            }
            
            # Create the lead
            lead_id = self.lead_service.create_lead(lead_data)
            
            # Add processed data to the result
            result = {
                'lead_id': lead_id,
                'status': status,
                'analysis': analysis,
                'booking_info': booking_info,
                'flight_info': flight_info,
                'suggested_actions': analysis.get('suggested_actions', [])
            }
            
            logger.info(f"Successfully processed inquiry, assigned status: {status}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing inquiry: {str(e)}")
            raise
    
    def update_inquiry_status(self, lead_id, new_data=None):
        """
        Automatically update the status of an inquiry based on new information
        or periodic checks against external systems.
        
        Args:
            lead_id (str): The ID of the lead to update
            new_data (dict, optional): New data related to the inquiry
            
        Returns:
            dict: Updated lead information
        """
        try:
            # Get current lead data
            lead = self.lead_service.get_lead(lead_id)
            if not lead:
                logger.error(f"Lead {lead_id} not found")
                return None
            
            current_status = lead.get('status')
            logger.info(f"Updating inquiry {lead_id}, current status: {current_status}")
            
            # Check if there's booking information to update
            booking_reference = None
            # Try to extract booking reference from lead notes
            if lead.get('notes') and 'booking reference' in lead.get('notes').lower():
                # Extract the booking reference using simple pattern matching
                # This could be enhanced with more sophisticated extraction
                notes = lead.get('notes').lower()
                if 'booking reference:' in notes:
                    booking_reference = notes.split('booking reference:')[1].split('\n')[0].strip()
                elif 'reference number:' in notes:
                    booking_reference = notes.split('reference number:')[1].split('\n')[0].strip()
            
            # If new data contains a booking reference, use that instead
            if new_data and new_data.get('booking_reference'):
                booking_reference = new_data.get('booking_reference')
            
            booking_info = None
            if booking_reference:
                booking_info = self._check_booking(booking_reference)
            
            # Perform AI analysis on any new content
            analysis = None
            if new_data and new_data.get('content'):
                analysis = self._analyze_with_ai(new_data.get('content'))
            
            # Determine if status should be updated
            new_status = self._determine_updated_status(
                current_status, 
                booking_info, 
                analysis,
                new_data
            )
            
            # If status changed, update the lead
            if new_status != current_status:
                update_data = {'status': new_status}
                
                # If we have new notes, append them
                if new_data and new_data.get('content'):
                    update_data['notes'] = f"{lead.get('notes', '')}\n\n--- {datetime.now().strftime('%Y-%m-%d %H:%M')} ---\n{new_data.get('content')}"
                
                # Update the lead in the database
                updated_lead = self.lead_service.update_lead(lead_id, update_data)
                
                # Add an interaction record for the status change
                interaction_data = {
                    'type': 'status_change',
                    'notes': f"Status automatically updated from {current_status} to {new_status}\n" +
                             f"Reason: {self._get_status_change_reason(current_status, new_status, booking_info, analysis)}"
                }
                
                self.lead_service.add_lead_interaction(lead_id, interaction_data)
                
                logger.info(f"Updated inquiry {lead_id} status from {current_status} to {new_status}")
                return updated_lead
            
            logger.info(f"No status update needed for inquiry {lead_id}")
            return lead
            
        except Exception as e:
            logger.error(f"Error updating inquiry status: {str(e)}")
            raise
    
    def check_flight_status(self, flight_number, departure_date):
        """
        Check the status of a flight by its number and departure date.
        
        Args:
            flight_number (str): The flight number
            departure_date (str): The departure date in YYYY-MM-DD format
            
        Returns:
            dict: Flight status information
        """
        try:
            # In a real implementation, this would call a flight status API
            # For now we'll use a simulated response
            logger.info(f"Checking status for flight {flight_number} on {departure_date}")
            
            # Simulate API call to flight status service
            return self._check_flight(flight_number, departure_date)
            
        except Exception as e:
            logger.error(f"Error checking flight status: {str(e)}")
            return {'error': str(e)}
    
    def check_booking_details(self, booking_reference):
        """
        Check details of a booking by its reference number.
        
        Args:
            booking_reference (str): The booking reference number
            
        Returns:
            dict: Booking details information
        """
        try:
            # In a real implementation, this would call the booking system API
            logger.info(f"Checking details for booking {booking_reference}")
            
            # Call SAMO API or use local database
            return self._check_booking(booking_reference)
            
        except Exception as e:
            logger.error(f"Error checking booking details: {str(e)}")
            return {'error': str(e)}
    
    def process_all_inquiries(self):
        """
        Process all active inquiries and update their statuses if needed.
        This method can be scheduled to run periodically.
        
        Returns:
            dict: Summary of processed inquiries and status changes
        """
        try:
            logger.info("Starting batch processing of all active inquiries")
            
            # Get all leads that are not in terminal statuses
            active_statuses = ['new', 'in_progress', 'pending']
            all_leads = []
            
            for status in active_statuses:
                leads = self.lead_service.get_leads(status=status)
                all_leads.extend(leads)
            
            logger.info(f"Found {len(all_leads)} active inquiries to process")
            
            # Process each lead
            results = {
                'total': len(all_leads),
                'updated': 0,
                'unchanged': 0,
                'errors': 0,
                'status_changes': {}
            }
            
            for lead in all_leads:
                try:
                    lead_id = lead.get('id')
                    old_status = lead.get('status')
                    
                    # Update the inquiry status
                    updated_lead = self.update_inquiry_status(lead_id)
                    
                    if updated_lead.get('status') != old_status:
                        results['updated'] += 1
                        new_status = updated_lead.get('status')
                        
                        # Track status changes
                        status_key = f"{old_status}_to_{new_status}"
                        if status_key not in results['status_changes']:
                            results['status_changes'][status_key] = 0
                        results['status_changes'][status_key] += 1
                    else:
                        results['unchanged'] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing lead {lead.get('id')}: {str(e)}")
                    results['errors'] += 1
            
            logger.info(f"Batch processing complete: {results['updated']} inquiries updated")
            return results
            
        except Exception as e:
            logger.error(f"Error in batch processing inquiries: {str(e)}")
            raise
    
    def _analyze_with_ai(self, content):
        """
        Analyze inquiry content with AI to categorize and prioritize.
        
        Args:
            content (str): The inquiry text content
            
        Returns:
            dict: Analysis results including category, urgency, etc.
        """
        try:
            logger.info("Analyzing inquiry content with AI")
            
            # Create the prompt for OpenAI
            prompt = f"""
            Analyze the following customer inquiry for a travel agency and provide structured information:
            
            INQUIRY: {content}
            
            Provide a JSON response with the following fields:
            - category: The category of the inquiry (booking, cancellation, modification, complaint, information, etc.)
            - urgency: A rating from 1-5 where 5 is extremely urgent
            - summary: A brief summary of the inquiry
            - interest: What travel products/destinations the customer is interested in
            - booking_reference: Any booking reference numbers mentioned (null if none)
            - flight_number: Any flight numbers mentioned (null if none)
            - flight_date: Any flight dates mentioned in YYYY-MM-DD format (null if none)
            - suggested_actions: A list of 1-3 suggested actions for the travel agent
            """
            
            # Call OpenAI API
            response = openai_client.chat.completions.create(
                model="gpt-4o", # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            analysis = json.loads(response.choices[0].message.content)
            logger.info(f"AI analysis complete: {analysis['category']}, urgency: {analysis['urgency']}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing with AI: {str(e)}")
            # Return a basic analysis as fallback
            return {
                'category': 'general',
                'urgency': 3,
                'summary': 'Could not analyze content',
                'interest': 'Unknown',
                'booking_reference': None,
                'flight_number': None,
                'flight_date': None,
                'suggested_actions': ['Review manually']
            }
    
    def _check_booking(self, booking_reference):
        """
        Check booking details using the SAMO API or local database.
        
        Args:
            booking_reference (str): The booking reference number
            
        Returns:
            dict: Booking information or None if not found
        """
        try:
            logger.info(f"Checking booking: {booking_reference}")
            
            # First try in local database
            booking = self.booking_service.get_booking(booking_reference)
            if booking:
                return booking
            
            # If not found locally, check SAMO API if token is available
            if samo_oauth_token:
                # This would be a real API call to the SAMO system
                # For now, we'll return a simulated response
                # In a real implementation, replace with actual API call
                
                # Simulated booking information
                return {
                    'reference': booking_reference,
                    'status': 'confirmed',  # or 'pending', 'cancelled'
                    'customer_name': 'John Smith',
                    'departure_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                    'return_date': (datetime.now() + timedelta(days=37)).strftime('%Y-%m-%d'),
                    'destination': 'Turkey',
                    'hotel': 'Sea View Resort',
                    'amount_paid': 1250.00,
                    'total_amount': 1500.00,
                    'balance_due': 250.00,
                    'payment_deadline': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                }
            
            logger.warning(f"Booking {booking_reference} not found")
            return None
            
        except Exception as e:
            logger.error(f"Error checking booking: {str(e)}")
            return None
    
    def _check_flight(self, flight_number, flight_date):
        """
        Check flight status using a flight status API.
        
        Args:
            flight_number (str): The flight number
            flight_date (str): The flight date in YYYY-MM-DD format
            
        Returns:
            dict: Flight information or None if not found
        """
        try:
            logger.info(f"Checking flight: {flight_number} on {flight_date}")
            
            # In a real implementation, this would call a flight status API
            # For now, we'll return a simulated response
            # Replace with actual API call in production
            
            # Simulated flight information
            return {
                'flight_number': flight_number,
                'departure_date': flight_date,
                'status': 'scheduled',  # or 'delayed', 'cancelled', 'completed'
                'departure_time': '10:30',
                'arrival_time': '13:45',
                'departure_airport': 'SVO',
                'arrival_airport': 'AYT',
                'terminal': 'D',
                'delay_minutes': 0,
            }
            
        except Exception as e:
            logger.error(f"Error checking flight: {str(e)}")
            return None
    
    def _determine_status(self, analysis, booking_info, flight_info):
        """
        Determine the appropriate status/column for an inquiry based on analysis.
        
        Args:
            analysis (dict): AI analysis of the inquiry
            booking_info (dict): Booking information if available
            flight_info (dict): Flight information if available
            
        Returns:
            str: The determined status
        """
        # Default status is 'new'
        status = 'new'
        
        # High urgency inquiries go to 'in_progress'
        if analysis.get('urgency', 0) >= 4:
            status = 'in_progress'
        
        # Complaints go to 'in_progress'
        if analysis.get('category') == 'complaint':
            status = 'in_progress'
        
        # Booking confirmations go to 'confirmed'
        if (analysis.get('category') == 'booking_confirmation' and 
            booking_info and booking_info.get('status') == 'confirmed'):
            status = 'confirmed'
        
        # Cancellations that are confirmed go to 'closed'
        if (analysis.get('category') == 'cancellation' and 
            booking_info and booking_info.get('status') == 'cancelled'):
            status = 'closed'
        
        # Flight issues that are urgent go to 'in_progress'
        if (analysis.get('category') == 'flight_issue' and 
            flight_info and flight_info.get('status') in ['delayed', 'cancelled']):
            status = 'in_progress'
        
        logger.info(f"Determined status: {status} based on analysis and external data")
        return status
    
    def _determine_updated_status(self, current_status, booking_info, analysis, new_data):
        """
        Determine if the status of an inquiry should be updated based on new information.
        
        Args:
            current_status (str): The current status of the inquiry
            booking_info (dict): Updated booking information if available
            analysis (dict): AI analysis of new content if available
            new_data (dict): Any new data related to the inquiry
            
        Returns:
            str: The updated status or the current status if no update needed
        """
        # Start with the current status
        new_status = current_status
        
        # Status transition rules
        if current_status == 'new':
            # New inquiries can move to in_progress or confirmed
            if booking_info and booking_info.get('status') == 'confirmed':
                new_status = 'confirmed'
            elif analysis and analysis.get('urgency', 0) >= 4:
                new_status = 'in_progress'
                
        elif current_status == 'in_progress':
            # In-progress inquiries can move to confirmed or closed
            if booking_info:
                if booking_info.get('status') == 'confirmed':
                    new_status = 'confirmed'
                elif booking_info.get('status') == 'cancelled':
                    new_status = 'closed'
        
        # Handle explicit status change requests in new data
        if new_data and new_data.get('requested_status'):
            requested_status = new_data.get('requested_status')
            # Validate that the requested status is valid
            valid_statuses = ['new', 'in_progress', 'confirmed', 'closed']
            if requested_status in valid_statuses:
                new_status = requested_status
        
        logger.info(f"Status determination: {current_status} -> {new_status}")
        return new_status
    
    def _get_status_change_reason(self, old_status, new_status, booking_info, analysis):
        """
        Generate a human-readable reason for a status change.
        
        Args:
            old_status (str): The previous status
            new_status (str): The new status
            booking_info (dict): Booking information if available
            analysis (dict): AI analysis if available
            
        Returns:
            str: The reason for the status change
        """
        reason = "Automatic status update"  # Default reason
        
        # Add more specific reasons based on the statuses and data
        if new_status == 'confirmed' and booking_info:
            reason = f"Booking confirmed in reservation system: {booking_info.get('reference')}"
            
        elif new_status == 'closed' and booking_info and booking_info.get('status') == 'cancelled':
            reason = f"Booking cancelled in reservation system: {booking_info.get('reference')}"
            
        elif new_status == 'in_progress' and analysis and analysis.get('urgency', 0) >= 4:
            reason = f"High urgency inquiry (level {analysis.get('urgency')}): {analysis.get('summary')}"
        
        return reason

# Singleton instance
_inquiry_processor = None

def get_inquiry_processor():
    """
    Get the singleton instance of the InquiryProcessor.
    """
    global _inquiry_processor
    if _inquiry_processor is None:
        _inquiry_processor = InquiryProcessor()
    return _inquiry_processor