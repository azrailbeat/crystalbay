"""
Официальная интеграция с Wazzup24 API v3
Реализована согласно документации https://wazzup24.ru/help/api-ru/
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class WazzupAPIv3:
    """Официальный клиент для Wazzup24 API v3"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('WAZZUP_API_KEY')
        self.base_url = "https://api.wazzup24.com/v3"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }
        
    def _make_request(self, method: str, endpoint: str, data: Any = None, params: dict = None) -> Any:
        """Выполнить HTTP запрос к API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30
            )
            
            logger.info(f"Wazzup API {method} {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                return response.json() if response.text else {}
            else:
                error_data = response.json() if response.text else {}
                logger.error(f"Wazzup API error: {response.status_code} - {error_data}")
                return {"error": True, "status_code": response.status_code, "data": error_data}
                
        except Exception as e:
            logger.error(f"Wazzup API request failed: {e}")
            return {"error": True, "message": str(e)}
    
    # ===================== ПОЛЬЗОВАТЕЛИ =====================
    
    def get_users(self) -> Any:
        """Получить список всех пользователей"""
        return self._make_request("GET", "/users")
    
    def get_user(self, user_id: str) -> Dict:
        """Получить данные конкретного пользователя"""
        return self._make_request("GET", f"/users/{user_id}")
    
    def create_users(self, users: List[Dict]) -> Dict:
        """
        Добавить или обновить пользователей (до 100 за раз)
        
        users: список с полями:
        - id (str): Идентификатор пользователя (до 64 символов)
        - name (str): Имя пользователя (до 150 символов)
        - phone (str, optional): Номер телефона в международном формате
        """
        if len(users) > 100:
            raise ValueError("Максимум 100 пользователей за один запрос")
            
        return self._make_request("POST", "/users", data=users)
    
    def delete_user(self, user_id: str) -> Dict:
        """Удалить пользователя"""
        return self._make_request("DELETE", f"/users/{user_id}")
    
    def bulk_delete_users(self, user_ids: List[str]) -> Dict:
        """Массово удалить пользователей"""
        return self._make_request("PATCH", "/users/bulk_delete", data=user_ids)
    
    # ===================== КОНТАКТЫ =====================
    
    def get_contacts(self) -> Any:
        """Получить список контактов"""
        return self._make_request("GET", "/contacts")
    
    def create_contacts(self, contacts: List[Dict]) -> Dict:
        """
        Создать или обновить контакты
        
        contacts: список с полями:
        - id (str): Идентификатор контакта в CRM
        - name (str): Имя контакта
        - phone (str, optional): Телефон в международном формате
        - email (str, optional): Email
        - crmUri (str, optional): Ссылка на контакт в CRM
        """
        return self._make_request("PATCH", "/contacts", data=contacts)
    
    # ===================== СДЕЛКИ =====================
    
    def get_deals(self) -> Any:
        """Получить список сделок"""
        return self._make_request("GET", "/deals")
    
    def create_deals(self, deals: List[Dict]) -> Dict:
        """
        Создать или обновить сделки
        
        deals: список с полями:
        - id (str): Идентификатор сделки в CRM
        - name (str): Название сделки
        - contactId (str): ID контакта
        - stageId (str): ID этапа воронки
        - responsibleUserId (str): ID ответственного
        - crmUri (str, optional): Ссылка на сделку в CRM
        """
        return self._make_request("PATCH", "/deals", data=deals)
    
    # ===================== ВОРОНКИ =====================
    
    def create_funnels(self, funnels: List[Dict]) -> Dict:
        """
        Загрузить воронки продаж с этапами
        
        funnels: список с полями:
        - id (str): Идентификатор воронки
        - name (str): Название воронки
        - stages (list): Список этапов с полями id, name
        """
        return self._make_request("PATCH", "/funnels", data=funnels)
    
    # ===================== СООБЩЕНИЯ =====================
    
    def send_message(self, chat_id: str, message_data: Dict) -> Dict:
        """
        Отправить сообщение
        
        chat_id: ID чата
        message_data: данные сообщения с полями:
        - text (str): Текст сообщения
        - type (str): Тип сообщения (text, image, etc.)
        """
        return self._make_request("POST", f"/chats/{chat_id}/messages", data=message_data)
    
    def get_messages(self, chat_id: str, limit: int = 50) -> Any:
        """Получить сообщения из чата"""
        params = {"limit": limit}
        return self._make_request("GET", f"/chats/{chat_id}/messages", params=params)
    
    # ===================== ВЕБХУКИ =====================
    
    def setup_webhooks(self, webhook_uri: str, subscriptions: Dict) -> Dict:
        """
        Настроить вебхуки
        
        webhook_uri: URL для получения вебхуков
        subscriptions: настройки подписок:
        - messagesAndStatuses (bool): Новые сообщения и статусы
        - contactsAndDealsCreation (bool): Создание контактов и сделок
        - channelsUpdates (bool): Обновления каналов
        - templateStatus (bool): Статусы шаблонов WABA
        """
        data = {
            "webhooksUri": webhook_uri,
            "subscriptions": subscriptions
        }
        return self._make_request("PATCH", "/webhooks", data=data)
    
    def get_webhooks_config(self) -> Dict:
        """Получить текущую конфигурацию вебхуков"""
        return self._make_request("GET", "/webhooks")
    
    # ===================== МАРКЕТПЛЕЙС (для партнеров) =====================
    
    def register_marketplace_integration(self, crm_code: str, auth_redirect_uri: str, secret: str) -> Dict:
        """
        Зарегистрировать интеграцию в маркетплейсе (для партнеров)
        
        crm_code: Код CRM для идентификации
        auth_redirect_uri: URL для авторизации
        secret: Секретный ключ для подтверждения
        """
        data = {
            "crmCode": crm_code,
            "authRedirectUri": auth_redirect_uri,
            "secret": secret
        }
        return self._make_request("POST", "/marketplace", data=data)
    
    def connect_integration(self, state: str, secret: str, crm_key: str, name: str) -> Dict:
        """
        Подключить интеграцию через WAuth
        
        state: Сгенерированный Wazzup ключ
        secret: Секретный ключ партнера
        crm_key: Ключ для идентификации в вебхуках
        name: Название интеграции
        """
        data = {
            "state": state,
            "secret": secret,
            "crmKey": crm_key,
            "name": name
        }
        return self._make_request("POST", "/connect", data=data)
    
    # ===================== КАНАЛЫ =====================
    
    def get_channels(self) -> Any:
        """Получить список каналов"""
        return self._make_request("GET", "/channels")
    
    def get_channel_status(self, channel_id: str) -> Dict:
        """Получить статус канала"""
        return self._make_request("GET", f"/channels/{channel_id}")
    
    # ===================== ПРОВЕРКА ПОДКЛЮЧЕНИЯ =====================
    
    def test_connection(self) -> Dict:
        """Проверить подключение к API"""
        try:
            result = self.get_users()
            if isinstance(result, list):
                return {
                    "success": True, 
                    "message": "Подключение к Wazzup24 API успешно",
                    "users_count": len(result)
                }
            elif result.get("error"):
                return {
                    "success": False,
                    "message": f"Ошибка API: {result.get('message', 'Неизвестная ошибка')}",
                    "details": result
                }
            else:
                return {"success": True, "message": "API доступен"}
        except Exception as e:
            return {"success": False, "message": f"Ошибка подключения: {str(e)}"}

    # ===================== УТИЛИТЫ =====================
    
    def validate_phone(self, phone: str) -> str:
        """Валидация и форматирование номера телефона для российского формата"""
        if not phone:
            return ""
        
        # Убираем все нецифровые символы
        digits = ''.join(filter(str.isdigit, phone))
        
        # Российские номера
        if digits.startswith('8') and len(digits) == 11:
            return '7' + digits[1:]  # 8 -> 7
        elif digits.startswith('7') and len(digits) == 11:
            return digits
        elif len(digits) == 10:
            return '7' + digits
        else:
            logger.warning(f"Неподдерживаемый формат телефона: {phone}")
            return phone  # Возвращаем как есть
    
    def format_user_for_wazzup(self, user_data: Dict) -> Dict:
        """Форматировать данные пользователя для отправки в Wazzup"""
        formatted = {
            "id": str(user_data.get("id", "")),
            "name": str(user_data.get("name", ""))
        }
        
        if user_data.get("phone"):
            formatted["phone"] = self.validate_phone(user_data["phone"])
            
        return formatted
    
    def format_contact_for_wazzup(self, contact_data: Dict) -> Dict:
        """Форматировать данные контакта для отправки в Wazzup"""
        formatted = {
            "id": str(contact_data.get("id", "")),
            "name": str(contact_data.get("name", ""))
        }
        
        if contact_data.get("phone"):
            formatted["phone"] = self.validate_phone(contact_data["phone"])
            
        if contact_data.get("email"):
            formatted["email"] = contact_data["email"]
            
        if contact_data.get("crm_uri"):
            formatted["crmUri"] = contact_data["crm_uri"]
            
        return formatted

# Создаем глобальный экземпляр
wazzup_api = WazzupAPIv3()

def get_wazzup_client() -> WazzupAPIv3:
    """Получить клиент Wazzup API"""
    return wazzup_api

if __name__ == "__main__":
    # Тестирование API
    api = WazzupAPIv3()
    result = api.test_connection()
    print(json.dumps(result, indent=2, ensure_ascii=False))