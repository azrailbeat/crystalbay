"""
Тесты API веб-приложения
"""
import os
import unittest
import sys
import json
import logging
from unittest.mock import patch, MagicMock
from datetime import datetime

# Добавляем родительскую директорию в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Импортируем Flask и создаем тестовое приложение
from flask import Flask
from app_api import register_api_routes
from models import _memory_leads, _memory_agents_config, LeadService

class TestAppAPI(unittest.TestCase):
    """Тесты для API маршрутов Flask-приложения"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Сохраняем оригинальные данные
        self.original_leads = _memory_leads.copy()
        self.original_config = _memory_agents_config.copy()
        
        # Очищаем данные для тестов
        _memory_leads.clear()
        
        # Создаем тестовое приложение Flask
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        register_api_routes(self.app)
        self.client = self.app.test_client()
        
        # Добавляем тестовые данные
        test_leads = [
            {
                'id': '1',
                'name': 'User 1',
                'email': 'user1@example.com',
                'phone': '+7 (999) 111-11-11',
                'status': 'new',
                'details': 'Запрос на тур в Европу',
                'source': 'website',
                'created_at': datetime.now().isoformat(),
                'tags': ['Европа', 'Экскурсии']
            },
            {
                'id': '2',
                'name': 'User 2',
                'email': 'user2@example.com',
                'phone': '+7 (999) 222-22-22',
                'status': 'in_progress',
                'details': 'Запрос о горнолыжном отдыхе',
                'source': 'phone',
                'created_at': datetime.now().isoformat(),
                'tags': ['Зима', 'Горнолыжный']
            }
        ]
        _memory_leads.extend(test_leads)
    
    def tearDown(self):
        """Очистка после каждого теста"""
        # Восстанавливаем оригинальные данные
        _memory_leads.clear()
        _memory_leads.extend(self.original_leads)
        
        # Восстанавливаем конфигурацию
        _memory_agents_config.clear()
        _memory_agents_config.update(self.original_config)
    
    def test_get_leads_api(self):
        """Тест API endpoint для получения всех лидов"""
        response = self.client.get('/api/leads')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('leads', data)
        self.assertEqual(len(data['leads']), 2)
        
        # Проверяем фильтрацию по статусу
        response = self.client.get('/api/leads?status=new')
        data = json.loads(response.data)
        self.assertEqual(len(data['leads']), 1)
        self.assertEqual(data['leads'][0]['status'], 'new')
    
    def test_get_lead_api(self):
        """Тест API endpoint для получения конкретного лида"""
        # Тест для существующего лида
        response = self.client.get('/api/leads/1')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('lead', data)
        self.assertEqual(data['lead']['id'], '1')
        
        # Тест для несуществующего лида
        response = self.client.get('/api/leads/999')
        self.assertEqual(response.status_code, 404)
    
    def test_update_lead_api(self):
        """Тест API endpoint для обновления лида"""
        # Данные для обновления
        update_data = {
            'name': 'Updated User 1',
            'email': 'updated@example.com',
            'tags': ['Европа', 'Семья']
        }
        
        # Отправляем запрос на обновление
        response = self.client.put(
            '/api/leads/1', 
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что данные обновились
        lead = LeadService.get_lead_fallback('1')
        self.assertEqual(lead['name'], 'Updated User 1')
        self.assertEqual(lead['email'], 'updated@example.com')
        self.assertEqual(len(lead['tags']), 2)
        self.assertIn('Семья', lead['tags'])
    
    def test_create_lead_api(self):
        """Тест API endpoint для создания нового лида"""
        # Данные нового лида
        new_lead_data = {
            'name': 'New User',
            'email': 'new@example.com',
            'phone': '+7 (999) 333-33-33',
            'details': 'Новый запрос о курортах Греции',
            'source': 'email',
            'tags': ['Греция', 'Пляжный отдых']
        }
        
        # Отправляем запрос на создание
        response = self.client.post(
            '/api/leads', 
            data=json.dumps(new_lead_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        # Проверяем, что лид создан
        data = json.loads(response.data)
        self.assertIn('lead', data)
        self.assertIn('id', data['lead'])
        
        # Проверяем, что лид добавлен в хранилище
        lead_id = data['lead']['id']
        lead = LeadService.get_lead_fallback(lead_id)
        self.assertIsNotNone(lead)
        self.assertEqual(lead['name'], 'New User')
        self.assertEqual(lead['status'], 'new')  # По умолчанию статус 'new'
    
    def test_update_lead_status_api(self):
        """Тест API endpoint для обновления статуса лида"""
        # Данные для обновления статуса
        status_data = {
            'status': 'negotiation'
        }
        
        # Отправляем запрос на обновление статуса
        response = self.client.put(
            '/api/leads/1/status', 
            data=json.dumps(status_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что статус обновился
        lead = LeadService.get_lead_fallback('1')
        self.assertEqual(lead['status'], 'negotiation')
    
    @patch('app_api.InquiryProcessor')
    def test_process_inquiry_api(self, mock_processor_class):
        """Тест API endpoint для обработки запроса с помощью ИИ"""
        # Настраиваем мок процессора
        mock_processor = MagicMock()
        mock_processor.process_inquiry.return_value = {
            'lead_id': 'test123',
            'status': 'in_progress',
            'suggestion': 'Test suggestion'
        }
        mock_processor_class.return_value = mock_processor
        
        # Данные запроса
        inquiry_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+7 (999) 123-45-67',
            'message': 'Запрос о турах в Таиланд в июле',
            'source': 'website'
        }
        
        # Отправляем запрос на обработку
        response = self.client.post(
            '/api/inquiries/process', 
            data=json.dumps(inquiry_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Проверяем ответ
        data = json.loads(response.data)
        self.assertIn('result', data)
        self.assertEqual(data['result']['lead_id'], 'test123')
        self.assertEqual(data['result']['status'], 'in_progress')
        
        # Проверяем, что процессор был вызван с правильными данными
        mock_processor.process_inquiry.assert_called_once_with(inquiry_data)
    
    @patch('app_api.InquiryProcessor')
    def test_analyze_lead_api(self, mock_processor_class):
        """Тест API endpoint для анализа лида с помощью ИИ"""
        # Настраиваем мок процессора
        mock_processor = MagicMock()
        mock_processor.analyze_lead.return_value = {
            'lead_id': '1',
            'status': 'in_progress',
            'suggestion': 'Test suggestion',
            'confidence': 0.85
        }
        mock_processor_class.return_value = mock_processor
        
        # Отправляем запрос на анализ
        response = self.client.post('/api/leads/1/analyze')
        
        self.assertEqual(response.status_code, 200)
        
        # Проверяем ответ
        data = json.loads(response.data)
        self.assertIn('result', data)
        self.assertEqual(data['result']['lead_id'], '1')
        self.assertEqual(data['result']['status'], 'in_progress')
        
        # Проверяем, что процессор был вызван с правильным ID
        mock_processor.analyze_lead.assert_called_once_with('1')
    
    @patch('app_api.APIIntegration')
    def test_check_booking_api(self, mock_api_class):
        """Тест API endpoint для проверки бронирования"""
        # Настраиваем мок API
        mock_api = MagicMock()
        mock_api.check_booking.return_value = {
            'reference': 'CB12345',
            'customer': {'name': 'John Doe'},
            'status': 'confirmed',
            'departure_date': '2025-07-15'
        }
        mock_api_class.return_value = mock_api
        
        # Отправляем запрос на проверку бронирования
        response = self.client.get('/api/bookings/CB12345')
        
        self.assertEqual(response.status_code, 200)
        
        # Проверяем ответ
        data = json.loads(response.data)
        self.assertIn('booking', data)
        self.assertEqual(data['booking']['reference'], 'CB12345')
        self.assertEqual(data['booking']['status'], 'confirmed')
        
        # Проверяем, что API был вызван с правильным референсом
        mock_api.check_booking.assert_called_once_with('CB12345')
    
    @patch('app_api.APIIntegration')
    def test_check_flight_api(self, mock_api_class):
        """Тест API endpoint для проверки статуса рейса"""
        # Настраиваем мок API
        mock_api = MagicMock()
        mock_api.check_flight.return_value = {
            'flight_number': 'SU1234',
            'departure_date': '2025-06-01',
            'status': 'scheduled',
            'airline': 'Aeroflot'
        }
        mock_api_class.return_value = mock_api
        
        # Данные для запроса
        flight_data = {
            'flight_number': 'SU1234',
            'flight_date': '2025-06-01'
        }
        
        # Отправляем запрос на проверку рейса
        response = self.client.post(
            '/api/flights/status', 
            data=json.dumps(flight_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Проверяем ответ
        data = json.loads(response.data)
        self.assertIn('flight', data)
        self.assertEqual(data['flight']['flight_number'], 'SU1234')
        self.assertEqual(data['flight']['status'], 'scheduled')
        
        # Проверяем, что API был вызван с правильными параметрами
        mock_api.check_flight.assert_called_once_with('SU1234', '2025-06-01')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()