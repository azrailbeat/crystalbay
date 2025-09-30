"""
Crystal Bay Travel - WhatsApp Connector
Интеграция с Wazzup API для обработки WhatsApp сообщений
"""

import os
import logging
import requests
from datetime import datetime
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class WhatsAppConnector:
    """Коннектор для работы с WhatsApp через Wazzup API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('WAZZUP_API_KEY')
        if not self.api_key:
            raise ValueError("WAZZUP_API_KEY не найден")
        
        self.base_url = "https://api.wazzup24.com/v3"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_channels(self) -> List[Dict]:
        """Получить список каналов WhatsApp"""
        try:
            response = requests.get(
                f"{self.base_url}/channels",
                headers=self.headers
            )
            
            if response.status_code == 200:
                channels = response.json()
                logger.info(f"Получено каналов: {len(channels)}")
                return channels
            else:
                logger.error(f"Ошибка получения каналов: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Ошибка получения каналов: {e}")
            return []
    
    def send_message(self, channel_id: str, chat_id: str, text: str) -> Dict:
        """Отправить текстовое сообщение"""
        try:
            data = {
                'channelId': channel_id,
                'chatId': chat_id,
                'chatType': 'whatsapp',
                'text': text
            }
            
            response = requests.post(
                f"{self.base_url}/message",
                headers=self.headers,
                json=data
            )
            
            result = response.json() if response.status_code == 200 else {}
            
            if response.status_code == 200:
                logger.info(f"Сообщение отправлено в чат {chat_id}")
            else:
                logger.error(f"Ошибка отправки сообщения: {response.text}")
            
            return {
                'ok': response.status_code == 200,
                'result': result,
                'error': response.text if response.status_code != 200 else None
            }
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            return {'ok': False, 'error': str(e)}
    
    def send_file(self, channel_id: str, chat_id: str, file_url: str, caption: Optional[str] = None) -> Dict:
        """Отправить файл/фото"""
        try:
            data = {
                'channelId': channel_id,
                'chatId': chat_id,
                'chatType': 'whatsapp',
                'file': file_url
            }
            if caption:
                data['caption'] = caption
            
            response = requests.post(
                f"{self.base_url}/message",
                headers=self.headers,
                json=data
            )
            
            result = response.json() if response.status_code == 200 else {}
            
            if response.status_code == 200:
                logger.info(f"Файл отправлен в чат {chat_id}")
            else:
                logger.error(f"Ошибка отправки файла: {response.text}")
            
            return {
                'ok': response.status_code == 200,
                'result': result,
                'error': response.text if response.status_code != 200 else None
            }
        except Exception as e:
            logger.error(f"Ошибка отправки файла: {e}")
            return {'ok': False, 'error': str(e)}
    
    def get_messages(self, channel_id: str, chat_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Получить сообщения"""
        try:
            params = {
                'channelId': channel_id,
                'limit': limit
            }
            if chat_id:
                params['chatId'] = chat_id
            
            response = requests.get(
                f"{self.base_url}/messages",
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                messages = response.json()
                logger.info(f"Получено сообщений: {len(messages)}")
                return messages
            else:
                logger.error(f"Ошибка получения сообщений: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Ошибка получения сообщений: {e}")
            return []
    
    def get_chats(self, channel_id: str) -> List[Dict]:
        """Получить список чатов"""
        try:
            response = requests.get(
                f"{self.base_url}/chats",
                headers=self.headers,
                params={'channelId': channel_id}
            )
            
            if response.status_code == 200:
                chats = response.json()
                logger.info(f"Получено чатов: {len(chats)}")
                return chats
            else:
                logger.error(f"Ошибка получения чатов: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Ошибка получения чатов: {e}")
            return []
    
    def set_webhook(self, url: str) -> Dict:
        """Установить webhook для получения сообщений"""
        try:
            data = {'url': url}
            
            response = requests.post(
                f"{self.base_url}/webhook",
                headers=self.headers,
                json=data
            )
            
            result = response.json() if response.status_code == 200 else {}
            
            if response.status_code == 200:
                logger.info(f"Webhook установлен: {url}")
            else:
                logger.error(f"Ошибка установки webhook: {response.text}")
            
            return {
                'ok': response.status_code == 200,
                'result': result,
                'error': response.text if response.status_code != 200 else None
            }
        except Exception as e:
            logger.error(f"Ошибка установки webhook: {e}")
            return {'ok': False, 'error': str(e)}
    
    def parse_message(self, webhook_data: Dict) -> Optional[Dict]:
        """Парсинг входящего сообщения из webhook"""
        try:
            message = webhook_data.get('messages', [{}])[0] if 'messages' in webhook_data else webhook_data
            
            if not message:
                return None
            
            parsed = {
                'message_id': str(message.get('messageId', '')),
                'chat_id': str(message.get('chatId', '')),
                'from_user_id': str(message.get('userId', '')),
                'from_phone': message.get('phone', ''),
                'from_username': message.get('userName', '') or message.get('phone', ''),
                'text': message.get('text', ''),
                'message_type': message.get('type', 'text'),
                'received_at': datetime.fromtimestamp(message.get('timestamp', 0) / 1000) if message.get('timestamp') else datetime.utcnow()
            }
            
            # Обработка медиа
            if message.get('file'):
                parsed['media_url'] = message['file'].get('url', '')
                if message.get('type') == 'image':
                    parsed['message_type'] = 'photo'
                elif message.get('type') == 'document':
                    parsed['message_type'] = 'document'
            
            return parsed
        
        except Exception as e:
            logger.error(f"Ошибка парсинга сообщения: {e}")
            return None
    
    def mark_as_read(self, channel_id: str, chat_id: str, message_id: str) -> Dict:
        """Отметить сообщение как прочитанное"""
        try:
            data = {
                'channelId': channel_id,
                'chatId': chat_id,
                'messageId': message_id
            }
            
            response = requests.post(
                f"{self.base_url}/messages/read",
                headers=self.headers,
                json=data
            )
            
            return {
                'ok': response.status_code == 200,
                'error': response.text if response.status_code != 200 else None
            }
        except Exception as e:
            logger.error(f"Ошибка отметки прочитанного: {e}")
            return {'ok': False, 'error': str(e)}
