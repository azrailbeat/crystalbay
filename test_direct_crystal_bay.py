#!/usr/bin/env python3
"""
Direct test of Crystal Bay SAMO API with confirmed OAuth token
"""

import requests
import json

def test_crystal_bay_direct():
    """Test direct connection to Crystal Bay SAMO API"""
    
    base_url = "https://booking-kz.crystalbay.com/export/default.php"
    oauth_token = "27bd59a7ac67422189789f0188167379"
    
    # Test different endpoint variations
    test_cases = [
        {
            "name": "SearchTour_TOWNFROMS (Basic)",
            "params": {
                "samo_action": "api",
                "version": "1.0", 
                "type": "json",
                "action": "SearchTour_TOWNFROMS",
                "oauth_token": oauth_token
            }
        },
        {
            "name": "SearchTour_STATES (Countries)",
            "params": {
                "samo_action": "api",
                "version": "1.0",
                "type": "json", 
                "action": "SearchTour_STATES",
                "oauth_token": oauth_token
            }
        },
        {
            "name": "Without version parameter",
            "params": {
                "samo_action": "api",
                "type": "json",
                "action": "SearchTour_TOWNFROMS", 
                "oauth_token": oauth_token
            }
        }
    ]
    
    for test in test_cases:
        print(f"\n=== Testing: {test['name']} ===")
        
        try:
            response = requests.get(base_url, params=test['params'], timeout=15)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"SUCCESS! Data keys: {list(data.keys()) if isinstance(data, dict) else 'Array response'}")
                except:
                    print(f"Response is not JSON: {response.text[:200]}...")
                    
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_crystal_bay_direct()