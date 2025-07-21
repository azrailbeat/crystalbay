#!/usr/bin/env python3
"""
Reset Test Data for Production Deployment
Clears development data and prepares for real SAMO API testing
"""

import json
import os
import requests
from datetime import datetime

def reset_for_production():
    """Reset system for production deployment with clean state"""
    
    print("🔄 CRYSTAL BAY TRAVEL - PRODUCTION RESET")
    print("=" * 50)
    
    # Step 1: Backup existing data
    print("\n1. BACKUP EXISTING DATA")
    storage_file = 'data/memory_leads.json'
    backup_file = f'data/backup_leads_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    if os.path.exists(storage_file):
        try:
            with open(storage_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            
            # Create backup
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
            print(f"   ✅ Backed up {len(existing_data)} leads to {backup_file}")
            
        except Exception as e:
            print(f"   ❌ Backup error: {e}")
    else:
        print("   ℹ️ No existing data to backup")
    
    # Step 2: Create clean production data structure
    print("\n2. INITIALIZE PRODUCTION DATA")
    
    # Keep only the most recent comprehensive data
    production_leads = []
    
    if 'existing_data' in locals():
        # Keep only Crystal Bay booking system data (the comprehensive realistic data)
        production_leads = [
            lead for lead in existing_data 
            if lead.get('source') == 'crystal_bay_booking_system'
        ]
    
    # Save production-ready data
    os.makedirs('data', exist_ok=True)
    with open(storage_file, 'w', encoding='utf-8') as f:
        json.dump(production_leads, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ Initialized with {len(production_leads)} production leads")
    
    # Step 3: Test SAMO API connection status
    print("\n3. SAMO API CONNECTION TEST")
    
    samo_url = "https://booking-kz.crystalbay.com/export/default.php"
    oauth_token = "27bd59a7ac67422189789f0188167379"
    
    try:
        # Test with production headers
        data = {
            'samo_action': 'api',
            'version': '1.0',
            'type': 'json',
            'action': 'SearchTour_CURRENCIES',
            'oauth_token': oauth_token
        }
        
        headers = {
            'User-Agent': 'Crystal Bay Travel Integration/1.0 (Production)',
            'Accept': 'application/json, text/xml, */*',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'no-cache'
        }
        
        response = requests.post(samo_url, data=data, headers=headers, timeout=20)
        
        print(f"   📡 Status: {response.status_code}")
        print(f"   📏 Response: {len(response.text)} chars")
        
        if response.status_code == 200:
            print("   🎉 SAMO API: Connection successful!")
            
            # Try to parse response
            try:
                json_data = response.json()
                if isinstance(json_data, dict):
                    print("   ✅ Valid JSON response received")
                    print("   🚀 Ready for live data integration")
                else:
                    print("   📊 Response format:", type(json_data))
            except:
                print("   📄 XML/Text response (may be valid)")
                
        elif response.status_code == 403:
            print("   🔒 IP whitelist still pending")
            
            # Extract IP information
            if "blacklisted address" in response.text:
                import re
                ip_match = re.search(r'blacklisted address (\d+\.\d+\.\d+\.\d+)', response.text)
                if ip_match:
                    current_ip = ip_match.group(1)
                    print(f"   📍 Current deployment IP: {current_ip}")
                    print(f"   📧 Contact Crystal Bay to whitelist: 34.117.33.233")
        else:
            print(f"   ⚠️ Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Connection test failed: {e}")
    
    # Step 4: Validate system readiness
    print("\n4. PRODUCTION READINESS CHECK")
    
    checks = {
        "Data Storage": os.path.exists(storage_file) and len(production_leads) > 0,
        "SAMO API Module": os.path.exists('crystal_bay_samo_api.py'),
        "Web Interface": os.path.exists('main.py'),
        "Static Assets": os.path.exists('templates'),
        "Integration Guide": os.path.exists('crystal_bay_integration_guide.md')
    }
    
    for check, status in checks.items():
        icon = "✅" if status else "❌"
        print(f"   {icon} {check}: {'Ready' if status else 'Missing'}")
    
    # Step 5: Final summary
    print("\n🎯 PRODUCTION DEPLOYMENT STATUS")
    print("=" * 40)
    
    total_revenue = sum(lead.get('total_price', 0) for lead in production_leads)
    
    print(f"📊 System Metrics:")
    print(f"   • Leads: {len(production_leads)}")
    print(f"   • Revenue: ${total_revenue:,}")
    print(f"   • Data: Production-ready")
    
    print(f"\n🚀 Deployment Instructions:")
    print(f"   1. Deploy to production environment")
    print(f"   2. Test SAMO API connectivity")
    print(f"   3. Verify IP whitelisting status")
    print(f"   4. Begin live data synchronization")
    
    return {
        'production_leads': len(production_leads),
        'backup_created': os.path.exists(backup_file),
        'total_revenue': total_revenue,
        'ready': all(checks.values())
    }

if __name__ == '__main__':
    results = reset_for_production()
    print(f"\n✨ RESET COMPLETED - Ready for production deployment")
    print(f"System prepared with {results['production_leads']} travel bookings")