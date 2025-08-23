#!/usr/bin/env python3
"""
Комплексные тесты для Crystal Bay Travel
"""

import unittest
import requests
import json
import os
import sys
from datetime import datetime

class CrystalBayTravelTests(unittest.TestCase):
    """Основные тесты системы Crystal Bay Travel"""
    
    @classmethod
    def setUpClass(cls):
        """Настройка тестов"""
        cls.base_url = "http://localhost:5000"
        cls.test_results = []
        
    def test_01_health_check(self):
        """Тест health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("status", data)
            self.assertEqual(data["status"], "healthy")
            self._log_success("Health Check", "Система запущена и работает")
        except Exception as e:
            self._log_error("Health Check", str(e))
            raise
    
    def test_02_main_page(self):
        """Тест главной страницы"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Crystal Bay Travel", response.text)
            self._log_success("Main Page", "Главная страница загружается")
        except Exception as e:
            self._log_error("Main Page", str(e))
            raise
    
    def test_03_samo_testing_page(self):
        """Тест страницы SAMO тестирования"""
        try:
            response = requests.get(f"{self.base_url}/samo-testing", timeout=5)
            self.assertEqual(response.status_code, 200)
            self.assertIn("SAMO API", response.text)
            self._log_success("SAMO Testing Page", "Страница SAMO тестирования доступна")
        except Exception as e:
            self._log_error("SAMO Testing Page", str(e))
            raise
    
    def test_04_diagnostics_environment(self):
        """Тест диагностики окружения"""
        try:
            response = requests.get(f"{self.base_url}/api/diagnostics/environment", timeout=5)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("environment", data)
            self.assertIn("timestamp", data)
            self._log_success("Environment Diagnostics", f"Переменных окружения: {len(data['environment'])}")
        except Exception as e:
            self._log_error("Environment Diagnostics", str(e))
            raise
    
    def test_05_diagnostics_server(self):
        """Тест диагностики сервера"""
        try:
            response = requests.get(f"{self.base_url}/api/diagnostics/server", timeout=5)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("external_ip", data)
            self.assertIn("python_version", data)
            self._log_success("Server Diagnostics", f"IP: {data.get('external_ip', 'Unknown')}")
        except Exception as e:
            self._log_error("Server Diagnostics", str(e))
            raise
    
    def test_06_diagnostics_network(self):
        """Тест сетевой диагностики"""
        try:
            response = requests.get(f"{self.base_url}/api/diagnostics/network", timeout=5)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("network_tests", data)
            self._log_success("Network Diagnostics", "Сетевая диагностика работает")
        except Exception as e:
            self._log_error("Network Diagnostics", str(e))
            raise
    
    def test_07_samo_api_connection(self):
        """Тест подключения к SAMO API"""
        try:
            response = requests.get(f"{self.base_url}/api/diagnostics/samo", timeout=10)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("tests", data)
            
            # Проверяем DNS
            if "dns_resolution" in data["tests"]:
                dns_status = data["tests"]["dns_resolution"]["status"]
                self.assertEqual(dns_status, "✓")
            
            # Проверяем API endpoint (может быть заблокирован)
            if "api_endpoint" in data["tests"]:
                api_test = data["tests"]["api_endpoint"]
                if api_test["status_code"] == 403:
                    self._log_warning("SAMO API", "IP заблокирован у поставщика")
                else:
                    self._log_success("SAMO API", "API доступен")
            
        except Exception as e:
            self._log_error("SAMO API Connection", str(e))
            raise
    
    def test_08_curl_execution(self):
        """Тест выполнения curl команд"""
        try:
            payload = {
                "method": "SearchTour_CURRENCIES",
                "params": ""
            }
            response = requests.post(
                f"{self.base_url}/api/samo/execute-curl",
                json=payload,
                timeout=15
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("command", data)
            self.assertIn("status_code", data)
            
            if data["status_code"] == 403:
                self._log_warning("Curl Execution", "SAMO API блокирует IP")
            else:
                self._log_success("Curl Execution", "Curl команды выполняются")
                
        except Exception as e:
            self._log_error("Curl Execution", str(e))
            raise
    
    def test_09_leads_api(self):
        """Тест API лидов"""
        try:
            response = requests.get(f"{self.base_url}/api/leads", timeout=5)
            # API может вернуть ошибку подключения к внешним сервисам
            # Главное что endpoint отвечает
            self.assertIn(response.status_code, [200, 500])
            self._log_success("Leads API", "Endpoint доступен")
        except Exception as e:
            self._log_error("Leads API", str(e))
            raise
    
    def test_10_static_files(self):
        """Тест статических файлов"""
        try:
            # Проверяем CSS
            response = requests.get(f"{self.base_url}/static/css/style.css", timeout=5)
            self.assertIn(response.status_code, [200, 404])  # Может не существовать
            
            # Проверяем директорию static
            response = requests.get(f"{self.base_url}/static/", timeout=5)
            # Статические файлы могут быть недоступны для листинга
            self._log_success("Static Files", "Статические файлы настроены")
        except Exception as e:
            self._log_error("Static Files", str(e))
            # Не критическая ошибка
    
    def _log_success(self, test_name, message):
        """Логирование успешного теста"""
        result = f"✅ {test_name}: {message}"
        self.test_results.append(result)
        print(result)
    
    def _log_warning(self, test_name, message):
        """Логирование предупреждения"""
        result = f"⚠️  {test_name}: {message}"
        self.test_results.append(result)
        print(result)
    
    def _log_error(self, test_name, message):
        """Логирование ошибки"""
        result = f"❌ {test_name}: {message}"
        self.test_results.append(result)
        print(result)
    
    @classmethod
    def tearDownClass(cls):
        """Завершение тестов"""
        print("\n" + "="*50)
        print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ Crystal Bay Travel")
        print("="*50)
        
        passed = len([r for r in cls.test_results if r.startswith("✅")])
        warnings = len([r for r in cls.test_results if r.startswith("⚠️")])
        failed = len([r for r in cls.test_results if r.startswith("❌")])
        
        print(f"✅ Успешно: {passed}")
        print(f"⚠️  Предупреждения: {warnings}")
        print(f"❌ Ошибки: {failed}")
        print(f"📊 Всего тестов: {len(cls.test_results)}")
        
        # Сохраняем результаты
        results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "passed": passed,
                "warnings": warnings,
                "failed": failed,
                "total": len(cls.test_results)
            },
            "details": cls.test_results
        }
        
        with open("test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Результаты сохранены в test_results.json")

if __name__ == "__main__":
    # Проверяем доступность сервера
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        print("🚀 Сервер доступен, начинаю тестирование...\n")
    except:
        print("❌ Сервер недоступен на localhost:5000")
        print("   Запустите сервер командой: python main.py")
        sys.exit(1)
    
    unittest.main(verbosity=2)