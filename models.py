"""
Database models for the Crystal Bay Travel application.
These models define the structure of the data in Supabase.
"""
import os
from datetime import datetime
from supabase import create_client, Client

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

class BookingService:
    """Service class for handling bookings in Supabase database"""
    
    @staticmethod
    def create_booking(booking_data):
        """
        Create a new booking in the Supabase database
        
        Args:
            booking_data (dict): The booking data including:
                - customer_name: Full name of the customer
                - customer_phone: Phone number
                - customer_email: Email address
                - tour_id: ID of the selected tour
                - departure_city: City of departure
                - destination_country: Country of destination
                - checkin_date: Check-in date
                - nights: Number of nights
                - adults: Number of adults
                - children: Number of children (optional)
                - price: Total price
                - currency: Currency code
                - status: Booking status (pending, confirmed, cancelled)
                - telegram_user_id: Telegram user ID if booked via Telegram
                
        Returns:
            dict: The created booking data with an ID
        """
        # Add creation timestamp
        booking_data['created_at'] = datetime.now().isoformat()
        
        # Insert into Supabase
        result = supabase.table("bookings").insert(booking_data).execute()
        
        # Return the created booking
        return result.data[0] if result.data else None
    
    @staticmethod
    def get_bookings(limit=100, status=None):
        """
        Get all bookings, optionally filtered by status
        
        Args:
            limit (int): Maximum number of bookings to return
            status (str, optional): Filter by booking status
            
        Returns:
            list: List of bookings
        """
        query = supabase.table("bookings").select("*").limit(limit)
        
        if status:
            query = query.eq("status", status)
            
        result = query.execute()
        return result.data if result.data else []
    
    @staticmethod
    def get_booking(booking_id):
        """
        Get a specific booking by ID
        
        Args:
            booking_id (str): The booking ID
            
        Returns:
            dict: The booking data or None if not found
        """
        result = supabase.table("bookings").select("*").eq("id", booking_id).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def update_booking_status(booking_id, status):
        """
        Update the status of a booking
        
        Args:
            booking_id (str): The booking ID
            status (str): The new status (pending, confirmed, cancelled)
            
        Returns:
            dict: The updated booking data
        """
        result = supabase.table("bookings").update({"status": status}).eq("id", booking_id).execute()
        return result.data[0] if result.data else None