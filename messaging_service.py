"""
Unified Messaging Service for Crystal Bay Travel
Handles Telegram, WhatsApp (via Wazzup24), and other messaging channels
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class MessageStore:
    """In-memory message store with PostgreSQL persistence"""
    
    def __init__(self):
        self.conversations = {}
        self.messages = {}
        self.db = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database connection"""
        try:
            import psycopg2
            database_url = os.environ.get('DATABASE_URL')
            if database_url:
                self.db = psycopg2.connect(database_url)
                self._create_tables()
                logger.info("MessageStore: Database connection established")
        except Exception as e:
            logger.warning(f"MessageStore: Using memory storage - {e}")
    
    def _create_tables(self):
        """Create messaging tables if they don't exist"""
        if not self.db:
            return
        
        try:
            cursor = self.db.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id VARCHAR(255) PRIMARY KEY,
                    lead_id VARCHAR(255),
                    channel VARCHAR(50) NOT NULL,
                    external_chat_id VARCHAR(255),
                    participant_name VARCHAR(255),
                    participant_phone VARCHAR(100),
                    status VARCHAR(50) DEFAULT 'active',
                    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{}'
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id VARCHAR(255) PRIMARY KEY,
                    conversation_id VARCHAR(255),
                    channel VARCHAR(50) NOT NULL,
                    external_message_id VARCHAR(255),
                    direction VARCHAR(10) NOT NULL,
                    sender_type VARCHAR(20) DEFAULT 'customer',
                    sender_id VARCHAR(255),
                    sender_name VARCHAR(255),
                    message_type VARCHAR(50) DEFAULT 'text',
                    content TEXT,
                    media_url TEXT,
                    media_type VARCHAR(50),
                    status VARCHAR(50) DEFAULT 'sent',
                    read_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{}'
                )
            ''')
            
            self.db.commit()
            logger.info("MessageStore: Tables created successfully")
        except Exception as e:
            logger.error(f"MessageStore: Error creating tables - {e}")
    
    def _generate_id(self, prefix='msg'):
        import time
        import random
        return f"{prefix}_{int(time.time())}_{random.randint(1000, 9999)}"
    
    def create_conversation(self, data: Dict) -> Dict:
        """Create a new conversation"""
        conv_id = self._generate_id('conv')
        conversation = {
            'id': conv_id,
            'lead_id': data.get('lead_id'),
            'channel': data.get('channel', 'unknown'),
            'external_chat_id': data.get('external_chat_id'),
            'participant_name': data.get('participant_name', 'Unknown'),
            'participant_phone': data.get('participant_phone'),
            'status': 'active',
            'last_message_at': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat(),
            'metadata': data.get('metadata', {})
        }
        
        if self.db:
            try:
                cursor = self.db.cursor()
                cursor.execute('''
                    INSERT INTO conversations (id, lead_id, channel, external_chat_id, participant_name, 
                                             participant_phone, status, last_message_at, created_at, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (conversation['id'], conversation['lead_id'], conversation['channel'],
                      conversation['external_chat_id'], conversation['participant_name'],
                      conversation['participant_phone'], conversation['status'],
                      conversation['last_message_at'], conversation['created_at'],
                      json.dumps(conversation['metadata'])))
                self.db.commit()
            except Exception as e:
                logger.error(f"Error saving conversation: {e}")
        
        self.conversations[conv_id] = conversation
        return conversation
    
    def find_conversation(self, channel: str, external_chat_id: str) -> Optional[Dict]:
        """Find conversation by channel and external chat ID"""
        if self.db:
            try:
                cursor = self.db.cursor()
                cursor.execute('''
                    SELECT id, lead_id, channel, external_chat_id, participant_name, 
                           participant_phone, status, last_message_at, created_at, metadata
                    FROM conversations 
                    WHERE channel = %s AND external_chat_id = %s 
                    ORDER BY created_at DESC LIMIT 1
                ''', (channel, external_chat_id))
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0], 'lead_id': row[1], 'channel': row[2],
                        'external_chat_id': row[3], 'participant_name': row[4],
                        'participant_phone': row[5], 'status': row[6],
                        'last_message_at': row[7].isoformat() if row[7] else None,
                        'created_at': row[8].isoformat() if row[8] else None,
                        'metadata': row[9] if row[9] else {}
                    }
            except Exception as e:
                logger.error(f"Error finding conversation: {e}")
        
        for conv in self.conversations.values():
            if conv['channel'] == channel and conv['external_chat_id'] == external_chat_id:
                return conv
        return None
    
    def get_conversations(self, channel: str = None, limit: int = 50) -> List[Dict]:
        """Get all conversations optionally filtered by channel"""
        if self.db:
            try:
                cursor = self.db.cursor()
                if channel:
                    cursor.execute('''
                        SELECT id, lead_id, channel, external_chat_id, participant_name, 
                               participant_phone, status, last_message_at, created_at, metadata
                        FROM conversations WHERE channel = %s
                        ORDER BY last_message_at DESC LIMIT %s
                    ''', (channel, limit))
                else:
                    cursor.execute('''
                        SELECT id, lead_id, channel, external_chat_id, participant_name, 
                               participant_phone, status, last_message_at, created_at, metadata
                        FROM conversations ORDER BY last_message_at DESC LIMIT %s
                    ''', (limit,))
                
                rows = cursor.fetchall()
                return [{
                    'id': row[0], 'lead_id': row[1], 'channel': row[2],
                    'external_chat_id': row[3], 'participant_name': row[4],
                    'participant_phone': row[5], 'status': row[6],
                    'last_message_at': row[7].isoformat() if row[7] else None,
                    'created_at': row[8].isoformat() if row[8] else None,
                    'metadata': row[9] if row[9] else {}
                } for row in rows]
            except Exception as e:
                logger.error(f"Error getting conversations: {e}")
        
        convs = list(self.conversations.values())
        if channel:
            convs = [c for c in convs if c['channel'] == channel]
        return convs[:limit]
    
    def create_message(self, data: Dict) -> Dict:
        """Create a new message"""
        msg_id = self._generate_id('msg')
        message = {
            'id': msg_id,
            'conversation_id': data.get('conversation_id'),
            'channel': data.get('channel', 'unknown'),
            'external_message_id': data.get('external_message_id'),
            'direction': data.get('direction', 'in'),
            'sender_type': data.get('sender_type', 'customer'),
            'sender_id': data.get('sender_id'),
            'sender_name': data.get('sender_name', 'Unknown'),
            'message_type': data.get('message_type', 'text'),
            'content': data.get('content', ''),
            'media_url': data.get('media_url'),
            'media_type': data.get('media_type'),
            'status': data.get('status', 'sent'),
            'read_at': None,
            'created_at': datetime.now().isoformat(),
            'metadata': data.get('metadata', {})
        }
        
        if self.db:
            try:
                cursor = self.db.cursor()
                cursor.execute('''
                    INSERT INTO chat_messages (id, conversation_id, channel, external_message_id, direction,
                                              sender_type, sender_id, sender_name, message_type, content,
                                              media_url, media_type, status, created_at, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (message['id'], message['conversation_id'], message['channel'],
                      message['external_message_id'], message['direction'], message['sender_type'],
                      message['sender_id'], message['sender_name'], message['message_type'],
                      message['content'], message['media_url'], message['media_type'],
                      message['status'], message['created_at'], json.dumps(message['metadata'])))
                
                cursor.execute('''
                    UPDATE conversations SET last_message_at = %s WHERE id = %s
                ''', (message['created_at'], message['conversation_id']))
                
                self.db.commit()
            except Exception as e:
                logger.error(f"Error saving message: {e}")
        
        self.messages[msg_id] = message
        return message
    
    def get_messages(self, conversation_id: str, limit: int = 50) -> List[Dict]:
        """Get messages for a conversation"""
        if self.db:
            try:
                cursor = self.db.cursor()
                cursor.execute('''
                    SELECT id, conversation_id, channel, external_message_id, direction,
                           sender_type, sender_id, sender_name, message_type, content,
                           media_url, media_type, status, read_at, created_at, metadata
                    FROM chat_messages WHERE conversation_id = %s
                    ORDER BY created_at DESC LIMIT %s
                ''', (conversation_id, limit))
                
                rows = cursor.fetchall()
                return [{
                    'id': row[0], 'conversation_id': row[1], 'channel': row[2],
                    'external_message_id': row[3], 'direction': row[4],
                    'sender_type': row[5], 'sender_id': row[6], 'sender_name': row[7],
                    'message_type': row[8], 'content': row[9], 'media_url': row[10],
                    'media_type': row[11], 'status': row[12],
                    'read_at': row[13].isoformat() if row[13] else None,
                    'created_at': row[14].isoformat() if row[14] else None,
                    'metadata': row[15] if row[15] else {}
                } for row in rows]
            except Exception as e:
                logger.error(f"Error getting messages: {e}")
        
        msgs = [m for m in self.messages.values() if m['conversation_id'] == conversation_id]
        return sorted(msgs, key=lambda x: x['created_at'], reverse=True)[:limit]
    
    def get_unread_count(self, channel: str = None) -> int:
        """Get count of unread incoming messages"""
        if self.db:
            try:
                cursor = self.db.cursor()
                if channel:
                    cursor.execute('''
                        SELECT COUNT(*) FROM chat_messages 
                        WHERE read_at IS NULL AND direction = 'in' AND channel = %s
                    ''', (channel,))
                else:
                    cursor.execute('''
                        SELECT COUNT(*) FROM chat_messages 
                        WHERE read_at IS NULL AND direction = 'in'
                    ''')
                return cursor.fetchone()[0]
            except Exception as e:
                logger.error(f"Error getting unread count: {e}")
        
        msgs = [m for m in self.messages.values() if m['direction'] == 'in' and not m['read_at']]
        if channel:
            msgs = [m for m in msgs if m['channel'] == channel]
        return len(msgs)


class TelegramConnector:
    """Telegram Bot API connector"""
    
    def __init__(self):
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.api_base = 'https://api.telegram.org/bot'
        self.is_connected = False
        self.bot_info = None
    
    def connect(self) -> Dict:
        """Test connection to Telegram API"""
        if not self.bot_token:
            return {'success': False, 'error': 'Bot token not configured'}
        
        try:
            response = requests.get(f"{self.api_base}{self.bot_token}/getMe", timeout=10)
            data = response.json()
            
            if data.get('ok'):
                self.is_connected = True
                self.bot_info = data.get('result', {})
                return {'success': True, 'bot_info': self.bot_info}
            return {'success': False, 'error': data.get('description', 'Unknown error')}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_message(self, chat_id: str, message: str, options: Dict = None) -> Dict:
        """Send message via Telegram"""
        if not self.bot_token:
            return {'success': False, 'error': 'Bot token not configured'}
        
        options = options or {}
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': options.get('parse_mode', 'HTML')
        }
        
        try:
            response = requests.post(
                f"{self.api_base}{self.bot_token}/sendMessage",
                json=payload,
                timeout=30
            )
            data = response.json()
            
            if data.get('ok'):
                result = data.get('result', {})
                return {
                    'success': True,
                    'message_id': result.get('message_id'),
                    'external_message_id': str(result.get('message_id'))
                }
            return {'success': False, 'error': data.get('description', 'Failed to send')}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_status(self) -> Dict:
        """Get connector status"""
        return {
            'channel': 'telegram',
            'connected': self.is_connected,
            'bot_token_set': bool(self.bot_token),
            'bot_info': self.bot_info
        }


class WazzupConnector:
    """Wazzup24 API connector for WhatsApp and other channels"""
    
    def __init__(self):
        self.api_key = os.environ.get('WAZZUP_API_KEY')
        self.channel_id = os.environ.get('WAZZUP_CHANNEL_ID')
        self.api_base = 'https://api.wazzup24.com/v3'
        self.is_connected = False
        self.channels = []
    
    def connect(self) -> Dict:
        """Test connection to Wazzup API"""
        if not self.api_key:
            return {'success': False, 'error': 'API key not configured'}
        
        try:
            response = requests.get(
                f"{self.api_base}/channels",
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                self.is_connected = True
                self.channels = response.json()
                return {'success': True, 'channels': self.channels}
            return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_headers(self) -> Dict:
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def send_message(self, chat_id: str, message: str, options: Dict = None) -> Dict:
        """Send message via Wazzup"""
        if not self.api_key:
            return {'success': False, 'error': 'API key not configured'}
        
        options = options or {}
        channel_id = options.get('channel_id', self.channel_id)
        
        if not channel_id:
            return {'success': False, 'error': 'Channel ID not specified'}
        
        payload = {
            'channelId': channel_id,
            'chatId': chat_id,
            'chatType': options.get('chat_type', 'whatsapp'),
            'text': message
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/message",
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    'success': True,
                    'message_id': data.get('messageId'),
                    'external_message_id': data.get('messageId')
                }
            return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_status(self) -> Dict:
        """Get connector status"""
        return {
            'channel': 'wazzup',
            'connected': self.is_connected,
            'api_key_set': bool(self.api_key),
            'channel_id': self.channel_id,
            'channels': self.channels
        }


class MessagingHub:
    """Central hub for unified messaging across all channels"""
    
    def __init__(self):
        self.store = MessageStore()
        self.telegram = TelegramConnector()
        self.wazzup = WazzupConnector()
        self.automation_rules = []
        self.is_initialized = False
    
    def initialize(self) -> Dict:
        """Initialize all connectors"""
        results = {}
        
        if os.environ.get('TELEGRAM_BOT_TOKEN'):
            results['telegram'] = self.telegram.connect()
        else:
            results['telegram'] = {'success': False, 'error': 'Token not configured'}
        
        if os.environ.get('WAZZUP_API_KEY'):
            results['wazzup'] = self.wazzup.connect()
        else:
            results['wazzup'] = {'success': False, 'error': 'API key not configured'}
        
        self.is_initialized = True
        logger.info("MessagingHub initialized")
        return results
    
    def send_message(self, channel: str, chat_id: str, message: str, options: Dict = None) -> Dict:
        """Send message through specified channel"""
        options = options or {}
        
        if channel == 'telegram':
            result = self.telegram.send_message(chat_id, message, options)
        elif channel in ['wazzup', 'whatsapp']:
            result = self.wazzup.send_message(chat_id, message, options)
        else:
            return {'success': False, 'error': f'Unknown channel: {channel}'}
        
        if result.get('success'):
            conversation = self.store.find_conversation(channel, chat_id)
            if not conversation:
                conversation = self.store.create_conversation({
                    'channel': channel,
                    'external_chat_id': chat_id,
                    'participant_name': options.get('participant_name', 'Unknown')
                })
            
            self.store.create_message({
                'conversation_id': conversation['id'],
                'channel': channel,
                'external_message_id': result.get('external_message_id'),
                'direction': 'out',
                'sender_type': 'agent',
                'sender_name': options.get('agent_name', 'System'),
                'content': message
            })
        
        return result
    
    def handle_incoming_message(self, channel: str, raw_message: Dict) -> Dict:
        """Handle incoming message from any channel"""
        normalized = self._normalize_message(channel, raw_message)
        
        conversation = self.store.find_conversation(channel, normalized['external_chat_id'])
        if not conversation:
            conversation = self.store.create_conversation({
                'channel': channel,
                'external_chat_id': normalized['external_chat_id'],
                'participant_name': normalized['sender_name'],
                'participant_phone': normalized.get('sender_phone')
            })
        
        saved_message = self.store.create_message({
            'conversation_id': conversation['id'],
            'channel': channel,
            'external_message_id': normalized['external_message_id'],
            'direction': 'in',
            'sender_type': 'customer',
            'sender_id': normalized['sender_id'],
            'sender_name': normalized['sender_name'],
            'message_type': normalized.get('message_type', 'text'),
            'content': normalized['content'],
            'media_url': normalized.get('media_url'),
            'metadata': normalized.get('metadata', {})
        })
        
        return {
            'success': True,
            'message': saved_message,
            'conversation': conversation
        }
    
    def _normalize_message(self, channel: str, raw: Dict) -> Dict:
        """Normalize message from different channel formats"""
        if channel == 'telegram':
            message = raw.get('message', raw)
            sender = message.get('from', {})
            chat = message.get('chat', {})
            return {
                'external_message_id': str(message.get('message_id', '')),
                'external_chat_id': str(chat.get('id', '')),
                'sender_id': str(sender.get('id', '')),
                'sender_name': f"{sender.get('first_name', '')} {sender.get('last_name', '')}".strip() or 'Unknown',
                'content': message.get('text', ''),
                'message_type': 'text',
                'metadata': {'update_id': raw.get('update_id')}
            }
        elif channel in ['wazzup', 'whatsapp']:
            return {
                'external_message_id': raw.get('messageId', raw.get('id', '')),
                'external_chat_id': raw.get('chatId', ''),
                'sender_id': raw.get('chatId', ''),
                'sender_name': raw.get('name', raw.get('chatId', 'Unknown')),
                'sender_phone': raw.get('chatId'),
                'content': raw.get('text', ''),
                'message_type': 'text',
                'metadata': {'channel_id': raw.get('channelId')}
            }
        return raw
    
    def get_conversations(self, channel: str = None, limit: int = 50) -> List[Dict]:
        return self.store.get_conversations(channel, limit)
    
    def get_messages(self, conversation_id: str, limit: int = 50) -> List[Dict]:
        return self.store.get_messages(conversation_id, limit)
    
    def get_unread_count(self, channel: str = None) -> int:
        return self.store.get_unread_count(channel)
    
    def get_status(self) -> Dict:
        return {
            'initialized': self.is_initialized,
            'connectors': {
                'telegram': self.telegram.get_status(),
                'wazzup': self.wazzup.get_status()
            },
            'automation_rules': len(self.automation_rules)
        }
    
    def get_channel_stats(self) -> Dict:
        channels = ['telegram', 'whatsapp', 'wazzup']
        stats = {}
        for channel in channels:
            convs = self.store.get_conversations(channel)
            unread = self.store.get_unread_count(channel)
            stats[channel] = {
                'total_conversations': len(convs),
                'unread_messages': unread,
                'status': 'active'
            }
        return stats


# Global instance
messaging_hub = MessagingHub()