import os
import logging
import json
from typing import Dict, Any
import openai
from openai import OpenAI

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# System context for the OpenAI model
SYSTEM_CONTEXT = """
You are a travel assistant for Crystal Bay Travel, a Russian travel agency specializing in tours and vacation packages.
Your role is to help customers find suitable tours, answer questions about destinations, and assist with the booking process.

Please follow these guidelines:
1. Be friendly, professional, and concise.
2. If asked about specific tour details, explain that users should use the bot's search functionality to get the most up-to-date information.
3. If you don't know specific pricing or availability, don't make up information - direct users to search for actual tours.
4. For questions about booking process, explain the steps: select departure city, destination, dates, and then book a tour.
5. Always respond in Russian language only.
6. Keep responses under 200 words.

Popular destinations include: Turkey, Egypt, UAE, Thailand, Cyprus, and Greece.
"""

async def process_message(message: str, user_context: Dict[str, Any]) -> str:
    """
    Process user message using OpenAI for natural language understanding.
    
    Args:
        message: The user's message text
        user_context: Dictionary containing user's session information
        
    Returns:
        str: The bot's response to the user
    """
    try:
        # Prepare context to send to OpenAI
        context_info = ""
        if user_context:
            if "departure_city" in user_context and "country" in user_context:
                context_info = "User has selected a departure city and destination country."
            elif "departure_city" in user_context:
                context_info = "User has selected a departure city but not a destination yet."
            
            if "selected_tour_info" in user_context:
                context_info += " User has selected a tour and is in the booking process."
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_CONTEXT + "\nContext: " + context_info},
                {"role": "user", "content": message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error in NLP processing: {e}")
        return "Извините, у меня возникли проблемы с обработкой вашего сообщения. Пожалуйста, попробуйте использовать кнопки для поиска туров или отправьте более простой запрос."

async def analyze_query_intent(query: str) -> Dict[str, Any]:
    """
    Analyze the user's query to determine their intent and extract relevant entities.
    
    Args:
        query: The user's message text
        
    Returns:
        Dict with intent and entities
    """
    try:
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": "Extract travel intent and entities from the user query. Identify if they're asking about a specific destination, date, duration, or have questions about booking process. Respond in JSON format with fields: intent (search, information, booking, other), destination (if mentioned), dates (if mentioned), duration (if mentioned)."
                },
                {"role": "user", "content": query}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        logger.error(f"Error in intent analysis: {e}")
        return {"intent": "unknown", "error": str(e)}
