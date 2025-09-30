"""
Crystal Bay Travel - Telegram Connector
Интеграция с Telegram Bot API для обработки сообщений
"""

import os
import logging
import requests
from datetime import datetime
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class TelegramConnector:
    """Коннектор для работы с Telegram Bot API"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN не найден")
        
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.webhook_url = None
    
    def set_webhook(self, url: str) -> Dict:
        """Установить webhook для получения сообщений"""
        try:
            response = requests.post(
                f"{self.base_url}/setWebhook",
                json={'url': url}
            )
            result = response.json()
            logger.info(f"Webhook установлен: {url}")
            self.webhook_url = url
            return result
        except Exception as e:
            logger.error(f"Ошибка установки webhook: {e}")
            return {'ok': False, 'error': str(e)}
    
    def delete_webhook(self) -> Dict:
        """Удалить webhook"""
        try:
            response = requests.post(f"{self.base_url}/deleteWebhook")
            result = response.json()
            logger.info("Webhook удален")
            self.webhook_url = None
            return result
        except Exception as e:
            logger.error(f"Ошибка удаления webhook: {e}")
            return {'ok': False, 'error': str(e)}
    
    def get_webhook_info(self) -> Dict:
        """Получить информацию о текущем webhook"""
        try:
            response = requests.get(f"{self.base_url}/getWebhookInfo")
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка получения информации о webhook: {e}")
            return {'ok': False, 'error': str(e)}
    
    def send_message(self, chat_id: str, text: str, reply_to_message_id: Optional[str] = None) -> Dict:
        """Отправить текстовое сообщение"""
        try:
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            if reply_to_message_id:
                data['reply_to_message_id'] = reply_to_message_id
            
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json=data
            )
            result = response.json()
            
            if result.get('ok'):
                logger.info(f"Сообщение отправлено в чат {chat_id}")
            else:
                logger.error(f"Ошибка отправки сообщения: {result}")
            
            return result
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            return {'ok': False, 'error': str(e)}
    
    def send_photo(self, chat_id: str, photo_url: str, caption: Optional[str] = None) -> Dict:
        """Отправить фото"""
        try:
            data = {
                'chat_id': chat_id,
                'photo': photo_url
            }
            if caption:
                data['caption'] = caption
            
            response = requests.post(
                f"{self.base_url}/sendPhoto",
                json=data
            )
            result = response.json()
            
            if result.get('ok'):
                logger.info(f"Фото отправлено в чат {chat_id}")
            else:
                logger.error(f"Ошибка отправки фото: {result}")
            
            return result
        except Exception as e:
            logger.error(f"Ошибка отправки фото: {e}")
            return {'ok': False, 'error': str(e)}
    
    def get_updates(self, offset: Optional[int] = None, limit: int = 100) -> List[Dict]:
        """Получить обновления (polling mode)"""
        try:
            params = {'limit': limit}
            if offset:
                params['offset'] = offset
            
            response = requests.get(
                f"{self.base_url}/getUpdates",
                params=params
            )
            result = response.json()
            
            if result.get('ok'):
                return result.get('result', [])
            else:
                logger.error(f"Ошибка получения обновлений: {result}")
                return []
        except Exception as e:
            logger.error(f"Ошибка получения обновлений: {e}")
            return []
    
    def parse_message(self, update: Dict) -> Optional[Dict]:
        """Парсинг входящего сообщения из webhook/update"""
        try:
            message = update.get('message', {})
            if not message:
                return None
            
            chat = message.get('chat', {})
            from_user = message.get('from', {})
            
            parsed = {
                'message_id': str(message.get('message_id')),
                'chat_id': str(chat.get('id')),
                'from_user_id': str(from_user.get('id')),
                'from_username': from_user.get('username') or from_user.get('first_name', ''),
                'text': message.get('text', ''),
                'message_type': 'text',
                'received_at': datetime.fromtimestamp(message.get('date', 0))
            }
            
            # Определяем тип сообщения
            if message.get('photo'):
                parsed['message_type'] = 'photo'
                photos = message['photo']
                if photos:
                    parsed['media_url'] = photos[-1].get('file_id')
                parsed['text'] = message.get('caption', '')
            
            elif message.get('document'):
                parsed['message_type'] = 'document'
                parsed['media_url'] = message['document'].get('file_id')
                parsed['text'] = message.get('caption', '')
            
            elif message.get('location'):
                parsed['message_type'] = 'location'
                location = message['location']
                parsed['text'] = f"Локация: {location.get('latitude')}, {location.get('longitude')}"
            
            return parsed
        
        except Exception as e:
            logger.error(f"Ошибка парсинга сообщения: {e}")
            return None
    
    def get_bot_info(self) -> Dict:
        """Получить информацию о боте"""
        try:
            response = requests.get(f"{self.base_url}/getMe")
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка получения информации о боте: {e}")
            return {'ok': False, 'error': str(e)}
    
    def mark_chat_read(self, chat_id: str) -> Dict:
        """Отметить сообщения как прочитанные (через sendChatAction)"""
        try:
            response = requests.post(
                f"{self.base_url}/sendChatAction",
                json={
                    'chat_id': chat_id,
                    'action': 'typing'
                }
            )
            return response.json()
        except Exception as e:
            logger.error(f"Ошибка отметки прочитанного: {e}")
            return {'ok': False, 'error': str(e)}
