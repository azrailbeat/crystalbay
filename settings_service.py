"""
Settings Service для Crystal Bay Travel
Сервис для работы с настройками системы
"""

import os
import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from models import Settings
from app import db

logger = logging.getLogger(__name__)

class SettingsService:
    """Сервис для работы с настройками системы"""
    
    # Настройки по умолчанию
    DEFAULT_SETTINGS = {
        # API настройки
        'samo_api_url': {
            'value': 'https://booking.crystalbay.com/export/default.php',
            'description': 'URL для SAMO API',
            'category': 'api',
            'is_secret': False
        },
        'samo_oauth_token': {
            'value': '',
            'description': 'OAuth токен для SAMO API',
            'category': 'api',
            'is_secret': True
        },
        'webapi_base_url': {
            'value': 'https://booking.crystalbay.com',
            'description': 'Базовый URL для WebAPI',
            'category': 'api',
            'is_secret': False
        },
        'webapi_bearer_token': {
            'value': '',
            'description': 'Bearer токен для WebAPI (ClaimSearch)',
            'category': 'api',
            'is_secret': True
        },
        'openai_api_key': {
            'value': '',
            'description': 'API ключ для OpenAI',
            'category': 'api',
            'is_secret': True
        },
        
        # Общие настройки
        'company_name': {
            'value': 'Crystal Bay Travel',
            'description': 'Название компании',
            'category': 'general',
            'is_secret': False
        },
        'default_currency': {
            'value': 'KZT',
            'description': 'Валюта по умолчанию',
            'category': 'general',
            'is_secret': False
        },
        'timezone': {
            'value': 'Asia/Almaty',
            'description': 'Часовой пояс',
            'category': 'general',
            'is_secret': False
        },
        
        # UI настройки
        'orders_per_page': {
            'value': '50',
            'description': 'Количество заявок на странице',
            'category': 'ui',
            'is_secret': False
        },
        'auto_refresh_interval': {
            'value': '30',
            'description': 'Интервал автообновления (секунды)',
            'category': 'ui',
            'is_secret': False
        }
    }
    
    def __init__(self):
        """Инициализация сервиса настроек"""
        self._settings_cache = {}
        self._load_defaults()
    
    def _load_defaults(self):
        """Загрузка настроек по умолчанию в БД"""
        try:
            with db.session.begin():
                for key, config in self.DEFAULT_SETTINGS.items():
                    # Проверяем, есть ли настройка в БД
                    existing = db.session.query(Settings).filter_by(key=key).first()
                    if not existing:
                        # Создаем новую настройку
                        setting = Settings(
                            key=key,
                            value=config['value'],
                            description=config['description'],
                            category=config['category'],
                            is_secret=config['is_secret']
                        )
                        db.session.add(setting)
                        logger.info(f"Создана настройка по умолчанию: {key}")
        except Exception as e:
            logger.error(f"Ошибка при загрузке настроек по умолчанию: {e}")
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Получить значение настройки"""
        try:
            # Сначала проверяем переменные окружения
            env_value = os.environ.get(key.upper())
            if env_value:
                return env_value
            
            # Проверяем кэш
            if key in self._settings_cache:
                return self._settings_cache[key]
            
            # Загружаем из БД
            setting = db.session.query(Settings).filter_by(key=key).first()
            if setting:
                self._settings_cache[key] = setting.value
                return setting.value
            
            # Возвращаем значение по умолчанию
            if key in self.DEFAULT_SETTINGS:
                return self.DEFAULT_SETTINGS[key]['value']
            
            return default
        except Exception as e:
            logger.error(f"Ошибка при получении настройки {key}: {e}")
            return default
    
    def set(self, key: str, value: str, description: str = None, category: str = 'general', is_secret: bool = False) -> bool:
        """Установить значение настройки"""
        try:
            with db.session.begin():
                setting = db.session.query(Settings).filter_by(key=key).first()
                if setting:
                    # Обновляем существующую настройку
                    setting.value = value
                    if description:
                        setting.description = description
                    setting.category = category
                    setting.is_secret = is_secret
                else:
                    # Создаем новую настройку
                    setting = Settings(
                        key=key,
                        value=value,
                        description=description,
                        category=category,
                        is_secret=is_secret
                    )
                    db.session.add(setting)
                
                # Обновляем кэш
                self._settings_cache[key] = value
                logger.info(f"Настройка {key} обновлена")
                return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении настройки {key}: {e}")
            return False
    
    def get_all(self, category: Optional[str] = None, include_secrets: bool = False) -> List[Dict[str, Any]]:
        """Получить все настройки"""
        try:
            query = db.session.query(Settings)
            if category:
                query = query.filter_by(category=category)
            
            settings = query.all()
            return [setting.to_dict(include_secrets=include_secrets) for setting in settings]
        except Exception as e:
            logger.error(f"Ошибка при получении всех настроек: {e}")
            return []
    
    def get_categories(self) -> List[str]:
        """Получить список категорий настроек"""
        try:
            categories = db.session.query(Settings.category).distinct().all()
            return [cat[0] for cat in categories]
        except Exception as e:
            logger.error(f"Ошибка при получении категорий: {e}")
            return ['general', 'api', 'ui']
    
    def delete(self, key: str) -> bool:
        """Удалить настройку"""
        try:
            with db.session.begin():
                setting = db.session.query(Settings).filter_by(key=key).first()
                if setting:
                    db.session.delete(setting)
                    # Удаляем из кэша
                    if key in self._settings_cache:
                        del self._settings_cache[key]
                    logger.info(f"Настройка {key} удалена")
                    return True
                return False
        except Exception as e:
            logger.error(f"Ошибка при удалении настройки {key}: {e}")
            return False
    
    def clear_cache(self):
        """Очистить кэш настроек"""
        self._settings_cache.clear()
        logger.info("Кэш настроек очищен")
    
    def get_api_config(self) -> Dict[str, str]:
        """Получить конфигурацию API"""
        return {
            'samo_api_url': self.get('samo_api_url'),
            'samo_oauth_token': self.get('samo_oauth_token'),
            'webapi_base_url': self.get('webapi_base_url'),
            'webapi_bearer_token': self.get('webapi_bearer_token'),
            'openai_api_key': self.get('openai_api_key')
        }

# Глобальный экземпляр сервиса
settings_service = SettingsService()