#!/usr/bin/env python3
"""
SAMO API Connectivity Test - Production Environment
Tests SAMO API connectivity with whitelisted IP 34.117.33.233
"""

import json
import requests
from datetime import datetime

def test_samo_connectivity():
    """Test SAMO API connectivity with whitelisted production IP"""
    
    print("🌐 SAMO API CONNECTIVITY TEST - PRODUCTION ENVIRONMENT")
    print("=" * 60)
    print(f"Deployment IP: 34.117.33.233 (whitelisted)")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    base_url = "https://booking-kz.crystalbay.com/export/default.php"
    oauth_token = "27bd59a7ac67422189789f0188167379"
    
    # Test endpoints in order of importance
    test_endpoints = [
        ('SearchTour_CURRENCIES', 'Currency data retrieval'),
        ('SearchTour_TOWNFROMS', 'Departure cities'),
        ('SearchTour_STATES', 'Available countries/destinations'),
        ('SearchTour_HOTELS', 'Hotel inventory'),
        ('SearchTour_TOURS', 'Tour packages'),
        ('SearchTour_PRICES', 'Tour pricing search')
    ]
    
    results = {}
    successful_connections = 0
    
    for action, description in test_endpoints:
        print(f"\n📡 Testing: {description} ({action})")
        
        try:
            data = {
                'samo_action': 'api',
                'version': '1.0',
                'type': 'json',
                'action': action,
                'oauth_token': oauth_token
            }
            
            headers = {
                'User-Agent': 'Crystal Bay Travel Integration/1.0',
                'Accept': 'application/json, text/xml, */*',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post(base_url, data=data, headers=headers, timeout=20)
            
            print(f"   Status: {response.status_code}")
            print(f"   Response size: {len(response.text)} chars")
            
            if response.status_code == 200:
                print("   ✅ Connection: Successful")
                successful_connections += 1
                
                # Try to parse JSON response
                try:
                    json_data = response.json()
                    if isinstance(json_data, dict):
                        if 'error' in json_data:
                            print(f"   ⚠️ API Error: {json_data.get('error', 'Unknown error')}")
                            results[action] = {'status': 'error', 'message': json_data.get('error')}
                        else:
                            print(f"   🎯 Data: Available")
                            # Count data items if it's a list or dict with items
                            data_count = 0
                            if isinstance(json_data, list):
                                data_count = len(json_data)
                            elif isinstance(json_data, dict) and 'data' in json_data:
                                data_count = len(json_data['data']) if isinstance(json_data['data'], list) else 1
                            
                            print(f"   📊 Records: {data_count}")
                            results[action] = {'status': 'success', 'data_count': data_count, 'response': json_data}
                    else:
                        print(f"   📄 Response type: {type(json_data)}")
                        results[action] = {'status': 'success', 'response_type': str(type(json_data))}
                        
                except json.JSONDecodeError:
                    # Might be XML or other format
                    if response.text.startswith('<?xml'):
                        print("   📄 Format: XML response")
                        results[action] = {'status': 'success', 'format': 'xml'}
                    else:
                        print(f"   📄 Format: {response.text[:50]}...")
                        results[action] = {'status': 'success', 'format': 'text'}
                        
            elif response.status_code == 403:
                print("   🔒 Connection: IP not whitelisted")
                if "blacklisted address" in response.text:
                    import re
                    ip_match = re.search(r'blacklisted address (\d+\.\d+\.\d+\.\d+)', response.text)
                    if ip_match:
                        current_ip = ip_match.group(1)
                        print(f"   📍 Current IP detected: {current_ip}")
                results[action] = {'status': 'blocked', 'current_ip': current_ip if 'ip_match' in locals() else None}
                
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   📄 Response: {response.text[:100]}...")
                results[action] = {'status': 'http_error', 'code': response.status_code}
                
        except Exception as e:
            print(f"   ❌ Connection Error: {str(e)}")
            results[action] = {'status': 'connection_error', 'error': str(e)}
    
    # Generate connectivity report
    print(f"\n🎯 CONNECTIVITY SUMMARY")
    print("=" * 30)
    print(f"Successful connections: {successful_connections}/{len(test_endpoints)}")
    
    if successful_connections == len(test_endpoints):
        print("✅ SAMO API: Fully operational")
        print("   All endpoints accessible")
        print("   Real-time data retrieval ready")
        connectivity_status = "operational"
    elif successful_connections > 0:
        print("⚠️ SAMO API: Partially accessible")
        print(f"   {successful_connections} endpoints working")
        print("   Some features may be limited")
        connectivity_status = "partial"
    else:
        print("❌ SAMO API: Not accessible")
        print("   IP whitelisting may be incomplete")
        print("   Contact Crystal Bay support")
        connectivity_status = "blocked"
    
    return {
        'connectivity_status': connectivity_status,
        'successful_connections': successful_connections,
        'total_endpoints': len(test_endpoints),
        'test_results': results,
        'test_timestamp': datetime.now().isoformat()
    }

if __name__ == '__main__':
    results = test_samo_connectivity()
    
    # Save results for integration into settings
    with open('data/samo_connectivity_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📋 Results saved for settings integration")
    print(f"Status: {results['connectivity_status']}")