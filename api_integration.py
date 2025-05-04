import os
import json
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Singleton instance
_api_integration_instance = None

class APIIntegration:
    """
    Integration with external APIs for booking, flight, and amenity information.
    """
    
    def __init__(self):
        """Initialize API integration with credentials"""
        self.samo_oauth_token = os.getenv('SAMO_OAUTH_TOKEN')
        self.samo_api_base_url = "https://api.samo.travel/v1"
        
        # Use mocks for development/demo when token not available
        self.use_mocks = not self.samo_oauth_token
        if self.use_mocks:
            logger.warning("SAMO_OAUTH_TOKEN not found, using mock data for demonstrations")
    
    def check_booking(self, booking_reference):
        """Check booking details in the SAMO API.
        
        Args:
            booking_reference (str): The booking reference number
            
        Returns:
            dict: Booking information or None if not found
        """
        if not booking_reference:
            return None
            
        try:
            if self.use_mocks:
                return self._get_mock_booking(booking_reference)
            
            url = f"{self.samo_api_base_url}/bookings/{booking_reference}"
            response = self._make_samo_request(url)
            
            if response.status_code == 200:
                booking_data = response.json()
                return self._format_booking_data(booking_data)
            elif response.status_code == 404:
                logger.warning(f"Booking not found: {booking_reference}")
                return None
            else:
                logger.error(f"API error checking booking {booking_reference}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error checking booking {booking_reference}: {e}")
            return None
    
    def search_bookings(self, customer_email=None, customer_phone=None, customer_name=None):
        """Search for bookings by customer information.
        
        Args:
            customer_email (str, optional): Customer's email address
            customer_phone (str, optional): Customer's phone number
            customer_name (str, optional): Customer's name
            
        Returns:
            list: List of booking information dictionaries
        """
        try:
            if self.use_mocks:
                return self._get_mock_bookings()
            
            url = f"{self.samo_api_base_url}/bookings/search"
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
            
            response = self._make_samo_request(url, params=params)
            
            if response.status_code == 200:
                booking_list = response.json().get('bookings', [])
                return [self._format_booking_data(b) for b in booking_list]
            else:
                logger.error(f"API error searching bookings: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching bookings: {e}")
            return []
    
    def check_flight(self, flight_number, flight_date):
        """Check flight status using a flight status API.
        
        Args:
            flight_number (str): The flight number
            flight_date (str): The flight date in YYYY-MM-DD format
            
        Returns:
            dict: Flight information or None if not found
        """
        if not flight_number or not flight_date:
            return None
            
        try:
            # For now, using mock data since we don't have a real flight API integration yet
            return self._get_mock_flight(flight_number, flight_date)
                
        except Exception as e:
            logger.error(f"Error checking flight {flight_number}: {e}")
            return None
    
    def check_hotel_amenities(self, hotel_id, checkin_date=None):
        """Check hotel amenities and availability.
        
        Args:
            hotel_id (str): The hotel ID in the SAMO system
            checkin_date (str, optional): Check-in date in YYYY-MM-DD format
            
        Returns:
            dict: Hotel amenities information
        """
        if not hotel_id:
            return None
            
        try:
            if self.use_mocks:
                return self._get_mock_hotel_amenities(hotel_id)
            
            url = f"{self.samo_api_base_url}/hotels/{hotel_id}"
            params = {}
            
            if checkin_date:
                params['checkin_date'] = checkin_date
            
            response = self._make_samo_request(url, params=params)
            
            if response.status_code == 200:
                amenities_data = response.json()
                return self._format_amenities_data(amenities_data)
            elif response.status_code == 404:
                logger.warning(f"Hotel not found: {hotel_id}")
                return None
            else:
                logger.error(f"API error checking hotel amenities {hotel_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error checking hotel amenities {hotel_id}: {e}")
            return None
    
    def create_booking(self, booking_data):
        """Create a new booking in the SAMO system.
        
        Args:
            booking_data (dict): The booking data to create
            
        Returns:
            dict: Created booking information or error
        """
        try:
            if self.use_mocks:
                # Generate a mock booking with reference
                mock_booking = self._get_mock_booking("CB-" + datetime.now().strftime("%y%m%d%H%M"))
                return {
                    "success": True,
                    "booking": mock_booking
                }
            
            url = f"{self.samo_api_base_url}/bookings"
            response = self._make_samo_request(url, method='POST', data=booking_data)
            
            if response.status_code == 201:
                return {
                    "success": True,
                    "booking": self._format_booking_data(response.json())
                }
            else:
                error_message = response.json().get('message', 'Unknown error')
                logger.error(f"API error creating booking: {response.status_code} - {error_message}")
                return {
                    "success": False,
                    "error": error_message
                }
                
        except Exception as e:
            logger.error(f"Error creating booking: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _make_samo_request(self, url, method='GET', params=None, data=None):
        """Make a request to the SAMO API with authentication.
        
        Args:
            url (str): The API endpoint URL
            method (str, optional): HTTP method (GET, POST, etc.)
            params (dict, optional): Query parameters
            data (dict, optional): Request data for POST/PUT
            
        Returns:
            Response: The API response
        """
        headers = {
            'Authorization': f'Bearer {self.samo_oauth_token}',
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
        """Format raw booking data from the SAMO API into a consistent structure.
        
        Args:
            raw_data (dict): Raw booking data from API
            
        Returns:
            dict: Formatted booking data
        """
        # In a real implementation, this would normalize the API response data
        # For now, we just return the mock data in our expected format
        return {
            'reference': raw_data.get('reference'),
            'status': raw_data.get('status'),
            'customer_name': raw_data.get('customer_name'),
            'customer_email': raw_data.get('customer_email'),
            'customer_phone': raw_data.get('customer_phone'),
            'departure_date': raw_data.get('departure_date'),
            'return_date': raw_data.get('return_date'),
            'destination': raw_data.get('destination'),
            'hotel': raw_data.get('hotel'),
            'total_amount': raw_data.get('total_amount'),
            'amount_paid': raw_data.get('amount_paid'),
            'created_at': raw_data.get('created_at')
        }
    
    def _format_amenities_data(self, raw_data):
        """Format raw amenities data from the SAMO API.
        
        Args:
            raw_data (dict): Raw amenities data from API
            
        Returns:
            dict: Formatted amenities data
        """
        return {
            'hotel_id': raw_data.get('id'),
            'name': raw_data.get('name'),
            'description': raw_data.get('description'),
            'stars': raw_data.get('stars'),
            'address': raw_data.get('address'),
            'city': raw_data.get('city'),
            'country': raw_data.get('country'),
            'amenities': raw_data.get('amenities', []),
            'photos': raw_data.get('photos', []),
            'available': raw_data.get('available', True),
            'min_price': raw_data.get('min_price'),
            'max_price': raw_data.get('max_price'),
            'currency': raw_data.get('currency')
        }
    
    def _get_mock_booking(self, booking_reference):
        """Generate mock booking data for demonstration.
        
        Args:
            booking_reference (str): The booking reference
            
        Returns:
            dict: Mock booking data
        """
        # Mock booking data for demonstration
        return {
            'reference': booking_reference,
            'status': 'confirmed',
            'customer_name': 'Анна Смирнова',
            'customer_email': 'anna@example.com',
            'customer_phone': '+7 (900) 123-45-67',
            'departure_date': '2025-07-15',
            'return_date': '2025-07-25',
            'destination': 'Анталия, Турция',
            'hotel': 'Crystal Bay Resort & Spa 5*',
            'total_amount': '€3,500',
            'amount_paid': '€1,750',
            'created_at': '2025-05-02T14:30:00Z'
        }
    
    def _get_mock_bookings(self):
        """Generate mock bookings list for demonstration.
        
        Returns:
            list: List of mock booking data
        """
        # Mock bookings data for demonstration
        return [
            self._get_mock_booking('CB-20250515001'),
            {
                'reference': 'CB-20250410002',
                'status': 'confirmed',
                'customer_name': 'Иван Петров',
                'customer_email': 'ivan@example.com',
                'customer_phone': '+7 (900) 234-56-78',
                'departure_date': '2025-06-10',
                'return_date': '2025-06-24',
                'destination': 'Барселона, Испания',
                'hotel': 'Barcelona Beach Hotel 4*',
                'total_amount': '€4,200',
                'amount_paid': '€4,200',
                'created_at': '2025-04-10T10:15:00Z'
            },
            {
                'reference': 'CB-20250328003',
                'status': 'pending',
                'customer_name': 'Мария Соловьева',
                'customer_email': 'maria@example.com',
                'customer_phone': '+7 (900) 345-67-89',
                'departure_date': '2025-08-05',
                'return_date': '2025-08-15',
                'destination': 'Рим, Италия',
                'hotel': 'Roma Grand Hotel 5*',
                'total_amount': '€5,100',
                'amount_paid': '€1,020',
                'created_at': '2025-03-28T16:45:00Z'
            }
        ]
    
    def _get_mock_flight(self, flight_number, flight_date):
        """Generate mock flight data for demonstration.
        
        Args:
            flight_number (str): The flight number
            flight_date (str): The flight date
            
        Returns:
            dict: Mock flight data
        """
        # Mock flight data for demonstration
        airline = self._get_airline_from_flight_number(flight_number)
        
        departure_time = "10:25"
        arrival_time = "14:40"
        
        # Add some variety based on flight number
        if flight_number.endswith('1') or flight_number.endswith('3') or flight_number.endswith('5'):
            status = "On Time"
        elif flight_number.endswith('2') or flight_number.endswith('4'):
            status = "Delayed 35m"
            arrival_time = "15:15"
        else:
            status = "Scheduled"
        
        # Generate different routes based on flight number
        if "SU" in flight_number:
            departure_airport = "Москва (SVO)"
            arrival_airport = "Анталия (AYT)"
        elif "TK" in flight_number:
            departure_airport = "Москва (VKO)"
            arrival_airport = "Стамбул (IST)"
        elif "EK" in flight_number:
            departure_airport = "Москва (DME)"
            arrival_airport = "Дубай (DXB)"
        else:
            departure_airport = "Санкт-Петербург (LED)"
            arrival_airport = "Ларнака (LCA)"
        
        return {
            'flight_number': flight_number,
            'airline': airline,
            'date': flight_date,
            'departure_airport': departure_airport,
            'departure_time': departure_time,
            'arrival_airport': arrival_airport,
            'arrival_time': arrival_time,
            'status': status,
            'terminal': 'Terminal ' + flight_number[-1],
            'gate': 'Gate ' + flight_number[-1] + (chr(ord('A') + int(flight_number[-1]) % 5) if flight_number[-1].isdigit() else 'A')
        }
    
    def _get_airline_from_flight_number(self, flight_number):
        """Get airline name based on flight number prefix.
        
        Args:
            flight_number (str): The flight number
            
        Returns:
            str: Airline name
        """
        # Map common airline codes to airline names
        airline_map = {
            'SU': 'Аэрофлот',
            'U6': 'Уральские авиалинии',
            'S7': 'S7 Airlines',
            'AZ': 'ITA Airways',
            'TK': 'Turkish Airlines',
            'EK': 'Emirates',
            'BA': 'British Airways',
            'LH': 'Lufthansa'
        }
        
        if not flight_number or len(flight_number) < 2:
            return 'Unknown Airline'
        
        prefix = ''.join(c for c in flight_number if not c.isdigit()).upper()
        return airline_map.get(prefix, 'Unknown Airline')
    
    def _get_mock_hotel_amenities(self, hotel_id):
        """Generate mock hotel amenities data for demonstration.
        
        Args:
            hotel_id (str): The hotel ID
            
        Returns:
            dict: Mock hotel amenities data
        """
        # Mock hotel amenities data for demonstration
        amenities = [
            'Wi-Fi',
            'Бассейн',
            'Ресторан',
            'Бар',
            'Спа-центр',
            'Фитнес-центр',
            'Кондиционер',
            'Парковка',
            'Обслуживание номеров',
            'Конференц-зал'
        ]
        
        photos = [
            'https://example.com/photos/hotel1_1.jpg',
            'https://example.com/photos/hotel1_2.jpg',
            'https://example.com/photos/hotel1_3.jpg'
        ]
        
        return {
            'hotel_id': hotel_id,
            'name': 'Crystal Bay Resort & Spa',
            'description': 'Роскошный курортный отель с видом на море, расположенный в живописной бухте.',
            'stars': 5,
            'address': 'Kemer Mh., 07980 Antalya',
            'city': 'Анталия',
            'country': 'Турция',
            'amenities': amenities,
            'photos': photos,
            'available': True,
            'min_price': 150,
            'max_price': 500,
            'currency': 'EUR'
        }


def get_api_integration():
    """Get the singleton instance of the APIIntegration.
    
    Returns:
        APIIntegration: The singleton instance
    """
    global _api_integration_instance
    
    if _api_integration_instance is None:
        _api_integration_instance = APIIntegration()
        
    return _api_integration_instance