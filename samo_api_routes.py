"""
API маршруты для работы с Crystal Bay SAMO API
Предоставляет веб-интерфейс для всех функций SAMO API
"""
import logging
from flask import request, jsonify, render_template
from datetime import datetime, timedelta
from crystal_bay_samo_api import get_crystal_bay_api

logger = logging.getLogger(__name__)

def register_samo_api_routes(app):
    """Регистрация маршрутов SAMO API"""
    
    # === ГЛАВНАЯ СТРАНИЦА SAMO API ===
    
    @app.route('/samo-api')
    def samo_api_dashboard():
        """Главная страница управления SAMO API"""
        return render_template('samo_api_dashboard.html')
    
    # === ТЕСТИРОВАНИЕ ===
    
    @app.route('/api/samo/test', methods=['GET'])
    def test_samo_connection():
        """Тестирование подключения к SAMO API"""
        try:
            api = get_crystal_bay_api()
            result = api.test_connection()
            return jsonify(result)
        except Exception as e:
            logger.error(f"Ошибка тестирования SAMO API: {e}")
            return jsonify({
                'success': False,
                'message': f'Ошибка: {str(e)}'
            }), 500
    
    # === СПРАВОЧНИКИ ===
    
    @app.route('/api/samo/townfroms', methods=['GET'])
    def get_townfroms():
        """Получить города отправления"""
        try:
            api = get_crystal_bay_api()
            result = api.get_townfroms()
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/states', methods=['GET'])
    def get_samo_states():
        """Получить страны"""
        try:
            api = get_crystal_bay_api()
            result = api.get_states()
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/currencies', methods=['GET'])
    def get_samo_currencies():
        """Получить валюты"""
        try:
            api = get_crystal_bay_api()
            result = api.get_currencies()
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/hotels', methods=['GET'])
    def get_samo_hotels():
        """Получить отели"""
        try:
            api = get_crystal_bay_api()
            state_key = request.args.get('state_key')
            result = api.get_hotels(state_key)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/tours', methods=['GET'])
    def get_samo_tours():
        """Получить туры"""
        try:
            api = get_crystal_bay_api()
            result = api.get_tours()
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # === ПОИСК ТУРОВ ===
    
    @app.route('/api/samo/search/prices', methods=['POST'])
    def search_tour_prices():
        """Поиск цен на туры"""
        try:
            api = get_crystal_bay_api()
            params = request.json or {}
            result = api.search_tour_prices(params)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/search/tours', methods=['POST'])
    def search_tours():
        """Детальный поиск туров"""
        try:
            api = get_crystal_bay_api()
            params = request.json or {}
            result = api.search_tours_detailed(params)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # === БРОНИРОВАНИЯ ===
    
    @app.route('/api/samo/bookings', methods=['GET'])
    def get_samo_bookings():
        """Получить список бронирований"""
        try:
            api = get_crystal_bay_api()
            date_from = request.args.get('date_from')
            date_to = request.args.get('date_to')
            result = api.get_bookings(date_from, date_to)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/bookings/<booking_id>', methods=['GET'])
    def get_samo_booking_details(booking_id):
        """Получить детали бронирования"""
        try:
            api = get_crystal_bay_api()
            result = api.get_booking_details(booking_id)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/bookings', methods=['POST'])
    def create_samo_booking():
        """Создать новое бронирование"""
        try:
            api = get_crystal_bay_api()
            booking_data = request.json or {}
            result = api.create_booking(booking_data)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/bookings/<booking_id>', methods=['PUT'])
    def update_samo_booking(booking_id):
        """Обновить бронирование"""
        try:
            api = get_crystal_bay_api()
            booking_data = request.json or {}
            result = api.update_booking(booking_id, booking_data)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/bookings/<booking_id>/cancel', methods=['POST'])
    def cancel_samo_booking(booking_id):
        """Отменить бронирование"""
        try:
            api = get_crystal_bay_api()
            data = request.json or {}
            reason = data.get('reason', '')
            result = api.cancel_booking(booking_id, reason)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # === КЛИЕНТЫ ===
    
    @app.route('/api/samo/persons', methods=['POST'])
    def create_person():
        """Создать клиента"""
        try:
            api = get_crystal_bay_api()
            person_data = request.json or {}
            result = api.create_person(person_data)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/persons/<person_id>', methods=['GET'])
    def get_samo_person(person_id):
        """Получить данные клиента"""
        try:
            api = get_crystal_bay_api()
            result = api.get_person(person_id)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/persons/<person_id>', methods=['PUT'])
    def update_person(person_id):
        """Обновить данные клиента"""
        try:
            api = get_crystal_bay_api()
            person_data = request.json or {}
            result = api.update_person(person_id, person_data)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # === ОТЧЕТЫ ===
    
    @app.route('/api/samo/reports/sales', methods=['GET'])
    def get_sales_report():
        """Отчет по продажам"""
        try:
            api = get_crystal_bay_api()
            date_from = request.args.get('date_from', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
            date_to = request.args.get('date_to', datetime.now().strftime('%Y-%m-%d'))
            result = api.get_sales_report(date_from, date_to)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/reports/financial', methods=['GET'])
    def get_financial_report():
        """Финансовый отчет"""
        try:
            api = get_crystal_bay_api()
            date_from = request.args.get('date_from', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
            date_to = request.args.get('date_to', datetime.now().strftime('%Y-%m-%d'))
            result = api.get_financial_report(date_from, date_to)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # === ДОПОЛНИТЕЛЬНЫЕ УСЛУГИ ===
    
    @app.route('/api/samo/services', methods=['GET'])
    def get_samo_services():
        """Получить дополнительные услуги"""
        try:
            api = get_crystal_bay_api()
            result = api.get_services()
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/services/book', methods=['POST'])
    def book_service():
        """Забронировать дополнительную услугу"""
        try:
            api = get_crystal_bay_api()
            service_data = request.json or {}
            result = api.book_service(service_data)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # === ПЛАТЕЖИ ===
    
    @app.route('/api/samo/payments/methods', methods=['GET'])
    def get_payment_methods():
        """Получить способы оплаты"""
        try:
            api = get_crystal_bay_api()
            result = api.get_payment_methods()
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/payments', methods=['POST'])
    def create_payment():
        """Создать платеж"""
        try:
            api = get_crystal_bay_api()
            payment_data = request.json or {}
            result = api.create_payment(payment_data)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/payments/<payment_id>/status', methods=['GET'])
    def get_payment_status(payment_id):
        """Получить статус платежа"""
        try:
            api = get_crystal_bay_api()
            result = api.get_payment_status(payment_id)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # === РАСШИРЕННОЕ ТЕСТИРОВАНИЕ И ДИАГНОСТИКА ===
    
    @app.route('/api/samo/get-ip', methods=['GET'])
    def get_server_ip():
        """Get current server IP address"""
        try:
            import requests
            response = requests.get('https://ifconfig.me', timeout=10)
            ip = response.text.strip()
            return jsonify({
                'success': True,
                'ip': ip
            })
        except Exception as e:
            logger.error(f"IP detection error: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'ip': 'Неизвестно'
            })

    @app.route('/api/samo/execute-curl', methods=['POST'])
    def execute_curl():
        """Execute curl command for SAMO API testing"""
        try:
            data = request.get_json()
            method = data.get('method', 'SearchTour_CURRENCIES')
            params = data.get('params', '')
            
            import subprocess
            import json as json_module
            
            # Build curl command
            base_data = f"samo_action=api&version=1.0&type=json&action={method}&oauth_token=27bd59a7ac67422189789f0188167379"
            if params:
                base_data += f"&{params}"
            
            curl_command = [
                'curl', '-X', 'POST',
                'https://booking-kz.crystalbay.com/export/default.php',
                '-H', 'Content-Type: application/x-www-form-urlencoded',
                '-H', 'User-Agent: Crystal Bay Travel Integration/1.0',
                '-d', base_data,
                '--max-time', '30'
            ]
            
            # Execute curl
            result = subprocess.run(curl_command, capture_output=True, text=True, timeout=35)
            
            # Parse response
            try:
                response_data = json_module.loads(result.stdout)
            except:
                response_data = result.stdout
            
            return jsonify({
                'success': result.returncode == 0,
                'command': ' '.join(curl_command),
                'result': response_data,
                'stderr': result.stderr,
                'returncode': result.returncode
            })
            
        except Exception as e:
            logger.error(f"Curl execution error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            })

    @app.route('/api/samo/server-curl-test', methods=['GET'])
    def server_curl_test():
        """Execute server-side curl test"""
        try:
            import subprocess
            
            curl_command = [
                'curl', '-w', '%{http_code}', '-o', '/tmp/samo_response.txt',
                '-X', 'POST',
                'https://booking-kz.crystalbay.com/export/default.php',
                '-H', 'Content-Type: application/x-www-form-urlencoded',
                '-H', 'User-Agent: Crystal Bay Travel Integration/1.0',
                '-d', 'samo_action=api&version=1.0&type=json&action=SearchTour_CURRENCIES&oauth_token=27bd59a7ac67422189789f0188167379',
                '--max-time', '30'
            ]
            
            result = subprocess.run(curl_command, capture_output=True, text=True, timeout=35)
            http_code = result.stdout.strip()
            
            # Read response
            try:
                with open('/tmp/samo_response.txt', 'r') as f:
                    response_content = f.read()
            except:
                response_content = 'Не удалось прочитать ответ'
            
            return jsonify({
                'success': http_code == '200',
                'command': ' '.join(curl_command),
                'http_code': http_code,
                'response': response_content,
                'stderr': result.stderr
            })
            
        except Exception as e:
            logger.error(f"Server curl test error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            })

    @app.route('/api/samo/network-diagnostics', methods=['GET'])
    def network_diagnostics():
        """Run network diagnostics for SAMO API"""
        try:
            import subprocess
            
            # Ping test
            ping_result = subprocess.run(['ping', '-c', '4', 'booking-kz.crystalbay.com'], 
                                       capture_output=True, text=True, timeout=15)
            
            # Traceroute (limited hops for speed)
            trace_result = subprocess.run(['traceroute', '-m', '10', 'booking-kz.crystalbay.com'], 
                                        capture_output=True, text=True, timeout=30)
            
            return jsonify({
                'success': True,
                'ping_success': ping_result.returncode == 0,
                'ping_result': ping_result.stdout,
                'traceroute': trace_result.stdout
            })
            
        except Exception as e:
            logger.error(f"Network diagnostics error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            })

    @app.route('/api/samo/dns-check', methods=['GET'])
    def dns_check():
        """Check DNS resolution for SAMO API domain"""
        try:
            import socket
            
            ip_address = socket.gethostbyname('booking-kz.crystalbay.com')
            
            return jsonify({
                'success': True,
                'domain': 'booking-kz.crystalbay.com',
                'ip_address': ip_address
            })
            
        except Exception as e:
            logger.error(f"DNS check error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            })

    @app.route('/api/samo/ssl-check', methods=['GET'])
    def ssl_check():
        """Check SSL certificate for SAMO API"""
        try:
            import ssl
            import socket
            from datetime import datetime
            
            context = ssl.create_default_context()
            with socket.create_connection(('booking-kz.crystalbay.com', 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname='booking-kz.crystalbay.com') as ssock:
                    cert = ssock.getpeercert()
                    
            expires = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            valid = expires > datetime.now()
            
            return jsonify({
                'success': True,
                'valid': valid,
                'expires': cert['notAfter'],
                'issuer': dict(x[0] for x in cert['issuer']),
                'subject': dict(x[0] for x in cert['subject'])
            })
            
        except Exception as e:
            logger.error(f"SSL check error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            })

    @app.route('/api/samo/whitelist-test', methods=['GET'])
    def whitelist_test():
        """Test if server IP is whitelisted by SAMO"""
        try:
            import requests
            
            # Get server IP
            ip_response = requests.get('https://ifconfig.me', timeout=10)
            server_ip = ip_response.text.strip()
            
            # Test SAMO API
            api = get_crystal_bay_api()
            result = api.get_currencies()
            
            whitelisted = 'error' not in result and '403' not in str(result)
            
            return jsonify({
                'success': True,
                'whitelisted': whitelisted,
                'server_ip': server_ip,
                'error_message': result.get('error', '') if not whitelisted else None
            })
            
        except Exception as e:
            logger.error(f"Whitelist test error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            })

    @app.route('/api/samo/ping', methods=['GET'])
    def samo_ping():
        """Simple ping endpoint for latency testing"""
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'pong': True
        })

    @app.route('/api/samo/logs', methods=['GET'])
    def get_samo_logs():
        """Get SAMO API logs"""
        try:
            # In production, this would read from actual log files
            # For now, return recent activity
            logs = [
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - SAMO API инициализирован",
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Последний тест подключения: ожидание",
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - IP whitelist статус: проверяется",
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - OAuth токен: настроен"
            ]
            
            return jsonify({
                'success': True,
                'logs': '\n'.join(logs)
            })
            
        except Exception as e:
            logger.error(f"Logs error: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'logs': f"Ошибка загрузки логов: {str(e)}"
            })

    @app.route('/api/samo/meals', methods=['GET'])
    def get_samo_meals():
        """Получить типы питания"""
        try:
            api = get_crystal_bay_api()
            result = api.get_meals()
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/samo/stars', methods=['GET'])
    def get_samo_stars():
        """Получить звездность отелей"""
        try:
            api = get_crystal_bay_api()
            result = api.get_stars()
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/samo/search-tours', methods=['POST'])
    def search_tours_with_params():
        """Поиск туров с параметрами"""
        try:
            api = get_crystal_bay_api()
            params = request.json or {}
            result = api.search_tours(params)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    logger.info("SAMO API routes registered successfully")