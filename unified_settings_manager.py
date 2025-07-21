"""
Улучшенный менеджер настроек с реальными данными вместо заглушек
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from models import LeadService

logger = logging.getLogger(__name__)

class RealDataSettingsManager:
    """Менеджер настроек с реальными данными системы"""
    
    def __init__(self):
        self.settings_file = "settings.json"
        self.backup_dir = "settings_backup"
        self._settings = {}
        self._load_settings()
        self._init_logging()
        
        # Инициализируем сервисы данных
        try:
            self.lead_service = LeadService()
        except Exception as e:
            logger.warning(f"Не удалось инициализировать LeadService: {e}")
            self.lead_service = None
    
    def _init_logging(self):
        """Инициализирует логирование с правильной конфигурацией"""
        log_config = self._settings.get('logging', {})
        
        # Настраиваем уровень логирования
        level = getattr(logging, log_config.get('level', 'INFO'), logging.INFO)
        
        # Настраиваем формат
        formatter = logging.Formatter(
            log_config.get('log_format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        
        # Настраиваем обработчики
        if not logger.handlers:
            # Консольный обработчик
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(level)
            logger.addHandler(console_handler)
            
            # Файловый обработчик если включен
            if log_config.get('enable_file_logging', True):
                try:
                    from logging.handlers import RotatingFileHandler
                    file_handler = RotatingFileHandler(
                        log_config.get('log_file', 'crystal_bay.log'),
                        maxBytes=10*1024*1024,  # 10MB
                        backupCount=5,
                        encoding='utf-8'
                    )
                    file_handler.setFormatter(formatter)
                    file_handler.setLevel(level)
                    logger.addHandler(file_handler)
                except Exception as e:
                    logger.warning(f"Не удалось настроить файловое логирование: {e}")
        
        logger.setLevel(level)
    
    def _load_settings(self):
        """Загружает настройки из файла или создает настройки по умолчанию"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self._settings = json.load(f)
                logger.info("Настройки загружены из файла")
            else:
                self._settings = self._get_real_default_settings()
                self._save_settings()
                logger.info("Созданы новые настройки с реальными данными")
        except Exception as e:
            logger.error(f"Ошибка загрузки настроек: {e}")
            self._settings = self._get_real_default_settings()
    
    def _get_real_default_settings(self) -> Dict[str, Any]:
        """Возвращает настройки по умолчанию с реальными данными из окружения"""
        
        # Получаем реальные данные из переменных окружения
        samo_token = os.getenv("SAMO_OAUTH_TOKEN", "")
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        openai_key = os.getenv("OPENAI_API_KEY", "")
        wazzup_key = os.getenv("WAZZUP_API_KEY", "")
        wazzup_secret = os.getenv("WAZZUP_API_SECRET", "")
        bitrix_webhook = os.getenv("BITRIX_WEBHOOK_URL", "")
        sendgrid_key = os.getenv("SENDGRID_API_KEY", "")
        supabase_url = os.getenv("SUPABASE_URL", "")
        supabase_key = os.getenv("SUPABASE_KEY", "")
        
        return {
            "system": {
                "name": "Crystal Bay Travel",
                "version": "1.2.0",
                "language": "ru",
                "timezone": "Asia/Almaty",
                "debug_mode": bool(os.getenv("DEBUG", "").lower() in ['true', '1']),
                "auto_backup": True,
                "backup_interval": 24,
                "environment": os.getenv("ENVIRONMENT", "production")
            },
            "integrations": {
                "samo_api": {
                    "enabled": bool(samo_token),
                    "endpoint": "https://booking-kz.crystalbay.com/export/default.php",
                    "oauth_token": samo_token,
                    "timeout": 30,
                    "max_retries": 3,
                    "default_currency": "USD",
                    "default_departure": "1",
                    "status": "connected" if samo_token else "not_configured"
                },
                "telegram_bot": {
                    "enabled": bool(telegram_token),
                    "token": telegram_token,
                    "welcome_message": "Добро пожаловать в Crystal Bay Travel! 🌊\nМы поможем вам найти идеальный тур.",
                    "auto_respond": True,
                    "response_timeout": 30,
                    "status": "active" if telegram_token else "not_configured"
                },
                "openai": {
                    "enabled": bool(openai_key),
                    "api_key": openai_key,
                    "model": "gpt-4o",
                    "temperature": 0.7,
                    "max_tokens": 1500,
                    "language": "ru",
                    "status": "active" if openai_key else "not_configured"
                },
                "wazzup24": {
                    "enabled": bool(wazzup_key and wazzup_secret),
                    "api_key": wazzup_key,
                    "api_secret": wazzup_secret,
                    "base_url": "https://api.wazzup24.com/v3",
                    "webhook_url": "",
                    "auto_create_contacts": True,
                    "auto_create_deals": True,
                    "status": "active" if (wazzup_key and wazzup_secret) else "not_configured"
                },
                "bitrix24": {
                    "enabled": bool(bitrix_webhook),
                    "webhook_url": bitrix_webhook,
                    "pipeline_id": "7",
                    "auto_sync": True,
                    "lead_source": "Crystal Bay CRM",
                    "status": "active" if bitrix_webhook else "not_configured"
                },
                "sendgrid": {
                    "enabled": bool(sendgrid_key),
                    "api_key": sendgrid_key,
                    "from_email": os.getenv("SENDGRID_FROM_EMAIL", "noreply@crystalbay.travel"),
                    "templates": {
                        "booking_confirmation": "",
                        "booking_reminder": "",
                        "lead_notification": ""
                    },
                    "auto_notify": True,
                    "status": "active" if sendgrid_key else "not_configured"
                },
                "supabase": {
                    "enabled": bool(supabase_url and supabase_key),
                    "url": supabase_url,
                    "key": supabase_key,
                    "auto_sync": True,
                    "sync_interval": 5,
                    "status": "connected" if (supabase_url and supabase_key) else "not_configured"
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
                "lead_response_time": 60,
                "booking_confirmation_required": True
            },
            "notifications": {
                "email_notifications": bool(sendgrid_key),
                "sms_notifications": False,
                "telegram_notifications": bool(telegram_token),
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
                "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "log_to_console": True
            },
            "_metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "version": "1.2.0"
            }
        }
    
    def get_setting(self, path: str, default=None):
        """Получает значение настройки по пути"""
        try:
            keys = path.split('.')
            value = self._settings
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            logger.debug(f"Настройка {path} не найдена, возвращаем значение по умолчанию")
            return default
    
    def set_setting(self, path: str, value: Any) -> bool:
        """Устанавливает значение настройки"""
        try:
            keys = path.split('.')
            current = self._settings
            
            # Навигируем до родительского объекта
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # Сохраняем старое значение для логирования
            old_value = current.get(keys[-1])
            current[keys[-1]] = value
            
            # Обновляем метаданные
            if '_metadata' not in self._settings:
                self._settings['_metadata'] = {}
            self._settings['_metadata']['last_updated'] = datetime.now().isoformat()
            
            logger.info(f"Настройка {path}: {old_value} → {value}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка установки настройки {path}: {e}")
            return False
    
    def update_multiple_settings(self, updates: Dict[str, Any]) -> Dict[str, bool]:
        """Обновляет несколько настроек и сохраняет изменения"""
        results = {}
        changes_made = False
        
        # Создаем резервную копию
        backup_created = self._create_backup()
        if not backup_created:
            logger.warning("Не удалось создать резервную копию перед обновлением")
        
        # Применяем изменения
        for path, value in updates.items():
            success = self.set_setting(path, value)
            results[path] = success
            if success:
                changes_made = True
        
        # Сохраняем если есть изменения
        if changes_made:
            if self._save_settings():
                logger.info(f"Успешно обновлено и сохранено {sum(results.values())} настроек")
                # Перенастраиваем логирование если изменились настройки логирования
                if any('logging.' in path for path in updates.keys()):
                    self._init_logging()
            else:
                logger.error("Ошибка сохранения настроек!")
                if backup_created:
                    self._restore_from_backup()
                # Помечаем все как неуспешные
                results = {path: False for path in updates.keys()}
        
        return results
    
    def _save_settings(self) -> bool:
        """Атомарно сохраняет настройки в файл"""
        try:
            # Создаем директорию если нужно
            os.makedirs(os.path.dirname(self.settings_file) if os.path.dirname(self.settings_file) else '.', exist_ok=True)
            
            # Атомарная запись через временный файл
            temp_file = self.settings_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
            
            # Заменяем оригинальный файл
            os.replace(temp_file, self.settings_file)
            
            logger.debug(f"Настройки сохранены в {self.settings_file}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения настроек: {e}")
            # Удаляем временный файл если он остался
            if os.path.exists(self.settings_file + '.tmp'):
                try:
                    os.remove(self.settings_file + '.tmp')
                except:
                    pass
            return False
    
    def _create_backup(self) -> bool:
        """Создает резервную копию настроек"""
        try:
            if not os.path.exists(self.settings_file):
                return True  # Нечего делать резервную копию
            
            os.makedirs(self.backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"settings_{timestamp}.json")
            
            import shutil
            shutil.copy2(self.settings_file, backup_file)
            
            logger.debug(f"Резервная копия создана: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания резервной копии: {e}")
            return False
    
    def _restore_from_backup(self) -> bool:
        """Восстанавливает настройки из последней резервной копии"""
        try:
            if not os.path.exists(self.backup_dir):
                return False
            
            # Находим последнюю резервную копию
            backup_files = [f for f in os.listdir(self.backup_dir) if f.startswith('settings_') and f.endswith('.json')]
            if not backup_files:
                return False
            
            latest_backup = sorted(backup_files)[-1]
            backup_path = os.path.join(self.backup_dir, latest_backup)
            
            # Восстанавливаем настройки
            with open(backup_path, 'r', encoding='utf-8') as f:
                self._settings = json.load(f)
            
            logger.warning(f"Настройки восстановлены из резервной копии: {latest_backup}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка восстановления из резервной копии: {e}")
            return False
    
    def get_integration_status(self, integration: str) -> Dict[str, Any]:
        """Получает реальный статус интеграции"""
        config = self.get_setting(f'integrations.{integration}', {})
        
        # Определяем статус на основе конфигурации
        if not config or not isinstance(config, dict):
            status = "not_found"
        elif not config.get('enabled', False):
            status = "disabled"
        else:
            # Проверяем наличие обязательных полей
            if integration == "samo_api":
                status = "active" if config.get('oauth_token') else "not_configured"
            elif integration == "telegram_bot":
                status = "active" if config.get('token') else "not_configured"
            elif integration == "openai":
                status = "active" if config.get('api_key') else "not_configured"
            elif integration == "wazzup24":
                status = "active" if (config.get('api_key') and config.get('api_secret')) else "not_configured"
            elif integration == "bitrix24":
                status = "active" if config.get('webhook_url') else "not_configured"
            elif integration == "sendgrid":
                status = "active" if config.get('api_key') else "not_configured"
            elif integration == "supabase":
                status = "active" if (config.get('url') and config.get('key')) else "not_configured"
            else:
                status = "unknown"
        
        return {
            "integration": integration,
            "status": status,
            "enabled": config.get('enabled', False) if isinstance(config, dict) else False,
            "config": config if isinstance(config, dict) else {}
        }
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Возвращает все настройки"""
        return self._settings.copy()

    def save_integration_settings(self, integration_name: str, settings: Dict[str, Any]) -> bool:
        """
        Сохранить настройки конкретной интеграции
        """
        try:
            # Получаем текущие настройки
            all_settings = dict(self._settings)
            
            if 'integrations' not in all_settings:
                all_settings['integrations'] = {}
            
            # Обновляем настройки интеграции
            all_settings['integrations'][integration_name] = settings
            
            # Сохраняем обновленные настройки
            self._settings = all_settings
            success = self._save_settings()
            
            if success:
                logger.info(f"Настройки интеграции {integration_name} успешно сохранены")
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка сохранения настроек интеграции {integration_name}: {e}")
            return False
    
    def save_all_settings_unified(self, settings: Dict[str, Any]) -> bool:
        """
        Сохранить все настройки
        """
        try:
            self._settings = settings
            success = self._save_settings()
            
            if success:
                logger.info("Все настройки успешно сохранены")
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка сохранения всех настроек: {e}")
            return False

    def get_all_settings(self) -> Dict[str, Any]:
        """Возвращает все настройки системы"""
        return self._settings.copy()

# Глобальный экземпляр улучшенного менеджера
real_settings_manager = RealDataSettingsManager()