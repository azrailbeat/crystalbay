"""
Wazzup24 Message Processor - обработка сообщений с ИИ ответами
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from wazzup_api_v3 import WazzupAPIv3
import openai

logger = logging.getLogger(__name__)

class WazzupMessageProcessor:
    """Процессор сообщений Wazzup24 с ИИ интеграцией"""
    
    def __init__(self):
        self.wazzup = WazzupAPIv3()
        
        # OpenAI configuration
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Message processing settings
        self.auto_reply_enabled = True
        self.processed_messages = set()  # Избегаем дублирования
        
    def get_recent_messages(self, limit: int = 50) -> List[Dict]:
        """Получить последние сообщения"""
        try:
            # Получаем последние чаты
            chats_response = self.wazzup.get_chats(limit=limit)
            
            if chats_response.get('error'):
                logger.error(f"Ошибка получения чатов: {chats_response}")
                return []
            
            messages = []
            # chats_response может быть списком напрямую или содержать ключ 'chats'
            chats = chats_response if isinstance(chats_response, list) else chats_response.get('chats', [])
            
            for chat in chats[:10]:  # Берем первые 10 чатов
                chat_id = chat.get('chatId')
                if not chat_id:
                    continue
                    
                # Получаем сообщения из чата
                chat_messages = self.wazzup.get_messages(chat_id, limit=20)
                
                if not chat_messages.get('error'):
                    # chat_messages может быть списком напрямую или содержать ключ 'messages'
                    messages_list = chat_messages if isinstance(chat_messages, list) else chat_messages.get('messages', [])
                    for msg in messages_list:
                        # Добавляем информацию о чате к сообщению
                        msg['chat_info'] = {
                            'chatId': chat_id,
                            'chatName': chat.get('chatName', ''),
                            'lastActivity': chat.get('lastActivity')
                        }
                        messages.append(msg)
            
            # Сортируем по времени (новые сначала)
            messages.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
            
            logger.info(f"Получено {len(messages)} сообщений из {len(chats)} чатов")
            return messages[:limit]
            
        except Exception as e:
            logger.error(f"Ошибка получения сообщений: {e}")
            return []
    
    def process_incoming_message(self, message: Dict) -> Dict:
        """Обработать входящее сообщение и сгенерировать ответ"""
        try:
            message_id = message.get('id')
            chat_id = message.get('chatId') or message.get('chat_info', {}).get('chatId')
            message_text = message.get('text', '')
            sender = message.get('senderName', 'Клиент')
            
            # Проверяем, не обработано ли уже это сообщение
            if message_id in self.processed_messages:
                return {'status': 'already_processed', 'message_id': message_id}
            
            # Проверяем, что это сообщение от клиента (не от нас)
            if message.get('fromMe', False):
                return {'status': 'outgoing_message', 'message_id': message_id}
            
            if not message_text.strip():
                return {'status': 'empty_message', 'message_id': message_id}
            
            logger.info(f"Обрабатываем сообщение от {sender}: {message_text[:100]}...")
            
            # Генерируем ответ с помощью ИИ
            ai_response = self.generate_ai_response(message_text, sender)
            
            if not ai_response:
                return {'status': 'ai_response_failed', 'message_id': message_id}
            
            # Отправляем ответ
            if self.auto_reply_enabled and chat_id:
                send_result = self.send_reply(chat_id, ai_response)
                
                if send_result.get('error'):
                    logger.error(f"Ошибка отправки ответа: {send_result}")
                    return {
                        'status': 'send_failed',
                        'message_id': message_id,
                        'ai_response': ai_response,
                        'error': send_result
                    }
                else:
                    logger.info(f"Ответ отправлен в чат {chat_id}")
                    self.processed_messages.add(message_id)
                    return {
                        'status': 'success',
                        'message_id': message_id,
                        'chat_id': chat_id,
                        'original_message': message_text,
                        'ai_response': ai_response,
                        'send_result': send_result
                    }
            else:
                return {
                    'status': 'response_generated',
                    'message_id': message_id,
                    'ai_response': ai_response,
                    'note': 'Auto-reply disabled or no chat_id'
                }
                
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def generate_ai_response(self, message_text: str, sender_name: str = "Клиент") -> str:
        """Генерировать ответ с помощью OpenAI"""
        try:
            # Системный промпт для турагентства
            system_prompt = """Вы - профессиональный менеджер турагентства Crystal Bay Travel. 
            
