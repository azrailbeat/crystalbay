#!/usr/bin/env python3
"""
Скрипт для сброса всех тестовых данных и создания одного тестового набора данных
для проверки функциональности системы. Использует in-memory хранилище вместо базы данных.
"""

import os
import sys
import logging
import json
import uuid
from datetime import datetime

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Импортируем модели и сервисы
try:
    from models import LeadService, AgentService, _memory_leads, _memory_ai_agents, _memory_lead_interactions
    logger.info("Импортированы модели и сервисы")
except ImportError as e:
    logger.error(f"Ошибка импорта моделей: {e}")
    sys.exit(1)

def reset_all_data():
    """Удаляет все существующие данные в in-memory хранилище"""
    try:
        # Очищаем in-memory хранилище обращений
        logger.info("Удаление всех обращений из in-memory хранилища...")
        _memory_leads.clear()
        logger.info("Все обращения удалены из in-memory хранилища")
        
        # Очищаем in-memory хранилище взаимодействий
        logger.info("Удаление всех взаимодействий из in-memory хранилища...")
        _memory_lead_interactions.clear()
        logger.info("Все взаимодействия удалены из in-memory хранилища")
        
        # Очищаем in-memory хранилище агентов
        logger.info("Удаление всех агентов из in-memory хранилища...")
        _memory_ai_agents.clear()
        logger.info("Все агенты удалены из in-memory хранилища")
        
        # Пытаемся удалить данные из базы данных (если доступна)
        logger.info("Попытка удаления данных из базы данных...")
        lead_service = LeadService()
        lead_service.delete_all_leads()
        
        return True
    except Exception as e:
        logger.error(f"Ошибка при удалении данных: {e}")
        return False

def create_test_data():
    """Создает один тестовый набор данных для проверки функциональности в in-memory хранилище"""
    try:
        # Создаем тестового агента
        logger.info("Создание тестового агента в in-memory хранилище...")
        agent_id = "agent-" + str(uuid.uuid4())
        agent_data = {
            "id": agent_id,
            "name": "Тестовый турагент",
            "description": "Агент для обработки запросов на туры",
            "system_prompt": "Вы - турагент компании Crystal Bay Travel. Ваша задача - вежливо помогать клиентам с выбором и бронированием туров.",
            "type": "tourism",
            "enabled": True,
            "usage": {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "last_used": None
            }
        }
        _memory_ai_agents[agent_id] = agent_data
        logger.info(f"Создан тестовый агент с ID: {agent_id}")
        
        # Создаем тестовое обращение по туру
        logger.info("Создание тестового обращения в in-memory хранилище...")
        lead_id = "1"  # Простой ID для тестирования
        lead_data = {
            "id": lead_id,
            "name": "Иван Петров",
            "email": "ivan.petrov@example.com",
            "phone": "+7 (999) 123-45-67",
            "interest": "Отдых в Таиланде",
            "details": "Интересует отдых в Angsana Laguna Phuket 5* на двоих с 15 июня на 10 дней. Нужен прямой перелет и трансфер от аэропорта. Рассматриваем номер с видом на море.",
            "status": "new",
            "source": "telegram",
            "created_at": datetime.now().isoformat(),
            "tags": ["Пляжный отдых", "Таиланд", "Премиум"],
            "tour_type": "beach",
            "destination": "Таиланд, Пхукет",
            "price_range": "150000-200000",
            "travelers": 2,
            "duration": "10 дней",
            "metadata": json.dumps({
                "booking": {
                    "reference": "TH-" + datetime.now().strftime("%y%m%d") + "-123",
                    "status": "confirmed",
                    "hotel": "Angsana Laguna Phuket 5*",
                    "destination": "Таиланд, Пхукет",
                    "checkin_date": "2025-06-15",
                    "checkout_date": "2025-06-25",
                    "room_type": "Deluxe Sea View",
                    "guests": 2,
                    "total_price": 185000,
                    "payment_status": "deposit"
                }
            })
        }
        
        # Добавляем в in-memory хранилище
        _memory_leads.append(lead_data)
        logger.info(f"Создано тестовое обращение с ID: {lead_id}")
        
        # Создаем взаимодействие для обращения
        logger.info("Создание тестового взаимодействия в in-memory хранилище...")
        interaction_id = "interaction-" + str(uuid.uuid4())
        interaction_data = {
            "id": interaction_id,
            "lead_id": lead_id,
            "type": "message",
            "content": "Добрый день! Интересует отдых в Таиланде, отель Angsana Laguna Phuket. Подскажите, пожалуйста, варианты.",
            "created_at": datetime.now().isoformat(),
            "direction": "incoming"
        }
        _memory_lead_interactions.append(interaction_data)
        logger.info(f"Создано тестовое взаимодействие с ID: {interaction_id}")
        
        # Создаем ответное взаимодействие
        response_id = "interaction-" + str(uuid.uuid4())
        response_data = {
            "id": response_id,
            "lead_id": lead_id,
            "type": "message",
            "content": "Здравствуйте, Иван! Благодарим за обращение в Crystal Bay Travel. Мы подобрали для вас отличный вариант отдыха в Angsana Laguna Phuket 5* на двоих с 15 июня на 10 дней. Стоимость тура с прямым перелетом, трансфером и номером Deluxe Sea View составляет 185 000 рублей. Хотите узнать подробнее или забронировать?",
            "created_at": datetime.now().isoformat(),
            "direction": "outgoing"
        }
        _memory_lead_interactions.append(response_data)
        logger.info(f"Создано ответное взаимодействие с ID: {response_id}")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка при создании тестовых данных: {e}")
        return False

if __name__ == "__main__":
    logger.info("Запуск скрипта сброса и создания тестовых данных")
    
    # Сброс данных
    if reset_all_data():
        logger.info("Данные успешно удалены")
    else:
        logger.error("Не удалось удалить данные")
        sys.exit(1)
    
    # Создание тестовых данных
    if create_test_data():
        logger.info("Тестовые данные успешно созданы")
    else:
        logger.error("Не удалось создать тестовые данные")
        sys.exit(1)
    
    logger.info("Скрипт выполнен успешно")
    logger.info("После выполнения скрипта перезагрузите страницу вручную для отображения новых данных")