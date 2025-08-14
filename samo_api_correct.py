"""
Правильная интеграция SAMO API согласно официальной документации
https://dokuwiki.samo.ru/doku.php?id=onlinest:api
"""
import logging
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class SamoAPIClient:
    """Правильная интеграция SAMO API согласно официальной документации"""
    
    def __init__(self, api_url: Optional[str] = None, oauth_token: Optional[str] = None):
        """
        Инициализация SAMO API клиента
        
        Args:
            api_url: URL API endpoint (например, https://touroperator.ru/samo/export/default.php)
            oauth_token: OAuth токен для авторизации
        """
        # Загрузка настроек из базы данных
        try:
            from models import SettingsService
            settings_service = SettingsService()
            settings = settings_service.get_samo_settings()
            
            self.api_url = api_url or settings.get('api_url', 'https://booking.crystalbay.com/export/default.php')
            self.oauth_token = oauth_token or settings.get('oauth_token', '27bd59a7ac67422189789f0188167379')
            self.timeout = int(settings.get('timeout', 30))
            self.user_agent = settings.get('user_agent', 'Crystal Bay Travel Integration/1.0')
        except Exception as e:
            logger.warning(f"Cannot load settings from database: {e}")
            self.api_url = api_url or 'https://booking.crystalbay.com/export/default.php'
            self.oauth_token = oauth_token or '27bd59a7ac67422189789f0188167379'
            self.timeout = 30
            self.user_agent = 'Crystal Bay Travel Integration/1.0'
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        
        logger.info(f"SAMO API клиент инициализирован: {self.api_url}")

    def make_request(self, action: str, additional_params: Optional[Dict[str, Any]] = None, method: str = 'GET') -> Dict[str, Any]:
        """
        Выполнить запрос к SAMO API согласно официальной документации
        
        Формат запроса согласно документации:
        GET/POST {api_url}?samo_action=api&version=1.0&oauth_token=xxx&type=json&action=xxx
        
        Args:
            action: Метод API (например, 'SearchTour_CURRENCIES')
            additional_params: Дополнительные параметры
            method: HTTP метод (GET или POST)
            
        Returns:
            dict: Ответ API или словарь с ошибкой
        """
        try:
            # Базовые обязательные параметры согласно документации
            params = {
                'samo_action': 'api',
                'version': '1.0',
                'oauth_token': self.oauth_token,
                'type': 'json',
                'action': action
            }
            
            # Добавление дополнительных параметров
            if additional_params:
                params.update(additional_params)
            
            # Логирование запроса
            logger.info(f"SAMO API запрос: {method} {action}")
            logger.info(f"URL: {self.api_url}")
            logger.info(f"Параметры: {json.dumps(params, ensure_ascii=False, indent=2)}")
            
            # Выполнение запроса
            if method.upper() == 'POST':
                response = self.session.post(
                    self.api_url,
                    data=params,
                    timeout=self.timeout
                )
            else:
                response = self.session.get(
                    self.api_url,
                    params=params,
                    timeout=self.timeout
                )
            
            logger.info(f"SAMO API ответ: {response.status_code} {response.reason}")
            
            # Обработка ответа
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Проверка формата ошибки согласно документации
                    if isinstance(data, dict) and 'error' in data:
                        error_code = data.get('error')
                        error_message = data.get('message', f'Код ошибки: {error_code}')
                        logger.error(f"SAMO API ошибка {action}: {error_code} - {error_message}")
                        return {'error': error_message, 'error_code': error_code}
                    
                    logger.info(f"SAMO API успешный ответ {action}: {len(str(data))} символов")
                    return data
                    
                except json.JSONDecodeError as e:
                    logger.error(f"SAMO API ошибка парсинга JSON {action}: {e}")
                    logger.error(f"Ответ сервера: {response.text[:500]}...")
                    return {'error': f'Ошибка парсинга JSON: {e}'}
                    
            elif response.status_code == 403:
                logger.error(f"SAMO API 403 Forbidden {action}: Проверьте IP whitelist и OAuth токен")
                return {'error': '403 Forbidden: IP не в whitelist или неверный OAuth токен'}
                
            elif response.status_code == 404:
                logger.error(f"SAMO API 404 Not Found {action}: Проверьте URL и метод API")
                return {'error': '404 Not Found: Неверный URL или метод API'}
                
            else:
                logger.error(f"SAMO API HTTP ошибка {action}: {response.status_code} {response.reason}")
                return {'error': f'HTTP {response.status_code}: {response.reason}'}
                
        except requests.exceptions.Timeout:
            logger.error(f"SAMO API таймаут {action}")
            return {'error': f'Таймаут запроса ({self.timeout}s)'}
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"SAMO API ошибка подключения {action}: {e}")
            return {'error': f'Ошибка подключения: {e}'}
            
        except Exception as e:
            logger.error(f"SAMO API неожиданная ошибка {action}: {e}")
            return {'error': f'Неожиданная ошибка: {e}'}

    # Методы справочников согласно документации
    
    def get_currencies(self) -> Dict[str, Any]:
        """Получить список валют"""
        return self.make_request('SearchTour_CURRENCIES')
    
    def get_town_froms(self) -> Dict[str, Any]:
        """Получить список городов отправления"""
        return self.make_request('SearchTour_TOWNFROMS')
    
    def get_states(self) -> Dict[str, Any]:
        """Получить список стран"""
        return self.make_request('SearchTour_STATES')
    
    def get_tours(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Получить список туров"""
        return self.make_request('SearchTour_TOURS', params)
    
    def search_tour_prices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Поиск цен на туры согласно документации SAMO API
        
        Обязательные параметры:
        - STATEINC: ID страны
        - TOWNFROMINC: ID города отправления  
        - CHECKIN_BEG/CHECKIN_END: диапазон дат заезда (YYYYMMDD)
        - NIGHTS_FROM/NIGHTS_TILL: диапазон количества ночей
        - ADULT: количество взрослых
        - CHILD: количество детей
        - CURRENCY: ID валюты
        - PRICEPAGE: номер страницы (по умолчанию 1)
        """
        return self.make_request('SearchTour_PRICES', params)
    
    def get_hotels(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Получить список отелей"""
        return self.make_request('SearchTour_HOTELS', params)
    
    def get_programs(self) -> Dict[str, Any]:
        """Получить список программ туров"""
        return self.make_request('SearchTour_PROGRAMS')
    
    def get_meals(self) -> Dict[str, Any]:
        """Получить список типов питания"""
        return self.make_request('SearchTour_MEALS')
    
    def get_stars(self) -> Dict[str, Any]:
        """Получить список звездности отелей"""
        return self.make_request('SearchTour_STARS')
    
    # Тестирование подключения
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Тестирование подключения к SAMO API
        Использует метод получения валют как простой тест
        """
        logger.info("Тестирование подключения к SAMO API...")
        result = self.get_currencies()
        
        if 'error' not in result:
            logger.info("SAMO API подключение успешно!")
            return {'success': True, 'message': 'Подключение к SAMO API успешно'}
        else:
            logger.error(f"SAMO API подключение неуспешно: {result.get('error')}")
            return {'success': False, 'error': result.get('error')}

    # Утилиты для отладки
    
    def get_api_info(self) -> Dict[str, Any]:
        """Получить информацию о настройках API"""
        return {
            'api_url': self.api_url,
            'oauth_token': f"{self.oauth_token[:8]}..." if self.oauth_token else None,
            'timeout': self.timeout,
            'user_agent': self.user_agent
        }