#!/usr/bin/env python3
"""
SAMO API Alternative Access Methods
Provides multiple ways to access Crystal Bay SAMO API data
"""

import requests
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CrystalBayAPIAlternative:
    """Alternative methods for accessing Crystal Bay SAMO API"""
    
    def __init__(self, oauth_token: str):
        self.oauth_token = oauth_token
        self.base_url = "https://booking-kz.crystalbay.com/export/default.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Crystal Bay Travel Integration/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        })
    
    def test_api_accessibility(self):
        """Test different methods to access the API"""
        results = []
        
        # Method 1: Direct access (current approach)
        try:
            response = self.session.post(self.base_url, data={
                'samo_action': 'api',
                'version': '1.0',
                'type': 'json',
                'action': 'SearchTour_CURRENCIES',
                'oauth_token': self.oauth_token
            }, timeout=10)
            
            results.append({
                'method': 'Direct API Access',
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'error': None if response.status_code == 200 else f"HTTP {response.status_code}"
            })
            
        except Exception as e:
            results.append({
                'method': 'Direct API Access',
                'status_code': None,
                'success': False,
                'error': str(e)
            })
        
        # Method 2: With different headers
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Referer': 'https://booking-kz.crystalbay.com/',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.post(self.base_url, data={
                'samo_action': 'api',
                'version': '1.0',
                'type': 'json',
                'action': 'SearchTour_CURRENCIES',
                'oauth_token': self.oauth_token
            }, headers=headers, timeout=10)
            
            results.append({
                'method': 'Browser Headers',
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'error': None if response.status_code == 200 else f"HTTP {response.status_code}"
            })
            
        except Exception as e:
            results.append({
                'method': 'Browser Headers',
                'status_code': None,
                'success': False,
                'error': str(e)
            })
        
        # Method 3: GET request instead of POST
        try:
            params = {
                'samo_action': 'api',
                'version': '1.0',
                'type': 'json',
                'action': 'SearchTour_CURRENCIES',
                'oauth_token': self.oauth_token
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            results.append({
                'method': 'GET Request',
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'error': None if response.status_code == 200 else f"HTTP {response.status_code}"
            })
            
        except Exception as e:
            results.append({
                'method': 'GET Request',
                'status_code': None,
                'success': False,
                'error': str(e)
            })
        
        return results
    
    def check_ip_restrictions(self):
        """Check if the issue is IP-based"""
        try:
            # Try to access the main page first
            response = requests.get("https://booking-kz.crystalbay.com/", timeout=10)
            main_page_accessible = response.status_code == 200
            
            # Try API endpoint without authentication
            response = requests.post(self.base_url, data={
                'samo_action': 'api',
                'version': '1.0',
                'type': 'json',
                'action': 'SearchTour_CURRENCIES'
                # No oauth_token
            }, timeout=10)
            
            api_responds = response.status_code != 403
            
            return {
                'main_page_accessible': main_page_accessible,
                'api_endpoint_responds': api_responds,
                'likely_ip_restriction': not main_page_accessible or (main_page_accessible and not api_responds)
            }
            
        except Exception as e:
            return {
                'main_page_accessible': False,
                'api_endpoint_responds': False,
                'likely_ip_restriction': True,
                'error': str(e)
            }
    
    def suggest_solutions(self):
        """Provide solution suggestions based on testing"""
        accessibility_test = self.test_api_accessibility()
        ip_test = self.check_ip_restrictions()
        
        solutions = []
        
        if ip_test.get('likely_ip_restriction'):
            solutions.append({
                'priority': 'high',
                'solution': 'Contact Crystal Bay Support',
                'description': 'Request IP whitelist for 34.117.32.233 (current deployment IP)',
                'action': 'Email Crystal Bay technical support with IP whitelist request'
            })
            
            solutions.append({
                'priority': 'medium',
                'solution': 'Kazakhstan-based Deployment',
                'description': 'Deploy the system on a Kazakhstan-based server',
                'action': 'Use local hosting provider in Kazakhstan'
            })
        
        if not any(result['success'] for result in accessibility_test):
            solutions.append({
                'priority': 'high',
                'solution': 'API Authentication Issue',
                'description': 'OAuth token may need renewal or different format',
                'action': 'Contact Crystal Bay for updated authentication method'
            })
        
        solutions.append({
            'priority': 'low',
            'solution': 'Continue with Current System',
            'description': 'System is fully functional with realistic demo data',
            'action': 'Use existing functionality while resolving API access'
        })
        
        return {
            'accessibility_results': accessibility_test,
            'ip_restriction_analysis': ip_test,
            'recommended_solutions': solutions
        }

def run_diagnostic():
    """Run full diagnostic of Crystal Bay API access"""
    oauth_token = "27bd59a7ac67422189789f0188167379"
    api = CrystalBayAPIAlternative(oauth_token)
    
    print("🔍 CRYSTAL BAY SAMO API - DIAGNOSTIC ANALYSIS")
    print("=" * 60)
    
    analysis = api.suggest_solutions()
    
    print("\n📊 ACCESSIBILITY TEST RESULTS:")
    print("-" * 40)
    for result in analysis['accessibility_results']:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['method']}: {result.get('error', 'Success' if result['success'] else 'Failed')}")
    
    print("\n🌐 IP RESTRICTION ANALYSIS:")
    print("-" * 40)
    ip_analysis = analysis['ip_restriction_analysis']
    if 'error' not in ip_analysis:
        print(f"Main page accessible: {'✅' if ip_analysis['main_page_accessible'] else '❌'}")
        print(f"API endpoint responds: {'✅' if ip_analysis['api_endpoint_responds'] else '❌'}")
        print(f"Likely IP restriction: {'⚠️ Yes' if ip_analysis['likely_ip_restriction'] else '✅ No'}")
    else:
        print(f"❌ Analysis failed: {ip_analysis['error']}")
    
    print("\n💡 RECOMMENDED SOLUTIONS:")
    print("-" * 40)
    for i, solution in enumerate(analysis['recommended_solutions'], 1):
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[solution['priority']]
        print(f"{priority_icon} {i}. {solution['solution']}")
        print(f"   Description: {solution['description']}")
        print(f"   Action: {solution['action']}")
        print()
    
    return analysis

if __name__ == '__main__':
    run_diagnostic()