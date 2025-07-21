#!/usr/bin/env python3
"""
Production Ready Demo - Crystal Bay System
Tests system with production IP configuration
"""

import json
import os
import requests
from datetime import datetime

def test_production_configuration():
    """Test production configuration with correct IP settings"""
    
    print("🚀 CRYSTAL BAY TRAVEL - PRODUCTION IP CONFIGURATION")
    print("=" * 55)
    
    # System Configuration
    SYSTEM_IP = "34.117.33.233"
    SAMO_URL = "https://booking-kz.crystalbay.com/export/default.php"
    OAUTH_TOKEN = "27bd59a7ac67422189789f0188167379"
    
    print(f"\n📍 SYSTEM CONFIGURATION")
    print(f"   System IP: {SYSTEM_IP}")
    print(f"   SAMO API: {SAMO_URL}")
    print(f"   OAuth Token: {OAUTH_TOKEN}")
    
    # Test data persistence
    print(f"\n📊 DATA PERSISTENCE STATUS")
    storage_file = 'data/memory_leads.json'
    
    if os.path.exists(storage_file):
        with open(storage_file, 'r', encoding='utf-8') as f:
            leads = json.load(f)
        
        print(f"   Leads loaded: {len(leads)}")
        
        if leads:
            sample_lead = leads[0]
            print(f"   Sample customer: {sample_lead.get('customer_name', 'Unknown')}")
            print(f"   Sample destination: {sample_lead.get('destination', 'Unknown')}")
    else:
        print(f"   No data file found")
    
    # Test SAMO API with production headers
    print(f"\n🔗 SAMO API CONNECTION TEST")
    
    try:
        data = {
            'samo_action': 'api',
            'version': '1.0',
            'type': 'json',
            'action': 'SearchTour_CURRENCIES',
            'oauth_token': OAUTH_TOKEN
        }
        
        headers = {
            'User-Agent': 'Crystal Bay Travel Integration/1.0',
            'Accept': 'application/json, text/xml, */*',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(SAMO_URL, data=data, headers=headers, timeout=15)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Length: {len(response.text)} chars")
        
        if response.status_code == 200:
            print(f"   ✅ SAMO API: Connection successful")
            try:
                json_data = response.json()
                print(f"   📊 Valid JSON response received")
            except:
                print(f"   📄 Response format: {response.text[:100]}...")
        
        elif response.status_code == 403:
            print(f"   🔒 SAMO API: IP whitelist required")
            if "blacklisted address" in response.text:
                import re
                ip_match = re.search(r'blacklisted address (\d+\.\d+\.\d+\.\d+)', response.text)
                if ip_match:
                    detected_ip = ip_match.group(1)
                    print(f"   Current IP detected: {detected_ip}")
            print(f"   📧 Request Crystal Bay to whitelist: {SYSTEM_IP}")
        
        else:
            print(f"   ⚠️ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Contact information for Crystal Bay
    print(f"\n📧 CRYSTAL BAY CONTACT REQUEST")
    print(f"=" * 35)
    print(f"Subject: SAMO API IP Whitelist Request")
    print(f"")
    print(f"Dear Crystal Bay Technical Support,")
    print(f"")
    print(f"Please whitelist the following IP for SAMO API access:")
    print(f"IP Address: {SYSTEM_IP}")
    print(f"OAuth Token: {OAUTH_TOKEN}")
    print(f"API Endpoint: {SAMO_URL}")
    print(f"")
    print(f"System: Crystal Bay Travel Integration")
    print(f"Purpose: Tour booking and inventory management")
    print(f"")
    print(f"Thank you,")
    print(f"Crystal Bay Travel Team")
    
    return {
        'system_ip': SYSTEM_IP,
        'samo_url': SAMO_URL,
        'oauth_token': OAUTH_TOKEN,
        'leads_count': len(leads) if 'leads' in locals() else 0
    }

if __name__ == '__main__':
    results = test_production_configuration()
    print(f"\n✅ CONFIGURATION COMPLETE")
    print(f"System configured with IP {results['system_ip']} for production deployment")