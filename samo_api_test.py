#!/usr/bin/env python3
"""
SAMO API Test Suite based on Trello documentation
Testing Anex Tour Partner API endpoints with proper authentication
"""

import os
import requests
import json
from datetime import datetime, timedelta
from api_integration import APIIntegration

class SAMOAPITester:
    """Test SAMO API endpoints using curl-equivalent requests"""
    
    def __init__(self):
        self.api = APIIntegration()
        self.base_url = "https://b2b.anextour.com/api/v1/partner"
        self.oauth_token = os.getenv('SAMO_OAUTH_TOKEN')
        
    def test_search_tour_prices(self):
        """
        Test SearchTour/PRICES endpoint as documented in Trello
        Equivalent curl command:
        
        curl -X GET "https://b2b.anextour.com/api/v1/partner/samo/SearchTour/PRICES" \
        -H "Authorization: Bearer $SAMO_OAUTH_TOKEN" \
        -G \
        -d "samo_action=api" \
        -d "type=json" \
        -d "action=SearchTour" \
        -d "oauth_token=$SAMO_OAUTH_TOKEN" \
        -d "TOWNFROMINC=1" \
        -d "STATEINC=12" \
        -d "CHECKIN_BEG=20250615" \
        -d "CHECKIN_END=20250625" \
        -d "NIGHTS_FROM=7" \
        -d "NIGHTS_TILL=14" \
        -d "ADULT=2" \
        -d "CHILD=0" \
        -d "CURRENCY=RUB" \
        -d "FILTER=1"
        """
        
        url = f"{self.base_url}/samo/SearchTour/PRICES"
        
        params = {
            'samo_action': 'api',
            'type': 'json',
            'action': 'SearchTour',
            'oauth_token': self.oauth_token,
            'TOWNFROMINC': '1',  # Moscow departure
            'STATEINC': '12',    # Turkey destination
            'CHECKIN_BEG': '20250615',
            'CHECKIN_END': '20250625', 
            'NIGHTS_FROM': '7',
            'NIGHTS_TILL': '14',
            'ADULT': '2',
            'CHILD': '0',
            'CURRENCY': 'RUB',
            'FILTER': '1'
        }
        
        headers = {
            'Authorization': f'Bearer {self.oauth_token}',
            'Accept': 'application/json',
            'User-Agent': 'Crystal Bay Travel Bot/1.0'
        }
        
        print(f"Testing SAMO API SearchTour endpoint...")
        print(f"URL: {url}")
        print(f"Parameters: {json.dumps(params, indent=2)}")
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Success! Found {len(data.get('tours', []))} tours")
                return {"status": "success", "data": data}
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return {"status": "error", "code": response.status_code, "message": response.text}
                
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def test_get_tour_details(self, tour_id):
        """
        Test GetTourDetails endpoint
        Equivalent curl:
        
        curl -X GET "https://b2b.anextour.com/api/v1/partner/samo/GetTourDetails" \
        -H "Authorization: Bearer $SAMO_OAUTH_TOKEN" \
        -G \
        -d "samo_action=api" \
        -d "type=json" \
        -d "action=GetTourDetails" \
        -d "oauth_token=$SAMO_OAUTH_TOKEN" \
        -d "tour_id=$TOUR_ID"
        """
        
        url = f"{self.base_url}/samo/GetTourDetails"
        
        params = {
            'samo_action': 'api',
            'type': 'json',
            'action': 'GetTourDetails',
            'oauth_token': self.oauth_token,
            'tour_id': tour_id
        }
        
        headers = {
            'Authorization': f'Bearer {self.oauth_token}',
            'Accept': 'application/json'
        }
        
        print(f"Getting tour details for ID: {tour_id}")
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"Tour details retrieved successfully")
                return {"status": "success", "data": data}
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return {"status": "error", "code": response.status_code, "message": response.text}
                
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def test_create_booking(self, booking_data):
        """
        Test CreateBooking endpoint
        Equivalent curl:
        
        curl -X POST "https://b2b.anextour.com/api/v1/partner/samo/CreateBooking" \
        -H "Authorization: Bearer $SAMO_OAUTH_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "samo_action": "api",
            "type": "json", 
            "action": "CreateBooking",
            "oauth_token": "$SAMO_OAUTH_TOKEN",
            "tour_id": "12345",
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "customer_phone": "+7-XXX-XXX-XXXX"
        }'
        """
        
        url = f"{self.base_url}/samo/CreateBooking"
        
        payload = {
            'samo_action': 'api',
            'type': 'json',
            'action': 'CreateBooking',
            'oauth_token': self.oauth_token,
            **booking_data
        }
        
        headers = {
            'Authorization': f'Bearer {self.oauth_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        print(f"Creating booking with data: {json.dumps(booking_data, indent=2)}")
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 201:
                data = response.json()
                print(f"Booking created successfully: {data.get('booking_reference', 'N/A')}")
                return {"status": "success", "data": data}
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return {"status": "error", "code": response.status_code, "message": response.text}
                
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def run_full_test_suite(self):
        """Run comprehensive test suite"""
        print("="*50)
        print("SAMO API Test Suite - Crystal Bay Travel")
        print("="*50)
        
        if not self.oauth_token:
            print("⚠️  SAMO_OAUTH_TOKEN not configured - tests will use mock data")
            return
        
        # Test 1: Search for tours
        print("\n1. Testing SearchTour endpoint...")
        search_result = self.test_search_tour_prices()
        
        # Test 2: Get tour details (if search was successful)
        if search_result.get('status') == 'success' and search_result.get('data', {}).get('tours'):
            first_tour = search_result['data']['tours'][0]
            tour_id = first_tour.get('id')
            if tour_id:
                print(f"\n2. Testing GetTourDetails for tour {tour_id}...")
                self.test_get_tour_details(tour_id)
        
        # Test 3: Create booking (with test data)
        print("\n3. Testing CreateBooking endpoint...")
        test_booking = {
            'tour_id': 'TEST_TOUR_123',
            'customer_name': 'Тест Тестов',
            'customer_email': 'test@crystalbay.travel',
            'customer_phone': '+7-999-123-4567',
            'adults': 2,
            'children': 0,
            'departure_date': '2025-06-15'
        }
        self.test_create_booking(test_booking)
        
        print("\n" + "="*50)
        print("Test suite completed!")
        print("="*50)

def main():
    """Run SAMO API tests"""
    tester = SAMOAPITester()
    tester.run_full_test_suite()

if __name__ == "__main__":
    main()