"""
Free WhatsApp Web Connector
Alternative to paid services like Wazzup24
Uses QR code authentication like WhatsApp Web

This module provides a framework for WhatsApp integration without subscription fees.
For production use, you would need to self-host a whatsapp-web.js server.
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class WhatsAppWebConnector:
    """
    Free WhatsApp connector using WhatsApp Web API approach.
    
    Options for production deployment:
    1. Evolution API (https://github.com/EvolutionAPI/evolution-api) - Free, self-hosted
    2. whatsapp-web.js REST API (https://github.com/chrishubert/whatsapp-api) - Free, Docker
    3. GREEN-API (https://green-api.com) - Low-cost alternative
    
    This connector abstracts the API calls so you can switch between providers.
    """
    
    PROVIDER_EVOLUTION = 'evolution'
    PROVIDER_WWJS = 'whatsapp-web-js'
    PROVIDER_GREEN_API = 'green-api'
    PROVIDER_DEMO = 'demo'
    
    def __init__(self):
        self.is_connected = False
        self.qr_code = None
        self.session_info = {}
    
    def _get_api_url(self) -> str:
        return os.environ.get('WHATSAPP_API_URL', '')
    
    def _get_api_key(self) -> str:
        return os.environ.get('WHATSAPP_API_KEY', '')
    
    def _get_instance_id(self) -> str:
        return os.environ.get('WHATSAPP_INSTANCE_ID', 'default')
    
    def _get_provider(self) -> str:
        return os.environ.get('WHATSAPP_PROVIDER', self.PROVIDER_DEMO)
        
    def get_status(self) -> Dict:
        """Get current connector status"""
        return {
            'channel': 'whatsapp',
            'provider': self._get_provider(),
            'connected': self.is_connected,
            'api_configured': bool(self._get_api_url() and self._get_api_key()),
            'instance_id': self._get_instance_id(),
            'session_info': self.session_info,
            'qr_available': bool(self.qr_code),
            'free_options': self._get_free_options_info()
        }
    
    def _get_free_options_info(self) -> List[Dict]:
        """Return list of free WhatsApp API options"""
        return [
            {
                'name': 'Evolution API',
                'url': 'https://github.com/EvolutionAPI/evolution-api',
                'type': 'self-hosted',
                'cost': 'Free (self-hosted)',
                'description': 'Open-source WhatsApp Web API with full features'
            },
            {
                'name': 'whatsapp-web.js',
                'url': 'https://github.com/chrishubert/whatsapp-api',
                'type': 'docker',
                'cost': 'Free (Docker)',
                'description': 'REST API wrapper for WhatsApp Web'
            },
            {
                'name': 'GREEN-API',
                'url': 'https://green-api.com',
                'type': 'cloud',
                'cost': 'Low-cost',
                'description': 'Affordable WhatsApp API service'
            },
            {
                'name': 'CallMeBot',
                'url': 'https://www.callmebot.com/blog/free-api-whatsapp-messages/',
                'type': 'cloud',
                'cost': 'Free (personal)',
                'description': 'Free API for personal notifications'
            }
        ]
    
    def connect(self) -> Dict:
        """Initialize connection to WhatsApp"""
        provider = self._get_provider()
        api_url = self._get_api_url()
        
        if provider == self.PROVIDER_DEMO:
            return self._demo_connect()
        
        if not api_url:
            return {
                'success': False,
                'error': 'API URL not configured',
                'hint': 'Set WHATSAPP_API_URL environment variable'
            }
        
        try:
            if provider == self.PROVIDER_EVOLUTION:
                return self._evolution_connect()
            elif provider == self.PROVIDER_WWJS:
                return self._wwjs_connect()
            elif provider == self.PROVIDER_GREEN_API:
                return self._green_api_connect()
            else:
                return self._demo_connect()
        except Exception as e:
            logger.error(f"WhatsApp connect error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _demo_connect(self) -> Dict:
        """Demo mode - simulates connection for UI testing"""
        self.is_connected = False
        self.session_info = {
            'mode': 'demo',
            'message': 'Демо режим - подключите реальный WhatsApp API'
        }
        return {
            'success': True,
            'mode': 'demo',
            'message': 'Демо режим активен. Для реального подключения настройте один из бесплатных провайдеров.',
            'free_options': self._get_free_options_info()
        }
    
    def _evolution_connect(self) -> Dict:
        """Connect using Evolution API"""
        try:
            headers = {'apikey': self._get_api_key()}
            response = requests.get(
                f"{self._get_api_url()}/instance/fetchInstances",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                instances = response.json()
                self.is_connected = True
                self.session_info = {'instances': instances}
                return {'success': True, 'instances': instances}
            
            return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _wwjs_connect(self) -> Dict:
        """Connect using whatsapp-web.js REST API"""
        try:
            headers = {'X-API-Key': self._get_api_key()}
            response = requests.get(
                f"{self._get_api_url()}/client/status/{self._get_instance_id()}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.is_connected = data.get('status') == 'CONNECTED'
                self.session_info = data
                return {'success': True, 'status': data}
            
            return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _green_api_connect(self) -> Dict:
        """Connect using GREEN-API"""
        try:
            response = requests.get(
                f"{self._get_api_url()}/waInstance{self._get_instance_id()}/getStateInstance/{self._get_api_key()}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.is_connected = data.get('stateInstance') == 'authorized'
                self.session_info = data
                return {'success': True, 'status': data}
            
            return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_qr_code(self) -> Dict:
        """Get QR code for WhatsApp Web authentication"""
        provider = self._get_provider()
        if provider == self.PROVIDER_DEMO:
            return {
                'success': True,
                'qr_code': None,
                'message': 'В демо режиме QR код недоступен. Настройте реальный провайдер.',
                'setup_instructions': self._get_setup_instructions()
            }
        
        try:
            if provider == self.PROVIDER_EVOLUTION:
                return self._evolution_get_qr()
            elif provider == self.PROVIDER_WWJS:
                return self._wwjs_get_qr()
            elif provider == self.PROVIDER_GREEN_API:
                return self._green_api_get_qr()
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
        return {'success': False, 'error': 'Unknown provider'}
    
    def _evolution_get_qr(self) -> Dict:
        headers = {'apikey': self._get_api_key()}
        response = requests.get(
            f"{self._get_api_url()}/instance/connect/{self._get_instance_id()}",
            headers=headers,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            self.qr_code = data.get('qrcode', {}).get('base64')
            return {'success': True, 'qr_code': self.qr_code}
        return {'success': False, 'error': f'HTTP {response.status_code}'}
    
    def _wwjs_get_qr(self) -> Dict:
        headers = {'X-API-Key': self._get_api_key()}
        response = requests.get(
            f"{self._get_api_url()}/client/getQR/{self._get_instance_id()}",
            headers=headers,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            self.qr_code = data.get('qrCode')
            return {'success': True, 'qr_code': self.qr_code}
        return {'success': False, 'error': f'HTTP {response.status_code}'}
    
    def _green_api_get_qr(self) -> Dict:
        response = requests.get(
            f"{self._get_api_url()}/waInstance{self._get_instance_id()}/qr/{self._get_api_key()}",
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            self.qr_code = data.get('message')
            return {'success': True, 'qr_code': self.qr_code}
        return {'success': False, 'error': f'HTTP {response.status_code}'}
    
    def send_message(self, chat_id: str, message: str, options: Dict = None) -> Dict:
        """Send message via WhatsApp"""
        provider = self._get_provider()
        if provider == self.PROVIDER_DEMO:
            return {
                'success': False,
                'error': 'Демо режим - отправка сообщений недоступна',
                'hint': 'Настройте реальный WhatsApp провайдер для отправки сообщений'
            }
        
        options = options or {}
        
        try:
            if provider == self.PROVIDER_EVOLUTION:
                return self._evolution_send_message(chat_id, message, options)
            elif provider == self.PROVIDER_WWJS:
                return self._wwjs_send_message(chat_id, message, options)
            elif provider == self.PROVIDER_GREEN_API:
                return self._green_api_send_message(chat_id, message, options)
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
        return {'success': False, 'error': 'Unknown provider'}
    
    def _evolution_send_message(self, chat_id: str, message: str, options: Dict) -> Dict:
        headers = {
            'apikey': self._get_api_key(),
            'Content-Type': 'application/json'
        }
        payload = {
            'number': chat_id,
            'text': message
        }
        response = requests.post(
            f"{self._get_api_url()}/message/sendText/{self._get_instance_id()}",
            headers=headers,
            json=payload,
            timeout=30
        )
        if response.status_code in [200, 201]:
            data = response.json()
            return {
                'success': True,
                'message_id': data.get('key', {}).get('id'),
                'external_message_id': data.get('key', {}).get('id')
            }
        return {'success': False, 'error': f'HTTP {response.status_code}'}
    
    def _wwjs_send_message(self, chat_id: str, message: str, options: Dict) -> Dict:
        headers = {
            'X-API-Key': self._get_api_key(),
            'Content-Type': 'application/json'
        }
        payload = {
            'chatId': chat_id if '@' in chat_id else f"{chat_id}@c.us",
            'message': message
        }
        response = requests.post(
            f"{self._get_api_url()}/client/sendMessage/{self._get_instance_id()}",
            headers=headers,
            json=payload,
            timeout=30
        )
        if response.status_code in [200, 201]:
            data = response.json()
            return {
                'success': True,
                'message_id': data.get('id', {}).get('_serialized'),
                'external_message_id': data.get('id', {}).get('_serialized')
            }
        return {'success': False, 'error': f'HTTP {response.status_code}'}
    
    def _green_api_send_message(self, chat_id: str, message: str, options: Dict) -> Dict:
        payload = {
            'chatId': chat_id if '@' in chat_id else f"{chat_id}@c.us",
            'message': message
        }
        response = requests.post(
            f"{self._get_api_url()}/waInstance{self._get_instance_id()}/sendMessage/{self._get_api_key()}",
            json=payload,
            timeout=30
        )
        if response.status_code in [200, 201]:
            data = response.json()
            return {
                'success': True,
                'message_id': data.get('idMessage'),
                'external_message_id': data.get('idMessage')
            }
        return {'success': False, 'error': f'HTTP {response.status_code}'}
    
    def _get_setup_instructions(self) -> Dict:
        """Get setup instructions for free WhatsApp integration"""
        return {
            'title': 'Бесплатная интеграция WhatsApp',
            'options': [
                {
                    'name': 'Evolution API (Рекомендуется)',
                    'steps': [
                        '1. Установите Docker на сервер',
                        '2. Запустите: docker run -d -p 8080:8080 atendai/evolution-api',
                        '3. Откройте http://your-server:8080 и создайте instance',
                        '4. Отсканируйте QR код в WhatsApp',
                        '5. Добавьте переменные: WHATSAPP_API_URL, WHATSAPP_API_KEY, WHATSAPP_PROVIDER=evolution'
                    ],
                    'docker_command': 'docker run -d --name evolution-api -p 8080:8080 atendai/evolution-api'
                },
                {
                    'name': 'whatsapp-web.js',
                    'steps': [
                        '1. Установите Docker',
                        '2. Запустите: docker run -p 3000:3000 chrishubert/whatsapp-api',
                        '3. Отсканируйте QR код из логов',
                        '4. Добавьте переменные: WHATSAPP_API_URL, WHATSAPP_PROVIDER=whatsapp-web-js'
                    ],
                    'docker_command': 'docker run -d -p 3000:3000 -e API_KEY=your-key chrishubert/whatsapp-api'
                }
            ],
            'note': 'Все решения бесплатны и требуют только сервер для хостинга'
        }


whatsapp_connector = WhatsAppWebConnector()
