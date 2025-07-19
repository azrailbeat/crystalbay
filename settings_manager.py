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
                "supabase": {
                    "enabled": True,
                    "url": os.getenv("SUPABASE_URL", ""),
                    "key": os.getenv("SUPABASE_KEY", ""),
                    "auto_sync": True,
                    "sync_interval": 5  # минуты
                },
                "sendgrid": {
                    "enabled": False,
                    "api_key": os.getenv("SENDGRID_API_KEY", ""),
                    "from_email": os.getenv("SENDGRID_FROM_EMAIL", "noreply@crystalbay.travel"),
                    "templates": {
                        "booking_confirmation": "",
                        "booking_reminder": "",
                        "lead_notification": ""
                    }
                },
                "wazzup": {
                    "enabled": False,
                    "api_key": os.getenv("WAZZUP_API_KEY", ""),
                    "api_secret": os.getenv("WAZZUP_API_SECRET", ""),
                    "webhook_url": "",
                    "auto_process": True
                },
                "bitrix24": {
                    "enabled": True,
                    "webhook_url": os.getenv("BITRIX_WEBHOOK_URL", ""),
                    "access_token": os.getenv("BITRIX_ACCESS_TOKEN", ""),
                    "pipeline_id": "7",
                    "auto_create_leads": True,
                    "sync_contacts": True
                }
            },
            "notifications": {
                "email_enabled": False,
                "telegram_enabled": True,
                "push_enabled": False,
                "new_lead_notification": True,
                "booking_confirmation": True,
                "system_alerts": True,
                "notification_channels": {
                    "critical": ["telegram", "email"],
                    "warning": ["telegram"],
                    "info": ["system"]
                }
            },
            "business": {
                "company_name": "Crystal Bay Travel",
                "contact_email": "info@crystalbay.travel",
                "contact_phone": "+7 (999) 123-45-67",
                "website": "https://crystalbay.travel",
                "office_hours": {
                    "start": "09:00",
                    "end": "18:00",
                    "timezone": "Asia/Almaty",
                    "working_days": [1, 2, 3, 4, 5]  # Пн-Пт
                },
                "currency": "USD",
                "default_markup": 10,  # %
                "commission_rate": 5,  # %
            },
            "ui": {
                "theme": "light",
                "sidebar_collapsed": False,
                "default_page": "dashboard",
                "items_per_page": 20,
                "auto_refresh": True,
                "refresh_interval": 30,  # секунды
                "show_tooltips": True,
                "compact_mode": False
            },
            "security": {
                "session_timeout": 3600,  # секунды
                "max_login_attempts": 5,
                "password_min_length": 8,
                "require_2fa": False,
                "api_rate_limit": 100,  # запросов в минуту
                "log_level": "INFO"
            },
            "analytics": {
                "track_user_actions": True,
                "track_api_calls": True,
                "retention_days": 90,
                "export_format": "json",
                "auto_reports": True,
                "report_frequency": "weekly"
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
        """Сохраняет настройки в файл"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, ensure_ascii=False, indent=2)
            logger.info("Настройки сохранены")
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения настроек: {e}")
            return False
    
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

# Глобальный экземпляр менеджера настроек
settings_manager = SettingsManager()