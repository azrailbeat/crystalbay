"""
Центральный менеджер настроек для Crystal Bay Travel System
Обеспечивает единое управление всеми настройками системы
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class SettingsManager:
    """Централизованный менеджер настроек системы"""
    
    def __init__(self):
        self.settings_file = "settings.json"
        self.backup_dir = "settings_backup"
        self._settings = {}
        self._load_settings()
    
    def _load_settings(self):
        """Загружает настройки из файла"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self._settings = json.load(f)
                logger.info("Настройки загружены успешно")
            else:
                self._settings = self._get_default_settings()
                self._save_settings()
                logger.info("Созданы настройки по умолчанию")
        except Exception as e:
            logger.error(f"Ошибка загрузки настроек: {e}")
            self._settings = self._get_default_settings()
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Возвращает настройки по умолчанию"""
        return {
            "system": {
                "name": "Crystal Bay Travel",
                "version": "1.0.0",
                "language": "ru",
                "timezone": "Asia/Almaty",
                "debug_mode": False,
                "auto_backup": True,
                "backup_interval": 24  # часы
            },
            "integrations": {
                "samo_api": {
                    "enabled": True,
                    "endpoint": "https://booking-kz.crystalbay.com/export/default.php",
                    "oauth_token": os.getenv("SAMO_OAUTH_TOKEN", ""),
                    "timeout": 30,
                    "max_retries": 3,
                    "default_currency": "USD",
                    "default_departure": "1"  # Алматы
                },
                "telegram_bot": {
                    "enabled": True,
                    "token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
                    "welcome_message": "Добро пожаловать в Crystal Bay Travel! 🌊",
                    "auto_respond": True,
                    "response_timeout": 30
                },
                "openai": {
                    "enabled": True,
                    "api_key": os.getenv("OPENAI_API_KEY", ""),
                    "model": "gpt-4o",
                    "temperature": 0.7,
                    "max_tokens": 1500,
                    "language": "ru"
                },
                "wazzup24": {
                    "enabled": True,
                    "api_key": os.getenv("WAZZUP_API_KEY", ""),
                    "api_secret": os.getenv("WAZZUP_API_SECRET", ""),
                    "base_url": "https://api.wazzup24.com/v3",
                    "client_api_key": os.getenv("WAZZUP_CLIENT_KEY", ""),
                    "webhook_url": "",
                    "auto_create_contacts": True,
                    "auto_create_deals": True
                },
                "bitrix24": {
                    "enabled": False,
                    "webhook_url": os.getenv("BITRIX_WEBHOOK_URL", ""),
                    "access_token": os.getenv("BITRIX_ACCESS_TOKEN", ""),
                    "domain": os.getenv("BITRIX_DOMAIN", ""),
                    "pipeline_id": "",
                    "auto_sync": True,
                    "lead_source": "Crystal Bay CRM"
                },
                "sendgrid": {
                    "enabled": False,
                    "api_key": os.getenv("SENDGRID_API_KEY", ""),
                    "from_email": os.getenv("SENDGRID_FROM_EMAIL", "noreply@crystalbay.travel"),
                    "templates": {
                        "booking_confirmation": "",
                        "booking_reminder": "",
                        "lead_notification": ""
                    },
                    "auto_notify": True
                },
                "supabase": {
                    "enabled": True,
                    "url": os.getenv("SUPABASE_URL", ""),
                    "key": os.getenv("SUPABASE_KEY", ""),
                    "auto_sync": True,
                    "sync_interval": 5  # минуты
                }
            },
            "business": {
                "company_name": "Crystal Bay Travel",
                "company_phone": "+7 (777) 123-45-67",
                "company_email": "info@crystalbay.travel",
                "company_address": "Алматы, Казахстан",
                "working_hours": "9:00 - 18:00",
                "timezone": "Asia/Almaty",
                "currency": "USD",
                "language": "ru",
                "auto_lead_assignment": True,
                "lead_response_time": 60,  # минуты
                "booking_confirmation_required": True
            },
            "notifications": {
                "email_notifications": True,
                "sms_notifications": False,
                "telegram_notifications": True,
                "new_lead_notification": True,
                "booking_confirmation_notification": True,
                "payment_notification": True,
                "system_alerts": True,
                "daily_reports": True,
                "weekly_reports": False
            },
            "logging": {
                "level": "INFO",
                "enable_file_logging": True,
                "log_file": "crystal_bay.log",
                "max_log_size": "10MB",
                "backup_count": 5,
                "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "last_updated": datetime.now().isoformat(),
            "created": datetime.now().isoformat()
        }
    
    def get_setting(self, path: str, default=None):
        """Получает значение настройки по пути (например: 'integrations.samo_api.enabled')"""
        try:
            keys = path.split('.')
            value = self._settings
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_setting(self, path: str, value: Any):
        """Устанавливает значение настройки по пути"""
        try:
            keys = path.split('.')
            settings = self._settings
            for key in keys[:-1]:
                if key not in settings:
                    settings[key] = {}
                settings = settings[key]
            settings[keys[-1]] = value
            self._settings["last_updated"] = datetime.now().isoformat()
            logger.info(f"Настройка {path} обновлена")
            return True
        except Exception as e:
            logger.error(f"Ошибка установки настройки {path}: {e}")
            return False
    
    def update_settings(self, updates: Dict[str, Any]):
        """Обновляет несколько настроек одновременно"""
        try:
            for path, value in updates.items():
                self.set_setting(path, value)
            self._save_settings()
            logger.info(f"Обновлено {len(updates)} настроек")
            return True
        except Exception as e:
            logger.error(f"Ошибка обновления настроек: {e}")
            return False
    
    def _save_settings(self):
        """Сохраняет настройки в файл с обработкой ошибок"""
        try:
            # Создаем резервную копию перед сохранением
            self._create_backup()
            
            # Добавляем метку времени последнего изменения
            self._settings['_metadata'] = {
                'last_updated': datetime.now().isoformat(),
                'version': self._settings.get('system', {}).get('version', '1.0.0')
            }
            
            # Атомарное сохранение через временный файл
            temp_file = self.settings_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
            
            # Заменяем основной файл после успешной записи
            os.replace(temp_file, self.settings_file)
            
            logger.info("Настройки сохранены успешно")
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения настроек: {e}")
            # Удаляем временный файл если он есть
            if os.path.exists(self.settings_file + '.tmp'):
                os.remove(self.settings_file + '.tmp')
            return False
    
    def _create_backup(self):
        """Создает резервную копию настроек"""
        try:
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir)
            
            if os.path.exists(self.settings_file):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = os.path.join(self.backup_dir, f"settings_{timestamp}.json")
                
                import shutil
                shutil.copy2(self.settings_file, backup_path)
                logger.info(f"Создана резервная копия: {backup_path}")
                
                # Удаляем старые резервные копии (оставляем последние 10)
                self._cleanup_old_backups()
                
        except Exception as e:
            logger.error(f"Ошибка создания резервной копии: {e}")
    
    def _cleanup_old_backups(self):
        """Удаляет старые резервные копии, оставляя только последние 10"""
        try:
            if not os.path.exists(self.backup_dir):
                return
                
            backup_files = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith("settings_") and filename.endswith(".json"):
                    filepath = os.path.join(self.backup_dir, filename)
                    backup_files.append((filepath, os.path.getctime(filepath)))
            
            # Сортируем по времени создания
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Удаляем файлы старше 10-го
            for filepath, _ in backup_files[10:]:
                os.remove(filepath)
                logger.info(f"Удалена старая резервная копия: {filepath}")
                
        except Exception as e:
            logger.error(f"Ошибка очистки резервных копий: {e}")
    
    def update_setting(self, path: str, value: Any) -> bool:
        """
        Обновляет конкретную настройку по пути
        path: строка вида 'integrations.samo_api.enabled'
        """
        try:
            keys = path.split('.')
            current = self._settings
            
            # Навигируем до родительского объекта
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # Устанавливаем значение
            old_value = current.get(keys[-1])
            current[keys[-1]] = value
            
            # Сохраняем изменения
            if self._save_settings():
                logger.info(f"Настройка {path} изменена: {old_value} -> {value}")
                return True
            else:
                # Откатываем изменение при ошибке сохранения
                current[keys[-1]] = old_value
                return False
                
        except Exception as e:
            logger.error(f"Ошибка обновления настройки {path}: {e}")
            return False
    
    def update_multiple_settings(self, updates: Dict[str, Any]) -> Dict[str, bool]:
        """
        Обновляет несколько настроек одновременно
        Возвращает результат для каждой настройки
        """
        results = {}
        rollback_needed = False
        original_settings = json.loads(json.dumps(self._settings))  # Deep copy
        
        try:
            # Применяем все изменения
            for path, value in updates.items():
                keys = path.split('.')
                current = self._settings
                
                # Навигируем до родительского объекта
                for key in keys[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                
                # Устанавливаем значение
                current[keys[-1]] = value
                results[path] = True
            
            # Сохраняем все изменения одновременно
            if self._save_settings():
                logger.info(f"Обновлено настроек: {len(updates)}")
                return results
            else:
                rollback_needed = True
                
        except Exception as e:
            logger.error(f"Ошибка массового обновления настроек: {e}")
            rollback_needed = True
        
        if rollback_needed:
            # Откатываем все изменения
            self._settings = original_settings
            return {path: False for path in updates.keys()}
        
        return results
    
    def validate_integration_config(self, integration: str) -> Dict[str, Any]:
        """
        Проверяет конфигурацию интеграции
        Возвращает статус и список ошибок
        """
        try:
            config = self.get_setting(f'integrations.{integration}')
            if not config:
                return {
                    'status': 'error',
                    'message': f'Конфигурация {integration} не найдена',
                    'errors': ['Configuration not found']
                }
            
            errors = []
            warnings = []
            
            # Проверяем обязательные поля для каждой интеграции
            if integration == 'samo_api':
                if not config.get('oauth_token'):
                    errors.append('OAuth токен не указан')
                if not config.get('endpoint'):
                    errors.append('Endpoint API не указан')
            
            elif integration == 'telegram_bot':
                if not config.get('token'):
                    errors.append('Токен бота не указан')
            
            elif integration == 'openai':
                if not config.get('api_key'):
                    errors.append('API ключ OpenAI не указан')
                if config.get('temperature', 0) > 1.0:
                    warnings.append('Температура больше 1.0 может давать непредсказуемые результаты')
            
            elif integration == 'wazzup24':
                if not config.get('api_key'):
                    errors.append('API ключ Wazzup24 не указан')
                if not config.get('api_secret'):
                    errors.append('API секрет Wazzup24 не указан')
            
            elif integration == 'bitrix24':
                if not config.get('webhook_url') and not config.get('access_token'):
                    errors.append('Не указан webhook URL или токен доступа')
            
            elif integration == 'sendgrid':
                if not config.get('api_key'):
                    errors.append('API ключ SendGrid не указан')
                if not config.get('from_email'):
                    errors.append('Email отправителя не указан')
            
            # Определяем общий статус
            if errors:
                status = 'error'
                message = f'Найдено ошибок: {len(errors)}'
            elif warnings:
                status = 'warning'
                message = f'Найдено предупреждений: {len(warnings)}'
            else:
                status = 'success'
                message = 'Конфигурация корректна'
            
            return {
                'status': status,
                'message': message,
                'errors': errors,
                'warnings': warnings,
                'enabled': config.get('enabled', False)
            }
            
        except Exception as e:
            logger.error(f"Ошибка валидации {integration}: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка валидации: {str(e)}',
                'errors': [str(e)]
            }
    
    def export_settings(self, export_path: Optional[str] = None) -> str:
        """Экспортирует настройки в JSON файл"""
        try:
            if not export_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_path = f"settings_export_{timestamp}.json"
            
            # Создаем копию настроек без секретных данных
            export_data = self._settings.copy()
            
            # Маскируем секретные данные
            secret_fields = [
                "integrations.samo_api.oauth_token",
                "integrations.telegram_bot.token",
                "integrations.openai.api_key",
                "integrations.supabase.key",
                "integrations.sendgrid.api_key",
                "integrations.wazzup.api_key",
                "integrations.wazzup.api_secret",
                "integrations.bitrix24.access_token"
            ]
            
            for field in secret_fields:
                value = self.get_setting(field)
                if value:
                    masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "*" * len(value)
                    self.set_setting_in_dict(export_data, field, masked_value)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Настройки экспортированы в {export_path}")
            return export_path
            
        except Exception as e:
            logger.error(f"Ошибка экспорта настроек: {e}")
            raise
    
    def set_setting_in_dict(self, data_dict: Dict, path: str, value: Any):
        """Устанавливает значение в словаре по пути"""
        keys = path.split('.')
        current = data_dict
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
    
    def backup_settings(self) -> str:
        """Создает резервную копию настроек"""
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"settings_backup_{timestamp}.json")
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Резервная копия создана: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Ошибка создания резервной копии: {e}")
            raise
    
    def restore_settings(self, backup_path: str):
        """Восстанавливает настройки из резервной копии"""
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                self._settings = json.load(f)
            
            self._save_settings()
            logger.info(f"Настройки восстановлены из {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка восстановления настроек: {e}")
            return False
    
    def get_integration_status(self) -> Dict[str, Dict[str, Any]]:
        """Возвращает статус всех интеграций"""
        integrations = self.get_setting("integrations", {})
        status = {}
        
        for name, config in integrations.items():
            if not isinstance(config, dict):
                continue
                
            enabled = config.get("enabled", False)
            
            # Проверяем наличие обязательных полей
            required_fields = self._get_required_fields(name)
            has_required = all(config.get(field) for field in required_fields)
            
            status[name] = {
                "enabled": enabled,
                "configured": has_required,
                "status": "active" if enabled and has_required else "inactive" if enabled else "disabled",
                "last_check": datetime.now().isoformat()
            }
        
        return status
    
    def _get_required_fields(self, integration_name: str) -> List[str]:
        """Возвращает список обязательных полей для интеграции"""
        required_map = {
            "samo_api": ["oauth_token", "endpoint"],
            "telegram_bot": ["token"],
            "openai": ["api_key"],
            "supabase": ["url", "key"],
            "sendgrid": ["api_key", "from_email"],
            "wazzup": ["api_key", "api_secret"],
            "bitrix24": ["webhook_url"]
        }
        return required_map.get(integration_name, [])
    
    def validate_settings(self) -> Dict[str, List[str]]:
        """Валидирует настройки и возвращает список ошибок"""
        errors = {}
        
        # Проверяем интеграции
        integrations = self.get_setting("integrations", {})
        for name, config in integrations.items():
            if not isinstance(config, dict):
                continue
                
            if config.get("enabled", False):
                required_fields = self._get_required_fields(name)
                missing_fields = [field for field in required_fields if not config.get(field)]
                
                if missing_fields:
                    errors[name] = [f"Отсутствуют обязательные поля: {', '.join(missing_fields)}"]
        
        # Проверяем системные настройки
        system_errors = []
        if not self.get_setting("business.company_name"):
            system_errors.append("Не указано название компании")
        if not self.get_setting("business.contact_email"):
            system_errors.append("Не указан контактный email")
            
        if system_errors:
            errors["system"] = system_errors
        
        return errors
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Возвращает все настройки"""
        return self._settings.copy()
    
    def reset_to_defaults(self):
        """Сбрасывает настройки к значениям по умолчанию"""
        self.backup_settings()  # Создаем резервную копию перед сбросом
        self._settings = self._get_default_settings()
        self._save_settings()
        logger.info("Настройки сброшены к значениям по умолчанию")

    def _test_samo_api(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Тестирует подключение к SAMO API"""
        try:
            import requests
            
            endpoint = config.get('endpoint')
            token = config.get('oauth_token')
            
            if not endpoint or not token:
                return {
                    'status': 'error',
                    'message': 'Не указан endpoint или токен'
                }
            
            # Простой тест подключения
            test_data = {
                'samo_action': 'api',
                'version': '1.0',
                'type': 'json',
                'oauth_token': token
            }
            
            response = requests.post(endpoint, data=test_data, timeout=10)
            
            if response.status_code == 200:
                return {
                    'status': 'success',
                    'message': 'Подключение к SAMO API работает'
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Ошибка HTTP: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Ошибка подключения: {str(e)}'
            }
    
    def _test_telegram_bot(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Тестирует Telegram Bot API"""
        try:
            import requests
            
            token = config.get('token')
            if not token:
                return {
                    'status': 'error',
                    'message': 'Токен не указан'
                }
            
            url = f"https://api.telegram.org/bot{token}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data.get('result', {})
                    return {
                        'status': 'success',
                        'message': f'Бот {bot_info.get("first_name", "Unknown")} активен'
                    }
                else:
                    return {
                        'status': 'error',
                        'message': f'Ошибка API: {data.get("description", "Unknown error")}'
                    }
            else:
                return {
                    'status': 'error',
                    'message': f'Ошибка HTTP: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Ошибка подключения: {str(e)}'
            }
    
    def _test_openai(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Тестирует OpenAI API"""
        try:
            from openai import OpenAI
            
            api_key = config.get('api_key')
            if not api_key:
                return {
                    'status': 'error',
                    'message': 'API ключ не указан'
                }
            
            client = OpenAI(api_key=api_key)
            
            # Простой тест с минимальным запросом
            response = client.chat.completions.create(
                model=config.get('model', 'gpt-4o'),
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            
            if response.choices:
                return {
                    'status': 'success',
                    'message': 'OpenAI API работает корректно'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Неожиданный ответ от API'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Ошибка OpenAI API: {str(e)}'
            }
    
    def _test_wazzup24(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Тестирует Wazzup24 API"""
        try:
            import requests
            import base64
            
            api_key = config.get('api_key')
            api_secret = config.get('api_secret')
            base_url = config.get('base_url', 'https://api.wazzup24.com/v3')
            
            if not api_key or not api_secret:
                return {
                    'status': 'error',
                    'message': 'API ключ или секрет не указаны'
                }
            
            # Создаем Basic Auth header
            credentials = f"{api_key}:{api_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/json'
            }
            
            # Тестовый запрос на получение профиля
            url = f"{base_url}/profile"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return {
                    'status': 'success',
                    'message': 'Wazzup24 API работает корректно'
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Ошибка HTTP: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Ошибка подключения: {str(e)}'
            }
    
    def _test_bitrix24(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Тестирует Bitrix24 API"""
        try:
            import requests
            
            webhook_url = config.get('webhook_url')
            access_token = config.get('access_token')
            domain = config.get('domain')
            
            if not webhook_url and not (access_token and domain):
                return {
                    'status': 'error',
                    'message': 'Не указан webhook URL или токен доступа'
                }
            
            # Формируем URL для тестового запроса
            if webhook_url:
                url = f"{webhook_url}/profile"
            else:
                url = f"https://{domain}/rest/{access_token}/profile"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    return {
                        'status': 'success',
                        'message': 'Bitrix24 API работает корректно'
                    }
                else:
                    return {
                        'status': 'warning',
                        'message': 'API отвечает, но данные могут быть некорректны'
                    }
            else:
                return {
                    'status': 'error',
                    'message': f'Ошибка HTTP: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Ошибка подключения: {str(e)}'
            }
    
    def _test_sendgrid(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Тестирует SendGrid API"""
        try:
            import requests
            
            api_key = config.get('api_key')
            if not api_key:
                return {
                    'status': 'error',
                    'message': 'API ключ не указан'
                }
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Тестовый запрос на получение данных аккаунта
            url = "https://api.sendgrid.com/v3/user/account"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return {
                    'status': 'success',
                    'message': 'SendGrid API работает корректно'
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Ошибка HTTP: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Ошибка подключения: {str(e)}'
            }
    
    def _test_supabase(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Тестирует Supabase подключение"""
        try:
            import requests
            
            url = config.get('url')
            key = config.get('key')
            
            if not url or not key:
                return {
                    'status': 'error',
                    'message': 'URL или ключ не указаны'
                }
            
            headers = {
                'apikey': key,
                'Content-Type': 'application/json'
            }
            
            # Тестовый запрос на проверку подключения
            test_url = f"{url}/rest/v1/"
            response = requests.get(test_url, headers=headers, timeout=10)
            
            if response.status_code in [200, 404]:  # 404 тоже OK, значит подключение работает
                return {
                    'status': 'success',
                    'message': 'Supabase подключение работает'
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Ошибка HTTP: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Ошибка подключения: {str(e)}'
            }

# Глобальный экземпляр менеджера настроек
settings_manager = SettingsManager()