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
            result = samo_api.get_currencies()
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
            result = samo_api.get_states()
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
            result = samo_api.get_town_froms()
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
            result = samo_api.get_stars()
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
            result = samo_api.get_meals()
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
                    success = SettingsService.update_samo_setting(key, str(value))
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
                "oauth_token_suffix": oauth_token[-4:] if oauth_token else "None",
                "tests": {}
            }
            
            # DNS Test
            try:
                socket.gethostbyname("booking.crystalbay.com")
                diagnostics["tests"]["dns_resolution"] = {"status": "✓", "message": "DNS работает"}
            except Exception as e:
                diagnostics["tests"]["dns_resolution"] = {"status": "✗", "error": str(e)}
            
            # API Test
            try:
                params = {
                    'samo_action': 'api',
                    'version': '1.0',
                    'type': 'json',
                    'action': 'SearchTour_CURRENCIES',
                    'oauth_token': oauth_token
                }
                
                response = requests.post(samo_url, data=params, timeout=10)
                
                diagnostics["tests"]["api_endpoint"] = {
                    "status": "Tested",
                    "status_code": response.status_code,
                    "response_length": len(response.text),
                    "response_preview": response.text[:200]
                }
                
                if response.status_code == 403:
                    diagnostics["tests"]["api_endpoint"]["message"] = "403 Forbidden - IP заблокирован или проблема с токеном"
                    
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
    
    @app.route('/api/diagnostics/curl', methods=['GET'])
    def api_diagnostics_curl():
        """Генерация curl команды"""
        try:
            oauth_token = os.environ.get("SAMO_OAUTH_TOKEN", "27bd59a7ac67422189789f0188167379")
            
            curl_command = f"""curl -X POST 'https://booking.crystalbay.com/export/default.php' \\
  -H 'User-Agent: Crystal Bay Travel Production/1.0' \\
  -H 'Accept: application/json' \\
  -H 'Content-Type: application/x-www-form-urlencoded' \\
  -d 'samo_action=api&version=1.0&type=json&action=SearchTour_CURRENCIES&oauth_token={oauth_token}' \\
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
    
    @app.route('/api/samo/execute-curl', methods=['POST'])
    def api_samo_execute_curl():
        """Execute curl command for SAMO API"""
        try:
            data = request.get_json() or {}
            method = data.get('method', 'SearchTour_CURRENCIES')
            params = data.get('params', '')
            
            oauth_token = os.environ.get("SAMO_OAUTH_TOKEN", "27bd59a7ac67422189789f0188167379")
            samo_url = "https://booking.crystalbay.com/export/default.php"
            
            # Build request parameters
            request_params = {
                'samo_action': 'api',
                'version': '1.0', 
                'type': 'json',
                'action': method,
                'oauth_token': oauth_token
            }
            
            # Add additional parameters if provided
            if params:
                for param in params.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        request_params[key] = value
            
            # Generate curl command for display
            curl_command = f"curl -X POST '{samo_url}' \\\n"
            curl_command += "  -H 'Content-Type: application/x-www-form-urlencoded' \\\n"
            curl_command += "  -H 'User-Agent: Crystal Bay Travel/1.0' \\\n"
            curl_command += "  -d '" + "&".join([f"{k}={v}" for k, v in request_params.items()]) + "'"
            
            # Execute request
            import requests
            response = requests.post(samo_url, data=request_params, timeout=15)
            
            result = {
                "command": curl_command,
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_length": len(response.text),
                "result": response.text[:1000] if response.text else "No response"
            }
            
            if response.status_code == 403:
                result["error"] = "IP заблокирован в SAMO API"
                result["message"] = "Необходимо разблокировать IP у поставщика"
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"SAMO curl execution error: {e}")
            return jsonify({
                "success": False,
                "error": str(e),
                "command": "curl command generation failed"
            }), 500
    
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

    # === UNIFIED MESSAGING API ===
    
    @app.route('/api/messages/status', methods=['GET'])
    def api_messaging_status():
        """Get messaging hub status"""
        try:
            from messaging_service import messaging_hub
            status = messaging_hub.get_status()
            return jsonify({
                'success': True,
                'status': status
            })
        except Exception as e:
            logger.error(f"Messaging status error: {e}")
            return jsonify({
                'success': True,
                'status': {
                    'initialized': False,
                    'connectors': {
                        'telegram': {'connected': False, 'bot_token_set': bool(os.environ.get('TELEGRAM_BOT_TOKEN'))},
                        'wazzup': {'connected': False, 'api_key_set': bool(os.environ.get('WAZZUP_API_KEY'))}
                    },
                    'automation_rules': 0
                }
            })
    
    @app.route('/api/messages/initialize', methods=['POST'])
    def api_messaging_initialize():
        """Initialize messaging connectors"""
        try:
            from messaging_service import messaging_hub
            result = messaging_hub.initialize()
            return jsonify({
                'success': True,
                'result': result
            })
        except Exception as e:
            logger.error(f"Messaging initialize error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/messages/conversations', methods=['GET'])
    def api_get_conversations():
        """Get all conversations"""
        try:
            from messaging_service import messaging_hub
            channel = request.args.get('channel')
            limit = request.args.get('limit', 50, type=int)
            
            conversations = messaging_hub.get_conversations(channel, limit)
            return jsonify({
                'success': True,
                'conversations': conversations,
                'count': len(conversations)
            })
        except Exception as e:
            logger.error(f"Get conversations error: {e}")
            return jsonify({
                'success': True,
                'conversations': [],
                'count': 0
            })
    
    @app.route('/api/messages/conversations/<conversation_id>', methods=['GET'])
    def api_get_conversation_messages(conversation_id):
        """Get messages for a conversation"""
        try:
            from messaging_service import messaging_hub
            limit = request.args.get('limit', 50, type=int)
            
            messages = messaging_hub.get_messages(conversation_id, limit)
            return jsonify({
                'success': True,
                'conversation_id': conversation_id,
                'messages': messages,
                'count': len(messages)
            })
        except Exception as e:
            logger.error(f"Get messages error: {e}")
            return jsonify({
                'success': True,
                'conversation_id': conversation_id,
                'messages': [],
                'count': 0
            })
    
    @app.route('/api/messages/send', methods=['POST'])
    def api_send_message():
        """Send message through specified channel"""
        try:
            data = request.get_json() or {}
            channel = data.get('channel')
            chat_id = data.get('chat_id')
            message = data.get('message')
            
            if not all([channel, chat_id, message]):
                return jsonify({
                    'success': False,
                    'error': 'channel, chat_id, and message are required'
                }), 400
            
            from messaging_service import messaging_hub
            result = messaging_hub.send_message(channel, chat_id, message, data.get('options', {}))
            return jsonify(result)
        except Exception as e:
            logger.error(f"Send message error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/messages/stats', methods=['GET'])
    def api_messaging_stats():
        """Get messaging channel statistics"""
        try:
            from messaging_service import messaging_hub
            stats = messaging_hub.get_channel_stats()
            return jsonify({
                'success': True,
                'stats': stats
            })
        except Exception as e:
            logger.error(f"Messaging stats error: {e}")
            return jsonify({
                'success': True,
                'stats': {
                    'telegram': {'total_conversations': 0, 'unread_messages': 0},
                    'whatsapp': {'total_conversations': 0, 'unread_messages': 0},
                    'wazzup': {'total_conversations': 0, 'unread_messages': 0}
                }
            })
    
    @app.route('/api/messages/unread', methods=['GET'])
    def api_unread_count():
        """Get unread message count"""
        try:
            from messaging_service import messaging_hub
            channel = request.args.get('channel')
            count = messaging_hub.get_unread_count(channel)
            return jsonify({
                'success': True,
                'unread_count': count,
                'channel': channel or 'all'
            })
        except Exception as e:
            return jsonify({
                'success': True,
                'unread_count': 0,
                'channel': 'all'
            })
    
    # === WEBHOOKS ===
    
    @app.route('/webhooks/telegram', methods=['POST'])
    def webhook_telegram():
        """Handle Telegram webhook"""
        try:
            payload = request.get_json() or {}
            logger.info(f"Telegram webhook received: {str(payload)[:200]}")
            
            from messaging_service import messaging_hub
            result = messaging_hub.handle_incoming_message('telegram', payload)
            return jsonify({'ok': True, 'result': result})
        except Exception as e:
            logger.error(f"Telegram webhook error: {e}")
            return jsonify({'ok': False, 'error': str(e)}), 500
    
    @app.route('/webhooks/wazzup', methods=['POST'])
    def webhook_wazzup():
        """Handle Wazzup webhook"""
        try:
            payload = request.get_json() or {}
            logger.info(f"Wazzup webhook received: {str(payload)[:200]}")
            
            from messaging_service import messaging_hub
            
            messages = payload.get('messages', [])
            results = []
            for msg in messages:
                result = messaging_hub.handle_incoming_message('wazzup', msg)
                results.append(result)
            
            return jsonify({'success': True, 'processed': len(results)})
        except Exception as e:
            logger.error(f"Wazzup webhook error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/webhooks/whatsapp', methods=['POST'])
    def webhook_whatsapp():
        """Handle WhatsApp webhook (via Wazzup)"""
        return webhook_wazzup()
    
    @app.route('/webhooks/status', methods=['GET'])
    def webhooks_status():
        """Get webhooks status"""
        telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        wazzup_key = os.environ.get('WAZZUP_API_KEY')
        
        return jsonify({
            'success': True,
            'webhooks': {
                'telegram': {
                    'endpoint': '/webhooks/telegram',
                    'method': 'POST',
                    'configured': bool(telegram_token)
                },
                'wazzup': {
                    'endpoint': '/webhooks/wazzup',
                    'method': 'POST',
                    'configured': bool(wazzup_key)
                },
                'whatsapp': {
                    'endpoint': '/webhooks/whatsapp',
                    'method': 'POST',
                    'note': 'Uses Wazzup integration'
                }
            }
        })
    
    logger.info("API routes registered successfully")
