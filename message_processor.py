"""
Crystal Bay Travel - Message Processing System with AI Agents
Система обработки обращений клиентов с интеграцией ИИ агентов
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import openai
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class MessageSource(Enum):
    TELEGRAM = "telegram"
    WAZZUP = "wazzup"
    EMAIL = "email"
    WEBSITE = "website"

class MessageStatus(Enum):
    NEW = "new"
    UNREAD = "unread"
    READ = "read"
    AI_PROCESSED = "ai_processed"
    REPLIED = "replied"
    CLOSED = "closed"

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class CustomerMessage:
    id: str
    customer_name: str
    customer_phone: Optional[str]
    customer_email: Optional[str]
    source: MessageSource
    content: str
    timestamp: datetime
    status: MessageStatus
    priority: Priority
    ai_processed: bool = False
    ai_confidence: float = 0.0
    ai_suggestions: List[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class ChatMessage:
    id: str
    message_id: str
    content: str
    type: str  # 'incoming', 'outgoing', 'ai_generated'
    timestamp: datetime
    ai_generated: bool = False
    metadata: Dict[str, Any] = None

class AIMessageProcessor:
    """ИИ агент для обработки сообщений клиентов"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.system_prompt = self._load_system_prompt()
        
    def _load_system_prompt(self) -> str:
        return """
Ты - профессиональный ИИ помощник для турагентства Crystal Bay Travel.

Твоя задача:
1. Анализировать сообщения клиентов
2. Определять приоритет обращения
3. Предлагать готовые ответы
4. Извлекать ключевую информацию о турах
5. Классифицировать тип запроса

Типы запросов:
- tour_inquiry: запрос информации о турах
- booking_request: заявка на бронирование
- complaint: жалоба или проблема
- general_info: общая информация
- support: техническая поддержка
- price_request: запрос цены

Приоритеты:
- urgent: жалобы, проблемы с оплатой
- high: запросы на бронирование, срочные вопросы
- medium: запросы информации о турах
- low: общие вопросы

Всегда отвечай на русском языке профессионально и дружелюбно.
"""

    def analyze_message(self, message: CustomerMessage) -> Dict[str, Any]:
        """Анализ сообщения клиента с помощью ИИ"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"""
Проанализируй это сообщение клиента:

Источник: {message.source.value}
Клиент: {message.customer_name}
Сообщение: {message.content}

Определи:
1. Тип запроса
2. Приоритет (urgent/high/medium/low)
3. Ключевые слова и информацию
4. Предложи 3 варианта ответа
5. Нужна ли эскалация к менеджеру

Ответь в формате JSON:
{
  "request_type": "тип запроса",
  "priority": "приоритет",
  "keywords": ["ключевые", "слова"],
  "extracted_info": {
    "destination": "направление",
    "dates": "даты",
    "budget": "бюджет",
    "pax": "количество человек"
  },
  "suggested_responses": [
    "Вариант ответа 1",
    "Вариант ответа 2", 
    "Вариант ответа 3"
  ],
  "requires_escalation": false,
  "confidence": 0.95,
  "notes": "дополнительные заметки"
}
                    """}
                ],
                response_format={"type": "json_object"},
                max_tokens=1000,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing message {message.id}: {e}")
            return {
                "request_type": "general_info",
                "priority": "medium",
                "keywords": [],
                "extracted_info": {},
                "suggested_responses": [
                    "Спасибо за ваше обращение. Наш менеджер свяжется с вами в ближайшее время.",
                    "Благодарим за интерес к нашим услугам. Мы обработаем ваш запрос и ответим в течение дня.",
                    "Здравствуйте! Ваше сообщение получено. Пожалуйста, ожидайте ответа от нашего специалиста."
                ],
                "requires_escalation": True,
                "confidence": 0.1,
                "notes": f"AI analysis failed: {str(e)}"
            }

    def generate_response(self, message: CustomerMessage, context: List[ChatMessage] = None) -> str:
        """Генерация ответа клиенту"""
        try:
            # Подготовка контекста разговора
            context_messages = []
            if context:
                for chat_msg in context[-5:]:  # Последние 5 сообщений
                    role = "user" if chat_msg.type == "incoming" else "assistant"
                    context_messages.append({"role": role, "content": chat_msg.content})
            
            messages = [
                {"role": "system", "content": self.system_prompt + """
                
Сгенерируй профессиональный ответ клиенту. Учитывай:
- Контекст предыдущих сообщений
- Специфику турагентства Crystal Bay Travel
- Необходимость предложить конкретные туры или услуги
- Дружелюбный, но профессиональный тон

