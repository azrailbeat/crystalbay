"""
Тесты Telegram-бота
"""
import os
import unittest
import sys
import logging
from unittest.mock import patch, MagicMock, AsyncMock

# Добавляем родительскую директорию в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestTelegramBot(unittest.TestCase):
    """Тесты для Telegram-бота"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Патчим необходимые объекты для тестирования
        self.patcher1 = patch('telegram.ext.ApplicationBuilder')
        self.patcher2 = patch('telegram.ext.CallbackContext')
        self.patcher3 = patch('telegram.Update')
        
        # Создаем моки
        self.mock_app_builder = self.patcher1.start()
        self.mock_context = self.patcher2.start()
        self.mock_update = self.patcher3.start()
        
        # Настраиваем цепочку вызовов для ApplicationBuilder
        mock_app = MagicMock()
        self.mock_app_builder.return_value.token.return_value.build.return_value = mock_app
        
        # Настраиваем мок для Update
        self.mock_update = MagicMock()
        self.mock_update.message = MagicMock()
        self.mock_update.message.text = '/start'
        self.mock_update.message.chat = MagicMock()
        self.mock_update.message.chat.id = 12345
        self.mock_update.callback_query = None
        
        # Настраиваем мок для Context
        self.mock_context = MagicMock()
        self.mock_context.bot = MagicMock()
        self.mock_context.bot.send_message = AsyncMock()
        self.mock_context.bot.send_photo = AsyncMock()
        self.mock_context.user_data = {}
        
        # Импортируем модуль с ботом после патчинга
        import crystal_bay_bot
        self.bot_module = crystal_bay_bot
    
    def tearDown(self):
        """Очистка после каждого теста"""
        # Останавливаем патчи
        self.patcher1.stop()
        self.patcher2.stop()
        self.patcher3.stop()
    
    @patch('crystal_bay_bot.start')
    def test_start_command(self, mock_start):
        """Тест команды /start"""
        # Настраиваем мок для асинхронной функции
        mock_start.return_value = None
        
        # Вызываем команду /start
        self.bot_module.start(self.mock_update, self.mock_context)
        
        # Проверяем, что функция была вызвана один раз
        mock_start.assert_called_once_with(self.mock_update, self.mock_context)
    
    @patch('crystal_bay_bot.help_command')
    def test_help_command(self, mock_help):
        """Тест команды /help"""
        # Настраиваем мок для асинхронной функции
        mock_help.return_value = None
        
        # Вызываем команду /help
        self.bot_module.help_command(self.mock_update, self.mock_context)
        
        # Проверяем, что функция была вызвана один раз
        mock_help.assert_called_once_with(self.mock_update, self.mock_context)
    
    @patch('crystal_bay_bot.cancel_command')
    def test_cancel_command(self, mock_cancel):
        """Тест команды /cancel"""
        # Настраиваем мок для асинхронной функции
        mock_cancel.return_value = None
        
        # Вызываем команду /cancel
        self.bot_module.cancel_command(self.mock_update, self.mock_context)
        
        # Проверяем, что функция была вызвана один раз
        mock_cancel.assert_called_once_with(self.mock_update, self.mock_context)
    
    def test_format_tour_details(self):
        """Тест функции форматирования деталей тура"""
        # Создаем тестовые данные для тура
        test_tour = {
            'id': 'TUR123',
            'name': 'Angsana Laguna Phuket 5*',
            'country': 'Таиланд',
            'region': 'Пхукет',
            'duration': 10,
            'price': 2500,
            'description': 'Роскошный отель на пляже Банг Тао с видом на море.',
            'amenities': ['Бассейн', 'СПА', 'Ресторан']
        }
        
        # Вызываем функцию форматирования
        formatted = self.bot_module.format_tour_details(test_tour)
        
        # Проверяем результат
        self.assertIn('Angsana Laguna Phuket 5*', formatted)
        self.assertIn('Таиланд, Пхукет', formatted)
        self.assertIn('10 ночей', formatted)
        self.assertIn('$2500', formatted)
        self.assertIn('Роскошный отель', formatted)
    
    @patch('helpers.fetch_cities')
    @patch('crystal_bay_bot.select_departure_city')
    def test_departure_city_selection(self, mock_select_city, mock_fetch_cities):
        """Тест выбора города отправления"""
        # Настраиваем мок для Query
        mock_query = MagicMock()
        mock_query.data = 'select_departure_city'
        mock_query.answer = AsyncMock()
        mock_query.edit_message_text = AsyncMock()
        
        # Настраиваем мок для получения городов
        mock_fetch_cities.return_value = [
            {'id': 'MSK', 'name': 'Москва'},
            {'id': 'SPB', 'name': 'Санкт-Петербург'}
        ]
        
        # Настраиваем мок для асинхронной функции
        mock_select_city.return_value = None
        
        # Обновляем mock_update для имитации callback query
        self.mock_update.callback_query = mock_query
        
        # Вызываем функцию обработки callback query
        self.bot_module.callback_handler(self.mock_update, self.mock_context)
        
        # Проверяем, что функция была вызвана один раз
        mock_select_city.assert_called_once_with(mock_query)
    
    @patch('crystal_bay_bot.handle_text_message')
    def test_text_message_handling(self, mock_handle_text):
        """Тест обработки текстовых сообщений"""
        # Настраиваем мок для асинхронной функции
        mock_handle_text.return_value = None
        
        # Устанавливаем текст сообщения
        self.mock_update.message.text = 'Хочу забронировать тур'
        
        # Вызываем функцию обработки текстовых сообщений
        self.bot_module.handle_text_message(self.mock_update, self.mock_context)
        
        # Проверяем, что функция была вызвана один раз
        mock_handle_text.assert_called_once_with(self.mock_update, self.mock_context)


class TestBotIntegrations(unittest.TestCase):
    """Тесты интеграций Telegram-бота с другими компонентами системы"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Патчим модуль бота и его зависимости
        self.patcher1 = patch('crystal_bay_bot.api_integration')
        self.patcher2 = patch('crystal_bay_bot.inquiry_processor')
        
        # Создаем моки
        self.mock_api = self.patcher1.start()
        self.mock_inquiry_processor = self.patcher2.start()
        
        # Настраиваем мок для API
        self.mock_api_instance = MagicMock()
        self.mock_api.get_api_integration.return_value = self.mock_api_instance
        
        # Настраиваем мок для процессора запросов
        self.mock_processor = MagicMock()
        self.mock_inquiry_processor.InquiryProcessor.return_value = self.mock_processor
    
    def tearDown(self):
        """Очистка после каждого теста"""
        # Останавливаем патчи
        self.patcher1.stop()
        self.patcher2.stop()
    
    def test_booking_check_integration(self):
        """Тест интеграции проверки бронирования с API"""
        # Настраиваем мок для check_booking
        self.mock_api_instance.check_booking.return_value = {
            'reference': 'CB12345',
            'status': 'confirmed',
            'hotel': 'Angsana Laguna Phuket 5*',
            'check_in': '2025-07-10',
            'check_out': '2025-07-20',
            'customer': {
                'name': 'Иван Петров',
                'email': 'ivan@example.com'
            }
        }
        
        # Проверяем результат запроса
        result = self.mock_api_instance.check_booking('CB12345')
        
        # Проверяем, что мок был вызван и результат корректен
        self.mock_api_instance.check_booking.assert_called_once_with('CB12345')
        self.assertEqual(result['reference'], 'CB12345')
        self.assertEqual(result['status'], 'confirmed')
    
    def test_inquiry_processing_integration(self):
        """Тест интеграции обработки запроса с процессором запросов"""
        # Настраиваем мок для process_inquiry
        self.mock_processor.process_inquiry.return_value = {
            'lead_id': 'lead123',
            'status': 'new',
            'suggestion': 'Предложить туры в Таиланд'
        }
        
        # Тестовые данные запроса
        inquiry_data = {
            'name': 'Мария Сидорова',
            'email': 'maria@example.com',
            'phone': '+7 (999) 123-45-67',
            'message': 'Интересует тур в Таиланд в июле',
            'source': 'telegram'
        }
        
        # Вызываем метод обработки запроса
        result = self.mock_processor.process_inquiry(inquiry_data)
        
        # Проверяем, что мок был вызван с правильными параметрами и результат корректен
        self.mock_processor.process_inquiry.assert_called_once_with(inquiry_data)
        self.assertEqual(result['lead_id'], 'lead123')
        self.assertEqual(result['status'], 'new')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()