import os
import logging
import openai
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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
        # Create a prompt with context
        system_prompt = (
            "Ты — помощник туристического агентства Crystal Bay Travel. "
            "Отвечай кратко, информативно, по-русски, в дружелюбной манере. "
            "Предпочитай короткие ответы, не больше 3-4 предложений, если пользователь "
            "не просит подробной информации."
        )
        
        # Add context from user session if available
        context_str = ""
        if user_context:
            if "departure_city" in user_context:
                context_str += f"Пользователь выбрал город вылета: {user_context['departure_city']}. "
            if "country" in user_context:
                context_str += f"Выбранная страна назначения: {user_context['country']}. "
            if "checkin" in user_context:
                context_str += f"Выбранная дата заезда: {user_context['checkin']}. "
        
        # Use the OpenAI API to generate a response
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Контекст пользователя: {context_str}\n\nСообщение пользователя: {message}"}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        bot_response = response.choices[0].message.content
        return bot_response
    
    except Exception as e:
        logger.error(f"Error processing message with OpenAI: {e}")
        return "Извините, я не могу обработать ваш запрос в данный момент. Пожалуйста, попробуйте позже или воспользуйтесь функцией поиска туров."

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
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": (
                    "Ты — анализатор намерений пользователя для туристического бота. "
                    "Определи главное намерение и извлеки сущности из запроса пользователя. "
                    "Верни результат в JSON формате с полями: intent, entities."
                )},
                {"role": "user", "content": query}
            ],
            max_tokens=300,
            response_format={"type": "json_object"}
        )
        
        result = response.choices[0].message.content
        
        # Parse the result, ensuring it's a valid JSON
        import json
        intent_data = json.loads(result)
        
        return intent_data
    
    except Exception as e:
        logger.error(f"Error analyzing query intent: {e}")
        return {
            "intent": "unknown",
            "entities": {}
        }