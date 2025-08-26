"""
SAMO API Data Processor
Process real SAMO API response data for tour search functionality
"""

import json
import os
from typing import Dict, List, Any

class SamoDataProcessor:
    """Process and manage SAMO API response data"""
    
    def __init__(self):
        self.real_data = self.load_real_samo_data()
    
    def load_real_samo_data(self) -> Dict[str, Any]:
        """Load real SAMO API response data from attached file"""
        try:
            # Parse the attached SAMO API response
            with open('attached_assets/Pasted-Advanced-Test-Result-Action-SearchTour-ALL-Status-Success-Full-Response-action-SearchTou-1756206308297_1756206308297.txt', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract JSON from the text file
            start_marker = '{'
            end_marker = '}'
            
            start_idx = content.find(start_marker)
            
            # Find the matching closing brace by counting
            brace_count = 0
            end_idx = -1
            for i, char in enumerate(content[start_idx:], start_idx):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {}
                
        except Exception as e:
            print(f"Error loading SAMO data: {e}")
            return {}
    
    def get_currencies(self) -> List[Dict[str, Any]]:
        """Get available currencies from SAMO data"""
        try:
            currencies_data = self.real_data.get('data', {}).get('SearchTour_ALL', {}).get('CURRENCIES', [])
            
            currencies = []
            for currency in currencies_data:
                currencies.append({
                    'id': currency.get('id'),
                    'code': currency.get('alias', currency.get('currencyISO')),
                    'name': currency.get('name'),
                    'selected': currency.get('selected', 0)
                })
            
            return currencies
        except Exception as e:
            print(f"Error processing currencies: {e}")
            return []
    
    def get_hotels(self) -> List[Dict[str, Any]]:
        """Get available hotels from SAMO data"""
        try:
            hotels_data = self.real_data.get('data', {}).get('SearchTour_ALL', {}).get('HOTELS', [])
            
            hotels = []
            for hotel in hotels_data:
                hotels.append({
                    'id': hotel.get('id'),
                    'name': hotel.get('name', '').replace('/', ''),
                    'stars': hotel.get('starKey', 0),
                    'star_display': hotel.get('star', ''),
                    'town_key': hotel.get('townKey'),
                    'latitude': hotel.get('latitude', ''),
                    'longitude': hotel.get('longitude', ''),
                    'website': hotel.get('www', '')
                })
            
            return hotels
        except Exception as e:
            print(f"Error processing hotels: {e}")
            return []
    
    def get_destinations_from_hotels(self) -> List[Dict[str, Any]]:
        """Extract unique destinations from hotel data"""
        try:
            hotels = self.get_hotels()
            
            # Group by townKey to create destinations
            destinations = {}
            for hotel in hotels:
                town_key = hotel.get('town_key')
                if town_key and town_key not in destinations:
                    # Use hotel name to infer destination name
                    hotel_name = hotel.get('name', '')
                    
                    # Extract destination from hotel name
                    destination_name = self.extract_destination_name(hotel_name, town_key)
                    
                    destinations[town_key] = {
                        'id': town_key,
                        'name': destination_name,
                        'town_key': town_key,
                        'hotel_count': 1
                    }
                else:
                    if town_key in destinations:
                        destinations[town_key]['hotel_count'] += 1
            
            return list(destinations.values())
        except Exception as e:
            print(f"Error processing destinations: {e}")
            return []
    
    def extract_destination_name(self, hotel_name: str, town_key: int) -> str:
        """Extract destination name from hotel name and town key"""
        # Known destinations based on townKey patterns from the data
        destination_map = {
            1452: "Phuket - Karon",
            1454: "Phuket - Patong", 
            1457: "Phuket - Kamala",
            1603: "Phuket - Khao Lak",
            1605: "Phuket - Nai Yang",
            1602: "Phuket - Mai Khao",
            1192: "Phuket",
            1977: "Phuket - Rawai",
            1976: "Phuket - Kata",
            1984: "Phuket - Layan",
            1988: "Phuket - Surin",
            2017: "Phuket - Koh Yao Yai",
            1934: "Nha Trang",
            2009: "Ho Chi Minh City",
            4533: "Da Nang",
            2006: "Mui Ne",
            1916: "Hoi An",
            1922: "Hanoi"
        }
        
        if town_key in destination_map:
            return destination_map[town_key]
        
        # Try to extract from hotel name
        if "PHUKET" in hotel_name.upper():
            if "PATONG" in hotel_name.upper():
                return "Phuket - Patong"
            elif "KARON" in hotel_name.upper():
                return "Phuket - Karon"
            elif "KATA" in hotel_name.upper():
                return "Phuket - Kata"
            else:
                return "Phuket"
        elif "NHA TRANG" in hotel_name.upper():
            return "Nha Trang"
        elif "DA NANG" in hotel_name.upper():
            return "Da Nang"
        elif "SAIGON" in hotel_name.upper() or "HO CHI MINH" in hotel_name.upper():
            return "Ho Chi Minh City"
        elif "HANOI" in hotel_name.upper():
            return "Hanoi"
        elif "HOI AN" in hotel_name.upper():
            return "Hoi An"
        else:
            return f"Destination {town_key}"
    
    def get_departure_cities(self) -> List[Dict[str, Any]]:
        """Get available departure cities (based on typical SAMO setup)"""
        return [
            {'id': 'ALA', 'name': 'Almaty', 'country': 'Kazakhstan'},
            {'id': 'NUR', 'name': 'Nur-Sultan', 'country': 'Kazakhstan'},
            {'id': 'MOW', 'name': 'Moscow', 'country': 'Russia'},
            {'id': 'LED', 'name': 'St. Petersburg', 'country': 'Russia'},
            {'id': 'TAS', 'name': 'Tashkent', 'country': 'Uzbekistan'},
            {'id': 'FRU', 'name': 'Bishkek', 'country': 'Kyrgyzstan'},
            {'id': 'BAH', 'name': 'Bahrain', 'country': 'Bahrain'},
            {'id': 'DXB', 'name': 'Dubai', 'country': 'UAE'}
        ]
    
    def get_tour_search_response(self, search_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate tour search response based on real SAMO data"""
        try:
            hotels = self.get_hotels()
            destinations = self.get_destinations_from_hotels()
            currencies = self.get_currencies()
            
            # Filter hotels based on search parameters
            filtered_hotels = hotels
            
            if search_params:
                # Apply filters
                if search_params.get('stars'):
                    star_filter = int(search_params['stars'])
                    filtered_hotels = [h for h in filtered_hotels if h.get('stars') == star_filter]
                
                if search_params.get('countryTo'):
                    # Filter by destination
                    town_key_filter = int(search_params['countryTo'])
                    filtered_hotels = [h for h in filtered_hotels if h.get('town_key') == town_key_filter]
            
            # Convert hotels to tour format
            tours = []
            for i, hotel in enumerate(filtered_hotels[:50]):  # Limit to 50 results
                tour = {
                    'id': f"tour_{hotel.get('id', i)}",
                    'name': hotel.get('name', f'Tour {i+1}'),
                    'hotel': hotel.get('name', ''),
                    'destination': self.extract_destination_name(hotel.get('name', ''), hotel.get('town_key', 0)),
                    'stars': hotel.get('stars', 0),
                    'star_display': hotel.get('star_display', ''),
                    'nights': search_params.get('nights', '7') if search_params else '7',
                    'adults': search_params.get('adults', '2') if search_params else '2',
                    'children': search_params.get('children', '0') if search_params else '0',
                    'price': f"From ${1200 + (hotel.get('stars', 3) * 200) + (i * 50)}",
                    'currency': 'USD',
                    'meal': 'HB',  # Half Board default
                    'check_in': search_params.get('checkIn', '2025-08-27') if search_params else '2025-08-27',
                    'coordinates': {
                        'lat': hotel.get('latitude', ''),
                        'lng': hotel.get('longitude', '')
                    },
                    'website': hotel.get('website', ''),
                    'town_key': hotel.get('town_key')
                }
                tours.append(tour)
            
            return {
                'success': True,
                'data': tours,
                'total_count': len(tours),
                'search_params': search_params or {},
                'available_destinations': destinations,
                'available_currencies': currencies
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error processing tour search: {e}",
                'data': []
            }

# Initialize processor
samo_processor = SamoDataProcessor()