import os
import logging
import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# API configuration
API_URL = "https://booking.crystalbay.com/export/default.php"
SAMO_TOKEN = os.getenv("SAMO_OAUTH_TOKEN")

async def fetch_cities(token: str) -> List[Dict[str, Any]]:
    """Fetch available departure cities from SAMO API."""
    try:
        response = requests.get(
            f"{API_URL}?samo_action=api&oauth_token={token}&type=json&action=SearchTour_TOWNFROMS"
        )
        response.raise_for_status()
        
        cities = response.json().get("SearchTour_TOWNFROMS", [])
        logger.info(f"Fetched {len(cities)} departure cities")
        return cities
    
    except Exception as e:
        logger.error(f"Error fetching cities: {e}")
        return []

async def fetch_countries(token: str, city_id: str) -> List[Dict[str, Any]]:
    """Fetch available countries based on departure city from SAMO API."""
    try:
        response = requests.post(
            f"{API_URL}?samo_action=api&oauth_token={token}&type=json&action=SearchTour_STATES",
            headers={'Content-Type': 'application/xml'},
            data=f'<data><TOWNFROMINC>{city_id}</TOWNFROMINC></data>'
        )
        response.raise_for_status()
        
        countries = response.json().get("SearchTour_STATES", [])
        logger.info(f"Fetched {len(countries)} countries for city ID {city_id}")
        return countries
    
    except Exception as e:
        logger.error(f"Error fetching countries: {e}")
        return []

async def fetch_tours(token: str, city_id: str, country_id: str, checkin_date: str) -> List[Dict[str, Any]]:
    """Fetch available tours based on selected criteria from SAMO API."""
    try:
        params = {
            "samo_action": "api",
            "oauth_token": token,
            "type": "json",
            "action": "SearchTour_TOURS",
            "townfrom": city_id,
            "stateinc": country_id,
            "checkin": checkin_date,
            "checkout": checkin_date,  # Same as checkin for API requirements
            "nights_min": 3,
            "nights_max": 14,
            "adults": 2,
            "currency": "RUB"
        }
        
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        
        tours = response.json().get("SearchTour_TOURS", [])
        logger.info(f"Fetched {len(tours)} tours for city {city_id}, country {country_id}, date {checkin_date}")
        return tours
    
    except Exception as e:
        logger.error(f"Error fetching tours: {e}")
        return []

def format_tour_details(tour: Dict[str, Any]) -> str:
    """Format tour details for display in Telegram message."""
    # Default values for missing fields
    hotel_name = tour.get("nameAlt", "Отель не указан")
    tour_type = tour.get("typeAlt", "Тип не указан")
    partner = tour.get("partnerAlt", "Партнер не указан")
    nights = tour.get("nights", "?")
    meal_type = tour.get("mealAlt", "Питание не указано")
    room_type = tour.get("roomAlt", "Тип номера не указан")
    
    # Price handling - use price if available, otherwise use priceInCurrency
    price = None
    if "price" in tour and tour["price"]:
        price = f"{tour['price']} {tour.get('currency', 'RUB')}"
    elif "priceInCurrency" in tour and tour["priceInCurrency"]:
        price = f"{tour['priceInCurrency']} {tour.get('currencyInCurrency', 'RUB')}"
    else:
        price = "Цена по запросу"
    
    # Format dates
    checkin_date = tour.get("checkin", "Дата не указана")
    if checkin_date and len(checkin_date) == 8:  # Format: YYYYMMDD
        checkin_date = f"{checkin_date[6:8]}.{checkin_date[4:6]}.{checkin_date[0:4]}"
    
    # Compose message
    tour_info = (
        f"*{hotel_name}*\n"
        f"🗓 *Дата заезда:* {checkin_date}\n"
        f"🌙 *Ночей:* {nights}\n"
        f"🍽 *Питание:* {meal_type}\n"
        f"🛏 *Размещение:* {room_type}\n"
        f"🔄 *Тип тура:* {tour_type}\n"
        f"🤝 *Туроператор:* {partner}\n"
        f"💰 *Цена:* {price}"
    )
    
    return tour_info

def generate_date_options(days_ahead: int = 30, start_from: Optional[datetime] = None) -> List[Dict[str, str]]:
    """Generate date options for the bot's date selector."""
    if not start_from:
        start_from = datetime.now()
    
    date_options = []
    for i in range(1, days_ahead + 1):
        date = start_from + timedelta(days=i)
        display_format = date.strftime("%d.%m")
        value_format = date.strftime("%Y%m%d")
        
        date_options.append({
            "display": display_format,
            "value": value_format
        })
    
    return date_options