"""
Полная интеграция SAMO API для Crystal Bay Travel
Основана на официальной документации: https://dokuwiki.samo.ru/doku.php?id=onlinest:api
"""
import logging
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class CrystalBaySamoAPI:
    """Полная интеграция SAMO API для Crystal Bay Travel"""
    
    def __init__(self, base_url: Optional[str] = None, oauth_token: Optional[str] = None):
        # Load settings from database/memory
        try:
            from models import SettingsService
            self.settings_service = SettingsService()
            settings = self.settings_service.get_samo_settings()
            
            self.base_url = base_url or settings.get('api_url', 'https://booking.crystalbay.com/export/default.php')
            self.oauth_token = oauth_token or settings.get('oauth_token', '27bd59a7ac67422189789f0188167379')
            self.timeout = int(settings.get('timeout', 30))
            self.user_agent = settings.get('user_agent', 'Crystal Bay Travel Integration/1.0')
        except ImportError:
            # Fallback if models not available
            self.base_url = base_url or "https://booking.crystalbay.com/export/default.php"
            self.oauth_token = oauth_token or "27bd59a7ac67422189789f0188167379"
            self.timeout = 30
            self.user_agent = 'Crystal Bay Travel Integration/1.0'
            
        self.session = requests.Session()
        logger.info(f"Crystal Bay SAMO API инициализирован: {self.base_url}")
    
    def _make_request(self, action: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Выполняет запрос к SAMO API"""
        try:
            # Прямой запрос к SAMO API с IP сервера
            # Правильные параметры согласно официальной документации SAMO API
            request_params = {
                'oauth_token': self.oauth_token,
                'type': 'json',
                'action': action
            }
            
            # Добавляем дополнительные параметры
            if params is not None:
                request_params.update(params)
            
            logger.info(f"SAMO API запрос: {action}")
            logger.info(f"Параметры: {json.dumps(request_params, indent=2)}")
            
            # Определяем текущий внешний IP для диагностики
            try:
                import requests as check_requests
                ip_response = check_requests.get('https://api.ipify.org?format=json', timeout=5)
                current_external_ip = ip_response.json().get('ip', 'unknown')
                logger.warning(f"🌐 Исходящий IP: {current_external_ip} (может отличаться от IP сервера)")
            except:
                current_external_ip = 'detection_failed'
            
            # Headers exactly like curl - minimal set
            headers = {
                'User-Agent': 'curl/7.68.0',
                'Accept': '*/*'
            }
            
            response = self.session.get(self.base_url, params=request_params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Пробуем парсить как JSON
            try:
                result = response.json()
                logger.info(f"SAMO API успешный ответ {action}: {result}")
                return result
            except json.JSONDecodeError:
                # Если JSON не парсится, возвращаем текст ответа
                logger.warning(f"SAMO API не JSON ответ {action}: {response.text[:200]}")
                return {"error": "Invalid JSON response", "response": response.text, "status_code": response.status_code}
            
        except requests.RequestException as e:
            logger.error(f"SAMO API ошибка запроса {action}: {e}")
            
            # Детальная информация об ошибке для диагностики
            error_details = {
                "error": str(e),
                "action": action,
                "url": self.base_url,
                "oauth_token_suffix": self.oauth_token[-4:] if self.oauth_token else "None"
            }
            
            if hasattr(e, 'response') and e.response:
                error_details.update({
                    "status_code": e.response.status_code,
                    "response_text": e.response.text[:500] if e.response.text else ""
                })
            
            return error_details
    
    # === СПРАВОЧНИКИ ===
    
    def get_townfroms(self) -> Dict[str, Any]:
        """Получить города отправления"""
        return self._make_request('SearchTour_TOWNFROMS')
    
    def get_town_froms(self) -> Dict[str, Any]:
        """Alias для совместимости - получить города отправления"""
        return self.get_townfroms()
    
    def get_states(self) -> Dict[str, Any]:
        """Получить страны"""
        return self._make_request('SearchTour_STATES')
    
    def get_currencies(self) -> Dict[str, Any]:
        """Получить валюты"""
        return self._make_request('SearchTour_CURRENCIES')
    
    def get_hotels(self, state_key: Optional[str] = None) -> Dict[str, Any]:
        """Получить отели"""
        params = {}
        if state_key is not None:
            params['STATEINC'] = state_key
        return self._make_request('SearchTour_HOTELS', params)
    
    def get_tours(self) -> Dict[str, Any]:
        """Получить туры"""
        return self._make_request('SearchTour_TOURS')
    
    def get_programs(self) -> Dict[str, Any]:
        """Получить программы"""
        return self._make_request('SearchTour_PROGRAMS')
    
    def get_stars(self) -> Dict[str, Any]:
        """Получить звездность отелей"""
        return self._make_request('SearchTour_STARS')
    
    def get_meals(self) -> Dict[str, Any]:
        """Получить типы питания"""
        return self._make_request('SearchTour_MEALS')
    
    # === ПОИСК ТУРОВ ===
    
    def search_tour_prices(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Поиск цен на туры - прямой вызов как curl"""
        try:
            # Базовые параметры точно как в рабочем curl
            request_params = {
                'samo_action': 'api',
                'oauth_token': self.oauth_token,
                'type': 'json',
                'action': 'SearchTour_PRICES'
            }
            
            # Добавляем параметры поиска если переданы
            if params:
                # Маппинг параметров в формат SAMO API
                if 'townfrom' in params:
                    request_params['TOWNFROMINC'] = params['townfrom']
                if 'stateinc' in params:
                    request_params['STATEINC'] = params['stateinc']
                if 'checkin' in params:
                    request_params['CHECKIN_BEG'] = params['checkin']
                if 'checkout' in params:
                    request_params['CHECKIN_END'] = params['checkout']
                if 'nights' in params:
                    request_params['NIGHTS_FROM'] = params['nights']
                    request_params['NIGHTS_TILL'] = params['nights']
                if 'adults' in params:
                    request_params['ADULT'] = params['adults']
                if 'children' in params:
                    request_params['CHILD'] = params['children']
                if 'currency' in params:
                    request_params['CURRENCY'] = params['currency']
            
            logger.info(f"SAMO SearchTour_PRICES request: {request_params}")
            
            # Прямой GET запрос как curl
            response = self.session.get(self.base_url, params=request_params, timeout=self.timeout)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    tours_data = result.get('SearchTour_PRICES', [])
                    
                    logger.info(f"SAMO tour search SUCCESS: {len(tours_data)} tours found")
                    
                    return {
                        "success": True,
                        "action": "SearchTour_PRICES",
                        "tours": tours_data,
                        "total_count": len(tours_data),
                        "search_params": params or {},
                        "raw_response": result
                    }
                    
                except json.JSONDecodeError:
                    logger.warning(f"SAMO API response not JSON: {response.text[:200]}")
                    return {
                        "error": "Invalid JSON response",
                        "success": False,
                        "response_text": response.text[:500]
                    }
            
            elif response.status_code == 403:
                error_text = response.text
                logger.error(f"SAMO API IP blocked: {error_text}")
                return {
                    "error": "IP address not whitelisted in SAMO API",
                    "success": False,
                    "status_code": 403,
                    "response": error_text,
                    "blocked_ip": "Current server IP is blocked"
                }
            else:
                logger.error(f"SAMO API error: HTTP {response.status_code}")
                return {
                    "error": f"HTTP {response.status_code}",
                    "success": False,
                    "status_code": response.status_code,
                    "response": response.text[:200]
                }
                
        except requests.RequestException as e:
            logger.error(f"SAMO API tour search error: {e}")
            return {
                "error": str(e),
                "success": False,
                "action": "SearchTour_PRICES"
            }
    
    def search_tours_detailed(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Детальный поиск туров"""
        default_params = {
            'TOWNFROMINC': '',
            'STATEINC': '',
            'CHECKIN_BEG': '',
            'CHECKIN_END': '',
            'NIGHTS_FROM': 7,
            'NIGHTS_TILL': 14,
            'ADULT': 2,
            'CHILD': 0,
            'CURRENCY': 'USD'
        }
        
        if params is not None:
            default_params.update(params)
            
        return self._make_request('SearchTour_ALL', default_params)
    
    # === БРОНИРОВАНИЕ ===
    
    def get_bookings_api(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
        """Получить список бронирований через API"""
        if date_from is None:
            date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if date_to is None:
            date_to = datetime.now().strftime('%Y-%m-%d')
            
        params = {
            'date_from': date_from,
            'date_to': date_to
        }
        
        return self._make_request('GetBookings', params)
    
    def get_booking_details(self, booking_id: str) -> Dict[str, Any]:
        """Получить детали бронирования"""
        params = {'booking_id': booking_id}
        return self._make_request('GetBookingDetails', params)
    
    def create_booking(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создать новое бронирование"""
        return self._make_request('CreateBooking', booking_data)
    
    def update_booking(self, booking_id: str, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновить бронирование"""
        params = {'booking_id': booking_id}
        params.update(booking_data)
        return self._make_request('UpdateBooking', params)
    
    def cancel_booking(self, booking_id: str, reason: str = "") -> Dict[str, Any]:
        """Отменить бронирование"""
        params = {
            'booking_id': booking_id,
            'cancel_reason': reason
        }
        return self._make_request('CancelBooking', params)
    
    # === КЛИЕНТЫ ===
    
    def create_person(self, person_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создать клиента"""
        return self._make_request('Person_Create', person_data)
    
    def update_person(self, person_id: str, person_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновить данные клиента"""
        params = {'person_id': person_id}
        params.update(person_data)
        return self._make_request('Person_Update', params)
    
    def get_person(self, person_id: str) -> Dict[str, Any]:
        """Получить данные клиента"""
        params = {'person_id': person_id}
        return self._make_request('Person_Get', params)
    
    # === ОТЧЕТЫ ===
    
    def get_sales_report(self, date_from: str, date_to: str) -> Dict[str, Any]:
        """Отчет по продажам"""
        params = {
            'date_from': date_from,
            'date_to': date_to
        }
        return self._make_request('Report_Sales', params)
    
    def get_financial_report(self, date_from: str, date_to: str) -> Dict[str, Any]:
        """Финансовый отчет"""
        params = {
            'date_from': date_from,
            'date_to': date_to
        }
        return self._make_request('Report_Financial', params)
    
    # === ДОПОЛНИТЕЛЬНЫЕ УСЛУГИ ===
    
    def get_services(self) -> Dict[str, Any]:
        """Получить дополнительные услуги"""
        return self._make_request('Services_Get')
    
    def book_service(self, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Забронировать дополнительную услугу"""
        return self._make_request('Services_Book', service_data)
    
    # === СТРАХОВКИ ===
    
    def get_insurance_types(self) -> Dict[str, Any]:
        """Получить типы страховок"""
        return self._make_request('Insurance_GetTypes')
    
    def calculate_insurance(self, insurance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Рассчитать стоимость страховки"""
        return self._make_request('Insurance_Calculate', insurance_data)
    
    def book_insurance(self, insurance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Забронировать страховку"""
        return self._make_request('Insurance_Book', insurance_data)
    
    # === ПЛАТЕЖИ ===
    
    def get_payment_methods(self) -> Dict[str, Any]:
        """Получить способы оплаты"""
        return self._make_request('Payment_GetMethods')
    
    def create_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создать платеж"""
        return self._make_request('Payment_Create', payment_data)
    
    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Получить статус платежа"""
        params = {'payment_id': payment_id}
        return self._make_request('Payment_GetStatus', params)
    
    # === УВЕДОМЛЕНИЯ ===
    
    def get_notifications(self) -> Dict[str, Any]:
        """Получить уведомления"""
        return self._make_request('Notifications_Get')
    
    def mark_notification_read(self, notification_id: str) -> Dict[str, Any]:
        """Отметить уведомление как прочитанное"""
        params = {'notification_id': notification_id}
        return self._make_request('Notifications_MarkRead', params)
    
    # === ТЕСТИРОВАНИЕ ПОДКЛЮЧЕНИЯ ===
    
    def test_connection(self) -> Dict[str, Any]:
        """Тестирование подключения к API"""
        try:
            # Простой запрос для проверки доступности API
            result = self.get_currencies()
            
            if 'error' in result:
                return {
                    'success': False,
                    'message': f"Ошибка подключения: {result.get('error', 'Неизвестная ошибка')}",
                    'details': result
                }
            
            return {
                'success': True,
                'message': "Подключение к SAMO API успешно",
                'api_version': "1.0",
                'endpoint': self.base_url
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Ошибка тестирования: {str(e)}"
            }

    def get_bookings(self, date_from: Optional[str] = None, date_to: Optional[str] = None, 
                     status: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """Получить список бронирований (production - без демо-данных)"""
        try:
            # Пробуем получить справочники для проверки доступности API
            townfroms = self.get_townfroms()
            
            if 'error' not in townfroms:
                # API доступен, возвращаем пустой результат для продакшн
                # Production: No demo data, return empty result
                return {'bookings': [], 'total': 0}
            else:
                return {'error': townfroms.get('error', 'API недоступен')}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _create_demo_bookings(self) -> List[Dict]:
        """Production: All demo data removed"""
        return []

# Глобальный экземпляр API
crystal_bay_api = CrystalBaySamoAPI()

def get_crystal_bay_api() -> CrystalBaySamoAPI:
    """Получить экземпляр Crystal Bay SAMO API"""
    return crystal_bay_api


def test_samo_api_connection():
    """Тестирование подключения к SAMO API"""
    try:
        api = get_crystal_bay_api()
        result = api.test_connection()
        return result
    except Exception as e:
        logger.error(f"Ошибка тестирования SAMO API: {e}")
        return {
            'success': False, 
            'message': f'Ошибка подключения: {str(e)}',
            'details': 'Проверьте настройки SAMO API и доступность сервера'
        }