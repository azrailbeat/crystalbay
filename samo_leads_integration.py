#!/usr/bin/env python3
"""
SAMO API Lead Integration Module
Интеграция для загрузки реальных заявок из SAMO API Crystal Bay Travel
"""

import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from crystal_bay_samo_api import CrystalBaySAMOAPI

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SAMOLeadsIntegration:
    """Класс для интеграции с SAMO API для загрузки заявок"""
    
    def __init__(self):
        """Инициализация интеграции SAMO API"""
        self.samo_api = CrystalBaySAMOAPI()
        self.is_connected = False
        
    def test_connection(self) -> bool:
        """Тестирует подключение к SAMO API"""
        try:
            result = self.samo_api.get_townfroms()
            if 'error' not in result:
                self.is_connected = True
                logger.info("✅ SAMO API подключение успешно")
                return True
            else:
                logger.warning(f"⚠️ SAMO API недоступен: {result.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к SAMO API: {e}")
            return False
    
    def load_recent_bookings(self, days_back: int = 30) -> List[Dict]:
        """
        Загружает последние бронирования из SAMO API
        
        Args:
            days_back: Количество дней назад для поиска
            
        Returns:
            Список заявок/бронирований
        """
        try:
            # Формируем даты для поиска
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            date_from = start_date.strftime('%Y-%m-%d')
            date_to = end_date.strftime('%Y-%m-%d')
            
            logger.info(f"🔄 Загружаем бронирования с {date_from} по {date_to}")
            
            # Получаем бронирования
            bookings_result = self.samo_api.get_bookings(date_from=date_from, date_to=date_to)
            
            if 'error' in bookings_result:
                logger.warning(f"⚠️ Ошибка загрузки бронирований: {bookings_result['error']}")
                return []
            
            bookings = bookings_result.get('bookings', [])
            logger.info(f"📋 Загружено {len(bookings)} бронирований")
            
            # Конвертируем в формат заявок
            leads = []
            for booking in bookings:
                lead = self._convert_booking_to_lead(booking)
                if lead:
                    leads.append(lead)
            
            return leads
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки бронирований: {e}")
            return []
    
    def search_tours_for_lead(self, search_params: Dict) -> List[Dict]:
        """
        Поиск туров для конкретной заявки
        
        Args:
            search_params: Параметры поиска тура
            
        Returns:
            Список найденных туров
        """
        try:
            logger.info(f"🔍 Поиск туров с параметрами: {search_params}")
            
            # Поиск туров через SAMO API
            result = self.samo_api.search_tour_prices(search_params)
            
            if 'error' in result:
                logger.warning(f"⚠️ Ошибка поиска туров: {result['error']}")
                return []
            
            tours = result.get('tours', [])
            logger.info(f"🎯 Найдено {len(tours)} туров")
            
            return tours
            
        except Exception as e:
            logger.error(f"❌ Ошибка поиска туров: {e}")
            return []
    
    def _convert_booking_to_lead(self, booking: Dict) -> Optional[Dict]:
        """
        Конвертирует бронирование SAMO в формат заявки Crystal Bay
        
        Args:
            booking: Данные бронирования из SAMO API
            
        Returns:
            Словарь с данными заявки или None
        """
        try:
            # Извлекаем основные данные
            customer_name = booking.get('customer_name', 'Неизвестный клиент')
            email = booking.get('customer_email', '')
            phone = booking.get('customer_phone', '')
            
            # Формируем описание тура
            tour_details = []
            if booking.get('destination'):
                tour_details.append(f"Направление: {booking['destination']}")
            if booking.get('hotel'):
                tour_details.append(f"Отель: {booking['hotel']}")
            if booking.get('departure_date'):
                tour_details.append(f"Даты: {booking['departure_date']}")
            if booking.get('nights'):
                tour_details.append(f"Ночей: {booking['nights']}")
            if booking.get('adults'):
                tour_details.append(f"Взрослых: {booking['adults']}")
            if booking.get('children'):
                tour_details.append(f"Детей: {booking['children']}")
            
            notes = "Заявка из SAMO API:\n" + "\n".join(tour_details)
            
            # Определяем статус
            samo_status = booking.get('status', 'new')
            status = self._map_samo_status_to_crystal_bay(samo_status)
            
            # Формируем теги
            tags = ['SAMO API']
            if booking.get('destination'):
                tags.append(booking['destination'])
            if booking.get('tour_type'):
                tags.append(booking['tour_type'])
            
            # Создаем заявку
            lead = {
                'id': f"samo_{booking.get('booking_id', datetime.now().timestamp())}",
                'customer_name': customer_name,
                'email': email,
                'phone': phone,
                'source': 'SAMO API',
                'status': status,
                'notes': notes,
                'tags': tags,
                'created_at': booking.get('created_at', datetime.now().isoformat()),
                'updated_at': datetime.now().isoformat(),
                'samo_booking_id': booking.get('booking_id'),
                'price': booking.get('total_amount', 0),
                'currency': booking.get('currency', 'USD')
            }
            
            return lead
            
        except Exception as e:
            logger.error(f"❌ Ошибка конвертации бронирования: {e}")
            return None
    
    def _map_samo_status_to_crystal_bay(self, samo_status: str) -> str:
        """
        Маппинг статусов SAMO в статусы Crystal Bay
        
        Args:
            samo_status: Статус из SAMO API
            
        Returns:
            Статус Crystal Bay
        """
        status_mapping = {
            'new': 'new',
            'confirmed': 'confirmed', 
            'paid': 'confirmed',
            'cancelled': 'closed',
            'completed': 'closed',
            'pending': 'in_progress',
            'processing': 'in_progress'
        }
        
        return status_mapping.get(samo_status.lower(), 'new')
    
    def sync_leads_to_system(self, leads_service) -> int:
        """
        Синхронизирует заявки из SAMO в систему Crystal Bay
        
        Args:
            leads_service: Сервис управления заявками
            
        Returns:
            Количество синхронизированных заявок
        """
        try:
            if not self.test_connection():
                logger.warning("⚠️ SAMO API недоступен, синхронизация пропущена")
                return 0
            
            # Загружаем заявки из SAMO
            samo_leads = self.load_recent_bookings(days_back=30)
            
            if not samo_leads:
                logger.info("📭 Новых заявок в SAMO API не найдено")
                return 0
            
            # Добавляем заявки в систему
            synced_count = 0
            for lead in samo_leads:
                try:
                    # Проверяем, не существует ли уже такая заявка
                    existing_lead = leads_service.get_lead_by_samo_id(lead.get('samo_booking_id'))
                    
                    if existing_lead:
                        # Обновляем существующую заявку
                        leads_service.update_lead(existing_lead['id'], lead)
                        logger.info(f"🔄 Обновлена заявка {lead['customer_name']}")
                    else:
                        # Создаем новую заявку
                        leads_service.create_lead(lead)
                        logger.info(f"➕ Добавлена заявка {lead['customer_name']}")
                    
                    synced_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка синхронизации заявки {lead.get('customer_name', 'Unknown')}: {e}")
                    continue
            
            logger.info(f"✅ Синхронизировано {synced_count} заявок из SAMO API")
            return synced_count
            
        except Exception as e:
            logger.error(f"❌ Ошибка синхронизации заявок: {e}")
            return 0

# Глобальный экземпляр интеграции
samo_integration = SAMOLeadsIntegration()

def get_samo_integration() -> SAMOLeadsIntegration:
    """Возвращает экземпляр интеграции SAMO API"""
    return samo_integration