import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import openai
from openai import OpenAI

from wazzup_integration import WazzupIntegration
from api_integration import APIIntegration
from bitrix_integration import bitrix
from models import LeadService

logger = logging.getLogger(__name__)

class IntelligentChatProcessor:
    """AI-powered chat processor that handles customer inquiries using SAMO API and Bitrix integration"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        self.wazzup = WazzupIntegration()
        self.samo_api = APIIntegration()
        self.lead_service = LeadService()
        
        # System prompt for travel assistant
        self.system_prompt = """
Вы - ИИ-ассистент Crystal Bay Travel, специализирующийся на туристических консультациях.

ВАШИ ВОЗМОЖНОСТИ:
1. Поиск туров через SAMO API
2. Предоставление информации о турах, ценах, отелях
3. Помощь с бронированием
4. Ответы на вопросы о документах и визах
5. Создание лидов в CRM системе

ИНСТРУКЦИИ:
- Всегда отвечайте дружелюбно и профессионально
- Используйте актуальные данные из SAMO API
- При поиске туров учитывайте бюджет, даты и предпочтения клиента
- Если нужна дополнительная информация, вежливо попросите её
- При готовности к бронированию, создавайте лид в системе
- Предоставляйте конкретные варианты с ценами и деталями

ФОРМАТ ОТВЕТА:
- Краткий и понятный текст
- Структурированная информация по турам
- Конкретные предложения и рекомендации
- Четкие следующие шаги для клиента

Отвечайте только на русском языке.
"""
    
    async def process_new_messages(self) -> Dict:
        """Process all new unread messages from Wazzup"""
        try:
            # Get unread messages
            unread_response = await self.wazzup.get_unread_messages()
            
            if unread_response.get('status') != 'success':
                return {"status": "error", "error": "Failed to get unread messages"}
            
            messages = unread_response.get('messages', [])
            processed_count = 0
            
            for message in messages:
                try:
                    result = await self.process_message(message)
                    if result.get('status') == 'success':
                        processed_count += 1
                        logger.info(f"Processed message {message.get('id')}")
                except Exception as e:
                    logger.error(f"Error processing message {message.get('id')}: {e}")
                    continue
            
            return {
                "status": "success", 
                "processed": processed_count,
                "total": len(messages)
            }
            
        except Exception as e:
            logger.error(f"Error in process_new_messages: {e}")
            return {"status": "error", "error": str(e)}
    
    async def process_message(self, message: Dict) -> Dict:
        """Process a single message and generate intelligent response"""
        try:
            message_text = message.get('text', '')
            chat_id = message.get('chatId', '')
            contact_id = message.get('contactId', '')
            
            if not message_text.strip():
                return {"status": "skipped", "reason": "Empty message"}
            
            # Get chat context
            chat_context = await self.get_chat_context(chat_id)
            
            # Analyze message intent
            intent_analysis = await self.analyze_message_intent(message_text, chat_context)
            
            # Generate response based on intent
            if intent_analysis.get('intent') == 'tour_search':
                response = await self.handle_tour_search(message_text, intent_analysis)
            elif intent_analysis.get('intent') == 'booking_inquiry':
                response = await self.handle_booking_inquiry(message_text, intent_analysis, contact_id)
            elif intent_analysis.get('intent') == 'info_request':
                response = await self.handle_info_request(message_text, intent_analysis)
            elif intent_analysis.get('intent') == 'complaint_support':
                response = await self.handle_support_request(message_text, intent_analysis, contact_id)
            else:
                response = await self.handle_general_inquiry(message_text, chat_context)
            
            # Send response through Wazzup
            if response.get('text'):
                send_result = await self.wazzup.send_message(chat_id, response['text'])
                
                # Create activity in Bitrix if enabled
                if intent_analysis.get('create_activity', False):
                    await self.create_bitrix_activity(contact_id, message_text, response['text'])
                
                # Create lead if customer shows booking intent
                if intent_analysis.get('create_lead', False):
                    await self.create_lead_from_conversation(contact_id, message_text, intent_analysis)
                
                return {"status": "success", "response_sent": True}
            
            return {"status": "success", "response_sent": False}
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {"status": "error", "error": str(e)}
    
    async def analyze_message_intent(self, message: str, context: Dict = None) -> Dict:
        """Use AI to analyze customer message intent"""
        try:
            analysis_prompt = f"""
Проанализируйте сообщение клиента туристического агентства и определите намерение.

СООБЩЕНИЕ: "{message}"
КОНТЕКСТ: {json.dumps(context or {}, ensure_ascii=False)}

Определите:
1. intent - основное намерение (tour_search, booking_inquiry, info_request, complaint_support, general)
2. destination - пункт назначения (если упомянут)
3. budget - бюджет (если упомянут)
4. dates - даты поездки (если упомянуты)
5. passengers - количество человек (если упомянуто)
6. create_lead - нужно ли создавать лид (true/false)
7. create_activity - нужно ли создавать активность в CRM (true/false)
8. urgency - срочность запроса (low, medium, high)
9. extracted_info - извлеченная ключевая информация

