import os
import json
import logging
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API credentials
SAMO_API_URL = "https://api.samo.ru/v2"
SAMO_OAUTH_TOKEN = os.environ.get("SAMO_OAUTH_TOKEN")

class APIIntegration:
    """
    Integration with external APIs for booking, flight, and amenity information.
    """
    
    def __init__(self):
        self.samo_token = SAMO_OAUTH_TOKEN
        logger.info("API Integration initialized")
        
    def check_booking(self, booking_reference):
        """
        Check booking details in the SAMO API.
        
        Args:
            booking_reference (str): The booking reference number
            
        Returns:
            dict: Booking information or None if not found
        """
        try:
            if not self.samo_token:
                logger.warning("SAMO OAuth token not available")
                return self._get_mock_booking(booking_reference)
                
            logger.info(f"Checking booking {booking_reference} in SAMO API")
            
            # The URL for getting a booking by reference
            url = f"{SAMO_API_URL}/bookings/{booking_reference}"
            
            # Make the API request
            response = self._make_samo_request(url)
            
            if response.status_code == 200:
                booking_data = response.json()
                logger.info(f"Successfully retrieved booking {booking_reference}")
                return self._format_booking_data(booking_data)
            elif response.status_code == 404:
                logger.warning(f"Booking {booking_reference} not found in SAMO API")
                return None
            else:
                logger.error(f"Error retrieving booking: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error checking booking: {str(e)}")
            return self._get_mock_booking(booking_reference)
    
    def search_bookings(self, customer_email=None, customer_phone=None, customer_name=None):
        """
        Search for bookings by customer information.
        
        Args:
            customer_email (str, optional): Customer's email address
            customer_phone (str, optional): Customer's phone number
            customer_name (str, optional): Customer's name
            
        Returns:
            list: List of booking information dictionaries
        """
        try:
            if not self.samo_token:
                logger.warning("SAMO OAuth token not available")
                return self._get_mock_bookings()
                
            # Build query parameters
            params = {}
            if customer_email:
                params['email'] = customer_email
            if customer_phone:
                params['phone'] = customer_phone
            if customer_name:
                params['name'] = customer_name
                
            if not params:
                logger.warning("No search criteria provided for bookings search")
                return []
                
            logger.info(f"Searching bookings with params: {params}")
            
            # The URL for searching bookings
            url = f"{SAMO_API_URL}/bookings/search"
            
            # Make the API request
            response = self._make_samo_request(url, params=params)
            
            if response.status_code == 200:
                bookings_data = response.json()
                logger.info(f"Successfully retrieved {len(bookings_data)} bookings")
                return [self._format_booking_data(booking) for booking in bookings_data]
            else:
                logger.error(f"Error searching bookings: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching bookings: {str(e)}")
            return self._get_mock_bookings()
    
    def check_flight(self, flight_number, flight_date):
        """
        Check flight status using a flight status API.
        
        Args:
            flight_number (str): The flight number
            flight_date (str): The flight date in YYYY-MM-DD format
            
        Returns:
            dict: Flight information or None if not found
        """
        try:
            logger.info(f"Checking flight {flight_number} on {flight_date}")
            
            # In a real implementation, this would use a flight status API
            # For demonstration purposes, we return mock data
            return self._get_mock_flight(flight_number, flight_date)
            
        except Exception as e:
            logger.error(f"Error checking flight: {str(e)}")
            return None
    
    def check_hotel_amenities(self, hotel_id, checkin_date=None):
        """
        Check hotel amenities and availability.
        
        Args:
            hotel_id (str): The hotel ID in the SAMO system
            checkin_date (str, optional): Check-in date in YYYY-MM-DD format
            
        Returns:
            dict: Hotel amenities information
        """
        try:
            if not self.samo_token:
                logger.warning("SAMO OAuth token not available")
                return self._get_mock_hotel_amenities(hotel_id)
                
            logger.info(f"Checking amenities for hotel {hotel_id}")
            
            # The URL for getting hotel amenities
            url = f"{SAMO_API_URL}/hotels/{hotel_id}/amenities"
            
            # Add check-in date to params if provided
            params = {}
            if checkin_date:
                params['checkin_date'] = checkin_date
            
            # Make the API request
            response = self._make_samo_request(url, params=params)
            
            if response.status_code == 200:
                amenities_data = response.json()
                logger.info(f"Successfully retrieved amenities for hotel {hotel_id}")
                return self._format_amenities_data(amenities_data)
            elif response.status_code == 404:
                logger.warning(f"Hotel {hotel_id} not found in SAMO API")
                return None
            else:
                logger.error(f"Error retrieving hotel amenities: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error checking hotel amenities: {str(e)}")
            return self._get_mock_hotel_amenities(hotel_id)
    
    def create_booking(self, booking_data):
        """
        Create a new booking in the SAMO system.
        
        Args:
            booking_data (dict): The booking data to create
            
        Returns:
            dict: Created booking information or error
        """
        try:
            if not self.samo_token:
                logger.warning("SAMO OAuth token not available")
                return {'error': 'SAMO API token not available'}
                
            logger.info("Creating new booking in SAMO API")
            
            # The URL for creating a booking
            url = f"{SAMO_API_URL}/bookings"
            
            # Make the API request
            response = self._make_samo_request(url, method='POST', data=booking_data)
            
            if response.status_code == 201:
                booking_data = response.json()
                logger.info(f"Successfully created booking {booking_data.get('reference')}")
                return self._format_booking_data(booking_data)
            else:
                error_msg = f"Error creating booking: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {'error': error_msg}
                
        except Exception as e:
            error_msg = f"Error creating booking: {str(e)}"
            logger.error(error_msg)
            return {'error': error_msg}
    
    def _make_samo_request(self, url, method='GET', params=None, data=None):
        """
        Make a request to the SAMO API with authentication.
        
        Args:
            url (str): The API endpoint URL
            method (str, optional): HTTP method (GET, POST, etc.)
            params (dict, optional): Query parameters
            data (dict, optional): Request data for POST/PUT
            
        Returns:
            Response: The API response
        """
        headers = {
            'Authorization': f'Bearer {self.samo_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if method.upper() == 'GET':
            return requests.get(url, headers=headers, params=params)
        elif method.upper() == 'POST':
            return requests.post(url, headers=headers, params=params, json=data)
        elif method.upper() == 'PUT':
            return requests.put(url, headers=headers, params=params, json=data)
        elif method.upper() == 'DELETE':
            return requests.delete(url, headers=headers, params=params)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
    
    def _format_booking_data(self, raw_data):
        """
        Format raw booking data from the SAMO API into a consistent structure.
        
        Args:
            raw_data (dict): Raw booking data from API
            
        Returns:
            dict: Formatted booking data
        """
        # Transform SAMO API response to our internal format
        # Adjust this based on the actual SAMO API response structure
        booking = {
            'reference': raw_data.get('reference') or raw_data.get('id'),
            'status': raw_data.get('status', 'unknown'),
            'customer_name': raw_data.get('customer', {}).get('name', ''),
            'customer_email': raw_data.get('customer', {}).get('email', ''),
            'customer_phone': raw_data.get('customer', {}).get('phone', ''),
            'departure_date': raw_data.get('departure_date'),
            'return_date': raw_data.get('return_date'),
            'destination': raw_data.get('destination', {}).get('name', ''),
            'hotel': raw_data.get('hotel', {}).get('name', ''),
            'amount_paid': raw_data.get('payment', {}).get('amount_paid', 0),
            'total_amount': raw_data.get('payment', {}).get('total_amount', 0),
            'created_at': raw_data.get('created_at'),
            'updated_at': raw_data.get('updated_at'),
        }
        
        # Calculate balance due
        if 'amount_paid' in booking and 'total_amount' in booking:
            booking['balance_due'] = booking['total_amount'] - booking['amount_paid']
        
        return booking
    
    def _format_amenities_data(self, raw_data):
        """
        Format raw amenities data from the SAMO API.
        
        Args:
            raw_data (dict): Raw amenities data from API
            
        Returns:
            dict: Formatted amenities data
        """
        # Transform SAMO API response to our internal format
        return {
            'hotel_id': raw_data.get('hotel_id'),
            'hotel_name': raw_data.get('hotel_name'),
            'categories': raw_data.get('categories', []),
            'amenities': raw_data.get('amenities', []),
            'is_available': raw_data.get('is_available', False),
            'notes': raw_data.get('notes', ''),
        }
    
    def _get_mock_booking(self, booking_reference):
        """
        Generate mock booking data for demonstration.
        
        Args:
            booking_reference (str): The booking reference
            
        Returns:
            dict: Mock booking data
        """
        # Only use this for development/demonstration purposes
        tomorrow = datetime.now() + timedelta(days=1)
        next_week = datetime.now() + timedelta(days=8)
        
        return {
            'reference': booking_reference,
            'status': 'confirmed',
            'customer_name': 'Иван Петров',
            'customer_email': 'ivan.petrov@example.com',
            'customer_phone': '+7 (900) 123-45-67',
            'departure_date': tomorrow.strftime('%Y-%m-%d'),
            'return_date': next_week.strftime('%Y-%m-%d'),
            'destination': 'Турция, Анталия',
            'hotel': 'Sea View Resort 5*',
            'amount_paid': 75000,
            'total_amount': 95000,
            'balance_due': 20000,
            'created_at': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'updated_at': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
        }
    
    def _get_mock_bookings(self):
        """
        Generate mock bookings list for demonstration.
        
        Returns:
            list: List of mock booking data
        """
        # Only use this for development/demonstration purposes
        bookings = [
            self._get_mock_booking('CB-12345'),
            self._get_mock_booking('CB-23456'),
            self._get_mock_booking('CB-34567')
        ]
        
        # Customize the mock bookings
        bookings[1]['status'] = 'pending'
        bookings[1]['customer_name'] = 'Мария Соколова'
        bookings[1]['destination'] = 'Египет, Хургада'
        
        bookings[2]['status'] = 'cancelled'
        bookings[2]['customer_name'] = 'Алексей Белов'
        bookings[2]['destination'] = 'Таиланд, Пхукет'
        
        return bookings
    
    def _get_mock_flight(self, flight_number, flight_date):
        """
        Generate mock flight data for demonstration.
        
        Args:
            flight_number (str): The flight number
            flight_date (str): The flight date
            
        Returns:
            dict: Mock flight data
        """
        # Only use this for development/demonstration purposes
        # In production, this would use a real flight status API
        
        status_options = ['scheduled', 'on-time', 'delayed', 'cancelled', 'landed']
        
        # Determine a predictable but seemingly random status based on the flight number
        status_index = sum(ord(c) for c in flight_number) % len(status_options)
        status = status_options[status_index]
        
        delay_minutes = 0
        if status == 'delayed':
            # Generate a delay between 30 minutes and 3 hours
            delay_minutes = ((sum(ord(c) for c in flight_number) % 7) + 1) * 30
        
        return {
            'flight_number': flight_number,
            'airline': self._get_airline_from_flight_number(flight_number),
            'departure_date': flight_date,
            'status': status,
            'departure_time': '10:30',
            'arrival_time': '13:45' if status != 'delayed' else f'{14 + (delay_minutes // 60)}:{45 + (delay_minutes % 60):02d}',
            'departure_airport': 'SVO',
            'arrival_airport': 'AYT',
            'terminal': 'D',
            'gate': 'G12',
            'delay_minutes': delay_minutes,
            'aircraft_type': 'Boeing 737-800',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'remarks': 'On time' if status == 'scheduled' or status == 'on-time' else 
                      f'Delayed by {delay_minutes} minutes' if status == 'delayed' else
                      'Cancelled' if status == 'cancelled' else
                      'Landed',
        }
    
    def _get_airline_from_flight_number(self, flight_number):
        """
        Get airline name based on flight number prefix.
        
        Args:
            flight_number (str): The flight number
            
        Returns:
            str: Airline name
        """
        prefix = flight_number.split(' ')[0] if ' ' in flight_number else flight_number[:2]
        
        airlines = {
            'SU': 'Аэрофлот',
            'S7': 'S7 Airlines',
            'U6': 'Уральские Авиалинии',
            'DP': 'Победа',
            'TK': 'Turkish Airlines',
            'EK': 'Emirates',
            'LH': 'Lufthansa',
            'BA': 'British Airways'
        }
        
        return airlines.get(prefix, 'Unknown Airline')
    
    def _get_mock_hotel_amenities(self, hotel_id):
        """
        Generate mock hotel amenities data for demonstration.
        
        Args:
            hotel_id (str): The hotel ID
            
        Returns:
            dict: Mock hotel amenities data
        """
        # Only use this for development/demonstration purposes
        return {
            'hotel_id': hotel_id,
            'hotel_name': 'Sea View Resort 5*',
            'categories': ['Pool', 'Spa', 'Dining', 'Activities', 'Services'],
            'amenities': [
                {'category': 'Pool', 'items': ['Outdoor pool', 'Indoor pool', 'Children\'s pool', 'Pool bar']},
                {'category': 'Spa', 'items': ['Massage', 'Sauna', 'Steam room', 'Beauty salon']},
                {'category': 'Dining', 'items': ['Main restaurant', 'A la carte restaurant', '24-hour room service', 'Beach bar']},
                {'category': 'Activities', 'items': ['Tennis court', 'Fitness center', 'Water sports', 'Kids club']},
                {'category': 'Services', 'items': ['Free WiFi', 'Concierge', 'Laundry service', 'Airport shuttle']},
            ],
            'is_available': True,
            'notes': 'All-inclusive resort with premium amenities',
        }

# Singleton instance
_api_integration = None

def get_api_integration():
    """
    Get the singleton instance of the APIIntegration.
    """
    global _api_integration
    if _api_integration is None:
        _api_integration = APIIntegration()
    return _api_integration