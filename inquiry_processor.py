import os
import logging
import json
import openai
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize singleton instance
_inquiry_processor_instance = None

class InquiryProcessor:
    """Process customer inquiries with AI and automated rules"""
    
    def __init__(self):
        """Initialize the inquiry processor"""
        # Initialize OpenAI client
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.client = openai.OpenAI(api_key=self.openai_api_key)
        
        # Status transitions map (current_status -> possible next statuses)
        self.status_transitions = {
            'new': ['in_progress', 'cancelled'],
            'in_progress': ['pending', 'cancelled'],
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['closed', 'cancelled'],
            'closed': [],  # Terminal state
            'cancelled': []  # Terminal state
        }
    
    def process_new_inquiry(self, inquiry_data):
        """Process a new inquiry with AI analysis
        
        Args:
            inquiry_data (dict): The inquiry data to process
            
        Returns:
            dict: Processing results
        """
        try:
            # Analyze the inquiry text with AI
            if 'notes' in inquiry_data and inquiry_data['notes']:
                analysis = self._analyze_with_ai(inquiry_data['notes'])
            else:
                analysis = {
                    'category': 'unknown',
                    'urgency': 1,
                    'summary': 'No content to analyze',
                    'suggested_actions': ['Contact customer for more information']
                }
            
            # Create the lead in the database
            from models import LeadService
            
            # Add analysis results to lead data
            inquiry_data['category'] = analysis.get('category')
            inquiry_data['urgency'] = analysis.get('urgency')
            
            # Set initial status
            if 'status' not in inquiry_data:
                inquiry_data['status'] = 'new'
            
            # Create lead
            lead = LeadService.create_lead(inquiry_data)
            
            # Add an interaction with the analysis
            interaction_data = {
                'type': 'ai_analysis',
                'notes': f"AI Analysis:\n\n" +
                        f"Category: {analysis.get('category')}\n" +
                        f"Urgency: {analysis.get('urgency')}/5\n" +
                        f"Summary: {analysis.get('summary')}\n\n" +
                        f"Suggested Actions:\n" + '\n'.join([f"- {action}" for action in analysis.get('suggested_actions', [])])
            }
            
            LeadService.add_lead_interaction(lead['id'], interaction_data)
            
            return {
                'success': True,
                'lead': lead,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Error processing inquiry: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_inquiry_status(self, lead_id, data=None):
        """Update the status of an inquiry based on rules or requested status
        
        Args:
            lead_id (str): The lead ID to update
            data (dict, optional): Optional data with requested status
            
        Returns:
            dict: Updated lead data or None if not found
        """
        try:
            from models import LeadService
            
            # Get current lead data
            lead = LeadService.get_lead(lead_id)
            if not lead:
                return None
            
            current_status = lead.get('status')
            requested_status = data.get('requested_status') if data else None
            
            # Determine next status
            next_status = None
            
            # If specific status requested, check if it's a valid transition
            if requested_status and requested_status in self.status_transitions.get(current_status, []):
                next_status = requested_status
            else:
                # Apply automatic rules based on current status
                next_status = self._determine_next_status(lead)
            
            # If status change determined, update the lead
            if next_status and next_status != current_status:
                update_data = {'status': next_status}
                
                # Add a status change interaction
                interaction_data = {
                    'type': 'status_change',
                    'notes': f"Status changed automatically from '{current_status}' to '{next_status}'"
                }
                LeadService.add_lead_interaction(lead_id, interaction_data)
                
                # Update the lead status
                return LeadService.update_lead(lead_id, update_data)
            
            return lead
            
        except Exception as e:
            logger.error(f"Error updating inquiry status: {e}")
            return None
    
    def process_all_inquiries(self):
        """Process all active inquiries with AI and rules
        
        Returns:
            dict: Processing results
        """
        try:
            from models import LeadService
            
            # Get all active leads (excluding closed and cancelled)
            active_statuses = ['new', 'in_progress', 'pending', 'confirmed']
            leads = []
            
            for status in active_statuses:
                status_leads = LeadService.get_leads(status=status)
                if status_leads:
                    leads.extend(status_leads)
            
            results = {
                'total': len(leads),
                'updated': 0,
                'failed': 0,
                'details': []
            }
            
            # Process each lead
            for lead in leads:
                try:
                    updated_lead = self.update_inquiry_status(lead['id'])
                    
                    if updated_lead and updated_lead.get('status') != lead.get('status'):
                        results['updated'] += 1
                        results['details'].append({
                            'lead_id': lead['id'],
                            'old_status': lead['status'],
                            'new_status': updated_lead['status']
                        })
                except Exception as e:
                    results['failed'] += 1
                    logger.error(f"Error processing lead {lead['id']}: {e}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing all inquiries: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_with_ai(self, text):
        """Analyze text with OpenAI to categorize and extract insights
        
        Args:
            text (str): The text to analyze
            
        Returns:
            dict: Analysis results
        """
        try:
            system_prompt = """
            You are an AI assistant for a travel agency. Analyze the customer inquiry and extract key information.
            Return a JSON response with the following fields:
            - category: The type of inquiry (e.g., beach_vacation, city_tour, cruise, flight_only, custom_tour, etc.)
            - urgency: Rate from 1-5 how urgent this inquiry seems (5 being most urgent)
            - summary: A brief 1-2 sentence summary of the inquiry
            - suggested_actions: A list of 2-3 specific actions the travel agent should take
            
            Base your analysis only on the facts in the text. If information is missing, suggest requesting it rather than making assumptions.
            """
            
            # Use the newest OpenAI model - gpt-4o which was released May 13, 2024.
            # Do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                response_format={"type": "json_object"}
            )
            
            try:
                analysis = json.loads(response.choices[0].message.content)
                return analysis
            except json.JSONDecodeError:
                # If JSON parsing fails, return a structured format of the raw content
                content = response.choices[0].message.content
                return {
                    'category': 'parsing_error',
                    'urgency': 3,
                    'summary': 'Failed to parse AI response',
                    'suggested_actions': ['Review the raw analysis', 'Contact customer for clarification'],
                    'raw_content': content
                }
                
        except Exception as e:
            logger.error(f"Error analyzing with AI: {e}")
            return {
                'category': 'error',
                'urgency': 3,
                'summary': f"Error during analysis: {str(e)}",
                'suggested_actions': ['Check AI service status', 'Try manual analysis']
            }
    
    def _determine_next_status(self, lead):
        """Determine the next status for a lead based on its current state
        
        Args:
            lead (dict): The lead data
            
        Returns:
            str: Next status or None if no change needed
        """
        current_status = lead.get('status')
        
        # Simple state machine logic
        if current_status == 'new':
            # Move new leads to in_progress if they're urgent
            urgency = lead.get('urgency', 0)
            if urgency >= 4:
                return 'in_progress'
                
        elif current_status == 'in_progress':
            # Check if there are recent interactions that might warrant moving to pending
            interactions = lead.get('interactions', [])
            if len(interactions) >= 3:
                return 'pending'
                
        elif current_status == 'pending':
            # Look for booking references in the notes that might indicate a confirmation
            notes = lead.get('notes', '')
            if 'booking confirmed' in notes.lower() or any(ref_pattern in notes for ref_pattern in ['CB-', 'BK-']):
                return 'confirmed'
        
        # No status change determined
        return None


def get_inquiry_processor():
    """Get the singleton instance of InquiryProcessor
    
    Returns:
        InquiryProcessor: The singleton instance
    """
    global _inquiry_processor_instance
    
    if _inquiry_processor_instance is None:
        _inquiry_processor_instance = InquiryProcessor()
        
    return _inquiry_processor_instance