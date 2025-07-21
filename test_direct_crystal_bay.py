#!/usr/bin/env python3
"""
Direct Crystal Bay SAMO API Testing
Test different authentication methods and request formats
"""

import requests
import json
import time
from urllib.parse import urlencode

def test_authentication_methods():
    """Test different ways to authenticate with Crystal Bay SAMO API"""
    
    base_url = "https://booking-kz.crystalbay.com/export/default.php"
    oauth_token = "27bd59a7ac67422189789f0188167379"
    
    print("🔍 TESTING CRYSTAL BAY SAMO API AUTHENTICATION METHODS")
    print("=" * 60)
    
    # Method 1: POST with form data (current approach)
    print("\n1. POST with application/x-www-form-urlencoded")
    try:
        data = {
            'samo_action': 'api',
            'version': '1.0', 
            'type': 'json',
            'action': 'SearchTour_CURRENCIES',
            'oauth_token': oauth_token
        }
        
        response = requests.post(base_url, data=data, timeout=15)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        if response.text:
            print(f"   Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Method 2: GET with query parameters
    print("\n2. GET with query parameters")
    try:
        params = {
            'samo_action': 'api',
            'version': '1.0',
            'type': 'json', 
            'action': 'SearchTour_CURRENCIES',
            'oauth_token': oauth_token
        }
        
        response = requests.get(base_url, params=params, timeout=15)
        print(f"   Status: {response.status_code}")
        if response.text:
            print(f"   Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Method 3: POST with JSON payload
    print("\n3. POST with JSON payload")
    try:
        json_data = {
            'samo_action': 'api',
            'version': '1.0',
            'type': 'json',
            'action': 'SearchTour_CURRENCIES',
            'oauth_token': oauth_token
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(base_url, json=json_data, headers=headers, timeout=15)
        print(f"   Status: {response.status_code}")
        if response.text:
            print(f"   Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Method 4: Different token format
    print("\n4. Alternative token format")
    try:
        data = {
            'action': 'SearchTour_CURRENCIES',
            'token': oauth_token,  # Different parameter name
            'format': 'json'
        }
        
        response = requests.post(base_url, data=data, timeout=15)
        print(f"   Status: {response.status_code}")
        if response.text:
            print(f"   Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Method 5: With session and proper headers
    print("\n5. With browser-like session")
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://booking-kz.crystalbay.com/',
            'Origin': 'https://booking-kz.crystalbay.com'
        })
        
        data = {
            'samo_action': 'api',
            'version': '1.0',
            'type': 'json',
            'action': 'SearchTour_CURRENCIES',
            'oauth_token': oauth_token
        }
        
        response = session.post(base_url, data=data, timeout=15)
        print(f"   Status: {response.status_code}")
        if response.text:
            print(f"   Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Method 6: Test without API action first
    print("\n6. Test basic endpoint accessibility")
    try:
        response = requests.get("https://booking-kz.crystalbay.com/", timeout=10)
        print(f"   Main site status: {response.status_code}")
        
        response = requests.post(base_url, data={'test': 'ping'}, timeout=10)
        print(f"   API endpoint basic test: {response.status_code}")
        
    except Exception as e:
        print(f"   Error: {e}")

def test_different_actions():
    """Test different SAMO API actions"""
    
    base_url = "https://booking-kz.crystalbay.com/export/default.php"
    oauth_token = "27bd59a7ac67422189789f0188167379"
    
    print("\n🎯 TESTING DIFFERENT SAMO API ACTIONS")
    print("=" * 45)
    
    actions = [
        'SearchTour_CURRENCIES',
        'SearchTour_TOWNFROMS', 
        'SearchTour_HOTELS',
        'SearchTour_PRICES',
        'GetTourInfo'
    ]
    
    for action in actions:
        print(f"\n📍 Testing action: {action}")
        try:
            data = {
                'samo_action': 'api',
                'version': '1.0',
                'type': 'json',
                'action': action,
                'oauth_token': oauth_token
            }
            
            response = requests.post(base_url, data=data, timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code != 403:
                print(f"   Response length: {len(response.text)} chars")
                if response.text and len(response.text) < 500:
                    print(f"   Content: {response.text}")
            
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == '__main__':
    test_authentication_methods()
    test_different_actions()
    
    print("\n🏁 CONCLUSION")
    print("=" * 30)
    print("If IP is whitelisted but still getting 403, possible issues:")
    print("1. OAuth token expired or invalid")
    print("2. Wrong API endpoint or parameters")
    print("3. Server-side API changes")
    print("4. Rate limiting or request format issues")
    print("\nRecommend contacting Crystal Bay for:")
    print("- Current API documentation")
    print("- Token validation")
    print("- Correct request format")