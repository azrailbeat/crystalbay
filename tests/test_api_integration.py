"""
Тесты интеграции с внешними API
"""
import os
import unittest
import sys
import logging
from unittest.mock import patch, MagicMock

# Добавляем родительскую директорию в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api_integration import APIIntegration, get_api_integration

class TestAPIIntegration(unittest.TestCase):
    """Тесты для класса APIIntegration"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.api = APIIntegration()
    
    def test_singleton_pattern(self):
        """Тест паттерна 'одиночка' для получения экземпляра API"""
        api1 = get_api_integration()
        api2 = get_api_integration()
        # Проверяем, что возвращается один и тот же экземпляр
        self.assertIs(api1, api2)
    
    def test_check_booking_mock(self):
        """Тест получения информации о бронировании (мок-данные)"""
        # Тест для существующего бронирования
        booking = self.api.check_booking('CB12345')
        self.assertIsNotNone(booking)
        self.assertEqual(booking['reference'], 'CB12345')
        self.assertIn('customer', booking)
        self.assertIn('status', booking)
        
        # Тест для несуществующего бронирования
        no_booking = self.api.check_booking('INVALID')
        self.assertIsNone(no_booking)
    
    def test_search_bookings_mock(self):
        """Тест поиска бронирований по данным клиента (мок-данные)"""
        # Поиск по email
        bookings = self.api.search_bookings(customer_email='john.doe@example.com')
        self.assertIsNotNone(bookings)
        self.assertGreater(len(bookings), 0)
        self.assertEqual(bookings[0]['customer']['email'], 'john.doe@example.com')
        
        # Поиск по несуществующему email
        no_bookings = self.api.search_bookings(customer_email='nonexistent@example.com')
        self.assertEqual(len(no_bookings), 0)
    
    def test_check_flight_mock(self):
        """Тест проверки статуса рейса (мок-данные)"""
        # Проверка существующего рейса
        flight = self.api.check_flight('SU1234', '2025-06-01')
        self.assertIsNotNone(flight)
        self.assertEqual(flight['flight_number'], 'SU1234')
        self.assertEqual(flight['departure_date'], '2025-06-01')
        
        # Проверка несуществующего рейса
        no_flight = self.api.check_flight('XX9999', '2025-06-01')
        self.assertIsNone(no_flight)
    
    def test_check_hotel_amenities_mock(self):
        """Тест проверки удобств отеля (мок-данные)"""
        # Проверка существующего отеля
        amenities = self.api.check_hotel_amenities('HTL123')
        self.assertIsNotNone(amenities)
        self.assertEqual(amenities['hotel_id'], 'HTL123')
        self.assertIn('amenities', amenities)
        self.assertIsInstance(amenities['amenities'], list)
        
        # Проверка несуществующего отеля
        no_amenities = self.api.check_hotel_amenities('INVALID')
        self.assertIsNone(no_amenities)
    
    @patch('api_integration.requests.request')
    def test_samo_request(self, mock_request):
        """Тест запросов к API SAMO с использованием моков"""
        # Настраиваем мок для успешного ответа
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'success', 'data': [{'test': 'data'}]}
        mock_request.return_value = mock_response
        
        # Выполняем запрос
        result = self.api._make_samo_request('/test/endpoint')
        
        # Проверяем, что метод был вызван с правильными параметрами
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs['method'], 'GET')
        self.assertIn('/test/endpoint', kwargs['url'])
        self.assertIn('Authorization', kwargs['headers'])
        
        # Проверяем результат
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json(), {'status': 'success', 'data': [{'test': 'data'}]})
        
        # Тестируем обработку ошибок
        mock_request.reset_mock()
        mock_request.side_effect = Exception('Test exception')
        
        # Проверяем, что исключение обрабатывается
        result = self.api._make_samo_request('/test/error')
        self.assertIsNone(result)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()