Ваши задачи:
- Консультировать клиентов по турам и путешествиям
- Помогать с выбором направлений, отелей, дат
- Отвечать на вопросы о документах, визах, страховке
- Собирать контактные данные для дальнейшей работы
- Говорить на русском языке профессионально и дружелюбно

Если клиент интересуется конкретным туром, предложите ему оставить контакты для персональной консультации.

Отвечайте кратко, информативно и по делу. Не используйте слишком длинные сообщения."""

            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            response = client.chat.completions.create(
                model="gpt-4o",  # Newest OpenAI model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Клиент {sender_name} написал: {message_text}"}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            logger.info(f"ИИ ответ сгенерирован: {ai_response[:100]}...")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Ошибка генерации ИИ ответа: {e}")
            return "Спасибо за ваше сообщение! Наш менеджер свяжется с вами в ближайшее время."
    
    def send_reply(self, chat_id: str, message_text: str) -> Dict:
        """Отправить ответ в чат"""
        try:
            return self.wazzup.send_message(chat_id, message_text)
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            return {'error': True, 'message': str(e)}
    
    def process_all_recent_messages(self) -> Dict:
        """Обработать все последние непрочитанные сообщения"""
        try:
            messages = self.get_recent_messages(limit=30)
            results = []
            
            for message in messages:
                # Обрабатываем только новые входящие сообщения (последние 24 часа)
                created_at = message.get('createdAt', '')
                if created_at:
                    try:
                        msg_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        now = datetime.now(msg_time.tzinfo)
                        hours_ago = (now - msg_time).total_seconds() / 3600
                        
                        # Обрабатываем сообщения не старше 24 часов
                        if hours_ago > 24:
                            continue
                    except:
                        pass  # Если не можем парсить время, обрабатываем
                
                result = self.process_incoming_message(message)
                if result['status'] not in ['already_processed', 'outgoing_message']:
                    results.append(result)
            
            return {
                'status': 'success',
                'processed_count': len(results),
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Ошибка массовой обработки сообщений: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def test_connection(self) -> Dict:
        """Тестирование подключения к Wazzup24 API"""
        try:
            # Тест получения пользователей
            users_response = self.wazzup.get_users()
            
            # Проверяем на ошибки только если это словарь
            if isinstance(users_response, dict) and users_response.get('error'):
                return {
                    'status': 'error',
                    'message': 'Ошибка подключения к Wazzup24 API',
                    'details': users_response
                }
            
            # users_response может быть списком напрямую
            if isinstance(users_response, list):
                users_list = users_response
            elif isinstance(users_response, dict):
                users_list = users_response.get('users', [])
            else:
                users_list = []
            
            # Тест получения чатов (опционально, может не поддерживаться)
            chats_count = 0
            try:
                chats_response = self.wazzup.get_chats(limit=5)
                if not chats_response.get('error'):
                    chats_list = chats_response if isinstance(chats_response, list) else chats_response.get('chats', [])
                    chats_count = len(chats_list)
            except Exception as e:
                logger.warning(f"Chats API не поддерживается: {e}")
                chats_count = 0
            
            return {
                'status': 'success',
                'message': 'Подключение к Wazzup24 API успешно',
                'users_count': len(users_list),
                'chats_count': chats_count,
                'api_key_valid': True
            }
            
        except Exception as e:
            logger.error(f"Ошибка тестирования соединения: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка тестирования: {str(e)}'
            }