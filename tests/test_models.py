"""
Тесты для моделей данных
"""
import os
import unittest
import sys
import logging
from datetime import datetime

# Добавляем родительскую директорию в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import (
    LeadService, BookingService, is_supabase_available,
    _memory_leads, _memory_ai_config, _memory_ai_agents
)

class TestLeadService(unittest.TestCase):
    """Тесты для сервиса работы с лидами"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Сохраняем оригинальные данные
        self.original_leads = _memory_leads.copy()
        # Очищаем данные для тестов
        _memory_leads.clear()
    
    def tearDown(self):
        """Очистка после каждого теста"""
        # Восстанавливаем оригинальные данные
        _memory_leads.clear()
        _memory_leads.extend(self.original_leads)
    
    def test_create_lead_fallback(self):
        """Тест создания лида с использованием резервного хранилища"""
        # Данные тестового лида
        test_lead = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+7 (999) 123-45-67',
            'source': 'test',
            'details': 'Test lead details',
            'tags': ['Test', 'API']
        }
        
        # Создаем лид через сервис
        result = LeadService.create_lead_fallback(test_lead)
        
        # Проверяем результат
        self.assertIsNotNone(result)
        self.assertIn('id', result)
        self.assertIn('created_at', result)
        self.assertEqual(result['name'], test_lead['name'])
        self.assertEqual(result['email'], test_lead['email'])
        self.assertEqual(result['phone'], test_lead['phone'])
        self.assertEqual(result['status'], 'new')  # По умолчанию статус должен быть 'new'
        
        # Проверяем, что лид добавлен в резервное хранилище
        self.assertEqual(len(_memory_leads), 1)
        self.assertEqual(_memory_leads[0]['name'], test_lead['name'])
    
    def test_get_leads_fallback(self):
        """Тест получения списка лидов из резервного хранилища"""
        # Добавляем тестовые лиды
        _memory_leads.extend([
            {
                'id': '1',
                'name': 'Test User 1',
                'email': 'test1@example.com',
                'phone': '+7 (999) 123-45-67',
                'source': 'test',
                'status': 'new',
                'created_at': datetime.now().isoformat(),
                'details': 'Test lead 1',
                'tags': ['Test', 'API']
            },
            {
                'id': '2',
                'name': 'Test User 2',
                'email': 'test2@example.com',
                'phone': '+7 (999) 987-65-43',
                'source': 'test',
                'status': 'in_progress',
                'created_at': datetime.now().isoformat(),
                'details': 'Test lead 2',
                'tags': ['Test', 'Web']
            }
        ])
        
        # Получаем все лиды
        leads = LeadService.get_leads_fallback()
        self.assertEqual(len(leads), 2)
        
        # Получаем лиды с фильтром по статусу
        new_leads = LeadService.get_leads_fallback(status='new')
        self.assertEqual(len(new_leads), 1)
        self.assertEqual(new_leads[0]['status'], 'new')
        
        # Проверяем сортировку по дате создания (новые в начале)
        self.assertEqual(leads[0]['id'], '2')
        self.assertEqual(leads[1]['id'], '1')
    
    def test_get_lead_fallback(self):
        """Тест получения конкретного лида по ID из резервного хранилища"""
        # Добавляем тестовый лид
        test_lead = {
            'id': 'test123',
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+7 (999) 123-45-67',
            'source': 'test',
            'status': 'new',
            'created_at': datetime.now().isoformat(),
            'details': 'Test lead details',
            'tags': ['Test', 'API']
        }
        _memory_leads.append(test_lead)
        
        # Получаем лид по ID
        lead = LeadService.get_lead_fallback('test123')
        self.assertIsNotNone(lead)
        self.assertEqual(lead['id'], 'test123')
        self.assertEqual(lead['name'], test_lead['name'])
        
        # Проверяем поведение при запросе несуществующего ID
        non_existent_lead = LeadService.get_lead_fallback('non_existent')
        self.assertIsNone(non_existent_lead)
    
    def test_update_lead_status_fallback(self):
        """Тест обновления статуса лида в резервном хранилище"""
        # Добавляем тестовый лид
        test_lead = {
            'id': 'test123',
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+7 (999) 123-45-67',
            'source': 'test',
            'status': 'new',
            'created_at': datetime.now().isoformat(),
            'details': 'Test lead details',
            'tags': ['Test', 'API']
        }
        _memory_leads.append(test_lead)
        
        # Обновляем статус лида
        updated_lead = LeadService.update_lead_status_fallback('test123', 'in_progress')
        self.assertIsNotNone(updated_lead)
        self.assertEqual(updated_lead['status'], 'in_progress')
        
        # Проверяем, что статус обновился в хранилище
        lead_in_memory = next((l for l in _memory_leads if l['id'] == 'test123'), None)
        self.assertIsNotNone(lead_in_memory)
        self.assertEqual(lead_in_memory['status'], 'in_progress')
        
        # Проверяем поведение при обновлении несуществующего лида
        non_existent_update = LeadService.update_lead_status_fallback('non_existent', 'in_progress')
        self.assertIsNone(non_existent_update)


class TestBookingService(unittest.TestCase):
    """Тесты для сервиса работы с бронированиями"""
    
    def test_format_status(self):
        """Тест форматирования статуса бронирования"""
        # Проверяем, что сервис корректно форматирует различные статусы
        self.assertEqual(BookingService.format_status('confirmed'), 'Подтверждено')
        self.assertEqual(BookingService.format_status('pending'), 'В ожидании')
        self.assertEqual(BookingService.format_status('cancelled'), 'Отменено')
        self.assertEqual(BookingService.format_status('unknown_status'), 'unknown_status')  # Неизвестный статус


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()