Если клиент спрашивает о турах - предложи связаться для подбора тура.
Если нужна техническая информация - предложи консультацию с менеджером.
"""},
                *context_messages,
                {"role": "user", "content": message.content}
            ]
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating response for message {message.id}: {e}")
            return "Спасибо за ваше сообщение. Наш менеджер свяжется с вами в ближайшее время для персональной консультации."

class MessageStorage:
    """Система хранения сообщений"""
    
    def __init__(self):
        self.messages_file = "data/messages.json"
        self.chat_history_file = "data/chat_history.json"
        self._ensure_data_directory()
        
    def _ensure_data_directory(self):
        os.makedirs("data", exist_ok=True)
        
        # Создаем файлы если их нет
        if not os.path.exists(self.messages_file):
            with open(self.messages_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False)
                
        if not os.path.exists(self.chat_history_file):
            with open(self.chat_history_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False)

    def save_message(self, message: CustomerMessage) -> bool:
        """Сохранение сообщения"""
        try:
            messages = self.get_all_messages()
            
            # Конвертируем в словарь для сохранения
            message_dict = {
                "id": message.id,
                "customer_name": message.customer_name,
                "customer_phone": message.customer_phone,
                "customer_email": message.customer_email,
                "source": message.source.value,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "status": message.status.value,
                "priority": message.priority.value,
                "ai_processed": message.ai_processed,
                "ai_confidence": message.ai_confidence,
                "ai_suggestions": message.ai_suggestions or [],
                "metadata": message.metadata or {}
            }
            
            # Обновляем существующее или добавляем новое
            message_exists = False
            for i, existing in enumerate(messages):
                if existing["id"] == message.id:
                    messages[i] = message_dict
                    message_exists = True
                    break
                    
            if not message_exists:
                messages.append(message_dict)
            
            # Сортируем по времени (новые первые)
            messages.sort(key=lambda x: x["timestamp"], reverse=True)
            
            with open(self.messages_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
                
            return True
            
        except Exception as e:
            logger.error(f"Error saving message {message.id}: {e}")
            return False

    def get_all_messages(self) -> List[Dict]:
        """Получение всех сообщений"""
        try:
            with open(self.messages_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading messages: {e}")
            return []

    def get_message_by_id(self, message_id: str) -> Optional[Dict]:
        """Получение сообщения по ID"""
        messages = self.get_all_messages()
        for message in messages:
            if message["id"] == message_id:
                return message
        return None

    def save_chat_message(self, chat_message: ChatMessage) -> bool:
        """Сохранение сообщения в чате"""
        try:
            with open(self.chat_history_file, 'r', encoding='utf-8') as f:
                chat_history = json.load(f)
            
            message_id = chat_message.message_id
            if message_id not in chat_history:
                chat_history[message_id] = []
            
            chat_dict = {
                "id": chat_message.id,
                "content": chat_message.content,
                "type": chat_message.type,
                "timestamp": chat_message.timestamp.isoformat(),
                "ai_generated": chat_message.ai_generated,
                "metadata": chat_message.metadata or {}
            }
            
            chat_history[message_id].append(chat_dict)
            
            # Сортируем по времени
            chat_history[message_id].sort(key=lambda x: x["timestamp"])
            
            with open(self.chat_history_file, 'w', encoding='utf-8') as f:
                json.dump(chat_history, f, ensure_ascii=False, indent=2)
                
            return True
            
        except Exception as e:
            logger.error(f"Error saving chat message: {e}")
            return False

    def get_chat_history(self, message_id: str) -> List[Dict]:
        """Получение истории чата"""
        try:
            with open(self.chat_history_file, 'r', encoding='utf-8') as f:
                chat_history = json.load(f)
            return chat_history.get(message_id, [])
        except Exception as e:
            logger.error(f"Error loading chat history for {message_id}: {e}")
            return []

class MessageManager:
    """Главный класс для управления сообщениями"""
    
    def __init__(self):
        self.storage = MessageStorage()
        self.ai_processor = AIMessageProcessor()
        
    def create_sample_messages(self):
        """Создание примеров сообщений для демонстрации"""
        sample_messages = [
            CustomerMessage(
                id="msg_001",
                customer_name="Анна Смирнова", 
                customer_phone="+7 777 123 4567",
                customer_email="anna@email.com",
                source=MessageSource.TELEGRAM,
                content="Здравствуйте! Хочу узнать о турах во Вьетнам на февраль 2025. Семья из 4 человек, бюджет до $3000.",
                timestamp=datetime.now() - timedelta(hours=2),
                status=MessageStatus.UNREAD,
                priority=Priority.HIGH,
                ai_processed=True,
                ai_confidence=0.92,
                ai_suggestions=[
                    "Рекомендую рассмотреть туры в Нячанг или Фукуок на февраль. Для семьи из 4 человек у нас есть отличные предложения в вашем бюджете.",
                    "Февраль - прекрасное время для посещения Вьетнама! Предлагаю встретиться для подбора оптимального тура.",
                    "Спасибо за интерес к нашим турам! Наш менеджер подготовит персональные предложения для вашей семьи."
                ],
                metadata={"lead_potential": "high", "destination": "Vietnam", "budget": 3000, "pax": 4}
            ),
            CustomerMessage(
                id="msg_002",
                customer_name="Максим Петров",
                customer_phone="+7 777 987 6543", 
                customer_email=None,
                source=MessageSource.WAZZUP,
                content="У меня проблема с оплатой тура. Деньги списались, но подтверждения нет!",
                timestamp=datetime.now() - timedelta(minutes=30),
                status=MessageStatus.NEW,
                priority=Priority.URGENT,
                ai_processed=True,
                ai_confidence=0.98,
                ai_suggestions=[
                    "Извините за неудобства! Немедленно проверим статус вашей оплаты. Пожалуйста, предоставьте номер заказа.",
                    "Мы разберем эту ситуацию в приоритетном порядке. Наш менеджер свяжется с вами в течение 15 минут.",
                    "Приносим извинения за техническую проблему. Сейчас проверим ваш платеж и решим вопрос."
                ],
                metadata={"complaint": True, "urgency": "immediate"}
            ),
            CustomerMessage(
                id="msg_003",
                customer_name="Елена Казакова",
                customer_phone=None,
                customer_email="elena.k@mail.ru", 
                source=MessageSource.EMAIL,
                content="Добрый день! Интересуют туры в Таиланд, Пхукет. Двое взрослых, 7-10 дней, март или апрель.",
                timestamp=datetime.now() - timedelta(hours=5),
                status=MessageStatus.READ,
                priority=Priority.MEDIUM,
                ai_processed=True,
                ai_confidence=0.87,
                ai_suggestions=[
                    "Пхукет в марте-апреле - отличный выбор! У нас есть туры от 7 до 14 дней с различными отелями.",
                    "Для двоих взрослых в Пхукет мы можем предложить несколько вариантов. Какой бюджет рассматриваете?",
                    "Спасибо за обращение! Отправлю вам подборку туров в Пхукет на март-апрель."
                ],
                metadata={"destination": "Thailand", "duration": "7-10", "pax": 2}
            ),
            CustomerMessage(
                id="msg_004",
                customer_name="Дмитрий Волков",
                customer_phone="+7 777 555 1234",
                customer_email=None,
                source=MessageSource.TELEGRAM,
                content="Можно ли забронировать тур в рассрочку?",
                timestamp=datetime.now() - timedelta(hours=1),
                status=MessageStatus.UNREAD,
                priority=Priority.LOW,
                ai_processed=False,
                ai_confidence=0.0,
                ai_suggestions=[],
                metadata={"payment_inquiry": True}
            )
        ]
        
        # Сохраняем примеры сообщений
        for message in sample_messages:
            self.storage.save_message(message)
            
        # Добавляем историю чата для некоторых сообщений
        self.storage.save_chat_message(ChatMessage(
            id="chat_001_1",
            message_id="msg_001",
            content="Здравствуйте! Хочу узнать о турах во Вьетнам на февраль 2025. Семья из 4 человек, бюджет до $3000.",
            type="incoming",
            timestamp=datetime.now() - timedelta(hours=2)
        ))
        
        self.storage.save_chat_message(ChatMessage(
            id="chat_001_2", 
            message_id="msg_001",
            content="Спасибо за обращение! Вьетнам в феврале - отличный выбор. Для семьи из 4 человек мы можем предложить туры в Нячанг, Фукуок или комбинированные программы. Какой формат отдыха предпочитаете - пляжный или с экскурсиями?",
            type="outgoing",
            timestamp=datetime.now() - timedelta(hours=1, minutes=45),
            ai_generated=True
        ))
        
        logger.info("Sample messages created successfully")

# Создаем глобальный экземпляр менеджера
message_manager = MessageManager()