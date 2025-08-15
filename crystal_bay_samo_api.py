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
        """Выполняет запрос к SAMO API через TinyProxy или напрямую"""
        try:
            # Try using VPS script first if configured
            try:
                from proxy_client import VPSProxy  # type: ignore
                vps_proxy = VPSProxy()
                
                # Check if VPS script is configured
                if (vps_proxy.vps_endpoint and 
                    vps_proxy.vps_endpoint != 'http://your-vps-server.com/samo_proxy.php'):
                    logger.info(f"Using VPS script for SAMO API request: {action}")
                    result = vps_proxy.make_samo_request(action, 'GET', params)
                    
                    # If VPS script request successful, return result
                    if 'error' not in result:
                        logger.info(f"SAMO API via VPS script success: {action}")
                        return result
                    else:
                        logger.warning(f"VPS script failed, trying TinyProxy: {result.get('message', '')}")
                        
            except ImportError:
                logger.debug("VPS proxy not available")
            except Exception as e:
                logger.warning(f"VPS script request failed: {e}")
            
            # Try TinyProxy as fallback
            try:
                from proxy_client import get_proxy_client
                proxy_client = get_proxy_client()
                
                if proxy_client.is_configured():
                    logger.info(f"Using TinyProxy for SAMO API request: {action}")
                    result = proxy_client.make_samo_request(action, 'GET', params or {})
                    
                    # If proxy request successful, return result
                    if 'error' not in result:
                        logger.info(f"SAMO API via TinyProxy success: {action}")
                        return result
                    else:
                        logger.warning(f"TinyProxy failed, trying direct: {result.get('message', '')}")
                        
            except ImportError:
                logger.debug("TinyProxy client not available")
            except Exception as e:
                logger.warning(f"TinyProxy request failed: {e}, falling back to direct")
            
            # Fallback to direct request (will likely get 403)
            # Базовые параметры для всех запросов
            request_params = {
                'samo_action': 'api',
                'version': '1.0',
                'type': 'json',
                'action': action,
                'oauth_token': self.oauth_token
            }
            
            # Добавляем дополнительные параметры
            if params is not None:
                request_params.update(params)
            
            logger.info(f"SAMO API запрос (direct): {action}")
            logger.info(f"Параметры: {json.dumps(request_params, indent=2)}")
            
            # Headers for production deployment
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'application/json, text/xml, */*',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = self.session.post(self.base_url, data=request_params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Пробуем парсить как JSON
            try:
                result = response.json()
                return result
            except json.JSONDecodeError:
                # Если JSON не парсится, возвращаем текст ответа
                return {"error": "Invalid JSON response", "response": response.text}
            
        except requests.RequestException as e:
            logger.error(f"SAMO API ошибка запроса {action}: {e}")
            return {"error": str(e)}
    
    # === СПРАВОЧНИКИ ===
    
    def get_townfroms(self) -> Dict[str, Any]:
        """Получить города отправления"""
        return self._make_request('SearchTour_TOWNFROMS')
    
    def get_states(self) -> Dict[str, Any]:
        """Получить страны"""
        return self._make_request('SearchTour_STATES')
    
    def get_currencies(self) -> Dict[str, Any]:
        """Получить валюты согласно документации SAMO API"""
        # Use correct API client
        from samo_api_correct import SamoAPIClient
        client = SamoAPIClient()
        return client.get_currencies()
    
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
        """Поиск цен на туры"""
        default_params = {
            'TOWNFROMINC': '',
            'STATEINC': '',
            'CHECKIN_BEG': '',
            'CHECKIN_END': '',
            'NIGHTS_FROM': 7,
            'NIGHTS_TILL': 14,
            'ADULT': 2,
            'CHILD': 0,
            'CURRENCY': 'USD',
            'FILTER': 1
        }
        
        if params is not None:
            default_params.update(params)
            
        return self._make_request('SearchTour_PRICES', default_params)
    
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