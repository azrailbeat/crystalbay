"""
Crystal Bay Travel - Database Models
Модели для работы с заявками, клиентами и SAMO данными
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase

# Базовый класс для моделей
class Base(DeclarativeBase):
    pass

class Client(Base):
    """Модель клиента"""
    __tablename__ = 'clients'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    email = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    orders = relationship("Order", back_populates="client")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Order(Base):
    """Модель заявки на тур"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    number = Column(String(100), unique=True, nullable=False)
    
    # Клиент данные (можем хранить напрямую для SAMO интеграции)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=True)
    client_name = Column(String(255), nullable=True)
    client_phone = Column(String(50), nullable=True)
    client_email = Column(String(255), nullable=True)
    
    # Параметры тура
    destination = Column(String(255), nullable=False)
    hotel = Column(String(255), nullable=True)  # Совместимость с SAMO данными
    hotel_name = Column(String(255), nullable=True)
    hotel_stars = Column(Integer, nullable=True)
    check_in = Column(DateTime, nullable=True)  # Допускаем NULL для новых заявок
    check_out = Column(DateTime, nullable=True)
    nights = Column(Integer, nullable=False, default=0)
    adults = Column(Integer, nullable=False, default=1)
    children = Column(Integer, nullable=False, default=0)
    meal = Column(String(50), nullable=True)  # Совместимость с SAMO данными
    meal_type = Column(String(50), nullable=True)
    
    # Финансы
    total_amount = Column(Float, nullable=True)
    currency = Column(String(10), default='KZT')
    
    # Статус
    status = Column(String(50), default='new')  # new, processing, confirmed, paid, cancelled
    
    # SAMO данные
    samo_id = Column(String(100), nullable=True, unique=True)  # ID заявки в SAMO API
    samo_tour_id = Column(String(100), nullable=True)
    samo_hotel_id = Column(String(100), nullable=True)
    samo_booking_id = Column(String(100), nullable=True)
    source = Column(String(50), default='manual')  # manual, SAMO_API, external
    
    # Дополнительно
    special_requests = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    client = relationship("Client", back_populates="orders")
    order_logs = relationship("OrderLog", back_populates="order")
    
    def to_dict(self):
        return {
            'id': self.id,
            'number': self.number,
            'client': self.client.to_dict() if self.client else None,
            'destination': self.destination,
            'hotel_name': self.hotel_name,
            'hotel_stars': self.hotel_stars,
            'check_in': self.check_in.isoformat() if self.check_in else None,
            'check_out': self.check_out.isoformat() if self.check_out else None,
            'nights': self.nights,
            'adults': self.adults,
            'children': self.children,
            'meal_type': self.meal_type,
            'total_amount': self.total_amount,
            'currency': self.currency,
            'status': self.status,
            'special_requests': self.special_requests,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class OrderLog(Base):
    """Лог изменений заявки"""
    __tablename__ = 'order_logs'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    
    action = Column(String(100), nullable=False)  # created, updated, status_changed, etc.
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    
    # User who made the change (для будущего расширения)
    user_id = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    order = relationship("Order", back_populates="order_logs")
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'action': self.action,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'description': self.description,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SamoCache(Base):
    """Кэш данных SAMO API"""
    __tablename__ = 'samo_cache'
    
    id = Column(Integer, primary_key=True)
    cache_key = Column(String(255), unique=True, nullable=False)
    cache_data = Column(Text, nullable=False)  # JSON data
    
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'cache_key': self.cache_key,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ApiLog(Base):
    """Лог API запросов"""
    __tablename__ = 'api_logs'
    
    id = Column(Integer, primary_key=True)
    api_type = Column(String(50), nullable=False)  # samo, webapi
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    request_data = Column(Text, nullable=True)
    response_data = Column(Text, nullable=True)
    response_code = Column(Integer, nullable=True)
    execution_time = Column(Float, nullable=True)  # в секундах
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'api_type': self.api_type,
            'endpoint': self.endpoint,
            'method': self.method,
            'response_code': self.response_code,
            'execution_time': self.execution_time,
            'success': self.success,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Settings(Base):
    """Настройки системы"""
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    description = Column(String(255), nullable=True)
    category = Column(String(50), nullable=False, default='general')  # general, api, ui
    is_secret = Column(Boolean, default=False)  # Скрывать ли значение в UI
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_secrets=False):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value if (include_secrets or not self.is_secret) else ('*' * 8 if self.value else None),
            'description': self.description,
            'category': self.category,
            'is_secret': self.is_secret,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }