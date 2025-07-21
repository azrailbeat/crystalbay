"""
SAMO API Leads Integration Module
Модуль для получения и синхронизации заявок из SAMO API Crystal Bay
"""
import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SAMOLeadsIntegration:
    """Интеграция с SAMO API для получения заявок"""
    
    def __init__(self):
        self.samo_oauth_token = os.getenv('SAMO_OAUTH_TOKEN')
        self.samo_api_base_url = "https://booking-kz.crystalbay.com/export/default.php"
        
        # SAMO API параметры
        self.samo_base_params = {
            'samo_action': 'api',
            'version': '1.0',
            'type': 'json',
            'oauth_token': self.samo_oauth_token
        }
        
        if not self.samo_oauth_token:
            logger.warning("SAMO_OAUTH_TOKEN не найден - заявки не будут загружаться")
        else:
            logger.info("SAMO Leads Integration инициализирована")
    
    def get_recent_bookings(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Получает последние заявки/бронирования из SAMO API
        
        Args:
            days_back: Количество дней назад для поиска заявок
            
        Returns:
            List[Dict]: Список заявок из SAMO API
        """
        if not self.samo_oauth_token:
            logger.warning("Токен SAMO API отсутствует")
            return []
        
        try:
            # Поиск бронирований за последние дни
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            params = self.samo_base_params.copy()
            params.update({
                'action': 'SearchBooking',  # Поиск бронирований
                'date_from': start_date.strftime('%Y-%m-%d'),
                'date_to': end_date.strftime('%Y-%m-%d'),
                'status': 'all'  # Все статусы
            })
            
            logger.info(f"Загружаю заявки SAMO API за последние {days_back} дней")
            
            response = requests.get(
                self.samo_api_base_url,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                bookings = self._parse_samo_bookings(data)
                logger.info(f"Загружено {len(bookings)} заявок из SAMO API")
                return bookings
            else:
                logger.error(f"Ошибка SAMO API: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Ошибка получения заявок SAMO: {e}")
            return []
    
    def _parse_samo_bookings(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Парсит ответ SAMO API и преобразует в формат заявок Crystal Bay
        
        Args:
            data: Ответ от SAMO API
            
        Returns:
            List[Dict]: Заявки в формате Crystal Bay
        """
        leads = []
        
        try:
            # Обрабатываем данные в зависимости от структуры ответа SAMO
            bookings = data.get('bookings', [])
            if not bookings and 'data' in data:
                bookings = data['data']
            if not bookings and isinstance(data, list):
                bookings = data
            
            for booking in bookings:
                lead = self._convert_booking_to_lead(booking)
                if lead:
                    leads.append(lead)
                    
        except Exception as e:
            logger.error(f"Ошибка парсинга заявок SAMO: {e}")
        
        return leads
    
    def _convert_booking_to_lead(self, booking: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Преобразует бронирование SAMO в формат заявки Crystal Bay
        
        Args:
            booking: Данные бронирования из SAMO
            
        Returns:
            Dict: Заявка в формате Crystal Bay или None
        """
        try:
            # Извлекаем основные поля из SAMO бронирования
            lead_id = str(booking.get('id', booking.get('booking_id', f"samo_{datetime.now().timestamp()}")))
            
            # Клиентские данные
            client_name = booking.get('client_name', 
                                    f"{booking.get('first_name', '')} {booking.get('last_name', '')}").strip()
            if not client_name:
                client_name = booking.get('contact_name', 'Клиент из SAMO')
            
            client_email = booking.get('email', booking.get('client_email', ''))
            client_phone = booking.get('phone', booking.get('client_phone', ''))
            
            # Данные тура
            tour_name = booking.get('tour_name', booking.get('hotel_name', ''))
            destination = booking.get('destination', booking.get('country', ''))
            departure_date = booking.get('departure_date', booking.get('checkin_date', ''))
            
            # Статус заявки
            booking_status = booking.get('status', 'new').lower()
            lead_status = self._map_samo_status_to_lead_status(booking_status)
            
            # Цена и валюта
            total_price = booking.get('total_price', booking.get('price', 0))
            currency = booking.get('currency', 'USD')
            
            # Создаем детальное описание
            details_parts = []
            if tour_name:
                details_parts.append(f"Тур: {tour_name}")
            if destination:
                details_parts.append(f"Направление: {destination}")
            if departure_date:
                details_parts.append(f"Дата выезда: {departure_date}")
            if total_price:
                details_parts.append(f"Стоимость: {total_price} {currency}")
            
            # Дополнительная информация
            adults = booking.get('adults', booking.get('adult_count', 0))
            children = booking.get('children', booking.get('child_count', 0))
            if adults or children:
                details_parts.append(f"Туристы: {adults} взр., {children} дет.")
            
            details = "; ".join(details_parts) if details_parts else "Заявка из SAMO API"
            
            # Определяем теги
            tags = ['SAMO API']
            if destination:
                tags.append(destination)
            if tour_name and 'пляж' in tour_name.lower():
                tags.append('Пляжный отдых')
            elif tour_name and any(word in tour_name.lower() for word in ['экскур', 'тур']):
                tags.append('Экскурсии')
            
            # Создаем заявку
            lead = {
                'id': f"samo_{lead_id}",
                'name': client_name,
                'email': client_email,
                'phone': client_phone,
                'source': 'samo_api',
                'status': lead_status,
                'created_at': booking.get('created_date', datetime.now().isoformat()),
                'details': details,
                'tags': tags,
                'samo_booking_id': lead_id,
                'tour_name': tour_name,
                'destination': destination,
                'departure_date': departure_date,
                'total_price': total_price,
                'currency': currency,
                'adults': adults,
                'children': children
            }
            
            return lead
            
        except Exception as e:
            logger.error(f"Ошибка преобразования бронирования SAMO: {e}")
            return None
    
    def _map_samo_status_to_lead_status(self, samo_status: str) -> str:
        """
        Маппинг статусов SAMO в статусы заявок Crystal Bay
        
        Args:
            samo_status: Статус из SAMO API
            
        Returns:
            str: Статус заявки для Crystal Bay
        """
        status_mapping = {
            'new': 'new',
            'pending': 'in_progress',
            'confirmed': 'confirmed',
            'paid': 'confirmed',
            'cancelled': 'closed',
            'completed': 'closed',
            'draft': 'new'
        }
        
        return status_mapping.get(samo_status.lower(), 'new')
    
    def sync_leads(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Синхронизирует заявки из SAMO API
        
        Args:
            days_back: Количество дней для синхронизации
            
        Returns:
            Dict: Результат синхронизации
        """
        try:
            # Получаем заявки из SAMO
            samo_leads = self.get_recent_bookings(days_back)
            
            if not samo_leads:
                return {
                    'success': False,
                    'message': 'Не удалось получить заявки из SAMO API',
                    'leads_count': 0
                }
            
            # Импортируем сервис для сохранения заявок
            from models import LeadService
            
            # Сохраняем каждую заявку
            saved_count = 0
            for lead in samo_leads:
                try:
                    # Проверяем, не существует ли уже такая заявка
                    existing_lead = LeadService.get_lead_by_id(lead['id'])
                    if existing_lead:
                        # Обновляем существующую заявку
                        LeadService.update_lead(lead['id'], lead)
                    else:
                        # Создаем новую заявку
                        LeadService.create_lead(lead)
                    saved_count += 1
                except Exception as e:
                    logger.error(f"Ошибка сохранения заявки {lead['id']}: {e}")
            
            return {
                'success': True,
                'message': f'Синхронизировано {saved_count} заявок из SAMO API',
                'leads_count': saved_count,
                'total_fetched': len(samo_leads)
            }
            
        except Exception as e:
            logger.error(f"Ошибка синхронизации заявок SAMO: {e}")
            return {
                'success': False,
                'message': f'Ошибка синхронизации: {str(e)}',
                'leads_count': 0
            }

# Глобальный экземпляр
samo_leads = SAMOLeadsIntegration()