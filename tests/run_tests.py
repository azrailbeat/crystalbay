#!/usr/bin/env python3
"""
Запуск всех тестов системы
"""
import os
import sys
import logging
import unittest
from unittest import TestLoader, TextTestRunner, TestSuite

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Добавляем родительскую директорию в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_tests(test_classes=None, verbose=2, failfast=False):
    """
    Запускает тесты для указанных классов или всех обнаруженных тестов.
    
    Args:
        test_classes (list, optional): Список классов тестов для запуска
        verbose (int, optional): Уровень детализации вывода (0-2). По умолчанию 2
        failfast (bool, optional): Остановка при первой ошибке
        
    Returns:
        TestResult: Результаты выполнения тестов
    """
    # Если классы не указаны, обнаруживаем все тесты
    if test_classes is None:
        logging.info("Обнаружение тестов в директории tests/...")
        loader = TestLoader()
        start_dir = os.path.dirname(__file__)
        suite = loader.discover(start_dir, pattern="test_*.py")
    else:
        # Создаем набор из указанных классов
        suite = TestSuite()
        loader = TestLoader()
        for test_class in test_classes:
            suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Запускаем тесты
    runner = TextTestRunner(verbosity=verbose, failfast=failfast)
    logging.info("Запуск тестов...")
    result = runner.run(suite)
    
    # Выводим сводку
    logging.info(f"Запущено тестов: {result.testsRun}")
    logging.info(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    
    if result.failures:
        logging.error(f"Провалено: {len(result.failures)}")
        for i, (test, traceback) in enumerate(result.failures, 1):
            logging.error(f"Ошибка {i}: {test}")
            logging.debug(traceback)
    
    if result.errors:
        logging.error(f"Ошибок: {len(result.errors)}")
        for i, (test, traceback) in enumerate(result.errors, 1):
            logging.error(f"Исключение {i}: {test}")
            logging.debug(traceback)
    
    return result

def run_selected_tests():
    """Запускает только выбранные тесты (для быстрой разработки)"""
    from tests.test_models import TestLeadService
    from tests.test_api_integration import TestAPIIntegration
    from tests.test_inquiry_processor import TestInquiryProcessor
    from tests.test_ui import TestUIFunctionality, TestUIAppearance
    from tests.test_telegram_bot import TestTelegramBot, TestBotIntegrations
    from tests.test_email_integration import TestEmailIntegration, TestEmailProcessor
    
    test_classes = [
        TestLeadService,
        TestAPIIntegration,
        TestInquiryProcessor,
        TestUIFunctionality,
        TestUIAppearance,
        TestTelegramBot,
        TestBotIntegrations,
        TestEmailIntegration,
        TestEmailProcessor
    ]
    
    return run_tests(test_classes=test_classes, verbose=2, failfast=True)

def run_all_tests():
    """Запускает все обнаруженные тесты"""
    return run_tests(verbose=2, failfast=False)

def run_unit_tests():
    """Запускает только модульные тесты"""
    return run_tests(
        verbose=2, 
        failfast=False
    )

def run_integration_tests():
    """Запускает только интеграционные тесты"""
    from tests.test_integration import TestFullSystemIntegration
    
    test_classes = [
        TestFullSystemIntegration
    ]
    
    return run_tests(test_classes=test_classes, verbose=2, failfast=False)

def run_ui_tests():
    """Запускает только UI тесты"""
    try:
        from tests.test_javascript_ui import TestJavaScriptUI
        from tests.test_ui import TestUIFunctionality, TestUIAppearance
        
        test_classes = [
            TestJavaScriptUI,
            TestUIFunctionality,
            TestUIAppearance
        ]
        
        return run_tests(test_classes=test_classes, verbose=2, failfast=False)
    except ImportError:
        logging.error("Не удалось импортировать UI тесты. Возможно, не установлен Selenium.")
        return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Запуск тестов для системы Crystal Bay Travel CRM')
    parser.add_argument('--all', action='store_true', help='Запустить все тесты')
    parser.add_argument('--unit', action='store_true', help='Запустить только модульные тесты')
    parser.add_argument('--integration', action='store_true', help='Запустить только интеграционные тесты')
    parser.add_argument('--ui', action='store_true', help='Запустить только UI тесты')
    parser.add_argument('--selected', action='store_true', help='Запустить только выбранные тесты')
    parser.add_argument('-v', '--verbose', type=int, choices=[0, 1, 2], default=2, help='Уровень детализации вывода')
    parser.add_argument('-f', '--failfast', action='store_true', help='Остановка при первой ошибке')
    
    args = parser.parse_args()
    
    if args.all:
        result = run_all_tests()
    elif args.unit:
        result = run_unit_tests()
    elif args.integration:
        result = run_integration_tests()
    elif args.ui:
        result = run_ui_tests()
    elif args.selected:
        result = run_selected_tests()
    else:
        # По умолчанию запускаем все тесты
        result = run_all_tests()
    
    # Устанавливаем код выхода в зависимости от результатов
    if result and (result.failures or result.errors):
        sys.exit(1)
    else:
        sys.exit(0)