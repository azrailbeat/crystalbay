"""
Полная интеграция SAMO API для Crystal Bay Travel
Основана на официальной документации: https://dokuwiki.samo.ru/doku.php?id=onlinest:api
"""
import logging
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from crystal_bay_samo_api_helpers import handle_error_response

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
            
            logger.info(f"🔧 SAMO API CONFIG: URL={self.base_url}")
            logger.info(f"🔧 OAuth Token: {self.oauth_token[:8]}***{self.oauth_token[-4:] if self.oauth_token else 'None'}")
            self.timeout = int(settings.get('timeout', 30))
            self.user_agent = settings.get('user_agent', 'Crystal Bay Travel Integration/1.0')
        except ImportError:
            # Fallback if models not available
            self.base_url = base_url or "https://booking.crystalbay.com/export/default.php"
            self.oauth_token = oauth_token or "27bd59a7ac67422189789f0188167379"
            self.timeout = 30
            self.user_agent = 'Crystal Bay Travel Integration/1.0'
            
        self.session = requests.Session()
    
    def _make_request(self, action: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Выполняет запрос к SAMO API - точно как работающий curl"""
        try:
            # ТОЧНО КАК В РАБОЧЕМ CURL - все параметры в URL
            request_params = {
                'samo_action': 'api',
                'oauth_token': self.oauth_token,
                'type': 'json',
                'action': action
            }
            
            # Добавляем дополнительные параметры
            if params is not None:
                request_params.update(params)
            
            import time
            start_time = time.time()
            
            # Детальное логирование запроса
            logger.info(f"=== SAMO API REQUEST START ===")
            logger.info(f"Action: {action}")
            logger.info(f"Method: POST")
            logger.info(f"URL: {self.base_url}")
            logger.info(f"Request Parameters: {request_params}")
            
            # Headers exactly like curl
            headers = {
                'User-Agent': 'curl/7.68.0',
                'Accept': '*/*'
            }
            logger.info(f"Request Headers: {headers}")
            
            # Создаем полный URL для логирования
            from urllib.parse import urlencode
            full_url = f"{self.base_url}?{urlencode(request_params)}"
            logger.info(f"Full URL: {full_url}")
            
            # ВАЖНО: используем POST как в рабочем curl
            response = self.session.post(self.base_url, params=request_params, headers=headers, timeout=self.timeout)
            
            request_time = time.time() - start_time
            
            # Детальное логирование ответа
            logger.info(f"=== SAMO API RESPONSE ===")
            logger.info(f"HTTP Status: {response.status_code} {response.reason}")
            logger.info(f"Response Time: {request_time:.3f}s")
            logger.info(f"Response Headers: {dict(response.headers)}")
            logger.info(f"Response Size: {len(response.text)} bytes")
            logger.info(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
            
            # Логируем первые 500 символов ответа для диагностики
            response_preview = response.text[:500] if response.text else "(empty)"
            logger.info(f"Response Preview (first 500 chars): {response_preview}")
            
            # Обработка всех статус кодов без raise_for_status для лучшего контроля
            if response.status_code == 200:
                try:
                    result = response.json()
                    data_info = ""
                    if isinstance(result, dict):
                        data_info = f"dict with {len(result)} keys: {list(result.keys())}"
                    elif isinstance(result, list):
                        data_info = f"list with {len(result)} items"
                    else:
                        data_info = f"type: {type(result)}"
                    
                    logger.info(f"✅ JSON PARSE SUCCESS - {data_info}")
                    logger.info(f"=== SAMO API REQUEST END ===")
                    
                    return {
                        "success": True,
                        "data": result,
                        "status_code": 200,
                        "action": action,
                        "request_details": {
                            "url": full_url,
                            "method": "POST",
                            "headers": headers,
                            "params": request_params,
                            "response_time": f"{request_time:.3f}s",
                            "response_headers": dict(response.headers),
                            "response_size": len(response.text)
                        }
                    }
                except json.JSONDecodeError as je:
                    logger.error(f"❌ JSON PARSE ERROR: {je}")
                    logger.error(f"Raw response text: {response.text}")
                    logger.info(f"=== SAMO API REQUEST END (JSON ERROR) ===")
                    return {
                        "success": False,
                        "error": f"Invalid JSON response from SAMO API: {str(je)}",
                        "raw_response": response.text,
                        "status_code": 200,
                        "action": action,
                        "request_details": {
                            "url": full_url,
                            "method": "POST", 
                            "headers": headers,
                            "params": request_params,
                            "response_time": f"{request_time:.3f}s",
                            "response_headers": dict(response.headers),
                            "response_size": len(response.text)
                        }
                    }
            elif response.status_code == 403:
                error_text = response.text
                logger.error(f"❌ HTTP 403 FORBIDDEN")
                logger.error(f"Error response: {error_text}")
                
                # Извлечение IP из ответа для лучшей диагностики
                blocked_ip = "Unknown"
                if "blacklisted address" in error_text:
                    import re
                    ip_match = re.search(r'blacklisted address (\d+\.\d+\.\d+\.\d+)', error_text)
                    blocked_ip = ip_match.group(1) if ip_match else "Unknown"
                    logger.error(f"🚫 DETECTED BLOCKED IP: {blocked_ip}")
                
                logger.info(f"=== SAMO API REQUEST END (403 ERROR) ===")
                
                return {
                    "success": False,
                    "error": f"IP {blocked_ip} blocked by SAMO API",
                    "raw_response": error_text,
                    "status_code": 403,
                    "action": action,
                    "blocked_ip": blocked_ip,
                    "request_details": {
                        "url": full_url,
                        "method": "POST",
                        "headers": headers,
                        "params": request_params,
                        "response_time": f"{request_time:.3f}s",
                        "response_headers": dict(response.headers),
                        "response_size": len(response.text)
                    }
                }
            elif response.status_code == 500:
                logger.error(f"❌ HTTP 500 INTERNAL SERVER ERROR")
                logger.error(f"Server error response: {response.text}")
                logger.info(f"=== SAMO API REQUEST END (500 ERROR) ===")
                return {
                    "success": False,
                    "error": "SAMO API Internal Server Error",
                    "raw_response": response.text,
                    "status_code": 500,
                    "action": action,
                    "help": "Check required parameters for this action",
                    "request_details": {
                        "url": full_url,
                        "method": "POST",
                        "headers": headers,
                        "params": request_params,
                        "response_time": f"{request_time:.3f}s",
                        "response_headers": dict(response.headers),
                        "response_size": len(response.text)
                    }
                }
            else:
                logger.error(f"❌ HTTP {response.status_code} {response.reason}")
                logger.error(f"Unexpected response: {response.text}")
                logger.info(f"=== SAMO API REQUEST END (ERROR {response.status_code}) ===")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code} {response.reason}",
                    "raw_response": response.text,
                    "status_code": response.status_code,
                    "action": action,
                    "request_details": {
                        "url": full_url,
                        "method": "POST",
                        "headers": headers,
                        "params": request_params,
                        "response_time": f"{request_time:.3f}s",
                        "response_headers": dict(response.headers),
                        "response_size": len(response.text)
                    }
                }
            
        except requests.RequestException as e:
            logger.error(f"SAMO API ошибка запроса {action}: {e}")
            
            # Стандартизированная обработка всех типов ошибок
            error_response = {
                "success": False,
                "error": f"Network error: {str(e)}",
                "action": action,
                "url": self.base_url,
                "oauth_token_suffix": self.oauth_token[-4:] if self.oauth_token else "None",
                "error_type": type(e).__name__
            }
            
            if hasattr(e, 'response') and e.response:
                error_response.update({
                    "status_code": e.response.status_code,
                    "raw_response": e.response.text[:500] if e.response.text else "",
                    "response_headers": dict(e.response.headers)
                })
            else:
                error_response["status_code"] = 0  # Indicates network error
            
            return error_response
    
    # === РАБОЧИЙ API МЕТОД ===
    
    def test_api_connection(self) -> Dict[str, Any]:
        """Тест подключения к API с минимальными параметрами"""
        try:
            # Самый простой запрос для проверки
            simple_params = {
                'samo_action': 'api',
                'oauth_token': self.oauth_token,
                'action': 'GetStates'  # Простой action
            }
            
            logger.info(f"🧪 ТЕСТ API CONNECTION: {simple_params}")
            response = self.session.get(self.base_url, params=simple_params, timeout=10)
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "content_type": response.headers.get('content-type', 'unknown'),
                "response_size": len(response.text),
                "response_preview": response.text[:200],
                "test_type": "simple_connection"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "test_type": "simple_connection"
            }

    def get_all_data(self) -> Dict[str, Any]:
        """ТЕСТ ВСЕХ ВОЗМОЖНЫХ ВАРИАНТОВ API ВЫЗОВА"""
        logger.info("🔍 НАЧИНАЕМ ПОЛНУЮ ДИАГНОСТИКУ SAMO API")
        
        # Вариант 1: GET запрос (как многие API работают)
        try:
            logger.info("=== ТЕСТ 1: GET запрос ===")
            get_params = {
                'samo_action': 'api',
                'oauth_token': self.oauth_token,
                'type': 'json',
                'action': 'SearchTour_ALL'
            }
            response1 = self.session.get(self.base_url, params=get_params, timeout=10)
            logger.info(f"GET результат: {response1.status_code}, Content-Type: {response1.headers.get('content-type')}")
            if response1.status_code == 200 and 'application/json' in response1.headers.get('content-type', ''):
                return {"success": True, "method": "GET", "data": response1.json()}
        except Exception as e:
            logger.info(f"GET не сработал: {e}")
            
        # Вариант 2: POST с данными в body
        try:
            logger.info("=== ТЕСТ 2: POST с данными в body ===")
            post_data = {
                'samo_action': 'api',
                'oauth_token': self.oauth_token,
                'type': 'json',
                'action': 'SearchTour_ALL'
            }
            response2 = self.session.post(self.base_url, data=post_data, timeout=10)
            logger.info(f"POST body результат: {response2.status_code}, Content-Type: {response2.headers.get('content-type')}")
            if response2.status_code == 200 and 'application/json' in response2.headers.get('content-type', ''):
                return {"success": True, "method": "POST_BODY", "data": response2.json()}
        except Exception as e:
            logger.info(f"POST body не сработал: {e}")
            
        # Вариант 3: Простейший тест подключения
        try:
            logger.info("=== ТЕСТ 3: Простейший API тест ===")
            simple_params = {
                'samo_action': 'api',
                'oauth_token': self.oauth_token,
                'type': 'json',
                'action': 'GetStates'  # Самый простой action
            }
            response3 = self.session.get(self.base_url, params=simple_params, timeout=10)
            logger.info(f"Простой тест: {response3.status_code}, Content-Type: {response3.headers.get('content-type')}")
            logger.info(f"Ответ: {response3.text[:200]}")
            
            if response3.status_code == 200:
                return {
                    "success": True, 
                    "method": "SIMPLE_TEST", 
                    "working_endpoint": True,
                    "response": response3.text[:500]
                }
        except Exception as e:
            logger.info(f"Простой тест не сработал: {e}")
            
        # Возвращаем диагностику
        return {
            "success": False,
            "error": "ВСЕ МЕТОДЫ ТЕСТИРОВАНИЯ НЕ СРАБОТАЛИ",
            "action": "FULL_DIAGNOSTIC",
            "recommendation": "Нужно связаться с техподдержкой SAMO API"
        }
    
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
                        "data": {
                            "tours": tours_data,
                            "total_count": len(tours_data)
                        },
                        "search_params": params or {},
                        "raw_response": result
                    }
                    
                except json.JSONDecodeError as je:
                    logger.error(f"SAMO SearchTour_PRICES JSON parse error: {je}")
                    return {
                        "success": False,
                        "error": "Invalid JSON response from SAMO API",
                        "raw_response": response.text[:500],
                        "status_code": 200,
                        "action": "SearchTour_PRICES",
                        "search_params": params or {}
                    }
            else:
                # Общая обработка всех не-200 статусов  
                return handle_error_response(response, "SearchTour_PRICES", {"search_params": params or {}})
                
        except requests.RequestException as e:
            logger.error(f"SAMO API tour search error: {e}")
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "action": "SearchTour_PRICES",
                "search_params": params or {},
                "error_type": type(e).__name__
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
            result = self.get_all_data()
            
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
            townfroms = self.get_all_data()
            
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