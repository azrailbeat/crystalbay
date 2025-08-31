"""
AI Assistant for SAMO Tourism System
Intelligent assistant for Crystal Bay Travel with SAMO API integration
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class SamoAIAssistant:
    """Intelligent assistant for SAMO tourism system"""
    
    def __init__(self):
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        if not self.openai_api_key:
            logger.warning("OpenAI API key not found. AI features will be limited.")
        
        # Load SAMO API integration
        try:
            from crystal_bay_samo_api import CrystalBaySamoAPI
            self.samo_api = CrystalBaySamoAPI()
            logger.info("SAMO API integrated successfully")
        except ImportError:
            logger.error("Failed to import SAMO API")
            self.samo_api = None
    
    def generate_openai_completion(self, messages: List[Dict], temperature: float = 0.7) -> str:
        """Generate AI completion using OpenAI"""
        if not self.openai_api_key:
            return "Извините, для работы ИИ-помощника требуется настройка OpenAI API ключа."
        
        try:
            import openai
            
            # Support both old and new openai versions
            try:
                # New version
                client = openai.OpenAI(api_key=self.openai_api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=temperature,
                    max_tokens=1000
                )
                return response.choices[0].message.content
            except AttributeError:
                # Old version fallback
                openai.api_key = self.openai_api_key
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=temperature,
                    max_tokens=1000
                )
                return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return f"Ошибка при обращении к ИИ: {str(e)}"
    
    def process_user_query(self, user_message: str, context: Dict = None) -> Dict[str, Any]:
        """Process user query with AI and SAMO integration"""
        
        # System prompt for tourism assistant
        system_prompt = """
Вы - умный помощник туристического агентства Crystal Bay Travel. 
Вы специализируетесь на:
- Поиске туров через систему SAMO
- Консультировании клиентов по направлениям
- Помощи в выборе отелей и туров
- Обработке запросов на бронирование

