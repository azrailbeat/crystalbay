"""
Диагностические утилиты для Crystal Bay Travel
Специально для решения проблем на продакшн сервере
"""
import os
import json
import requests
import logging
from datetime import datetime
from typing import Dict, Any
import socket
import ssl

logger = logging.getLogger(__name__)

class ProductionDiagnostics:
    """Диагностика для продакшн сервера"""
    
    @staticmethod
    def check_environment() -> Dict[str, Any]:
        """Проверка переменных окружения"""
        return {
            "timestamp": datetime.now().isoformat(),
            "environment": {
                "SUPABASE_URL": "✓" if os.environ.get("SUPABASE_URL") else "✗ Отсутствует",
                "SUPABASE_KEY": "✓" if os.environ.get("SUPABASE_KEY") else "✗ Отсутствует", 
                "OPENAI_API_KEY": "✓" if os.environ.get("OPENAI_API_KEY") else "✗ Отсутствует",
                "SAMO_OAUTH_TOKEN": "✓" if os.environ.get("SAMO_OAUTH_TOKEN") else "✗ Отсутствует",
                "DATABASE_URL": "✓" if os.environ.get("DATABASE_URL") else "✗ Отсутствует"
            }
        }
    
    @staticmethod
    def check_samo_connection() -> Dict[str, Any]:
        """Детальная проверка SAMO API подключения"""
        samo_url = "https://booking.crystalbay.com/export/default.php"
        oauth_token = os.environ.get("SAMO_OAUTH_TOKEN", "27bd59a7ac67422189789f0188167379")
        
        diagnostics = {
            "timestamp": datetime.now().isoformat(),
            "api_url": samo_url,
            "oauth_token_suffix": oauth_token[-4:] if oauth_token else "None",
            "tests": {}
        }
        
        # 1. DNS Resolution
        try:
            socket.gethostbyname("booking.crystalbay.com")
            diagnostics["tests"]["dns_resolution"] = {"status": "✓", "message": "DNS работает"}
        except Exception as e:
            diagnostics["tests"]["dns_resolution"] = {"status": "✗", "error": str(e)}
        
        # 2. SSL Certificate
        try:
            context = ssl.create_default_context()
            with socket.create_connection(("booking.crystalbay.com", 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname="booking.crystalbay.com") as ssock:
                    cert = ssock.getpeercert()
                    diagnostics["tests"]["ssl_certificate"] = {
                        "status": "✓", 
                        "subject": dict(x[0] for x in cert['subject']),
                        "issuer": dict(x[0] for x in cert['issuer']),
                        "expires": cert['notAfter']
                    }
        except Exception as e:
            diagnostics["tests"]["ssl_certificate"] = {"status": "✗", "error": str(e)}
        
        # 3. HTTP Connection
        try:
            response = requests.get("https://booking.crystalbay.com", timeout=15)
            diagnostics["tests"]["http_connection"] = {
                "status": "✓",
                "status_code": response.status_code,
                "headers": dict(response.headers)
            }
        except Exception as e:
            diagnostics["tests"]["http_connection"] = {"status": "✗", "error": str(e)}
        
        # 4. API Endpoint Test
        try:
            params = {
                'samo_action': 'api',
                'version': '1.0',
                'type': 'json',
                'action': 'SearchTour_CURRENCIES',
                'oauth_token': oauth_token
            }
            
            headers = {
                'User-Agent': 'Crystal Bay Travel Production/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post(samo_url, data=params, headers=headers, timeout=15)
            
            diagnostics["tests"]["api_endpoint"] = {
                "status": "Tested",
                "status_code": response.status_code,
                "response_length": len(response.text),
                "response_preview": response.text[:200],
                "headers": dict(response.headers)
            }
            
            if response.status_code == 403:
                diagnostics["tests"]["api_endpoint"]["message"] = "403 Forbidden - проверьте IP whitelist и OAuth токен"
            elif response.status_code == 200:
                try:
                    json_response = response.json()
                    diagnostics["tests"]["api_endpoint"]["json_valid"] = True
                    diagnostics["tests"]["api_endpoint"]["api_response"] = json_response
                except:
                    diagnostics["tests"]["api_endpoint"]["json_valid"] = False
                    
        except Exception as e:
            diagnostics["tests"]["api_endpoint"] = {"status": "✗", "error": str(e)}
        
        return diagnostics
    
    @staticmethod
    def get_server_info() -> Dict[str, Any]:
        """Информация о сервере"""
        try:
            # Получить внешний IP
            external_ip = "Unknown"
            try:
                response = requests.get("https://httpbin.org/ip", timeout=10)
                external_ip = response.json().get("origin", "Unknown")
            except:
                try:
                    response = requests.get("https://icanhazip.com", timeout=10)
                    external_ip = response.text.strip()
                except:
                    pass
            
            return {
                "timestamp": datetime.now().isoformat(),
                "external_ip": external_ip,
                "user_agent": "Crystal Bay Travel Production/1.0",
                "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
                "environment_vars_count": len([k for k in os.environ.keys() if not k.startswith('_')])
            }
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    @staticmethod 
    def generate_curl_command() -> str:
        """Генерация curl команды для тестирования"""
        oauth_token = os.environ.get("SAMO_OAUTH_TOKEN", "27bd59a7ac67422189789f0188167379")
        
        curl_command = f"""curl -X POST 'https://booking.crystalbay.com/export/default.php' \\
  -H 'User-Agent: Crystal Bay Travel Production/1.0' \\
  -H 'Accept: application/json' \\
  -H 'Content-Type: application/x-www-form-urlencoded' \\
  -d 'samo_action=api&version=1.0&type=json&action=SearchTour_CURRENCIES&oauth_token={oauth_token}' \\
  -v --connect-timeout 15 --max-time 30"""
        
        return curl_command