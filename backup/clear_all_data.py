#!/usr/bin/env python3
"""
Скрипт для полного удаления всех данных из системы.
Очищает и in-memory хранилище и базу данных (если доступна).
"""

import os
import sys
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Импортируем модели и сервисы
try:
    from models import LeadService, _memory_leads, _memory_ai_agents, _memory_lead_interactions
    logger.info("Импортированы модели и сервисы")
except ImportError as e:
    logger.error(f"Ошибка импорта моделей: {e}")
    sys.exit(1)

def clear_all_data():
    """Удаляет все существующие данные из системы"""
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

if __name__ == "__main__":
    logger.info("Запуск скрипта очистки всех данных")
    
    # Очистка данных
    if clear_all_data():
        logger.info("Все данные успешно удалены")
    else:
        logger.error("Произошла ошибка при удалении данных")
        sys.exit(1)
    
    logger.info("Скрипт выполнен успешно")
    logger.info("После выполнения скрипта перезагрузите страницу вручную для отображения изменений")