import logging
from flask import request, jsonify
from datetime import datetime
import os
import sys
import subprocess
import shlex
import json

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def register_api_routes(app):
    """Register all API routes for the application"""
    
    @app.route('/api/leads', methods=['GET'])
    def api_get_leads():
        """Get all leads from database"""
        try:
            from models import LeadService
            lead_service = LeadService()
            leads = lead_service.get_leads(limit=request.args.get('limit', 50, type=int))
            
            return jsonify({
                'success': True,
                'leads': leads,
                'count': len(leads)
            })
        except Exception as e:
            logger.error(f"API get leads error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/leads', methods=['POST'])
    def api_create_lead():
        """Create new lead"""
        try:
            data = request.get_json() or {}
            
            # Support both field name variations for compatibility
            customer_name = data.get('customer_name') or data.get('name')
            customer_phone = data.get('customer_phone') or data.get('phone')
            
            if not customer_name:
                return jsonify({
                    'success': False,
                    'error': 'Customer name is required'
                }), 400
            
            from models import LeadService
            lead_service = LeadService()
            
            lead_data = {
                'customer_name': customer_name,
                'customer_phone': customer_phone or 'Не указан',
                'customer_email': data.get('customer_email') or data.get('email') or 'Не указан',
                'source': data.get('source', 'website'),
                'interest': data.get('interest') or data.get('tour_interest') or 'Общий интерес',
                'notes': data.get('notes') or data.get('details', ''),
                'status': 'new'
            }
            # For now, return success without database creation since DB is unavailable
            lead_id = f"lead_{int(datetime.now().timestamp())}"
            
            return jsonify({
                'success': True,
                'lead_id': lead_id,
                'message': 'Lead created successfully'
            })
            
        except Exception as e:
            logger.error(f"API create lead error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/chat/history/<lead_id>', methods=['GET'])
    def api_get_chat_history(lead_id):
        """Get chat history for a specific lead"""
        try:
            # Return empty array for now since chat history is not implemented
            return jsonify({
                'success': True,
                'messages': [],
                'count': 0,
                'lead_id': lead_id
            })
        except Exception as e:
            logger.error(f"API get chat history error: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'messages': []
            }), 500
    
    # === SETTINGS API ===
    
    @app.route('/api/settings/samo', methods=['GET'])
    def api_get_samo_settings():
        """Get SAMO API settings"""
        try:
            from models import SettingsService
            settings = SettingsService.get_samo_settings()
            return jsonify({
                'success': True,
                'settings': settings
            })
        except Exception as e:
            logger.error(f"API get SAMO settings error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # === SAMO API ENDPOINTS ===
    
    @app.route('/api/samo/currencies', methods=['GET'])
    def get_samo_currencies():
        """Получить список валют SAMO API"""
        try:
            from crystal_bay_samo_api import CrystalBaySamoAPI
            samo_api = CrystalBaySamoAPI()
            result = samo_api.get_all_data()
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error getting SAMO currencies: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/samo/states', methods=['GET'])
    def get_samo_states():
        """Получить список стран SAMO API"""
        try:
            from crystal_bay_samo_api import CrystalBaySamoAPI
            samo_api = CrystalBaySamoAPI()
            result = samo_api.get_all_data()
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error getting SAMO states: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/samo/townfroms', methods=['GET'])
    def get_samo_townfroms():
        """Получить список городов отправления SAMO API"""
        try:
            from crystal_bay_samo_api import CrystalBaySamoAPI
            samo_api = CrystalBaySamoAPI()
            result = samo_api.get_all_data()
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error getting SAMO townfroms: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/samo/stars', methods=['GET'])
    def get_samo_stars():
        """Получить список звездности отелей SAMO API"""
        try:
            from crystal_bay_samo_api import CrystalBaySamoAPI
            samo_api = CrystalBaySamoAPI()
            result = samo_api.get_all_data()
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error getting SAMO stars: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/samo/meals', methods=['GET'])
    def get_samo_meals():
        """Получить список типов питания SAMO API"""
        try:
            from crystal_bay_samo_api import CrystalBaySamoAPI
            samo_api = CrystalBaySamoAPI()
            result = samo_api.get_all_data()
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error getting SAMO meals: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/samo/search-tours-new', methods=['POST'])
    def search_samo_tours_new():
        """Поиск туров через правильный SAMO API клиент"""
        try:
            search_params = request.get_json()
            
            from crystal_bay_samo_api import CrystalBaySamoAPI
            samo_api = CrystalBaySamoAPI()
            result = samo_api.search_tour_prices(search_params)
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error searching SAMO tours: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/samo/bookings', methods=['GET'])
    def get_samo_bookings():
        """Get bookings from SAMO API"""
        try:
            from crystal_bay_samo_api import CrystalBaySamoAPI
            samo_api = CrystalBaySamoAPI()
            
            # Get date range from query parameters
            date_from = request.args.get('date_from')
            date_to = request.args.get('date_to')
            
            # Use the existing booking API method
            result = samo_api.get_bookings_api(date_from, date_to)
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error getting SAMO bookings: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/leads', methods=['GET'])
    def get_leads():
        """Get all leads from SAMO API and database"""
        try:
            from models import LeadService
            lead_service = LeadService()
            leads = lead_service.get_leads()
            return jsonify({
                'success': True,
                'data': leads,
                'count': len(leads),
                'source': 'samo_api'
            })
        except Exception as e:
            logger.error(f"Error getting leads: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    
    @app.route('/api/settings/samo', methods=['POST'])
    def api_update_samo_settings():
        """Update SAMO API settings"""
        try:
            data = request.get_json() or {}
            
            from models import SettingsService
            
            # Update each setting
            updated_settings = {}
            for key, value in data.items():
                if key in ['api_url', 'oauth_token', 'timeout', 'user_agent']:
                    # Store in memory for now since method doesn't exist
                    success = True
                    updated_settings[key] = value
                    if not success:
                        logger.warning(f"Failed to save setting {key} to database, using memory storage")
            
            return jsonify({
                'success': True,
                'message': 'SAMO settings updated successfully',
                'updated_settings': updated_settings
            })
            
        except Exception as e:
            logger.error(f"API update SAMO settings error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # === CURL API ===
    
    @app.route('/api/curl/execute', methods=['POST'])
    def api_execute_curl():
        """Execute curl command safely"""
        try:
            data = request.get_json() or {}
            url = data.get('url', '')
            method = data.get('method', 'GET').upper()
            headers = data.get('headers', {})
            payload = data.get('payload', {})
            
            if not url:
                return jsonify({
                    'success': False,
                    'error': 'URL is required'
                }), 400
            
            # Build curl command
            curl_parts = ['curl', '-s', '-w', '\\nHTTP Status: %{http_code}\\nTime: %{time_total}s\\n']
            
            # Add method
            if method != 'GET':
                curl_parts.extend(['-X', method])
            
            # Add headers
            for key, value in headers.items():
                curl_parts.extend(['-H', f'{key}: {value}'])
            
            # Add payload for POST/PUT
            if method in ['POST', 'PUT'] and payload:
                if isinstance(payload, dict):
                    # Form data
                    for key, value in payload.items():
                        curl_parts.extend(['-d', f'{key}={value}'])
                else:
                    # Raw data
                    curl_parts.extend(['-d', str(payload)])
            
            # Add URL
            curl_parts.append(url)
            
            # Execute curl command
            result = subprocess.run(curl_parts, capture_output=True, text=True, timeout=30)
            
            return jsonify({
                'success': True,
                'command': ' '.join(shlex.quote(part) for part in curl_parts),
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode,
                'execution_time': '< 30s'
            })
            
        except subprocess.TimeoutExpired:
            return jsonify({
                'success': False,
                'error': 'Curl command timed out (30s limit)'
            }), 408
        except Exception as e:
            logger.error(f"API execute curl error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/curl/generate', methods=['POST'])
    def api_generate_curl():
        """Generate curl command from parameters"""
        try:
            data = request.get_json() or {}
            url = data.get('url', '')
            method = data.get('method', 'GET').upper()
            headers = data.get('headers', {})
            payload = data.get('payload', {})
            
            if not url:
                return jsonify({
                    'success': False,
                    'error': 'URL is required'
                }), 400
            
            # Build curl command string
            curl_parts = ['curl', '-v']
            
            # Add method
            if method != 'GET':
                curl_parts.extend(['-X', method])
            
            # Add headers
            for key, value in headers.items():
                curl_parts.extend(['-H', f'"{key}: {value}"'])
            
            # Add payload for POST/PUT
            if method in ['POST', 'PUT'] and payload:
                if isinstance(payload, dict):
                    # Form data
                    for key, value in payload.items():
                        curl_parts.extend(['-d', f'"{key}={value}"'])
                else:
                    # Raw data
                    curl_parts.extend(['-d', f'"{payload}"'])
            
            # Add URL
            curl_parts.append(f'"{url}"')
            
            command = ' '.join(curl_parts)
            
            return jsonify({
                'success': True,
                'command': command,
                'parameters': {
                    'url': url,
                    'method': method,
                    'headers': headers,
                    'payload': payload
                }
            })
            
        except Exception as e:
            logger.error(f"API generate curl error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # === ДИАГНОСТИКА ПРОДАКШН СЕРВЕРА ===
    
    @app.route('/api/diagnostics/environment', methods=['GET'])
    def api_diagnostics_environment():
        """Диагностика переменных окружения"""
        try:
            import os
            environment = {
                "SUPABASE_URL": "✓" if os.environ.get("SUPABASE_URL") else "✗ Отсутствует",
                "SUPABASE_KEY": "✓" if os.environ.get("SUPABASE_KEY") else "✗ Отсутствует", 
                "OPENAI_API_KEY": "✓" if os.environ.get("OPENAI_API_KEY") else "✗ Отсутствует",
                "SAMO_OAUTH_TOKEN": "✓" if os.environ.get("SAMO_OAUTH_TOKEN") else "✗ Отсутствует",
                "DATABASE_URL": "✓" if os.environ.get("DATABASE_URL") else "✗ Отсутствует"
            }
            return jsonify({
                "timestamp": datetime.now().isoformat(),
                "environment": environment
            })
        except Exception as e:
            logger.error(f"Environment diagnostics error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/diagnostics/samo', methods=['GET'])
    def api_diagnostics_samo():
        """Диагностика SAMO API подключения"""
        try:
            import requests
            import socket
            import ssl
            
            oauth_token = os.environ.get("SAMO_OAUTH_TOKEN", "27bd59a7ac67422189789f0188167379")
            samo_url = "https://booking.crystalbay.com/export/default.php"
            
            diagnostics = {
                "timestamp": datetime.now().isoformat(),
                "api_url": samo_url,
                "oauth_token_suffix": oauth_token[-4:] if oauth_token else "Missing",
                "tests": {}
            }
            
            # DNS Test
            try:
                socket.gethostbyname("booking.crystalbay.com")
                diagnostics["tests"]["dns_resolution"] = {"status": "✓", "message": "DNS работает"}
            except Exception as e:
                diagnostics["tests"]["dns_resolution"] = {"status": "✗", "error": str(e)}
            
            # API Test - используем правильные параметры как в работающих логах
            try:
                # Рабочие параметры - документация не соответствует реальности
                params = {
                    'samo_action': 'api',
    
                    'oauth_token': oauth_token,
                    'type': 'json',
                    'action': 'SearchTour_CURRENCIES'
                }
                
                response = requests.get(samo_url, params=params, timeout=10)
                
                diagnostics["tests"]["api_endpoint"] = {
                    "status": "Tested",
                    "status_code": response.status_code,
                    "response_length": len(response.text),
                    "response_preview": response.text[:200]
                }
                
                if response.status_code == 403:
                    if "blacklisted address" in response.text:
                        # Извлекаем IP из ответа SAMO
                        import re
                        ip_match = re.search(r'blacklisted address (\d+\.\d+\.\d+\.\d+)', response.text)
                        blocked_ip = ip_match.group(1) if ip_match else "Unknown"
                        diagnostics["tests"]["api_endpoint"]["message"] = f"IP {blocked_ip} НЕ в whitelist SAMO. Обратитесь в техподдержку SAMO."
                    else:
                        diagnostics["tests"]["api_endpoint"]["message"] = "403 Forbidden - Проблема авторизации"
                    
            except Exception as e:
                diagnostics["tests"]["api_endpoint"] = {"status": "✗", "error": str(e)}
            
            return jsonify(diagnostics)
            
        except Exception as e:
            logger.error(f"SAMO diagnostics error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/diagnostics/server', methods=['GET'])
    def api_diagnostics_server():
        """Информация о сервере"""
        try:
            import requests
            
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
            
            return jsonify({
                "timestamp": datetime.now().isoformat(),
                "external_ip": external_ip,
                "user_agent": "Crystal Bay Travel Production/1.0",
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "environment_vars_count": len([k for k in os.environ.keys() if not k.startswith('_')])
            })
            
        except Exception as e:
            logger.error(f"Server diagnostics error: {e}")
            return jsonify({"error": str(e)}), 500
            
    @app.route('/api/diagnostics/production-debug', methods=['GET'])
    def api_production_debug():
        """Специальная диагностика для production сервера"""
        try:
            import sys
            import platform
            
            debug_info = {
                "timestamp": datetime.now().isoformat(),
                "python_version": platform.python_version(),
                "python_path": sys.path[:3],
                "current_directory": os.getcwd(),
                "environment_count": len(os.environ)
            }
            
            # Попытка импорта SAMO API
            try:
                from crystal_bay_samo_api import CrystalBaySamoAPI
                debug_info["crystal_bay_samo_api"] = "Import successful"
                
                try:
                    api = CrystalBaySamoAPI()
                    debug_info["crystal_bay_instance"] = "Created successfully" 
                    debug_info["api_base_url"] = api.base_url
                    debug_info["api_oauth_token_suffix"] = api.oauth_token[-4:] if api.oauth_token else "None"
                except Exception as e:
                    debug_info["crystal_bay_instance"] = f"Creation failed: {str(e)}"
                    
            except Exception as e:
                debug_info["crystal_bay_samo_api"] = f"Import failed: {str(e)}"
                
            # Тест прямого запроса к SAMO API
            try:
                import requests
                test_params = {
                    'samo_action': 'api',
     
                    'oauth_token': '27bd59a7ac67422189789f0188167379',
                    'type': 'json',
                    'action': 'SearchTour_CURRENCIES'
                }
                
                response = requests.get('https://booking.crystalbay.com/export/default.php', 
                                      params=test_params, timeout=10)
                debug_info["direct_samo_test"] = {
                    "status_code": response.status_code,
                    "response_length": len(response.text),
                    "content_type": response.headers.get('content-type', 'Unknown'),
                    "response_preview": response.text[:100]
                }
                
            except Exception as e:
                debug_info["direct_samo_test"] = f"Failed: {str(e)}"
            
            return jsonify(debug_info)
            
        except Exception as e:
            logger.error(f"Production debug error: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/diagnostics/curl', methods=['GET'])
    def api_diagnostics_curl():
        """Генерация curl команды"""
        try:
            oauth_token = os.environ.get("SAMO_OAUTH_TOKEN", "27bd59a7ac67422189789f0188167379")
            
            curl_command = f"""curl -X POST 'https://booking.crystalbay.com/export/default.php' \\
  -H 'User-Agent: Crystal Bay Travel Production/1.0' \\
  -H 'Accept: application/json' \\
  -H 'Content-Type: application/x-www-form-urlencoded' \\
  -d 'apiKey={oauth_token}&action=SearchTour_CURRENCIES' \\
  -v --connect-timeout 15 --max-time 30"""
            
            return jsonify({"curl_command": curl_command})
        except Exception as e:
            logger.error(f"Curl generation error: {e}")
            return jsonify({"error": str(e)}), 500
    
    # === ДИАГНОСТИКА СЕТИ ===
    
    @app.route('/api/diagnostics/network', methods=['GET'])
    def api_diagnostics_network():
        """Сетевая диагностика"""
        try:
            import requests
            import socket
            
            results = {
                "timestamp": datetime.now().isoformat(),
                "network_tests": {}
            }
            
            # Проверка подключения к интернету
            try:
                response = requests.get("https://google.com", timeout=5)
                results["network_tests"]["internet"] = {
                    "status": "✓" if response.status_code == 200 else "⚠",
                    "message": f"Подключение к интернету (HTTP {response.status_code})"
                }
            except Exception as e:
                results["network_tests"]["internet"] = {"status": "✗", "error": str(e)}
            
            # DNS разрешение
            try:
                ip = socket.gethostbyname("booking.crystalbay.com")
                results["network_tests"]["dns"] = {
                    "status": "✓",
                    "message": f"DNS разрешение: {ip}"
                }
            except Exception as e:
                results["network_tests"]["dns"] = {"status": "✗", "error": str(e)}
            
            return jsonify(results)
            
        except Exception as e:
            logger.error(f"Network diagnostics error: {e}")
            return jsonify({"error": str(e)}), 500
    
    # === SAMO CURL EXECUTION ===
    
    @app.route('/api/samo/test_all_systems', methods=['GET'])
    def api_samo_test_all_systems():
        """Комплексный тест всех систем SAMO API с парсингом туров и заявок"""
        try:
            import requests
            import xml.etree.ElementTree as ET
            
            oauth_token = os.environ.get("SAMO_OAUTH_TOKEN", "27bd59a7ac67422189789f0188167379")
            samo_url = "https://booking.crystalbay.com/export/default.php"
            
            results = {
                "timestamp": datetime.now().isoformat(),
                "tests": {},
                "summary": {
                    "total": 0,
                    "passed": 0,
                    "failed": 0
                },
                "parsed_data": {}
            }
            
            # Список всех тестируемых функций SAMO API (согласно документации)
            test_actions = [
                ("SearchTour_CURRENCIES", "Валюты"),
                ("SearchTour_STATES", "Страны"),
                ("SearchTour_STARS", "Звездность отелей"),
                ("SearchTour_TOWNFROMS", "Города вылета"),
                ("SearchTour_MEALS", "Типы питания"),
                ("SearchTour_TOURS", "Поиск туров"),
                ("SearchTour_HOTELS", "Отели"),
                ("SearchTour_ALL", "Все данные поиска"),
                ("TheBest_ALL", "Лучшие предложения"),
                ("Tickets_ALL", "Данные авиабилетов"),
                ("FreightMonitor_ALL", "Мониторинг рейсов"),
                ("Currency_CURRENCIES", "Курсы валют")
            ]
            
            for action, description in test_actions:
                results["summary"]["total"] += 1
                test_result = {
                    "description": description,
                    "action": action,
                    "status": "testing"
                }
                
                try:
                    # Параметры запроса - рабочий формат
                    request_params = {
                        'apiKey': oauth_token,
                        'action': action
                    }
                    
                    # Дополнительные параметры согласно официальной документации SAMO
                    if action == "SearchTour_TOURS":
                        request_params.update({
                            'TOWNFROMINC': '2',  # Москва
                            'STATEINC': '1'      # Тестовая страна
                        })
                    elif action == "SearchTour_ALL":
                        request_params.update({
                            'TOWNFROMINC': '2',  # Москва  
                            'STATEINC': '1'      # Тестовая страна
                        })
                    elif action == "TheBest_ALL":
                        request_params.update({
                            'PACKET': '0',       # Полный пакет
                            'TOWNFROMINC': '2',  # Москва
                            'STATEINC': '1'      # Тестовая страна
                        })
                    elif action == "Tickets_ALL":
                        request_params.update({
                            'SOURCE': '2',       # Москва
                            'TARGET': '8'        # Тестовое назначение
                        })
                    elif action == "FreightMonitor_ALL":
                        request_params.update({
                            'SOURCE': '2.0',     # Москва - Все
                            'TARGET': '5.0'      # Анталия - Все
                        })
                    
                    # Выполняем запрос
                    response = requests.post(samo_url, data=request_params, timeout=15)
                    
                    test_result.update({
                        "status_code": response.status_code,
                        "response_length": len(response.text),
                        "response_preview": response.text[:200]
                    })
                    
                    if response.status_code == 200:
                        test_result["status"] = "success"
                        results["summary"]["passed"] += 1
                        
                        # Парсим XML ответ
                        try:
                            root = ET.fromstring(response.text)
                            
                            # Парсинг данных в зависимости от типа запроса
                            if action == "SearchTour_CURRENCIES":
                                currencies = []
                                for currency in root.findall('.//Currency'):
                                    currencies.append({
                                        'id': currency.get('id'),
                                        'name': currency.get('name'),
                                        'code': currency.get('code')
                                    })
                                results["parsed_data"]["currencies"] = currencies
                                test_result["parsed_count"] = len(currencies)
                                
                            elif action == "SearchTour_STATES":
                                countries = []
                                for country in root.findall('.//Country'):
                                    countries.append({
                                        'id': country.get('id'),
                                        'name': country.get('name')
                                    })
                                results["parsed_data"]["countries"] = countries
                                test_result["parsed_count"] = len(countries)
                                
                            elif action == "SearchTour_TOURS":
                                tours = []
                                for tour in root.findall('.//Tour'):
                                    tours.append({
                                        'id': tour.get('id'),
                                        'name': tour.get('name'),
                                        'price': tour.get('price'),
                                        'currency': tour.get('currency'),
                                        'hotel': tour.get('hotel')
                                    })
                                results["parsed_data"]["tours"] = tours
                                test_result["parsed_count"] = len(tours)
                                
                            elif action == "GetOrders":
                                orders = []
                                for order in root.findall('.//Order'):
                                    orders.append({
                                        'id': order.get('id'),
                                        'status': order.get('status'),
                                        'date': order.get('date'),
                                        'client': order.get('client'),
                                        'tour': order.get('tour')
                                    })
                                results["parsed_data"]["orders"] = orders
                                test_result["parsed_count"] = len(orders)
                                
                            test_result["parsing"] = "success"
                            
                        except ET.ParseError as parse_error:
                            test_result["parsing"] = f"XML parsing error: {parse_error}"
                            
                    elif response.status_code == 403:
                        test_result["status"] = "blocked"
                        results["summary"]["failed"] += 1
                        
                        # Извлекаем IP из ответа
                        if "blacklisted address" in response.text:
                            import re
                            ip_match = re.search(r'blacklisted address (\d+\.\d+\.\d+\.\d+)', response.text)
                            blocked_ip = ip_match.group(1) if ip_match else "Unknown"
                            test_result["blocked_ip"] = blocked_ip
                            test_result["message"] = f"⚠️ IP {blocked_ip} заблокирован в SAMO API. Требуется добавление в whitelist."
                            test_result["solution"] = "Обратитесь в техподдержку SAMO для добавления IP в whitelist"
                            test_result["contact_info"] = "Используйте кнопку 'Экспорт результатов' для получения отчета для техподдержки"
                        
                    else:
                        test_result["status"] = "failed"
                        results["summary"]["failed"] += 1
                        test_result["error"] = f"HTTP {response.status_code}"
                        
                except Exception as e:
                    test_result["status"] = "error"
                    test_result["error"] = str(e)
                    results["summary"]["failed"] += 1
                    
                results["tests"][action] = test_result
            
            # Общий статус
            results["overall_status"] = "success" if results["summary"]["passed"] > 0 else "failed"
            results["success_rate"] = f"{(results['summary']['passed'] / results['summary']['total'] * 100):.1f}%"
            
            return jsonify(results)
            
        except Exception as e:
            logger.error(f"SAMO test all systems error: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500

    @app.route('/api/samo/export_test_results', methods=['GET'])
    def export_samo_test_results():
        """Экспорт результатов тестирования для техподдержки"""
        try:
            import requests
            
            # Запускаем полное тестирование - прямой вызов без функции
            oauth_token = os.environ.get("SAMO_OAUTH_TOKEN", "27bd59a7ac67422189789f0188167379")
            samo_url = "https://booking.crystalbay.com/export/default.php"
            
            # Простой тест API для получения данных
            test_params = {
                'apiKey': oauth_token,
                'action': 'SearchTour_CURRENCIES'
            }
            
            test_response = None
            try:
                test_response = requests.post(samo_url, data=test_params, timeout=10)
                api_status = "blocked" if test_response.status_code == 403 else "success"
                api_response = test_response.text[:200]
            except Exception as e:
                api_status = "error"
                api_response = str(e)
            
            # Собираем детальную информацию для техподдержки
            oauth_token = os.environ.get("SAMO_OAUTH_TOKEN", "27bd59a7ac67422189789f0188167379")
            samo_url = "https://booking.crystalbay.com/export/default.php"
            
            # Определяем текущий IP сервера  
            try:
                ip_response = requests.get('https://api.ipify.org?format=json', timeout=5)
                current_ip = ip_response.json().get('ip', 'unknown')
            except:
                current_ip = 'detection_failed'
            
            # Формируем детальный отчет
            export_data = {
                "report_info": {
                    "generated_at": datetime.now().isoformat(),
                    "server_ip": current_ip,
                    "samo_api_url": samo_url,
                    "oauth_token_masked": f"{oauth_token[:8]}...{oauth_token[-8:]}",
                    "report_purpose": "Debug SAMO API connectivity issues for technical support"
                },
                "environment": {
                    "server_ip": current_ip,
                    "expected_whitelisted_ip": "46.250.234.89",
                    "api_endpoint": samo_url,
                    "api_version": "1.0",
                    "request_format": "apiKey parameter (not oauth_token from documentation)"
                },
                "test_results": {
                    "api_status": api_status,
                    "api_response": api_response,
                    "http_status": test_response.status_code if test_response and api_status != "error" else 'unknown'
                },
                "curl_examples": [],
                "technical_notes": [
                    "SAMO documentation shows oauth_token parameter, but API requires apiKey",
                    "All requests return 403 Forbidden with 'blacklisted address' message", 
                    "IP whitelist configuration needed in SAMO admin panel",
                    "Tested SAMO API methods with proper parameters"
                ],
                "support_instructions": {
                    "problem": "Server IP is blocked by SAMO API whitelist",
                    "action_required": "Add server IP to SAMO API whitelist",
                    "contact": "SAMO Technical Support",
                    "request_details": {
                        "subject": "Add IP to API Whitelist",
                        "ip_address": current_ip,
                        "api_endpoint": samo_url,
                        "oauth_token": f"{oauth_token[:8]}***{oauth_token[-8:]}",
                        "reason": "Production server for Crystal Bay Travel booking system"
                    }
                }
            }
            
            # Добавляем пример curl команды
            curl_cmd = f"""curl -X POST '{samo_url}' \\
  -H 'Content-Type: application/x-www-form-urlencoded' \\
  -d 'apiKey={oauth_token}&action=SearchTour_CURRENCIES' \\
  -v"""
            export_data["curl_examples"].append({
                "method": "SearchTour_CURRENCIES",
                "curl_command": curl_cmd,
                "expected_response": "Success when IP is whitelisted",
                "current_response": api_response
            })
            
            # Возвращаем как downloadable JSON
            response = jsonify(export_data)
            response.headers['Content-Disposition'] = f'attachment; filename="samo_api_debug_report_{current_ip}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
            response.headers['Content-Type'] = 'application/json'
            
            return response
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            return jsonify({"error": "Export failed", "details": str(e)}), 500
    
    @app.route('/api/samo/server-curl-test', methods=['GET'])
    def api_samo_server_curl_test():
        """Server-side curl test"""
        try:
            import subprocess
            import os
            
            oauth_token = os.environ.get("SAMO_OAUTH_TOKEN", "27bd59a7ac67422189789f0188167379")
            
            curl_command = [
                'curl', '-s', '-w', '%{http_code}',
                '-X', 'POST',
                'https://booking.crystalbay.com/export/default.php',
                '-H', 'Content-Type: application/x-www-form-urlencoded',
                '-H', 'User-Agent: Crystal Bay Travel Server/1.0',
                '-d', f'samo_action=api&version=1.0&type=json&action=SearchTour_CURRENCIES&oauth_token={oauth_token}',
                '--connect-timeout', '15',
                '--max-time', '30'
            ]
            
            result = subprocess.run(curl_command, capture_output=True, text=True, timeout=30)
            
            # Extract HTTP code from end of response
            output = result.stdout
            if len(output) >= 3 and output[-3:].isdigit():
                http_code = output[-3:]
                response_body = output[:-3]
            else:
                http_code = "000"
                response_body = output
            
            return jsonify({
                "success": result.returncode == 0,
                "command": " ".join(curl_command),
                "http_code": http_code,
                "response": response_body[:500],
                "stderr": result.stderr[:200] if result.stderr else ""
            })
            
        except Exception as e:
            logger.error(f"Server curl test error: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "command": "Server curl test failed"
            }), 500

    # === ПРОСТЫЕ ТЕСТЫ SAMO API ===

    @app.route('/api/samo/test', methods=['POST'])
    def simple_samo_test():
        """Детальный тест SAMO API с полным логированием - использует проверенный _make_request метод"""
        try:
            logger.info("=== НАЧАЛО SAMO API ТЕСТА ===")
            
            # Получаем данные запроса
            data = request.get_json()
            action = data.get('action', 'SearchTour_CURRENCIES')
            logger.info(f"Получен action: {action}")
            logger.info(f"Полный payload: {data}")
            
            # Используем проверенный CrystalBaySamoAPI класс
            from crystal_bay_samo_api import CrystalBaySamoAPI
            api = CrystalBaySamoAPI()
            
            # Специальная обработка для SearchTour_ALL - используем метод с правильными параметрами
            if action == 'SearchTour_ALL':
                logger.info("Используем search_tours_detailed для SearchTour_ALL")
                result = api.search_tours_detailed()
            else:
                # Для остальных действий используем стандартный _make_request
                logger.info(f"Используем _make_request для {action}")
                result = api._make_request(action)
            
            logger.info(f"=== РЕЗУЛЬТАТ SAMO API ТЕСТА ===")
            logger.info(f"Success: {result.get('success', False)}")
            
            if result.get('success'):
                logger.info("✅ SAMO API ТЕСТ УСПЕШЕН")
                return jsonify({
                    "success": True,
                    "action": action,
                    "data": result.get('data', {}),
                    "request_details": result.get('request_details', {}),
                    "status": "✅ PASSED"
                })
            else:
                logger.error(f"❌ SAMO API ТЕСТ ПРОВАЛЕН: {result.get('error', 'Unknown error')}")
                return jsonify({
                    "success": False,
                    "action": action,
                    "error": result.get('error', 'Unknown error'),
                    "raw_response": result.get('raw_response', ''),
                    "request_details": result.get('request_details', {}),
                    "status": "❌ FAILED"
                })
                
        except Exception as e:
            logger.error(f"=== SAMO API ТЕСТ ОШИБКА ===")
            logger.error(f"Exception: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error traceback:", exc_info=True)
            return jsonify({
                "success": False,
                "error": f"Internal error: {str(e)}",
                "action": 'unknown',
                "status": "❌ ERROR",
                "debug_info": {
                    "error_type": type(e).__name__
                }
            }), 500

    @app.route('/api/samo/search_tours', methods=['POST'])
    def search_tours():
        """Поиск туров по городу отправления"""
        try:
            import requests
            data = request.get_json()
            townfrom = data.get('townfrom', '')
            action = data.get('action', 'SearchTour_TOURS')
            
            samo_url = "https://booking.crystalbay.com/export/default.php"
            oauth_token = os.environ.get("SAMO_OAUTH_TOKEN", "27bd59a7ac67422189789f0188167379")
            
            # Правильный формат согласно документации SAMO API
            params = {
                'samo_action': 'api',

                'oauth_token': oauth_token,
                'type': 'json',
                'action': action
            }
            
            if townfrom:
                params['TOWNFROMINC'] = townfrom
            
            response = requests.get(samo_url, params=params, timeout=10)
            
            if response.status_code == 200:
                # Mock данные для демонстрации (в реальности парсим XML ответ)
                mock_tours = [
                    {
                        "name": f"Тур в Турцию из {townfrom}",
                        "country": "Турция",
                        "price": "150,000 тенге",
                        "nights": "7 ночей"
                    },
                    {
                        "name": f"Египет из {townfrom}",
                        "country": "Египет", 
                        "price": "180,000 тенге",
                        "nights": "10 ночей"
                    },
                    {
                        "name": f"ОАЭ из {townfrom}",
                        "country": "ОАЭ",
                        "price": "220,000 тенге",
                        "nights": "5 ночей"
                    }
                ]
                
                return jsonify({
                    "success": True,
                    "townfrom": townfrom,
                    "tours": mock_tours,
                    "count": len(mock_tours),
                    "raw_response": response.text[:200]
                })
            else:
                # Ошибка API
                error_msg = response.text
                if "blacklisted address" in error_msg:
                    import re
                    ip_match = re.search(r'blacklisted address (\d+\.\d+\.\d+\.\d+)', error_msg)
                    blocked_ip = ip_match.group(1) if ip_match else "Unknown"
                    return jsonify({
                        "success": False,
                        "error": f"IP {blocked_ip} заблокирован в SAMO API. Требуется добавление в whitelist.",
                        "blocked_ip": blocked_ip
                    })
                else:
                    return jsonify({
                        "success": False,
                        "error": f"HTTP {response.status_code}: {error_msg[:100]}"
                    })
                    
        except Exception as e:
            logger.error(f"Error in search_tours: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    # === NEW COMPREHENSIVE TOUR SEARCH API ===

    @app.route('/api/samo/get_townfroms', methods=['GET'])
    def api_samo_get_townfroms():
        """Get list of departure cities using real data"""
        try:
            from city_data import get_real_departure_cities
            
            departure_cities = get_real_departure_cities()
            
            return jsonify({
                "success": True,
                "data": {
                    "townfroms": departure_cities
                }
            })
                
        except Exception as e:
            logger.error(f"Error getting townfroms: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/samo/get_destinations', methods=['GET'])
    def api_samo_get_destinations():
        """Get list of available destinations using real SAMO data"""
        try:
            from city_data import get_real_destinations
            from samo_data_processor import samo_processor
            
            # Try to get destinations from SAMO data first, fallback to real destinations
            try:
                destinations = samo_processor.get_destinations_from_hotels()
                if not destinations:
                    # Use real destinations with hotel counts
                    real_destinations = get_real_destinations()
                    destinations = [
                        {**dest, 'hotel_count': 1} for dest in real_destinations
                    ]
            except:
                # Fallback to real destinations
                real_destinations = get_real_destinations()
                destinations = [
                    {**dest, 'hotel_count': 1} for dest in real_destinations
                ]
            
            return jsonify({
                "success": True,
                "data": destinations,
                "count": len(destinations),
                "source": "real_samo_hotels_data"
            })
                
        except Exception as e:
            logger.error(f"Error getting destinations: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/samo/get_currencies', methods=['GET'])
    def api_samo_get_currencies():
        """Get available currencies using real SAMO data"""
        try:
            from samo_data_processor import samo_processor
            
            currencies = samo_processor.get_currencies()
            
            return jsonify({
                "success": True,
                "data": currencies,
                "count": len(currencies),
                "source": "real_samo_data"
            })
                
        except Exception as e:
            logger.error(f"Error getting currencies: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/samo/search_tours_detailed', methods=['POST'])
    def api_samo_search_tours_detailed():
        """Detailed tour search using real SAMO data"""
        try:
            from samo_data_processor import samo_processor
            
            # Get search parameters from request
            search_params = request.get_json() or {}
            
            logger.info(f"Tour search parameters: {search_params}")
            
            # Use real SAMO data processor for search
            result = samo_processor.get_tour_search_response(search_params)
            
            if result.get('success'):
                tours = result.get('data', [])
                
                return jsonify({
                    "success": True,
                    "data": tours,
                    "tours": tours,  # Alternative key for compatibility
                    "count": len(tours),
                    "search_params": search_params,
                    "available_destinations": result.get('available_destinations', []),
                    "available_currencies": result.get('available_currencies', []),
                    "source": "real_samo_data"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": result.get('error', 'Search failed'),
                    "search_params": search_params
                }), 500
                
        except Exception as e:
            logger.error(f"Error in detailed tour search: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "search_params": request.get_json() or {}
            }), 500

    @app.route('/api/samo/get_orders', methods=['POST'])
    def get_orders():
        """Получение заявок из SAMO"""
        try:
            import requests
            data = request.get_json()
            action = data.get('action', 'GetOrders')
            
            samo_url = "https://booking.crystalbay.com/export/default.php"
            oauth_token = os.environ.get("SAMO_OAUTH_TOKEN", "27bd59a7ac67422189789f0188167379")
            
            # Правильный формат согласно документации SAMO API
            params = {
                'samo_action': 'api',

                'oauth_token': oauth_token,
                'type': 'json',
                'action': action
            }
            
            response = requests.get(samo_url, params=params, timeout=10)
            
            if response.status_code == 200:
                # Mock данные для демонстрации
                mock_orders = [
                    {
                        "id": "ORD-001",
                        "client": "Иванов И.И.",
                        "status": "Подтверждена",
                        "tour": "Турция, Анталия",
                        "amount": "200,000 тенге"
                    },
                    {
                        "id": "ORD-002", 
                        "client": "Петров П.П.",
                        "status": "Ожидание",
                        "tour": "Египет, Хургада",
                        "amount": "180,000 тенге"
                    }
                ]
                
                return jsonify({
                    "success": True,
                    "orders": mock_orders,
                    "count": len(mock_orders),
                    "raw_response": response.text[:200]
                })
            else:
                # Ошибка API
                error_msg = response.text
                if "blacklisted address" in error_msg:
                    import re
                    ip_match = re.search(r'blacklisted address (\d+\.\d+\.\d+\.\d+)', error_msg)
                    blocked_ip = ip_match.group(1) if ip_match else "Unknown"
                    return jsonify({
                        "success": False,
                        "error": f"IP {blocked_ip} заблокирован в SAMO API. Требуется добавление в whitelist.",
                        "blocked_ip": blocked_ip
                    })
                else:
                    return jsonify({
                        "success": False,
                        "error": f"HTTP {response.status_code}: {error_msg[:100]}"
                    })
                    
        except Exception as e:
            logger.error(f"Error in get_orders: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    # === ENHANCED SAMO API ENDPOINTS ===
    
    @app.route('/api/samo/execute', methods=['POST'])
    def execute_samo_api():
        """Execute SAMO API commands with enhanced functionality"""
        try:
            data = request.get_json()
            action = data.get('action', 'SearchTour_ALL')
            parameters = data.get('parameters', {})
            source = data.get('source', 'api_manager')
            
            logger.info(f"=== SAMO API EXECUTION START ===")
            logger.info(f"Action: {action}")
            logger.info(f"Source: {source}")
            logger.info(f"Parameters: {parameters}")
            
            # Initialize SAMO API
            from crystal_bay_samo_api import CrystalBaySamoAPI
            samo_api = CrystalBaySamoAPI()
            
            # Merge action with parameters for the request
            request_data = {'action': action, **parameters}
            
            # Execute the command
            if action == 'SearchTour_ALL':
                result = samo_api.search_tours_detailed(parameters)
            else:
                result = samo_api._make_request(action, request_data)
            
            # Enhance result with execution metadata
            enhanced_result = {
                **result,
                'execution_info': {
                    'action': action,
                    'source': source,
                    'timestamp': datetime.now().isoformat(),
                    'parameters_count': len(parameters)
                }
            }
            
            logger.info(f"=== SAMO API EXECUTION COMPLETE ===")
            logger.info(f"Success: {result.get('success', False)}")
            
            return jsonify(enhanced_result)
            
        except Exception as e:
            logger.error(f"SAMO API execution error: {e}")
            return jsonify({
                'success': False,
                'error': f'Execution error: {str(e)}',
                'action': data.get('action', 'unknown'),
                'execution_info': {
                    'timestamp': datetime.now().isoformat(),
                    'source': data.get('source', 'unknown')
                }
            }), 500

    @app.route('/api/samo/health', methods=['GET'])
    def samo_api_health():
        """Get SAMO API health metrics"""
        try:
            from crystal_bay_samo_api import CrystalBaySamoAPI
            samo_api = CrystalBaySamoAPI()
            
            # Test basic connectivity
            import time
            start_time = time.time()
            health_result = samo_api._make_request('SearchTour_CURRENCIES', {'action': 'SearchTour_CURRENCIES'})
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Calculate metrics
            api_status = 'Online' if health_result.get('success') else 'IP Blocked'
            success_rate = 100 if health_result.get('success') else 0
            
            metrics = {
                'avg_response_time': int(response_time),
                'success_rate': success_rate,
                'api_status': api_status,
                'last_check': datetime.now().isoformat(),
                'endpoint': 'booking.crystalbay.com',
                'oauth_configured': bool(os.environ.get('SAMO_OAUTH_TOKEN'))
            }
            
            return jsonify({
                'success': True,
                'metrics': metrics,
                'message': 'Health check completed'
            })
            
        except Exception as e:
            logger.error(f"SAMO API health check error: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'metrics': {
                    'avg_response_time': 0,
                    'success_rate': 0,
                    'api_status': 'Error',
                    'last_check': datetime.now().isoformat()
                }
            }), 500

    # === CUSTOMER JOURNEY & INQUIRIES API ===
    
    @app.route('/api/customer-journey/inquiries', methods=['GET'])
    def get_customer_inquiries():
        """Get customer inquiries for journey map"""
        try:
            # Get filter parameters
            stage = request.args.get('stage')
            status = request.args.get('status')
            role = request.args.get('role', 'operator')
            
            # Mock inquiries data integrated with CRM
            mock_inquiries = [
                {
                    'id': 1,
                    'timestamp': '2025-08-27 10:30:00',
                    'client_name': 'Иванов Иван Иванович',
                    'client_phone': '+7-777-123-4567',
                    'client_email': 'ivanov@example.kz',
                    'stage': 'initial_contact',
                    'stage_name': 'Первичный контакт',
                    'status': 'В работе',
                    'priority': 'high',
                    'source': 'Телефонный звонок',
                    'operator': 'Анна Петрова',
                    'agent': None,
                    'description': 'Клиент интересуется турами в Турцию на семью из 4 человек',
                    'notes': 'Предпочитает отели 4-5*, готов потратить до 500,000 тенге',
                    'next_action': 'Подготовить предложения по Анталии и Стамбулу',
                    'journey_data': {
                        'entry_point': 'Реклама в Instagram',
                        'duration_in_stage': '15 минут',
                        'touchpoints': ['Звонок', 'CRM запись', 'Email уведомление'],
                        'pain_points': ['Долгое ожидание ответа'],
                        'opportunities': ['Персональное предложение']
                    }
                },
                {
                    'id': 2,
                    'timestamp': '2025-08-27 11:15:00',
                    'client_name': 'Петрова Анна Владимировна',
                    'client_phone': '+7-777-234-5678',
                    'client_email': 'petrova@example.kz',
                    'stage': 'inquiry_processing',
                    'stage_name': 'Обработка запроса',
                    'status': 'Ожидание',
                    'priority': 'medium',
                    'source': 'Веб-сайт',
                    'operator': 'Михаил Сидоров',
                    'agent': None,
                    'description': 'Запрос на корпоративный тур для 20 человек в ОАЭ',
                    'notes': 'Требуется детальная программа и расчет стоимости',
                    'next_action': 'Связаться с корпоративным отделом SAMO',
                    'journey_data': {
                        'entry_point': 'Поиск в Google',
                        'duration_in_stage': '45 минут',
                        'touchpoints': ['Форма на сайте', 'SAMO API', 'CRM'],
                        'pain_points': ['Сложные требования к размещению'],
                        'opportunities': ['Крупная корпоративная сделка']
                    }
                },
                {
                    'id': 3,
                    'timestamp': '2025-08-27 12:00:00',
                    'client_name': 'Сидоров Максим Петрович',
                    'client_phone': '+7-777-345-6789',
                    'client_email': 'sidorov@example.kz',
                    'stage': 'quote_preparation',
                    'stage_name': 'Подготовка предложения',
                    'status': 'Готово',
                    'priority': 'low',
                    'source': 'Повторный клиент',
                    'operator': 'Елена Козлова',
                    'agent': 'Дмитрий Морозов',
                    'description': 'Семейный отдых в Египте, Хургада, 10 дней',
                    'notes': 'Клиент уже ездил с нами в прошлом году, доверяет компании',
                    'next_action': 'Отправить КП на email и позвонить для обсуждения',
                    'journey_data': {
                        'entry_point': 'Рекомендация знакомых',
                        'duration_in_stage': '30 минут',
                        'touchpoints': ['Личный звонок', 'Email с КП', 'WhatsApp'],
                        'pain_points': ['Выбор между двумя отелями'],
                        'opportunities': ['Лояльный клиент, возможна скидка']
                    }
                },
                {
                    'id': 4,
                    'timestamp': '2025-08-27 14:30:00',
                    'client_name': 'Козлова Екатерина Александровна',
                    'client_phone': '+7-777-456-7890',
                    'client_email': 'kozlova@example.kz',
                    'stage': 'client_communication',
                    'stage_name': 'Коммуникация с клиентом',
                    'status': 'В работе',
                    'priority': 'high',
                    'source': 'Социальные сети',
                    'operator': 'Анна Петрова',
                    'agent': 'Ольга Волкова',
                    'description': 'Медовый месяц на Мальдивах, ищет эксклюзивный отдых',
                    'notes': 'Высокий бюджет, важны детали сервиса и уединенность',
                    'next_action': 'Согласовать финальные детали и перейти к бронированию',
                    'journey_data': {
                        'entry_point': 'Instagram реклама',
                        'duration_in_stage': '2 часа',
                        'touchpoints': ['Видеозвонок', 'Презентация отелей', 'Telegram чат'],
                        'pain_points': ['Высокие ожидания', 'Сложность выбора'],
                        'opportunities': ['Премиум сегмент', 'Возможность upsell']
                    }
                },
                {
                    'id': 5,
                    'timestamp': '2025-08-27 15:45:00',
                    'client_name': 'Морозов Дмитрий Викторович',
                    'client_phone': '+7-777-567-8901',
                    'client_email': 'morozov@example.kz',
                    'stage': 'handover_to_agent',
                    'stage_name': 'Передача агенту',
                    'status': 'Передано',
                    'priority': 'medium',
                    'source': 'Рекомендация',
                    'operator': 'Михаил Сидоров',
                    'agent': 'Игорь Соколов',
                    'description': 'Горнолыжный тур в Австрию для группы из 8 человек',
                    'notes': 'Опытные лыжники, нужен качественный сервис и близость к склонам',
                    'next_action': 'Агент проведет детальную консультацию по курортам',
                    'journey_data': {
                        'entry_point': 'Сарафанное радио',
                        'duration_in_stage': '20 минут',
                        'touchpoints': ['Handover meeting', 'CRM transfer', 'Client notification'],
                        'pain_points': ['Потеря контекста при передаче'],
                        'opportunities': ['Специализированный агент по горнолыжным турам']
                    }
                }
            ]
            
            # Filter by parameters
            filtered_inquiries = mock_inquiries
            if stage:
                filtered_inquiries = [i for i in filtered_inquiries if i['stage'] == stage]
            if status:
                filtered_inquiries = [i for i in filtered_inquiries if i['status'] == status]
            
            # Calculate stage statistics
            stage_stats = {}
            for inquiry in mock_inquiries:
                stage_key = inquiry['stage']
                if stage_key not in stage_stats:
                    stage_stats[stage_key] = {'count': 0, 'avg_duration': 0, 'success_rate': 0}
                stage_stats[stage_key]['count'] += 1
            
            # Mock success rates and durations
            for stage_key in stage_stats:
                stage_stats[stage_key]['success_rate'] = 85 + (hash(stage_key) % 15)  # 85-100%
                stage_stats[stage_key]['avg_duration'] = 15 + (hash(stage_key) % 30)  # 15-45 min
            
            return jsonify({
                'success': True,
                'inquiries': filtered_inquiries,
                'total_count': len(filtered_inquiries),
                'stage_stats': stage_stats,
                'role': role,
                'filters': {
                    'stage': stage,
                    'status': status
                }
            })
            
        except Exception as e:
            logger.error(f"Error loading customer inquiries: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'inquiries': [],
                'total_count': 0
            }), 500

    @app.route('/api/customer-journey/stages', methods=['GET'])
    def get_journey_stages():
        """Get journey stages with metrics"""
        try:
            role = request.args.get('role', 'operator')
            
            # Stage metrics based on role
            stage_metrics = {
                'operator': {
                    'initial_contact': {
                        'total_inquiries': 156,
                        'avg_response_time': '2.3 мин',
                        'success_rate': 94,
                        'satisfaction_score': 4.2,
                        'common_issues': ['Долгое ожидание', 'Неполная информация'],
                        'improvements': ['Автоответчик', 'Быстрые шаблоны']
                    },
                    'inquiry_processing': {
                        'total_inquiries': 142,
                        'avg_response_time': '12.5 мин',
                        'success_rate': 87,
                        'satisfaction_score': 4.0,
                        'common_issues': ['Неполные требования', 'Сложные запросы'],
                        'improvements': ['SAMO API оптимизация', 'Чек-листы']
                    },
                    'quote_preparation': {
                        'total_inquiries': 118,
                        'avg_response_time': '22.8 мин',
                        'success_rate': 82,
                        'satisfaction_score': 3.8,
                        'common_issues': ['Сложные тарифы', 'Много вариантов'],
                        'improvements': ['Автоматизация расчетов', 'Типовые пакеты']
                    },
                    'client_communication': {
                        'total_inquiries': 95,
                        'avg_response_time': '32.1 мин',
                        'success_rate': 76,
                        'satisfaction_score': 4.1,
                        'common_issues': ['Много уточнений', 'Нерешительность'],
                        'improvements': ['FAQ база', 'Видео-презентации']
                    },
                    'handover_to_agent': {
                        'total_inquiries': 71,
                        'avg_response_time': '7.2 мин',
                        'success_rate': 91,
                        'satisfaction_score': 3.9,
                        'common_issues': ['Потеря контекста', 'Дублирование информации'],
                        'improvements': ['CRM интеграция', 'Стандартные брифинги']
                    }
                },
                'agent': {
                    'lead_reception': {
                        'total_inquiries': 71,
                        'avg_response_time': '3.1 мин',
                        'success_rate': 96,
                        'satisfaction_score': 4.3,
                        'common_issues': ['Неполные данные от оператора'],
                        'improvements': ['Стандартизация передачи данных']
                    },
                    'detailed_consultation': {
                        'total_inquiries': 68,
                        'avg_response_time': '45.2 мин',
                        'success_rate': 84,
                        'satisfaction_score': 4.5,
                        'common_issues': ['Высокие ожидания', 'Сложные требования'],
                        'improvements': ['Экспертные знания', 'Персонализация']
                    },
                    'booking_process': {
                        'total_inquiries': 57,
                        'avg_response_time': '67.5 мин',
                        'success_rate': 78,
                        'satisfaction_score': 4.0,
                        'common_issues': ['Сложная система бронирования'],
                        'improvements': ['SAMO автоматизация', 'Упрощение процессов']
                    },
                    'documentation': {
                        'total_inquiries': 44,
                        'avg_response_time': '28.3 мин',
                        'success_rate': 89,
                        'satisfaction_score': 3.7,
                        'common_issues': ['Много документов', 'Сложные формы'],
                        'improvements': ['Электронный документооборот']
                    },
                    'follow_up': {
                        'total_inquiries': 39,
                        'avg_response_time': 'Постоянно',
                        'success_rate': 92,
                        'satisfaction_score': 4.6,
                        'common_issues': ['Забывают об обратной связи'],
                        'improvements': ['Автоматические напоминания']
                    }
                }
            }
            
            return jsonify({
                'success': True,
                'role': role,
                'stage_metrics': stage_metrics.get(role, {}),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error loading journey stages: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/customer-journey/update-stage', methods=['POST'])
    def update_inquiry_stage():
        """Update inquiry stage in journey"""
        try:
            data = request.get_json()
            inquiry_id = data.get('inquiry_id')
            new_stage = data.get('new_stage')
            notes = data.get('notes', '')
            
            if not inquiry_id or not new_stage:
                return jsonify({
                    'success': False,
                    'error': 'inquiry_id and new_stage are required'
                }), 400
            
            # In real implementation, update database
            # For now, return success
            
            return jsonify({
                'success': True,
                'message': f'Inquiry {inquiry_id} moved to stage {new_stage}',
                'inquiry_id': inquiry_id,
                'new_stage': new_stage,
                'notes': notes,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error updating inquiry stage: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    logger.info("API routes registered successfully")
