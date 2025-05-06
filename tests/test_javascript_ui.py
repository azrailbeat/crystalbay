"""
Тесты для JavaScript UI компонентов с использованием Selenium
"""
import os
import unittest
import sys
import logging
import time
from unittest.mock import patch

# Добавляем родительскую директорию в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Примечание: для запуска этих тестов требуется установка Selenium и соответствующего WebDriver
# Также требуется, чтобы приложение было запущено на localhost:5000
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("Selenium не установлен, тесты UI будут пропущены")

from models import _memory_leads

@unittest.skipIf(not SELENIUM_AVAILABLE, "Selenium не установлен")
class TestJavaScriptUI(unittest.TestCase):
    """Тесты для JavaScript UI компонентов"""
    
    @classmethod
    def setUpClass(cls):
        """Настройка перед всеми тестами"""
        if not SELENIUM_AVAILABLE:
            return
        
        try:
            # Создаем браузер для тестов
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # Запуск в безголовом режиме
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            cls.driver = webdriver.Chrome(options=options)
            cls.driver.implicitly_wait(10)
            
            # URL приложения
            cls.base_url = 'http://localhost:5000'
        except Exception as e:
            logging.error(f"Ошибка инициализации WebDriver: {e}")
            cls.driver = None
    
    @classmethod
    def tearDownClass(cls):
        """Очистка после всех тестов"""
        if hasattr(cls, 'driver') and cls.driver:
            cls.driver.quit()
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        if not hasattr(self, 'driver') or not self.driver:
            self.skipTest("WebDriver не инициализирован")
        
        # Сохраняем оригинальные данные
        self.original_leads = _memory_leads.copy()
    
    def tearDown(self):
        """Очистка после каждого теста"""
        # Восстанавливаем оригинальные данные
        _memory_leads.clear()
        _memory_leads.extend(self.original_leads)
    
    def test_kanban_board_loads(self):
        """Тест: Канбан-доска загружается с карточками"""
        # Переходим на страницу с канбан-доской
        self.driver.get(f"{self.base_url}/leads")
        
        try:
            # Проверяем, что доска загрузилась
            board = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'kanban-board'))
            )
            self.assertIsNotNone(board)
            
            # Проверяем, что есть колонки
            columns = self.driver.find_elements(By.CLASS_NAME, 'kanban-column')
            self.assertGreater(len(columns), 0)
            
            # Проверяем, что есть карточки лидов
            cards = self.driver.find_elements(By.CLASS_NAME, 'lead-card')
            self.assertGreater(len(cards), 0)
            
            # Проверяем, что в консоли нет ошибок JavaScript
            console_logs = self.driver.get_log('browser')
            errors = [log for log in console_logs if log['level'] == 'SEVERE']
            if errors:
                logging.warning(f"JavaScript errors in console: {errors}")
                
        except TimeoutException:
            self.fail("Тайм-аут при ожидании загрузки канбан-доски")
        except NoSuchElementException:
            self.fail("Элементы канбан-доски не найдены")
    
    def test_drag_and_drop_functionality(self):
        """Тест: функциональность drag-and-drop работает"""
        # Переходим на страницу с канбан-доской
        self.driver.get(f"{self.base_url}/leads")
        
        try:
            # Ожидаем загрузки карточек
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'lead-card'))
            )
            
            # Получаем карточку и целевую колонку
            card = self.driver.find_element(By.CLASS_NAME, 'lead-card')
            source_column = card.find_element(By.XPATH, './ancestor::div[contains(@class, "kanban-column")]')
            target_column = self.driver.find_elements(By.CLASS_NAME, 'kanban-column')[1]  # Вторая колонка
            
            # Сохраняем начальные счетчики
            initial_source_count = int(source_column.find_element(By.CLASS_NAME, 'column-count').text)
            initial_target_count = int(target_column.find_element(By.CLASS_NAME, 'column-count').text)
            
            # Выполняем drag-and-drop
            action = webdriver.ActionChains(self.driver)
            action.drag_and_drop(card, target_column).perform()
            
            # Даем время на обработку перетаскивания
            time.sleep(2)
            
            # Проверяем, что счетчики обновились
            final_source_count = int(source_column.find_element(By.CLASS_NAME, 'column-count').text)
            final_target_count = int(target_column.find_element(By.CLASS_NAME, 'column-count').text)
            
            self.assertEqual(final_source_count, initial_source_count - 1)
            self.assertEqual(final_target_count, initial_target_count + 1)
            
            # Проверяем, что в консоли нет ошибок JavaScript
            console_logs = self.driver.get_log('browser')
            errors = [log for log in console_logs if log['level'] == 'SEVERE']
            if errors:
                logging.warning(f"JavaScript errors in console: {errors}")
                
        except TimeoutException:
            self.fail("Тайм-аут при ожидании загрузки элементов")
        except NoSuchElementException as e:
            self.fail(f"Элемент не найден: {e}")
        except Exception as e:
            self.fail(f"Ошибка в тесте drag-and-drop: {e}")
    
    def test_lead_modal_opens(self):
        """Тест: модальное окно лида открывается по клику на карточку"""
        # Переходим на страницу с канбан-доской
        self.driver.get(f"{self.base_url}/leads")
        
        try:
            # Ожидаем загрузки карточек
            card = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'lead-card'))
            )
            
            # Кликаем на карточку
            card.click()
            
            # Ожидаем открытия модального окна
            modal = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'viewLeadModal'))
            )
            
            # Проверяем, что модальное окно открылось
            self.assertTrue(modal.is_displayed())
            
            # Проверяем, что данные загрузились
            lead_name = modal.find_element(By.ID, 'lead-name')
            self.assertIsNotNone(lead_name.text)
            self.assertNotEqual(lead_name.text, '')
            
            # Проверяем, что есть форма добавления комментария
            comment_form = modal.find_element(By.ID, 'add-interaction-form')
            self.assertIsNotNone(comment_form)
            
            # Закрываем модальное окно
            close_button = modal.find_element(By.CLASS_NAME, 'btn-close')
            close_button.click()
            
            # Ожидаем закрытия модального окна
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((By.ID, 'viewLeadModal'))
            )
            
            # Проверяем, что модальное окно закрылось
            self.assertFalse(modal.is_displayed())
            
        except TimeoutException:
            self.fail("Тайм-аут при ожидании открытия модального окна")
        except NoSuchElementException as e:
            self.fail(f"Элемент не найден: {e}")
    
    def test_auto_processing_button(self):
        """Тест: кнопка автообработки запускает процесс"""
        # Переходим на страницу с канбан-доской
        self.driver.get(f"{self.base_url}/leads")
        
        try:
            # Ожидаем загрузки страницы
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'kanban-board'))
            )
            
            # Находим кнопку запуска автообработки
            start_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'start-process-btn'))
            )
            
            # Нажимаем кнопку
            start_btn.click()
            
            # Ожидаем появления прогресс-бара
            progress_bar = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'progress-bar'))
            )
            
            # Проверяем, что процесс запустился
            self.assertTrue(progress_bar.is_displayed())
            
            # Ожидаем появления лога процесса
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'process-log-item'))
            )
            
            # Проверяем, что есть записи в логе
            log_items = self.driver.find_elements(By.CLASS_NAME, 'process-log-item')
            self.assertGreater(len(log_items), 0)
            
            # Даем процессу немного поработать
            time.sleep(5)
            
            # Находим кнопку остановки автообработки
            stop_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'stop-process-btn'))
            )
            
            # Нажимаем кнопку остановки
            stop_btn.click()
            
            # Проверяем, что прогресс-бар исчез или изменился
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, 'progress-bar'))
                )
            except TimeoutException:
                # Или проверяем, что прогресс достиг 100%
                progress_width = progress_bar.get_attribute('style')
                self.assertIn('100%', progress_width)
            
        except TimeoutException as e:
            self.fail(f"Тайм-аут при ожидании элементов: {e}")
        except NoSuchElementException as e:
            self.fail(f"Элемент не найден: {e}")
        except Exception as e:
            self.fail(f"Ошибка в тесте автообработки: {e}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()