Ответьте JSON объектом.
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Вы - аналитик намерений для туристического агентства. Отвечайте только JSON."},
                    {"role": "user", "content": analysis_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error analyzing message intent: {e}")
            return {"intent": "general", "create_lead": False, "create_activity": True}
    
    async def handle_tour_search(self, message: str, intent: Dict) -> Dict:
        """Handle tour search requests using SAMO API"""
        try:
            # Extract search parameters
            destination = intent.get('destination', '')
            budget = intent.get('budget', 0)
            dates = intent.get('dates', '')
            passengers = intent.get('passengers', 1)
            
            # Search tours using SAMO API
            search_params = {
                'destination': destination,
                'budget_max': budget,
                'adults': passengers,
                'departure_date': dates
            }
            
            # Use synchronous method from APIIntegration
            tours = self.samo_api.search_tours(search_params)
            
            if not tours or tours.get('status') == 'error':
                response_text = f"""
К сожалению, не удалось найти туры по вашему запросу.

Пожалуйста, уточните:
• Куда планируете поехать?
• На какие даты?
• Количество человек?
• Примерный бюджет?

Наши менеджеры подберут лучшие варианты специально для вас!
"""
            else:
                # Format tour results
                response_text = await self.format_tour_results(tours.get('tours', []), intent)
            
            return {"text": response_text, "intent": "tour_search"}
            
        except Exception as e:
            logger.error(f"Error handling tour search: {e}")
            return {"text": "Произошла ошибка при поиске туров. Наш менеджер свяжется с вами в ближайшее время.", "intent": "error"}
    
    async def handle_booking_inquiry(self, message: str, intent: Dict, contact_id: str) -> Dict:
        """Handle booking inquiries and create leads"""
        try:
            # Generate response using AI with booking context
            booking_prompt = f"""
Клиент интересуется бронированием тура. Сообщение: "{message}"

Проанализированные данные:
{json.dumps(intent.get('extracted_info', {}), ensure_ascii=False)}

Создайте профессиональный ответ, который:
1. Подтверждает интерес к бронированию
2. Запрашивает недостающую информацию
3. Объясняет следующие шаги
4. Предлагает связаться с менеджером

Ответ должен быть дружелюбным и профессиональным.
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": booking_prompt}
                ],
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content
            
            # Add booking information
            response_text += """

📞 Для завершения бронирования свяжитесь с нашим менеджером:
• Телефон: +7 (xxx) xxx-xx-xx
• WhatsApp: +7 (xxx) xxx-xx-xx
• Или оставьте заявку, и мы перезвоним в течение 15 минут!
"""
            
            return {"text": response_text, "intent": "booking"}
            
        except Exception as e:
            logger.error(f"Error handling booking inquiry: {e}")
            return {"text": "Отлично! Вы готовы к бронированию. Наш менеджер свяжется с вами для уточнения деталей.", "intent": "booking"}
    
    async def handle_info_request(self, message: str, intent: Dict) -> Dict:
        """Handle information requests about tours, visas, documents"""
        try:
            info_prompt = f"""
Клиент запрашивает информацию: "{message}"

Предоставьте полную и точную информацию о:
- Требованиях к документам и визам
- Особенностях направления
- Рекомендациях по поездке
- Актуальных предложениях

Используйте профессиональную информацию туристического агентства.
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": info_prompt}
                ],
                temperature=0.5
            )
            
            return {"text": response.choices[0].message.content, "intent": "info"}
            
        except Exception as e:
            logger.error(f"Error handling info request: {e}")
            return {"text": "Спасибо за ваш вопрос! Наш специалист предоставит подробную информацию в ближайшее время.", "intent": "info"}
    
    async def handle_support_request(self, message: str, intent: Dict, contact_id: str) -> Dict:
        """Handle support requests and complaints"""
        try:
            # Escalate to human support
            support_text = """
Благодарим за обращение! Ваш запрос передан нашему менеджеру для персональной работы.

🔔 Мы обязательно решим все вопросы и свяжемся с вами в течение часа.

Для срочных вопросов:
📞 +7 (xxx) xxx-xx-xx
✉️ support@crystalbay.travel
"""
            
            # Create high-priority activity in Bitrix
            if bitrix.is_configured():
                await self.create_bitrix_activity(
                    contact_id, 
                    message, 
                    "SUPPORT REQUEST - HIGH PRIORITY",
                    activity_type="support"
                )
            
            return {"text": support_text, "intent": "support"}
            
        except Exception as e:
            logger.error(f"Error handling support request: {e}")
            return {"text": "Ваше обращение принято. Менеджер свяжется с вами в ближайшее время.", "intent": "support"}
    
    async def handle_general_inquiry(self, message: str, context: Dict) -> Dict:
        """Handle general inquiries with AI assistant"""
        try:
            general_prompt = f"""
Ответьте на сообщение клиента как профессиональный консультант Crystal Bay Travel.

СООБЩЕНИЕ: "{message}"
КОНТЕКСТ: {json.dumps(context, ensure_ascii=False)}

Ответ должен быть:
- Дружелюбным и профессиональным
- Полезным и информативным
- Содержать призыв к действию или следующие шаги
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": general_prompt}
                ],
                temperature=0.7
            )
            
            return {"text": response.choices[0].message.content, "intent": "general"}
            
        except Exception as e:
            logger.error(f"Error handling general inquiry: {e}")
            return {"text": "Спасибо за сообщение! Как могу помочь с планированием вашего путешествия?", "intent": "general"}
    
    async def format_tour_results(self, tours: List[Dict], intent: Dict) -> str:
        """Format tour search results for customer"""
        if not tours:
            return "К сожалению, туры по вашему запросу не найдены. Попробуйте изменить параметры поиска."
        
        formatted_text = "🌟 Найденные туры для вас:\n\n"
        
        for i, tour in enumerate(tours[:5], 1):  # Show max 5 tours
            formatted_text += f"""
{i}. 📍 {tour.get('destination', 'Направление не указано')}
   💰 Цена: от {tour.get('price', 'уточняется')} руб.
   📅 Даты: {tour.get('dates', 'гибкие даты')}
   🏨 Отель: {tour.get('hotel', 'различные варианты')}
   ⭐ Рейтинг: {tour.get('rating', 'н/д')}
   
