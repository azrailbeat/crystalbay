"""
Тесты для модуля интеграции с электронной почтой
"""
import os
import unittest
import sys
import logging
from unittest.mock import patch, MagicMock

# Добавляем родительскую директорию в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from email_integration import EmailIntegration
from email_processor import EmailProcessor
from models import LeadService, _memory_leads

class TestEmailIntegration(unittest.TestCase):
    """Тесты для класса EmailIntegration"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Сохраняем оригинальные данные
        self.original_leads = _memory_leads.copy()
        
        # Очищаем данные для тестов
        _memory_leads.clear()
        
        # Патчим SendGrid
        self.patcher = patch('email_integration.SendGridAPIClient')
        self.mock_sendgrid = self.patcher.start()
        
        # Настраиваем мок для SendGrid
        self.mock_sg_instance = MagicMock()
        self.mock_sendgrid.return_value = self.mock_sg_instance
        
        # Создаем экземпляр интеграции
        self.email_integration = EmailIntegration()
    
    def tearDown(self):
        """Очистка после каждого теста"""
        # Восстанавливаем оригинальные данные
        _memory_leads.clear()
        _memory_leads.extend(self.original_leads)
        
        # Останавливаем патч
        self.patcher.stop()
    
    @patch('email_integration.os.environ.get')
    def test_is_configured(self, mock_env_get):
        """Тест проверки настройки SendGrid"""
        # Случай, когда API-ключ настроен
        mock_env_get.return_value = 'SG.test-api-key'
        self.assertTrue(self.email_integration.is_configured())
        
        # Случай, когда API-ключ не настроен
        mock_env_get.return_value = None
        self.assertFalse(self.email_integration.is_configured())
    
    @patch('email_integration.Mail')
    @patch('email_integration.Email')
    @patch('email_integration.To')
    @patch('email_integration.Content')
    def test_send_email(self, mock_content, mock_to, mock_email, mock_mail):
        """Тест отправки электронной почты"""
        # Настраиваем моки
        mock_mail_instance = MagicMock()
        mock_mail.return_value = mock_mail_instance
        
        # Вызываем метод отправки
        result = self.email_integration.send_email(
            to_email='test@example.com',
            subject='Test Subject',
            text_content='Test Content'
        )
        
        # Проверяем вызовы методов
        mock_email.assert_called_once()
        mock_to.assert_called_once()
        mock_content.assert_called_once()
        mock_mail.assert_called_once()
        self.mock_sg_instance.send.assert_called_once_with(mock_mail_instance)
        
        # Проверяем результат
        self.assertTrue(result)
        
        # Проверяем обработку ошибок
        self.mock_sg_instance.send.side_effect = Exception("SendGrid API Error")
        result = self.email_integration.send_email(
            to_email='test@example.com',
            subject='Test Subject',
            text_content='Test Content'
        )
        self.assertFalse(result)
    
    @patch('email_processor.EmailProcessor.process_email')
    def test_receive_webhook(self, mock_process_email):
        """Тест обработки входящего вебхука"""
        # Настраиваем мок для обработки email
        mock_process_email.return_value = {
            'name': 'Test User',
            'email': 'from@example.com',
            'details': 'Test message',
            'source': 'email'
        }
        
        # Патчим LeadService.create_lead
        with patch('models.LeadService.create_lead') as mock_create_lead:
            # Настраиваем мок для create_lead
            mock_create_lead.return_value = {
                'id': 'lead123',
                'name': 'Test User',
                'email': 'from@example.com',
                'status': 'new'
            }
            
            # Создаем тестовые данные вебхука
            webhook_data = {
                'from': 'Test User <from@example.com>',
                'subject': 'Запрос о турах',
                'text': 'Хочу узнать о турах в Таиланд.'
            }
            
            # Обрабатываем вебхук
            result = self.email_integration.receive_webhook(webhook_data)
            
            # Проверяем результат
            self.assertIsNotNone(result)
            self.assertEqual(result['id'], 'lead123')
            
            # Проверяем вызовы методов
            mock_process_email.assert_called_once()
            mock_create_lead.assert_called_once()
    
    @patch('email_integration.EmailIntegration._send_auto_response')
    def test_auto_response(self, mock_send_auto_response):
        """Тест автоматического ответа"""
        # Настраиваем мок для _send_auto_response
        mock_send_auto_response.return_value = True
        
        # Создаем тестовый запрос
        test_lead = {
            'id': 'lead123',
            'name': 'Test User',
            'email': 'test@example.com',
            'status': 'new',
            'details': 'Запрос о турах'
        }
        
        # Проверяем отправку автоответа
        result = self.email_integration._send_auto_response(test_lead)
        
        # Проверяем результат
        self.assertTrue(result)
        mock_send_auto_response.assert_called_once_with(test_lead)


class TestEmailProcessor(unittest.TestCase):
    """Тесты для класса EmailProcessor"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.processor = EmailProcessor()
    
    def test_extract_email(self):
        """Тест извлечения адреса электронной почты"""
        # Тестовые случаи
        test_cases = [
            ('John Doe <john@example.com>', 'john@example.com'),
            ('<jane@example.com>', 'jane@example.com'),
            ('test@example.com', 'test@example.com'),
            ('Invalid', '')
        ]
        
        # Проверяем каждый случай
        for from_header, expected in test_cases:
            result = self.processor._extract_email(from_header)
            self.assertEqual(result, expected)
    
    def test_extract_name(self):
        """Тест извлечения имени отправителя"""
        # Тестовые случаи
        test_cases = [
            ('John Doe <john@example.com>', 'John Doe'),
            ('<jane@example.com>', ''),
            ('test@example.com', ''),
            ('Jane Smith', 'Jane Smith')
        ]
        
        # Проверяем каждый случай
        for from_header, expected in test_cases:
            result = self.processor._extract_name(from_header)
            self.assertEqual(result, expected)
    
    def test_extract_phone(self):
        """Тест извлечения номера телефона"""
        # Тестовые случаи
        test_bodies = [
            ('Мой номер телефона: +7 (999) 123-45-67', '+7 (999) 123-45-67'),
            ('Тел: 8-800-123-4567', '8-800-123-4567'),
            ('Телефон +79991234567', '+79991234567'),
            ('Нет номера телефона', '')
        ]
        
        # Проверяем каждый случай
        for body, expected in test_bodies:
            result = self.processor._extract_phone(body)
            self.assertEqual(result, expected)
    
    def test_determine_interest(self):
        """Тест определения интереса по теме и содержанию письма"""
        # Тестовые случаи
        test_cases = [
            ('Запрос о турах в Таиланд', 'Хочу узнать о пляжном отдыхе', 'Пляжный отдых'),
            ('Горнолыжный курорт', 'Интересуют горные лыжи', 'Горнолыжный отдых'),
            ('Экскурсии', 'Хочу посмотреть достопримечательности', 'Экскурсионный тур'),
            ('Общий вопрос', 'Подскажите варианты отдыха', 'Консультация')
        ]
        
        # Проверяем каждый случай
        for subject, body, expected in test_cases:
            result = self.processor._determine_interest(subject, body)
            self.assertEqual(result, expected)
    
    def test_process_email(self):
        """Тест обработки электронного письма"""
        # Создаем тестовое содержимое письма
        email_content = """
From: Test User <test@example.com>
Subject: Запрос о турах в Таиланд
Date: Tue, 6 May 2025 10:00:00 +0300

Здравствуйте!

Я бы хотел узнать о турах в Таиланд на июль 2025 года.
Интересует пляжный отдых на Пхукете для семьи из 3 человек.

Мой телефон: +7 (999) 123-45-67

С уважением,
Test User
"""
        
        # Обрабатываем письмо
        result = self.processor.process_email(email_content)
        
        # Проверяем результат
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Test User')
        self.assertEqual(result['email'], 'test@example.com')
        self.assertEqual(result['phone'], '+7 (999) 123-45-67')
        self.assertEqual(result['source'], 'email')
        self.assertIn('Таиланд', result['details'])
        self.assertEqual(result['interest'], 'Пляжный отдых')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()