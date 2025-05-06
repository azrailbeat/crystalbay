"""
Интеграционные тесты всей системы
"""
import os
import unittest
import sys
import logging
from unittest.mock import patch, MagicMock
import json
from datetime import datetime

# Добавляем родительскую директорию в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Импортируем компоненты системы
from flask import Flask
from app_api import register_api_routes
from models import (
    LeadService, BookingService, is_supabase_available, 
    _memory_leads, _memory_agents_config, _memory_ai_agents
)
from inquiry_processor import InquiryProcessor
from api_integration import APIIntegration, get_api_integration
from nlp_processor import NLPProcessor

class TestFullSystemIntegration(unittest.TestCase):
    """
    Интеграционные тесты, проверяющие взаимодействие всех компонентов системы
    """
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Сохраняем оригинальные данные
        self.original_leads = _memory_leads.copy()
        self.original_config = _memory_agents_config.copy()
        self.original_agents = _memory_ai_agents.copy()
        
        # Очищаем данные для тестов
        _memory_leads.clear()
        
        # Настраиваем тестовую конфигурацию
        _memory_agents_config.update({
            'auto_process_enabled': True,
            'default_agent_id': 'test_agent'
        })
        
        # Создаем тестовое приложение Flask
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        register_api_routes(self.app)
        self.client = self.app.test_client()
        
        # Настраиваем патчи для внешних компонентов
        self.openai_patcher = patch('inquiry_processor.OpenAI')
        self.mock_openai = self.openai_patcher.start()
        
        # Настраиваем мок для ChatCompletion
        mock_chat = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        
        mock_message.content = '{"status": "in_progress", "suggestion": "Test suggestion", "confidence": 0.85}'
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_chat.return_value = mock_response
        
        self.mock_openai.return_value.chat.completions.create = mock_chat
        
        # Патч для API интеграции
        self.api_patcher = patch('api_integration.requests.request')
        self.mock_api_request = self.api_patcher.start()
        
        # Настраиваем мок для API запросов
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'success', 'data': {'test': 'data'}}
        self.mock_api_request.return_value = mock_response
    
    def tearDown(self):
        """Очистка после каждого теста"""
        # Восстанавливаем оригинальные данные
        _memory_leads.clear()
        _memory_leads.extend(self.original_leads)
        
        # Восстанавливаем конфигурацию
        _memory_agents_config.clear()
        _memory_agents_config.update(self.original_config)
        
        # Восстанавливаем агентов
        _memory_ai_agents.clear()
        _memory_ai_agents.update(self.original_agents)
        
        # Останавливаем патчи
        self.openai_patcher.stop()
        self.api_patcher.stop()
    
    def test_end_to_end_inquiry_handling(self):
        """
        Тест полного цикла обработки запроса:
        1. Получение запроса
        2. Обработка AI
        3. Создание лида
        4. Изменение статуса
        5. Поиск связанных данных
        6. Генерация ответа
        """
        # Данные запроса
        inquiry_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+7 (999) 123-45-67',
            'message': 'Здравствуйте! Меня интересует тур в Таиланд на июль, для семьи из 4 человек. Подскажите варианты?',
            'source': 'website'
        }
        
        # 1. Отправляем запрос на обработку через API
        response = self.client.post(
            '/api/inquiries/process', 
            data=json.dumps(inquiry_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Получаем ID созданного лида
        data = json.loads(response.data)
        self.assertIn('result', data)
        lead_id = data['result']['lead_id']
        
        # 2. Проверяем, что лид создан в хранилище
        lead = LeadService.get_lead_fallback(lead_id)
        self.assertIsNotNone(lead)
        self.assertEqual(lead['name'], 'Test User')
        self.assertEqual(lead['email'], 'test@example.com')
        
        # 3. Проверяем взаимодействие со SAMO API для поиска туров
        api = get_api_integration()
        
        # Настраиваем мок для ответа API
        booking_info = {
            'bookings': [
                {
                    'reference': 'CB12345',
                    'customer': {
                        'name': 'Test User',
                        'email': 'test@example.com'
                    },
                    'status': 'pending',
                    'destination': 'Thailand',
                    'travel_dates': {
                        'departure': '2025-07-15',
                        'return': '2025-07-29'
                    },
                    'travelers': 4,
                    'amount': 320000,
                    'currency': 'RUB'
                }
            ]
        }
        
        self.mock_api_request.return_value.json.return_value = booking_info
        
        # Ищем бронирования для клиента
        bookings = api.search_bookings(customer_email='test@example.com')
        self.assertIsNotNone(bookings)
        self.assertEqual(len(bookings), 1)
        self.assertEqual(bookings[0]['reference'], 'CB12345')
        
        # 4. Изменяем статус лида через API и добавляем информацию о бронировании
        update_data = {
            'status': 'negotiation',
            'details': lead['details'] + '\n\nНайдено бронирование: CB12345'
        }
        
        response = self.client.put(
            f'/api/leads/{lead_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что данные обновились
        updated_lead = LeadService.get_lead_fallback(lead_id)
        self.assertEqual(updated_lead['status'], 'negotiation')
        self.assertIn('CB12345', updated_lead['details'])
        
        # 5. Добавляем взаимодействие через API
        interaction_data = {
            'content': 'Клиенту предложены варианты туров в Таиланд на июль.',
            'user_id': 'agent1',
            'user_name': 'Travel Agent'
        }
        
        response = self.client.post(
            f'/api/leads/{lead_id}/interactions',
            data=json.dumps(interaction_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        # 6. Генерируем ответ для клиента с NLP (имитация)
        nlp_processor = NLPProcessor()
        
        # Настраиваем мок для генерации ответа
        mock_chat = self.mock_openai.return_value.chat.completions.create
        mock_message = MagicMock()
        mock_message.content = 'Здравствуйте! Спасибо за обращение. Мы подобрали для вас варианты туров в Таиланд на июль...'
        mock_chat.return_value.choices[0].message = mock_message
        
        # Генерируем ответ
        processor = InquiryProcessor()
        response_text = processor.generate_response(lead_id)
        
        self.assertIsNotNone(response_text)
        self.assertIn('Здравствуйте!', response_text)
        
        # 7. Проверяем полный цикл статусов лида
        statuses = ['new', 'in_progress', 'negotiation', 'booked', 'canceled']
        
        for status in statuses:
            # Обновляем статус
            response = self.client.put(
                f'/api/leads/{lead_id}/status',
                data=json.dumps({'status': status}),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            
            # Проверяем, что статус обновился
            updated = LeadService.get_lead_fallback(lead_id)
            self.assertEqual(updated['status'], status)
    
    def test_batch_processing_with_fallback(self):
        """
        Тест пакетной обработки с использованием резервного хранилища:
        1. Создание нескольких лидов
        2. Пакетная обработка через InquiryProcessor
        3. Проверка обновления статусов
        4. Проверка работы с ошибкой в API
        """
        # 1. Создаем тестовые лиды
        test_leads = [
            {
                'name': 'User 1',
                'email': 'user1@example.com',
                'phone': '+7 (999) 111-11-11',
                'details': 'Запрос на тур в Европу',
                'source': 'website',
                'status': 'new'
            },
            {
                'name': 'User 2',
                'email': 'user2@example.com',
                'phone': '+7 (999) 222-22-22',
                'details': 'Запрос о горнолыжном отдыхе',
                'source': 'phone',
                'status': 'new'
            },
            {
                'name': 'User 3',
                'email': 'user3@example.com',
                'phone': '+7 (999) 333-33-33',
                'details': 'Запрос о пляжном отдыхе в Греции',
                'source': 'email',
                'status': 'new'
            }
        ]
        
        # Создаем лиды через API
        lead_ids = []
        for lead_data in test_leads:
            response = self.client.post(
                '/api/leads',
                data=json.dumps(lead_data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)
            lead_ids.append(data['lead']['id'])
        
        # 2. Имитируем сбой Supabase
        with patch('models.is_supabase_available', return_value=False):
            # Получаем все лиды через API
            response = self.client.get('/api/leads')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertIn('leads', data)
            self.assertEqual(len(data['leads']), 3)
            
            # 3. Запускаем пакетную обработку через API
            response = self.client.post('/api/inquiries/process-all')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertIn('results', data)
            self.assertEqual(len(data['results']), 3)
        
        # 4. Проверяем, что все лиды обработаны
        for lead_id in lead_ids:
            lead = LeadService.get_lead_fallback(lead_id)
            self.assertEqual(lead['status'], 'in_progress')
        
        # 5. Имитируем ошибку в OpenAI API
        self.mock_openai.return_value.chat.completions.create.side_effect = Exception("API error")
        
        # Обновляем статусы лидов обратно в 'new'
        for lead_id in lead_ids:
            LeadService.update_lead_status_fallback(lead_id, 'new')
        
        # Запускаем пакетную обработку снова
        response = self.client.post('/api/inquiries/process-all')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('results', data)
        
        # Проверяем, что все результаты содержат ошибку
        for result in data['results']:
            self.assertEqual(result['status'], 'error')
            self.assertIn('error', result)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()