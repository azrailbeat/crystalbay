"""
Тесты для модуля обработки запросов
"""
import os
import unittest
import sys
import logging
from unittest.mock import patch, MagicMock, ANY

# Добавляем родительскую директорию в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from inquiry_processor import InquiryProcessor
from models import LeadService, _memory_leads, _memory_agents_config

class TestInquiryProcessor(unittest.TestCase):
    """Тесты для класса InquiryProcessor"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Сохраняем оригинальные данные
        self.original_leads = _memory_leads.copy()
        self.original_config = _memory_agents_config.copy()
        
        # Настраиваем тестовую конфигурацию
        _memory_agents_config.update({
            'auto_process_enabled': True,
            'default_agent_id': 'test_agent'
        })
        
        # Очищаем данные для тестов
        _memory_leads.clear()
        
        # Создаем процессор запросов с моком OpenAI
        self.patcher = patch('openai.OpenAI')
        self.mock_openai = self.patcher.start()
        
        # Настраиваем мок для ChatCompletion
        mock_chat = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        
        mock_message.content = '{"status": "in_progress", "suggestion": "Test suggestion", "confidence": 0.85}'
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_chat.return_value = mock_response
        
        # Применяем мок к методу chat.completions.create
        self.mock_openai.return_value.chat.completions.create = mock_chat
        
        # Переопределяем OpenAI в inquiry_processor для тестирования
        import inquiry_processor
        inquiry_processor.openai.OpenAI = self.mock_openai
        
        # Создаем экземпляр процессора
        self.processor = InquiryProcessor()
    
    def tearDown(self):
        """Очистка после каждого теста"""
        # Восстанавливаем оригинальные данные
        _memory_leads.clear()
        _memory_leads.extend(self.original_leads)
        
        # Восстанавливаем конфигурацию
        _memory_agents_config.clear()
        _memory_agents_config.update(self.original_config)
        
        # Останавливаем моки
        self.patcher.stop()
    
    def test_process_inquiry(self):
        """Тест обработки нового запроса"""
        # Тестовые данные запроса
        inquiry_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+7 (999) 123-45-67',
            'message': 'Хочу забронировать тур в Таиланд для всей семьи в июле.',
            'source': 'website'
        }
        
        # Обрабатываем запрос
        result = self.processor.process_inquiry(inquiry_data)
        
        # Проверяем результат
        self.assertIsNotNone(result)
        self.assertIn('lead_id', result)
        self.assertIn('status', result)
        self.assertEqual(result['status'], 'in_progress')
        self.assertIn('suggestion', result)
        
        # Проверяем, что создан лид в хранилище
        self.assertEqual(len(_memory_leads), 1)
        self.assertEqual(_memory_leads[0]['name'], 'Test User')
        self.assertEqual(_memory_leads[0]['status'], 'in_progress')
        
        # Проверяем, что был вызван OpenAI API
        self.mock_openai.return_value.chat.completions.create.assert_called_once()
    
    def test_process_leads_batch(self):
        """Тест массовой обработки лидов"""
        # Создаем тестовые лиды
        test_leads = [
            {
                'id': '1',
                'name': 'User 1',
                'email': 'user1@example.com',
                'phone': '+7 (999) 111-11-11',
                'status': 'new',
                'details': 'Запрос на тур в Европу',
                'source': 'website',
                'created_at': '2025-05-06T10:00:00'
            },
            {
                'id': '2',
                'name': 'User 2',
                'email': 'user2@example.com',
                'phone': '+7 (999) 222-22-22',
                'status': 'new',
                'details': 'Запрос о горнолыжном отдыхе',
                'source': 'phone',
                'created_at': '2025-05-06T11:00:00'
            }
        ]
        
        _memory_leads.extend(test_leads)
        
        # Обрабатываем пакет лидов
        results = self.processor.process_leads_batch(limit=2)
        
        # Проверяем результаты
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIn('lead_id', result)
            self.assertIn('status', result)
            self.assertEqual(result['status'], 'in_progress')
        
        # Проверяем, что статусы лидов обновлены
        for lead in _memory_leads:
            self.assertEqual(lead['status'], 'in_progress')
        
        # Проверяем, что OpenAI API был вызван дважды
        self.assertEqual(self.mock_openai.return_value.chat.completions.create.call_count, 2)
    
    def test_analyze_lead(self):
        """Тест анализа лида с помощью ИИ"""
        # Создаем тестовый лид
        test_lead = {
            'id': 'test123',
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+7 (999) 123-45-67',
            'status': 'new',
            'details': 'Запрос о турах в Таиланд в июле.',
            'source': 'website',
            'created_at': '2025-05-06T10:00:00'
        }
        
        _memory_leads.append(test_lead)
        
        # Анализируем лид
        result = self.processor.analyze_lead(test_lead)
        
        # Проверяем результат
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'in_progress')
        self.assertIn('suggestion', result)
        self.assertIn('confidence', result)
        
        # Проверяем, что статус лида обновлен
        lead = LeadService.get_lead_fallback('test123')
        self.assertEqual(lead['status'], 'in_progress')
        
        # Проверяем вызов OpenAI
        self.mock_openai.return_value.chat.completions.create.assert_called_once_with(
            model="gpt-4o",
            messages=ANY,
            response_format={"type": "json_object"}
        )
    
    def test_generate_response(self):
        """Тест генерации ответа для клиента"""
        # Создаем тестовый лид
        test_lead = {
            'id': 'test123',
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+7 (999) 123-45-67',
            'status': 'in_progress',
            'details': 'Запрос о турах в Таиланд в июле.',
            'source': 'website',
            'created_at': '2025-05-06T10:00:00'
        }
        
        _memory_leads.append(test_lead)
        
        # Устанавливаем мок для генерации ответа
        mock_chat = self.mock_openai.return_value.chat.completions.create
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = 'Здравствуйте! Мы подобрали для вас несколько вариантов туров в Таиланд на июль...'
        mock_choice.message = mock_message
        mock_chat.return_value.choices = [mock_choice]
        
        # Генерируем ответ
        response = self.processor.generate_response('test123')
        
        # Проверяем результат
        self.assertIsNotNone(response)
        self.assertTrue(response['success'])
        self.assertEqual(response['lead_id'], 'test123')
        self.assertIn('Здравствуйте!', response['response'])
        
        # Проверяем вызов OpenAI
        mock_chat.assert_called_with(
            model="gpt-4o",
            messages=ANY
        )
    
    @patch('inquiry_processor.logging')
    def test_error_handling(self, mock_logging):
        """Тест обработки ошибок"""
        # Настраиваем мок для имитации ошибки
        self.mock_openai.return_value.chat.completions.create.side_effect = Exception("API error")
        
        # Создаем тестовый лид
        test_lead = {
            'id': 'test123',
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+7 (999) 123-45-67',
            'status': 'new',
            'details': 'Запрос о турах в Таиланд в июле.',
            'source': 'website',
            'created_at': '2025-05-06T10:00:00'
        }
        
        _memory_leads.append(test_lead)
        
        # Вызываем метод, который должен вызвать ошибку
        result = self.processor.analyze_lead(test_lead)
        
        # Проверяем, что обрабатывается правильно
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'new')
        self.assertIn('Ошибка обработки AI', result['suggestion'])
        
        # Проверяем, что ошибка логируется
        mock_logging.error.assert_called()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()