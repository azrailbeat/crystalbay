#!/usr/bin/env python3
"""
SAMO API Settings Integration
Integrates SAMO connectivity status into the settings panel
"""

import json
import os
import requests
from datetime import datetime
from flask import jsonify

def get_samo_connectivity_status():
    """Get current SAMO API connectivity status"""
    
    # Load latest connectivity test results
    connectivity_file = 'data/samo_connectivity_results.json'
    
    if os.path.exists(connectivity_file):
        with open(connectivity_file, 'r') as f:
            results = json.load(f)
        
        # Extract current IP from test results
        current_ip = None
        for test_result in results.get('test_results', {}).values():
            if 'current_ip' in test_result:
                current_ip = test_result['current_ip']
                break
        
        return {
            'status': results['connectivity_status'],
            'successful_connections': results['successful_connections'],
            'total_endpoints': results['total_endpoints'],
            'current_ip': current_ip,
            'expected_ip': '34.117.33.233',
            'last_test': results.get('test_timestamp'),
            'message': get_status_message(results['connectivity_status'], current_ip)
        }
    else:
        return {
            'status': 'untested',
            'message': 'SAMO API connectivity not tested',
            'current_ip': None,
            'expected_ip': '34.117.33.233'
        }

def get_status_message(status, current_ip):
    """Generate human-readable status message"""
    
    if status == 'operational':
        return "SAMO API fully connected and operational"
    elif status == 'partial':
        return "SAMO API partially accessible - some endpoints working"
    elif status == 'blocked':
        if current_ip:
            return f"SAMO API blocked - IP {current_ip} needs whitelisting by Crystal Bay"
        else:
            return "SAMO API blocked - IP whitelisting required"
    else:
        return "SAMO API status unknown"

def test_samo_connection_now():
    """Run immediate SAMO connectivity test"""
    
    base_url = "https://booking-kz.crystalbay.com/export/default.php"
    oauth_token = "27bd59a7ac67422189789f0188167379"
    
    try:
        # Quick test with currencies endpoint
        data = {
            'samo_action': 'api',
            'version': '1.0',
            'type': 'json',
            'action': 'SearchTour_CURRENCIES',
            'oauth_token': oauth_token
        }
        
        headers = {
            'User-Agent': 'Crystal Bay Travel Integration/1.0',
            'Accept': 'application/json, text/xml, */*',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(base_url, data=data, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # Success - API is working
            return {
                'status': 'operational',
                'message': 'SAMO API connection successful',
                'test_timestamp': datetime.now().isoformat(),
                'response_code': 200
            }
        elif response.status_code == 403:
            # IP not whitelisted
            current_ip = None
            if "blacklisted address" in response.text:
                import re
                ip_match = re.search(r'blacklisted address (\d+\.\d+\.\d+\.\d+)', response.text)
                if ip_match:
                    current_ip = ip_match.group(1)
            
            return {
                'status': 'blocked',
                'message': f'SAMO API blocked - IP {current_ip} needs whitelisting',
                'current_ip': current_ip,
                'test_timestamp': datetime.now().isoformat(),
                'response_code': 403
            }
        else:
            return {
                'status': 'error',
                'message': f'SAMO API error - HTTP {response.status_code}',
                'test_timestamp': datetime.now().isoformat(),
                'response_code': response.status_code
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'message': f'SAMO API connection error: {str(e)}',
            'test_timestamp': datetime.now().isoformat()
        }

def get_deployment_info():
    """Get current deployment information"""
    
    return {
        'environment': 'development' if os.getenv('REPL_ID') else 'production',
        'expected_production_ip': '34.117.33.233',
        'samo_api_endpoint': 'https://booking-kz.crystalbay.com/export/default.php',
        'oauth_token': '27bd59a7ac67422189789f0188167379',
        'deployment_status': 'Configuration ready for production deployment'
    }

def generate_settings_dashboard_data():
    """Generate comprehensive data for settings dashboard"""
    
    connectivity = get_samo_connectivity_status()
    deployment = get_deployment_info()
    
    # Determine overall integration status
    if connectivity['status'] == 'operational':
        integration_status = 'connected'
        status_color = 'success'
        action_needed = False
    elif connectivity['status'] == 'blocked':
        integration_status = 'blocked'
        status_color = 'danger'
        action_needed = True
    else:
        integration_status = 'pending'
        status_color = 'warning'
        action_needed = True
    
    return {
        'samo_api': {
            'status': integration_status,
            'status_color': status_color,
            'connectivity': connectivity,
            'deployment': deployment,
            'action_needed': action_needed,
            'next_steps': get_next_steps(connectivity['status'], connectivity.get('current_ip'))
        }
    }

def get_next_steps(status, current_ip):
    """Get actionable next steps based on current status"""
    
    if status == 'operational':
        return [
            "SAMO API is fully connected",
            "Real-time tour data retrieval available",
            "System ready for live bookings"
        ]
    elif status == 'blocked':
        return [
            f"Contact Crystal Bay support to whitelist IP: {current_ip or 'unknown'}",
            "Request production IP 34.117.33.233 to be whitelisted",
            "Deploy to production environment for full connectivity"
        ]
    else:
        return [
            "Deploy system to production environment",
            "Test SAMO API connectivity",
            "Verify IP whitelisting with Crystal Bay"
        ]

if __name__ == '__main__':
    # Test the integration
    data = generate_settings_dashboard_data()
    print(json.dumps(data, indent=2, default=str))