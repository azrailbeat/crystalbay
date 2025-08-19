#!/usr/bin/env python3
"""
Customer Journey Test Suite для Crystal Bay Travel System
Проверяет все основные пользовательские сценарии
"""
import requests
import json
from datetime import datetime
import time

BASE_URL = "http://localhost:5000"

class CustomerJourneyTests:
    """Тестирование пользовательских сценариев"""
    
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_result(self, test_name, status, details=""):
        """Логирование результата теста"""
        result = {
            "test": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        print(f"[{status}] {test_name}: {details}")
        
    def test_dashboard_accessibility(self):
        """Тест доступности дашборда"""
        try:
            response = self.session.get(f"{BASE_URL}/")
            if response.status_code == 200:
                if "Дашборд" in response.text and "Crystal Bay" in response.text:
                    self.log_result("Dashboard Accessibility", "PASS", "Дашборд загружается корректно")
                else:
                    self.log_result("Dashboard Accessibility", "FAIL", "Отсутствует базовый контент")
            else:
                self.log_result("Dashboard Accessibility", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Dashboard Accessibility", "ERROR", str(e))
            
    def test_leads_management_flow(self):
        """Тест управления лидами"""
        try:
            # Доступность страницы лидов
            response = self.session.get(f"{BASE_URL}/leads")
            if response.status_code != 200:
                self.log_result("Leads Management", "FAIL", f"Страница лидов недоступна: {response.status_code}")
                return
                
            # Проверка наличия канбан доски
            if "kanban-board" in response.text and ("Новые" in response.text or "новые" in response.text):
                self.log_result("Leads Kanban Board", "PASS", "Канбан доска отображается")
            else:
                self.log_result("Leads Kanban Board", "FAIL", "Канбан доска не найдена")
                
            # Тест API создания лида
            lead_data = {
                "customer_name": "Тестовый Клиент",
                "customer_phone": "+7 777 123 45 67",
                "customer_email": "test@crystalbay.com",
                "source": "website",
                "interest": "beach",
                "notes": "Тестовая заявка"
            }
            
            response = self.session.post(f"{BASE_URL}/api/leads", json=lead_data)
            if response.status_code in [200, 201]:
                self.log_result("Lead Creation API", "PASS", "Лид создается через API")
            else:
                self.log_result("Lead Creation API", "FAIL", f"Ошибка создания лида: {response.status_code}")
                
        except Exception as e:
            self.log_result("Leads Management", "ERROR", str(e))
            
    def test_tours_search_functionality(self):
        """Тест функциональности поиска туров"""
        try:
            # Доступность страницы поиска туров
            response = self.session.get(f"{BASE_URL}/tours-search")
            if response.status_code != 200:
                self.log_result("Tours Search Page", "FAIL", f"Страница недоступна: {response.status_code}")
                return
                
            # Проверка формы поиска
            if "stateinc" in response.text and "townfrominc" in response.text:
                self.log_result("Tours Search Form", "PASS", "Форма поиска присутствует")
            else:
                self.log_result("Tours Search Form", "FAIL", "Форма поиска не найдена")
                
            # Тест SAMO API статуса
            response = self.session.get(f"{BASE_URL}/api/samo/test")
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.log_result("SAMO API Connection", "PASS", "SAMO API подключен")
                else:
                    self.log_result("SAMO API Connection", "WARNING", "SAMO API недоступен (ожидается 403)")
            else:
                self.log_result("SAMO API Connection", "FAIL", f"Ошибка тестирования API: {response.status_code}")
                
        except Exception as e:
            self.log_result("Tours Search", "ERROR", str(e))
            
    def test_samo_testing_interface(self):
        """Тест интерфейса тестирования SAMO API"""
        try:
            response = self.session.get(f"{BASE_URL}/samo-testing")
            if response.status_code == 200:
                if "SAMO" in response.text and ("test" in response.text.lower() or "тест" in response.text.lower()):
                    self.log_result("SAMO Testing Interface", "PASS", "Интерфейс тестирования доступен")
                else:
                    self.log_result("SAMO Testing Interface", "FAIL", "Неполный интерфейс тестирования")
            else:
                self.log_result("SAMO Testing Interface", "FAIL", f"Страница недоступна: {response.status_code}")
        except Exception as e:
            self.log_result("SAMO Testing Interface", "ERROR", str(e))
            
    def test_settings_management(self):
        """Тест управления настройками"""
        try:
            response = self.session.get(f"{BASE_URL}/unified-settings")
            if response.status_code == 200:
                if "SAMO API" in response.text and "Wazzup" in response.text:
                    self.log_result("Settings Interface", "PASS", "Панель настроек доступна")
                else:
                    self.log_result("Settings Interface", "FAIL", "Неполная панель настроек")
            else:
                self.log_result("Settings Interface", "FAIL", f"Настройки недоступны: {response.status_code}")
        except Exception as e:
            self.log_result("Settings Management", "ERROR", str(e))
            
    def test_responsive_layout(self):
        """Тест адаптивной вёрстки"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
            }
            response = self.session.get(f"{BASE_URL}/", headers=headers)
            if response.status_code == 200:
                if "viewport" in response.text and "bootstrap" in response.text:
                    self.log_result("Responsive Layout", "PASS", "Мобильная версия поддерживается")
                else:
                    self.log_result("Responsive Layout", "WARNING", "Возможны проблемы с мобильной версией")
            else:
                self.log_result("Responsive Layout", "FAIL", f"Ошибка загрузки: {response.status_code}")
        except Exception as e:
            self.log_result("Responsive Layout", "ERROR", str(e))
            
    def test_navigation_menu(self):
        """Тест навигационного меню"""
        try:
            response = self.session.get(f"{BASE_URL}/")
            if response.status_code == 200:
                # Проверяем основные ссылки меню
                menu_items = ["leads", "tours-search", "samo-testing", "unified-settings"]
                missing_items = []
                
                for item in menu_items:
                    if f'href="/{item}"' not in response.text and f"href='{item}'" not in response.text:
                        missing_items.append(item)
                        
                if not missing_items:
                    self.log_result("Navigation Menu", "PASS", "Все пункты меню присутствуют")
                else:
                    self.log_result("Navigation Menu", "WARNING", f"Отсутствуют ссылки: {missing_items}")
            else:
                self.log_result("Navigation Menu", "FAIL", f"Ошибка загрузки: {response.status_code}")
        except Exception as e:
            self.log_result("Navigation Menu", "ERROR", str(e))
            
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("🚀 Запуск тестирования Customer Journey для Crystal Bay Travel")
        print("=" * 60)
        
        # Основные тесты доступности
        self.test_dashboard_accessibility()
        self.test_navigation_menu()
        self.test_responsive_layout()
        
        # Функциональные тесты
        self.test_leads_management_flow()
        self.test_tours_search_functionality()
        self.test_samo_testing_interface()
        self.test_settings_management()
        
        # Выводим итоговый отчет
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ")
        print("=" * 60)
        
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.test_results if r['status'] == 'WARNING'])
        errors = len([r for r in self.test_results if r['status'] == 'ERROR'])
        
        print(f"✅ Успешно: {passed}")
        print(f"⚠️  Предупреждения: {warnings}")
        print(f"❌ Ошибки: {failed}")
        print(f"🔥 Критические ошибки: {errors}")
        print(f"📈 Общий результат: {passed}/{len(self.test_results)} тестов пройдено")
        
        # Детали по ошибкам
        if failed > 0 or errors > 0:
            print("\n🔍 ДЕТАЛИ ОШИБОК:")
            for result in self.test_results:
                if result['status'] in ['FAIL', 'ERROR']:
                    print(f"- {result['test']}: {result['details']}")
                    
        return {
            'total': len(self.test_results),
            'passed': passed,
            'failed': failed,
            'warnings': warnings,
            'errors': errors,
            'results': self.test_results
        }

if __name__ == "__main__":
    tester = CustomerJourneyTests()
    results = tester.run_all_tests()
    
    # Сохраняем результаты в файл
    with open('test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в test_results.json")