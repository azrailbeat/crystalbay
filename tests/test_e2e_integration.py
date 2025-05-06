"""
Тесты сквозной интеграции системы
"""
import os
import unittest
import sys
import logging
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Добавляем родительскую директорию в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Импортируем Flask для создания тестового клиента
from flask import Flask
from app_api import register_api_routes
from models import (
    LeadService, BookingService, is_supabase_available, 
    _memory_leads, _memory_ai_config, _memory_ai_agents
)
from inquiry_processor import InquiryProcessor
from api_integration import APIIntegration, get_api_integration

class TestEndToEndIntegration(unittest.TestCase):
    """
    Сквозные интеграционные тесты, проверяющие полный путь пользователя через систему
    """
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Сохраняем оригинальные данные
        self.original_leads = _memory_leads.copy()
        self.original_config = _memory_ai_config.copy()
        self.original_agents = _memory_ai_agents.copy()
        
        # Очищаем данные для тестов
        _memory_leads.clear()
        
        # Настраиваем тестовую конфигурацию агентов
        _memory_ai_config.update({
            'auto_process_enabled': True,
            'default_agent_id': 'test_agent'
        })
        
        # Настраиваем тестового агента
        _memory_ai_agents.update({
            'test_agent': {
                'id': 'test_agent',
                'name': 'Тестовый агент',
                'description': 'Агент для тестирования',
                'system_prompt': 'Вы - тестовый агент для проверки системы',
                'active': True
            }
        })
        
        # Создаем тестовое приложение Flask
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        register_api_routes(self.app)
        self.client = self.app.test_client()
        
        # Настраиваем патчи для внешних компонентов
        # Патч для проверки доступности Supabase - всегда должен возвращать False в тестах
        self.supabase_patcher = patch('models.is_supabase_available')
        self.mock_supabase_check = self.supabase_patcher.start()
        self.mock_supabase_check.return_value = False
        
        # Патч для openai
        self.openai_patcher = patch('inquiry_processor.openai')
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
        
        self.mock_openai.chat.completions.create = mock_chat
        
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
        _memory_ai_config.clear()
        _memory_ai_config.update(self.original_config)
        
        # Восстанавливаем агентов
        _memory_ai_agents.clear()
        _memory_ai_agents.update(self.original_agents)
        
        # Останавливаем патчи
        self.supabase_patcher.stop()
        self.openai_patcher.stop()
        self.api_patcher.stop()
    
    def test_end_to_end_lead_flow(self):
        """
        Тест полного жизненного цикла лида от создания до завершения.
        
        Сценарий:
        1. Создание нового лида
        2. Обработка лида с помощью ИИ
        3. Изменение статуса лида вручную
        4. Добавление комментария к лиду
        5. Поиск соответствующего бронирования
        6. Завершение процесса с лидом
        """
        # 1. Создание нового лида через API
        lead_data = {
            'name': 'Тестовый Клиент',
            'email': 'test@example.com',
            'phone': '+7 (999) 123-45-67',
            'details': 'Интересует тур в Таиланд на июль 2025 года, семья из 4 человек',
            'source': 'website',
            'tags': ['Таиланд', 'Семейный отдых', 'Лето 2025']
        }
        
        response = self.client.post(
            '/api/leads',
            data=json.dumps(lead_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201, 'Лид должен быть успешно создан')
        
        # Получаем ID созданного лида
        data = json.loads(response.data)
        lead_id = data['lead']['id']
        
        # 2. Обработка лида с помощью ИИ
        response = self.client.post(f'/api/leads/{lead_id}/analyze')
        
        self.assertEqual(response.status_code, 200, 'Анализ лида должен быть успешным')
        
        # Проверяем, что статус лида изменен на "в работе"
        response = self.client.get(f'/api/leads/{lead_id}')
        data = json.loads(response.data)
        self.assertEqual(data['lead']['status'], 'in_progress', 'Статус должен быть изменен на "в работе"')
        
        # 3. Изменение статуса лида на "переговоры"
        response = self.client.put(
            f'/api/leads/{lead_id}/status',
            data=json.dumps({'status': 'negotiation'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200, 'Изменение статуса должно быть успешным')
        
        # Проверяем, что статус изменен
        response = self.client.get(f'/api/leads/{lead_id}')
        data = json.loads(response.data)
        self.assertEqual(data['lead']['status'], 'negotiation', 'Статус должен быть "переговоры"')
        
        # 4. Добавление комментария к лиду
        interaction_data = {
            'content': 'Клиенту предложены варианты туров в Таиланд',
            'user_id': 'agent1',
            'user_name': 'Менеджер'
        }
        
        response = self.client.post(
            f'/api/leads/{lead_id}/interactions',
            data=json.dumps(interaction_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201, 'Комментарий должен быть успешно добавлен')
        
        # Проверяем, что комментарий добавлен
        response = self.client.get(f'/api/leads/{lead_id}/interactions')
        data = json.loads(response.data)
        self.assertGreaterEqual(len(data['interactions']), 1, 'Должен быть хотя бы один комментарий')
        
        # 5. Настраиваем мок для поиска бронирований
        booking_response = {
            'bookings': [
                {
                    'reference': 'CB12345',
                    'destination': 'Thailand',
                    'customer': {
                        'name': 'Тестовый Клиент',
                        'email': 'test@example.com'
                    },
                    'status': 'confirmed',
                    'departure_date': '2025-07-15',
                    'return_date': '2025-07-29',
                    'guests': 4,
                    'amount': 450000,
                    'currency': 'RUB'
                }
            ]
        }
        self.mock_api_request.return_value.json.return_value = booking_response
        
        # Делаем запрос через API для поиска бронирований
        response = self.client.get(f'/api/bookings/search?email=test@example.com')
        
        self.assertEqual(response.status_code, 200, 'Поиск бронирований должен быть успешным')
        
        # Проверяем, что бронирование найдено
        data = json.loads(response.data)
        self.assertGreaterEqual(len(data['bookings']), 1, 'Должно быть найдено хотя бы одно бронирование')
        self.assertEqual(data['bookings'][0]['reference'], 'CB12345', 'Номер бронирования должен совпадать')
        
        # 6. Обновляем лид с информацией о бронировании
        update_data = {
            'booking_reference': 'CB12345',
            'details': data['lead']['details'] + '\n\nЗабронирован тур: CB12345, вылет 15.07.2025'
        }
        
        response = self.client.put(
            f'/api/leads/{lead_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200, 'Обновление лида должно быть успешным')
        
        # 7. Изменение статуса лида на "забронировано"
        response = self.client.put(
            f'/api/leads/{lead_id}/status',
            data=json.dumps({'status': 'booked'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200, 'Изменение статуса должно быть успешным')
        
        # Проверяем, что статус изменен
        response = self.client.get(f'/api/leads/{lead_id}')
        data = json.loads(response.data)
        self.assertEqual(data['lead']['status'], 'booked', 'Статус должен быть "забронировано"')
    
    def test_batch_processing_workflow(self):
        """
        Тест пакетной обработки лидов с последующей обработкой результатов.
        
        Сценарий:
        1. Создание нескольких лидов с разными источниками и статусами
        2. Обработка партии лидов через механизм автоматической обработки
        3. Проверка результатов обработки - статусы, аналитика, теги
        4. Проверка фильтрации и сортировки лидов через API
        """
        # 1. Создание тестовых лидов
        test_leads = [
            {
                'name': 'Клиент 1',
                'email': 'client1@example.com',
                'phone': '+7 (999) 111-11-11',
                'details': 'Интересует пляжный отдых в Турции на август 2025',
                'source': 'website',
                'status': 'new',
                'tags': ['Турция', 'Пляжный отдых']
            },
            {
                'name': 'Клиент 2',
                'email': 'client2@example.com',
                'phone': '+7 (999) 222-22-22',
                'details': 'Нужен экскурсионный тур по Европе на сентябрь 2025',
                'source': 'email',
                'status': 'new',
                'tags': ['Европа', 'Экскурсии']
            },
            {
                'name': 'Клиент 3',
                'email': 'client3@example.com',
                'phone': '+7 (999) 333-33-33',
                'details': 'Ищу горнолыжный курорт в Альпах на январь 2026',
                'source': 'telegram',
                'status': 'new',
                'tags': ['Альпы', 'Горные лыжи']
            }
        ]
        
        lead_ids = []
        for lead_data in test_leads:
            response = self.client.post(
                '/api/leads',
                data=json.dumps(lead_data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 201, 'Лид должен быть успешно создан')
            data = json.loads(response.data)
            lead_ids.append(data['lead']['id'])
        
        # 2. Запускаем пакетную обработку лидов
        response = self.client.post('/api/inquiries/process-all')
        
        self.assertEqual(response.status_code, 200, 'Пакетная обработка должна быть успешной')
        
        # Проверяем результаты обработки
        data = json.loads(response.data)
        self.assertEqual(len(data['results']), 3, 'Должны быть обработаны все 3 лида')
        
        # 3. Проверяем, что статусы лидов обновлены
        response = self.client.get('/api/leads')
        
        data = json.loads(response.data)
        for lead in data['leads']:
            self.assertEqual(lead['status'], 'in_progress', 'Статус всех лидов должен быть "в работе"')
        
        # 4. Тестируем фильтрацию по источнику
        response = self.client.get('/api/leads?source=website')
        
        data = json.loads(response.data)
        self.assertEqual(len(data['leads']), 1, 'Должен быть найден 1 лид из источника website')
        self.assertEqual(data['leads'][0]['name'], 'Клиент 1', 'Имя клиента должно совпадать')
        
        # 5. Тестируем поиск по тегам
        response = self.client.get('/api/leads?tag=Европа')
        
        data = json.loads(response.data)
        self.assertEqual(len(data['leads']), 1, 'Должен быть найден 1 лид с тегом Европа')
        self.assertEqual(data['leads'][0]['name'], 'Клиент 2', 'Имя клиента должно совпадать')
    
    def test_data_integrity_across_components(self):
        """
        Тест для проверки сохранности данных при переходах между компонентами системы.
        
        Сценарий:
        1. Создание лида с определенными данными
        2. Обработка лида с сохранением метрик и аналитики
        3. Получение данных через разные API эндпоинты
        4. Проверка идентичности данных в разных представлениях
        """
        # Текущая дата для тестирования
        current_date = datetime.now()
        test_date = current_date.strftime('%Y-%m-%d')
        
        # 1. Создание лида с датами и специфическими полями
        lead_data = {
            'name': 'Тест Целостности',
            'email': 'integrity@example.com',
            'phone': '+7 (999) 999-99-99',
            'details': f'Запрос на тур в Грецию на дату {test_date}, для 2 взрослых и 1 ребенка',
            'source': 'website',
            'tags': ['Греция', 'Семейный отдых'],
            'additional_data': {
                'travel_date': test_date,
                'adults': 2,
                'children': 1,
                'budget': 250000,
                'preferred_hotels': ['Hotel A', 'Hotel B']
            }
        }
        
        response = self.client.post(
            '/api/leads',
            data=json.dumps(lead_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201, 'Лид должен быть успешно создан')
        
        # Получаем ID созданного лида
        data = json.loads(response.data)
        lead_id = data['lead']['id']
        
        # 2. Настраиваем мок для обработки лида с сохранением аналитики
        analysis_result = {
            'status': 'in_progress',
            'suggestion': 'Предложить туры в Грецию с семейными номерами',
            'confidence': 0.95,
            'analytics': {
                'destination': 'Greece',
                'travel_date': test_date,
                'party_size': 3,
                'budget': 250000,
                'interests': ['beach', 'family', 'culture'],
                'priority': 'high'
            }
        }
        
        mock_message = MagicMock()
        mock_message.content = json.dumps(analysis_result)
        self.mock_openai.return_value.chat.completions.create.return_value.choices[0].message = mock_message
        
        # Обрабатываем лид
        response = self.client.post(f'/api/leads/{lead_id}/analyze')
        
        self.assertEqual(response.status_code, 200, 'Анализ лида должен быть успешным')
        
        # 3. Получаем данные через разные API эндпоинты
        # Получение через основной API лидов
        response1 = self.client.get(f'/api/leads/{lead_id}')
        
        # Получение через API аналитики
        response2 = self.client.get(f'/api/analytics/leads/{lead_id}')
        
        # Получение через API взаимодействий
        response3 = self.client.get(f'/api/leads/{lead_id}/interactions')
        
        # 4. Проверка целостности данных
        data1 = json.loads(response1.data)
        self.assertEqual(data1['lead']['name'], 'Тест Целостности', 'Имя должно совпадать')
        self.assertEqual(data1['lead']['status'], 'in_progress', 'Статус должен совпадать')
        
        # Если API аналитики существует:
        if response2.status_code == 200:
            data2 = json.loads(response2.data)
            if 'analytics' in data2 and 'destination' in data2['analytics']:
                self.assertEqual(data2['analytics']['destination'], 'Greece', 'Анализ направления должен совпадать')
        
        # Проверка, что взаимодействие было создано
        data3 = json.loads(response3.data)
        if data3['interactions']:
            self.assertTrue(any('предложить туры' in i['content'].lower() for i in data3['interactions']), 
                           'Должно быть взаимодействие с предложением туров')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()