Отвечайте дружелюбно, профессионально и информативно. 
Используйте данные из системы SAMO для точных ответов.
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # Add context if available
        if context:
            context_text = f"Контекст: {json.dumps(context, ensure_ascii=False)}"
            messages.insert(1, {"role": "system", "content": context_text})
        
        # Generate AI response
        ai_response = self.generate_openai_completion(messages)
        
        # Try to extract actions from the response
        actions = self._extract_actions_from_response(user_message, ai_response)
        
        return {
            'ai_response': ai_response,
            'actions': actions,
            'timestamp': datetime.now().isoformat(),
            'query': user_message
        }
    
    def _extract_actions_from_response(self, user_query: str, ai_response: str) -> List[Dict]:
        """Extract potential actions from user query"""
        actions = []
        
        query_lower = user_query.lower()
        
        # Detect tour search intent
        search_keywords = ['найди тур', 'ищу тур', 'хочу поехать', 'подбери тур', 'тур в', 'отдых в']
        if any(keyword in query_lower for keyword in search_keywords):
            actions.append({
                'type': 'search_tours',
                'description': 'Поиск туров в системе SAMO',
                'parameters': self._extract_search_parameters(user_query)
            })
        
        # Detect destination info request
        info_keywords = ['расскажи о', 'информация о', 'что интересного в', 'погода в', 'когда лучше ехать в']
        if any(keyword in query_lower for keyword in info_keywords):
            actions.append({
                'type': 'destination_info',
                'description': 'Получение информации о направлении'
            })
        
        # Detect booking intent
        booking_keywords = ['забронировать', 'бронь', 'хочу купить', 'оформить тур']
        if any(keyword in query_lower for keyword in booking_keywords):
            actions.append({
                'type': 'booking_assistance',
                'description': 'Помощь с бронированием'
            })
        
        return actions
    
    def _extract_search_parameters(self, user_query: str) -> Dict:
        """Extract search parameters from user query"""
        parameters = {}
        
        query_lower = user_query.lower()
        
        # Extract destinations
        destinations = ['вьетнам', 'таиланд', 'бали', 'нячанг', 'пхукет', 'дананг', 'хошимин']
        for dest in destinations:
            if dest in query_lower:
                parameters['destination'] = dest.title()
                break
        
        # Extract number of people
        import re
        adults_match = re.search(r'(\d+)\s*(взрослы|человек)', query_lower)
        if adults_match:
            parameters['adults'] = int(adults_match.group(1))
        
        children_match = re.search(r'(\d+)\s*(ребен|детей)', query_lower)
        if children_match:
            parameters['children'] = int(children_match.group(1))
        
        # Extract duration
        duration_match = re.search(r'(\d+)\s*(дней|ночей)', query_lower)
        if duration_match:
            parameters['nights'] = int(duration_match.group(1))
        
        return parameters
    
    def search_tours_with_ai(self, parameters: Dict) -> Dict[str, Any]:
        """Search tours using SAMO API with AI assistance"""
        if not self.samo_api:
            return {
                'success': False,
                'error': 'SAMO API не доступен'
            }
        
        try:
            # Search tours using SAMO API
            result = self.samo_api.search_tour_prices(parameters)
            
            if result.get('success'):
                # Enhance results with AI descriptions
                tours = result.get('data', [])
                enhanced_tours = self._enhance_tours_with_ai(tours)
                
                return {
                    'success': True,
                    'data': enhanced_tours,
                    'total_count': len(enhanced_tours),
                    'ai_enhanced': True
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error searching tours with AI: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _enhance_tours_with_ai(self, tours: List[Dict]) -> List[Dict]:
        """Enhance tour descriptions with AI"""
        enhanced_tours = []
        
        for tour in tours[:10]:  # Limit to avoid API costs
            try:
                # Generate AI description for tour
                prompt = f"""
Создайте краткое привлекательное описание тура:
Отель: {tour.get('hotel', '')}
Направление: {tour.get('destination', '')}
Звезды: {tour.get('stars', '')}
Питание: {tour.get('meal', '')}

Описание должно быть до 100 слов, привлекательным и информативным.
"""
                
                messages = [
                    {"role": "system", "content": "Вы - эксперт по туризму. Создавайте привлекательные описания туров."},
                    {"role": "user", "content": prompt}
                ]
                
                ai_description = self.generate_openai_completion(messages, temperature=0.8)
                
                # Add AI description to tour
                enhanced_tour = tour.copy()
                enhanced_tour['ai_description'] = ai_description
                enhanced_tours.append(enhanced_tour)
                
            except Exception as e:
                logger.error(f"Error enhancing tour: {e}")
                enhanced_tours.append(tour)
        
        # Add remaining tours without AI enhancement to avoid costs
        enhanced_tours.extend(tours[10:])
        
        return enhanced_tours
    
    def get_destination_recommendations(self, preferences: Dict) -> Dict[str, Any]:
        """Get AI-powered destination recommendations"""
        
        preferences_text = ', '.join([f"{k}: {v}" for k, v in preferences.items()])
        
        prompt = f"""
На основе предпочтений клиента: {preferences_text}

Порекомендуйте 3-5 лучших туристических направлений из доступных:
- Вьетнам (Нячанг, Дананг, Хошимин, Фукуок)
- Таиланд (Пхукет, Патонг)
- Индонезия (Бали - Семиньяк, Кута)

Для каждого направления укажите:
1. Почему подходит клиенту
2. Лучшее время для поездки
3. Особенности направления
4. Примерный бюджет

Ответ структурируйте в JSON формате.
"""
        
        messages = [
            {"role": "system", "content": "Вы - эксперт по туризму. Давайте персонализированные рекомендации."},
            {"role": "user", "content": prompt}
        ]
        
        ai_response = self.generate_openai_completion(messages, temperature=0.7)
        
        try:
            # Try to parse JSON response
            recommendations = json.loads(ai_response)
        except (json.JSONDecodeError, ValueError):
            # Fallback to text response
            recommendations = {
                'text_recommendations': ai_response,
                'structured': False
            }
        
        return {
            'success': True,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_customer_inquiry(self, inquiry_text: str) -> Dict[str, Any]:
        """Analyze customer inquiry and extract structured data"""
        
        prompt = f"""
Проанализируйте обращение клиента и извлеките структурированную информацию:

Текст обращения: "{inquiry_text}"

Верните JSON с полями:
- intent: намерение клиента (search_tour, get_info, complaint, booking, other)
- destination: желаемое направление (если указано)
- budget: бюджет (если указан)
- adults: количество взрослых
- children: количество детей
- duration: продолжительность поездки
- dates: предполагаемые даты
- priority: приоритет обращения (high, medium, low)
- sentiment: тональность (positive, neutral, negative)
- keywords: ключевые слова
- suggested_actions: рекомендуемые действия

Если информация не указана, используйте null.
"""
        
        messages = [
            {"role": "system", "content": "Вы - ИИ-аналитик туристических запросов."},
            {"role": "user", "content": prompt}
        ]
        
        ai_response = self.generate_openai_completion(messages, temperature=0.3)
        
        try:
            analysis = json.loads(ai_response)
        except (json.JSONDecodeError, ValueError):
            analysis = {
                'intent': 'other',
                'text': ai_response,
                'structured': False
            }
        
        return {
            'success': True,
            'analysis': analysis,
            'original_text': inquiry_text,
            'timestamp': datetime.now().isoformat()
        }

# Global instance
ai_assistant = SamoAIAssistant()