"""
        
        formatted_text += """
💡 Хотите узнать подробности или забронировать тур?
Напишите номер интересующего варианта или свяжитесь с менеджером!

📞 +7 (xxx) xxx-xx-xx
"""
        
        return formatted_text
    
    async def get_chat_context(self, chat_id: str) -> Dict:
        """Get recent chat context for better responses"""
        try:
            # Get last 10 messages from chat
            messages_response = await self.wazzup.get_chat_messages(chat_id, limit=10)
            
            if messages_response.get('status') == 'success':
                messages = messages_response.get('messages', [])
                return {
                    "recent_messages": messages,
                    "message_count": len(messages),
                    "chat_id": chat_id
                }
            
            return {"chat_id": chat_id}
            
        except Exception as e:
            logger.error(f"Error getting chat context: {e}")
            return {"chat_id": chat_id}
    
    async def create_bitrix_activity(self, contact_id: str, message: str, response: str, activity_type: str = "chat") -> Dict:
        """Create activity in Bitrix CRM"""
        try:
            if not bitrix.is_configured():
                return {"status": "skipped", "reason": "Bitrix not configured"}
            
            activity_data = {
                "subject": f"Чат с клиентом - {activity_type}",
                "description": f"Сообщение клиента: {message}\n\nОтвет: {response}",
                "type_id": 4,  # Email/message type
                "completed": "Y",
                "direction": 2  # Incoming
            }
            
            result = bitrix.add_activity("contact", contact_id, activity_data)
            return result
            
        except Exception as e:
            logger.error(f"Error creating Bitrix activity: {e}")
            return {"status": "error", "error": str(e)}
    
    async def create_lead_from_conversation(self, contact_id: str, message: str, intent: Dict) -> Dict:
        """Create lead in both local system and Bitrix"""
        try:
            # Extract lead data from intent
            lead_data = {
                "title": "Лид из чата Wazzup",
                "description": f"Автоматически создан из сообщения: {message}",
                "source": "wazzup_chat",
                "destination": intent.get('destination', ''),
                "budget": intent.get('budget', ''),
                "passengers": intent.get('passengers', 1),
                "urgency": intent.get('urgency', 'medium'),
                "contact_id": contact_id
            }
            
            # Create in local system
            local_lead = self.lead_service.create_lead(lead_data)
            
            # Create in Bitrix if configured
            if bitrix.is_configured():
                bitrix_result = bitrix.create_lead(lead_data)
                logger.info(f"Lead created in Bitrix: {bitrix_result}")
            
            return {"status": "success", "lead_id": local_lead.get('id')}
            
        except Exception as e:
            logger.error(f"Error creating lead: {e}")
            return {"status": "error", "error": str(e)}
    
    async def start_monitoring(self, interval: int = 30) -> None:
        """Start continuous monitoring of Wazzup messages"""
        logger.info(f"Starting chat monitoring with {interval}s interval")
        
        while True:
            try:
                result = await self.process_new_messages()
                if result.get('processed', 0) > 0:
                    logger.info(f"Processed {result['processed']} messages")
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)

# Global instance
chat_processor = IntelligentChatProcessor()