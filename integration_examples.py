"""
Integration Examples for Crystal Bay Travel Lead Import System
This file contains practical examples for implementing various lead import integrations
"""

import requests
import json
from datetime import datetime

# Example 1: Email Service Integration (SendGrid Inbound Parse)
def setup_sendgrid_webhook():
    """
    Example of how to configure SendGrid's Inbound Parse webhook
    to automatically convert emails into leads
    """
    webhook_config = {
        "url": "https://your-domain.replit.app/api/leads/import/webhook/email",
        "hostname": "leads.crystalbaytours.com",  # Your subdomain
        "send_raw": False,
        "spam_check": True
    }
    
    print("SendGrid Inbound Parse Configuration:")
    print("1. Go to SendGrid Dashboard > Settings > Inbound Parse")
    print("2. Add a new host & URL:")
    print(f"   Hostname: {webhook_config['hostname']}")
    print(f"   URL: {webhook_config['url']}")
    print("3. Configure your MX records to point to SendGrid")
    print("4. All emails sent to support@leads.crystalbaytours.com will become leads")

# Example 2: Website Widget Integration
def create_contact_form_integration():
    """
    Example HTML for integrating the lead capture widget
    """
    html_example = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Your Travel Website</title>
    </head>
    <body>
        <h1>Plan Your Dream Vacation</h1>
        
        <!-- Crystal Bay Travel Lead Widget -->
        <div id="crystal-bay-lead-widget"></div>
        <script src="https://your-domain.replit.app/static/js/lead-widget.js"></script>
        
        <!-- Or manual initialization with custom options -->
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            new CrystalBayWidget('crystal-bay-lead-widget', {
                apiUrl: 'https://your-domain.replit.app/api/leads/import/widget',
                theme: 'light'  // optional customization
            });
        });
        </script>
    </body>
    </html>
    '''
    
    print("Website Integration Example:")
    print(html_example)

# Example 3: Partner API Integration
def partner_api_example():
    """
    Example of how a travel partner would send leads via API
    """
    api_endpoint = "https://your-domain.replit.app/api/leads/import/api"
    api_key = "your_partner_api_key"
    
    lead_data = {
        "customer": {
            "name": "Maria Rodriguez",
            "email": "maria@example.com",
            "phone": "+34 600 123 456"
        },
        "inquiry": {
            "type": "Luxury vacation",
            "message": "Looking for 5-star resort in Maldives for anniversary",
            "destination": "Maldives",
            "budget": 10000,
            "travel_date": "2025-09-15",
            "duration": "7 nights"
        },
        "source_info": {
            "partner_name": "LuxuryTravel Partners",
            "reference_id": "LTP_001_2025"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    
    # Example API call
    response_example = {
        "success": True,
        "lead_id": "lead_123",
        "message": "Lead created from API successfully",
        "partner_reference": "LTP_001_2025"
    }
    
    print("Partner API Integration Example:")
    print(f"POST {api_endpoint}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Body: {json.dumps(lead_data, indent=2)}")
    print(f"Response: {json.dumps(response_example, indent=2)}")

# Example 4: Bulk Import from CSV/Excel
def bulk_import_example():
    """
    Example of how to bulk import leads from a CSV file
    """
    bulk_data = {
        "leads": [
            {
                "type": "email",
                "data": {
                    "from": "customer1@example.com",
                    "subject": "Turkey vacation inquiry",
                    "body": "Planning family trip to Turkey in summer",
                    "received_at": "2025-01-01T10:00:00Z"
                }
            },
            {
                "type": "widget",
                "data": {
                    "name": "John Smith",
                    "email": "john@example.com",
                    "phone": "+1-555-0123",
                    "message": "Interested in European tours"
                }
            },
            {
                "type": "api",
                "data": {
                    "name": "Alice Johnson",
                    "email": "alice@example.com",
                    "message": "Honeymoon package inquiry",
                    "destination": "Bali",
                    "budget": 5000
                }
            }
        ]
    }
    
    print("Bulk Import Example:")
    print("POST /api/leads/import/bulk")
    print(json.dumps(bulk_data, indent=2))

# Example 5: WordPress Plugin Integration
def wordpress_plugin_example():
    """
    Example PHP code for WordPress integration
    """
    php_code = '''
    <?php
    // WordPress function to send form data to Crystal Bay Travel
    function send_to_crystal_bay($form_data) {
        $api_url = 'https://your-domain.replit.app/api/leads/import/widget';
        
        $lead_data = array(
            'name' => $form_data['name'],
            'email' => $form_data['email'],
            'phone' => $form_data['phone'],
            'message' => $form_data['message'],
            'widget_id' => 'wordpress_contact_form',
            'page_url' => get_permalink(),
            'utm_source' => $_GET['utm_source'] ?? '',
            'utm_campaign' => $_GET['utm_campaign'] ?? ''
        );
        
        $response = wp_remote_post($api_url, array(
            'headers' => array('Content-Type' => 'application/json'),
            'body' => json_encode($lead_data),
            'timeout' => 30
        ));
        
        if (is_wp_error($response)) {
            error_log('Crystal Bay API Error: ' . $response->get_error_message());
            return false;
        }
        
        $body = wp_remote_retrieve_body($response);
        $result = json_decode($body, true);
        
        return $result['success'] ?? false;
    }
    
    // Hook into Contact Form 7 submission
    add_action('wpcf7_mail_sent', function($contact_form) {
        $submission = WPCF7_Submission::get_instance();
        $form_data = $submission->get_posted_data();
        send_to_crystal_bay($form_data);
    });
    ?>
    '''
    
    print("WordPress Integration Example:")
    print(php_code)

# Example 6: Zapier Integration
def zapier_integration_example():
    """
    Example of how to set up Zapier integration
    """
    zapier_config = {
        "trigger": "New Email in Gmail",
        "filter": "Subject contains 'travel' OR 'vacation' OR 'tour'",
        "action": "Webhook POST",
        "webhook_url": "https://your-domain.replit.app/api/leads/import/email",
        "payload": {
            "from": "{{trigger.from}}",
            "subject": "{{trigger.subject}}",
            "body": "{{trigger.body_plain}}",
            "received_at": "{{trigger.date}}"
        }
    }
    
    print("Zapier Integration Setup:")
    print("1. Create a new Zap")
    print("2. Trigger: Gmail - New Email")
    print("3. Filter: Email subject contains travel keywords")
    print("4. Action: Webhooks - POST")
    print(f"5. URL: {zapier_config['webhook_url']}")
    print(f"6. Payload: {json.dumps(zapier_config['payload'], indent=2)}")

# Example 7: Facebook Lead Ads Integration
def facebook_leads_integration():
    """
    Example of Facebook Lead Ads webhook integration
    """
    webhook_verification = '''
    # Facebook webhook verification (add this to your Flask app)
    @app.route('/api/leads/import/facebook', methods=['GET'])
    def facebook_webhook_verify():
        verify_token = "your_facebook_verify_token"
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode == 'subscribe' and token == verify_token:
            return challenge
        return 'Forbidden', 403
    
    @app.route('/api/leads/import/facebook', methods=['POST'])
    def facebook_webhook():
        data = request.get_json()
        
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                if change.get('field') == 'leadgen':
                    lead_id = change['value']['leadgen_id']
                    # Fetch lead details from Facebook Graph API
                    # Convert to our lead format and save
                    process_facebook_lead(lead_id)
        
        return 'OK', 200
    '''
    
    print("Facebook Lead Ads Integration:")
    print(webhook_verification)

# Example 8: Testing the API endpoints
def test_api_endpoints():
    """
    Test script for validating all API endpoints
    """
    base_url = "https://your-domain.replit.app"
    
    # Test email import
    email_test = {
        "from": "test@example.com",
        "subject": "Test email lead",
        "body": "This is a test email for lead generation"
    }
    
    # Test widget import
    widget_test = {
        "name": "Test User",
        "email": "testuser@example.com",
        "message": "Test widget submission"
    }
    
    # Test API import
    api_test = {
        "customer": {
            "name": "API Test User",
            "email": "apitest@example.com"
        },
        "inquiry": {
            "type": "Test inquiry",
            "message": "Testing API integration"
        }
    }
    
    test_cases = [
        ("POST", f"{base_url}/api/leads/import/email", email_test),
        ("POST", f"{base_url}/api/leads/import/widget", widget_test),
        ("POST", f"{base_url}/api/leads/import/api", api_test),
        ("GET", f"{base_url}/api/leads/import/status", None)
    ]
    
    print("API Testing Script:")
    for method, url, data in test_cases:
        print(f"\n{method} {url}")
        if data:
            print(f"Data: {json.dumps(data, indent=2)}")

if __name__ == "__main__":
    print("Crystal Bay Travel - Lead Import Integration Examples")
    print("=" * 60)
    
    setup_sendgrid_webhook()
    print("\n" + "="*60 + "\n")
    
    create_contact_form_integration()
    print("\n" + "="*60 + "\n")
    
    partner_api_example()
    print("\n" + "="*60 + "\n")
    
    bulk_import_example()
    print("\n" + "="*60 + "\n")
    
    wordpress_plugin_example()
    print("\n" + "="*60 + "\n")
    
    zapier_integration_example()
    print("\n" + "="*60 + "\n")
    
    facebook_leads_integration()
    print("\n" + "="*60 + "\n")
    
    test_api_endpoints()