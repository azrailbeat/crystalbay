"""
AI Chat Service for Crystal Bay Travel
Handles AI-powered responses for messaging with configurable agents and prompts
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from openai import OpenAI

logger = logging.getLogger(__name__)

def get_openai_api_key():
    """Safely retrieve OpenAI API key from environment"""
    return os.environ.get("OPENAI_API_NEW_KEY") or os.environ.get("OPENAI_API_KEY")

def get_openai_client():
    """Get OpenAI client instance"""
    api_key = get_openai_api_key()
    if api_key:
        return OpenAI(api_key=api_key)
    return None

def get_ai_model():
    """Get configured AI model from environment or default"""
    return os.environ.get("AI_MODEL", "gpt-4o")


DEFAULT_SYSTEM_PROMPT = """Вы - опытный менеджер туристического агентства Crystal Bay Travel.
Ваша задача - помогать клиентам с подбором туров, отвечать на вопросы о направлениях, 
ценах и условиях бронирования.

Правила общения:
- Будьте вежливы и профессиональны
- Отвечайте кратко и по существу
- Предлагайте конкретные варианты туров когда это уместно
- Уточняйте детали: даты, бюджет, количество человек
- При необходимости предлагайте связаться с живым менеджером

Ключевые направления: Турция, Египет, ОАЭ, Таиланд, Мальдивы, Европа.
"""

AI_AGENTS_CONFIG = {
    "travel_consultant": {
        "id": "travel_consultant",
        "name": "Консультант по турам",
        "type": "chat",
        "description": "Основной агент для консультаций по турам",
        "prompt": DEFAULT_SYSTEM_PROMPT,
        "active": True,
        "settings": {
            "max_tokens": 500,
            "auto_reply": True
        }
    },
    "lead_qualifier": {
        "id": "lead_qualifier", 
        "name": "Квалификатор лидов",
        "type": "classification",
        "description": "Определяет готовность клиента к покупке",
        "prompt": """Вы - эксперт по квалификации лидов в туризме.
Проанализируйте диалог и определите:
1. Уровень заинтересованности (горячий/теплый/холодный)
2. Предполагаемый бюджет
3. Срочность (ближайшие дни/недели/месяцы)
4. Рекомендуемые действия менеджера

Ответьте в формате JSON.""",
        "active": True,
        "settings": {
            "max_tokens": 300,
            "auto_reply": False
        }
    },
    "quick_responder": {
        "id": "quick_responder",
        "name": "Быстрые ответы",
        "type": "auto",
        "description": "Автоматические ответы на типовые вопросы",
        "prompt": """Вы - быстрый помощник Crystal Bay Travel.
Давайте краткие ответы на простые вопросы о:
- Рабочих часах (10:00-19:00 МСК)
- Способах связи
- Общей информации о компании

Для сложных вопросов предложите связаться с менеджером.""",
        "active": True,
        "settings": {
            "max_tokens": 150,
            "auto_reply": True
        }
    }
}


class AIConversationManager:
    """Manages AI mode for conversations"""
    
    _conversation_modes = {}
    
    @classmethod
    def set_mode(cls, conversation_id: str, mode: str, agent_id: str = None) -> Dict:
        """Set AI mode for a conversation
        
        Args:
            conversation_id: The conversation ID
            mode: 'auto', 'manual', or 'assisted'
            agent_id: The AI agent to use (optional)
        """
        cls._conversation_modes[conversation_id] = {
            "mode": mode,
            "agent_id": agent_id or "travel_consultant",
            "updated_at": datetime.now().isoformat()
        }
        return cls._conversation_modes[conversation_id]
    
    @classmethod
    def get_mode(cls, conversation_id: str) -> Dict:
        """Get AI mode for a conversation"""
        return cls._conversation_modes.get(conversation_id, {
            "mode": "manual",
            "agent_id": None,
            "updated_at": None
        })
    
    @classmethod
    def is_auto_mode(cls, conversation_id: str) -> bool:
        """Check if conversation is in auto mode"""
        mode_data = cls.get_mode(conversation_id)
        return mode_data.get("mode") == "auto"


class AIChatService:
    """Service for generating AI chat responses"""
    
    @staticmethod
    def get_agent(agent_id: str) -> Optional[Dict]:
        """Get agent configuration by ID"""
        try:
            from models import AIAgentService
            agent = AIAgentService.get_ai_agent(agent_id)
            if agent:
                return agent
        except Exception as e:
            logger.debug(f"Could not get agent from DB: {e}")
        
        return AI_AGENTS_CONFIG.get(agent_id)
    
    @staticmethod
    def get_all_agents() -> List[Dict]:
        """Get all available AI agents"""
        try:
            from models import AIAgentService
            db_agents = AIAgentService.get_ai_agents()
            if db_agents:
                return db_agents
        except Exception as e:
            logger.debug(f"Could not get agents from DB: {e}")
        
        return list(AI_AGENTS_CONFIG.values())
    
    @staticmethod
    def generate_response(
        conversation_history: List[Dict],
        agent_id: str = "travel_consultant",
        context: Dict = None
    ) -> Dict:
        """Generate AI response for a conversation
        
        Args:
            conversation_history: List of messages in the conversation
            agent_id: Which AI agent to use
            context: Additional context (customer info, etc)
            
        Returns:
            Dict with response text and metadata
        """
        client = get_openai_client()
        if not client:
            return {
                "success": False,
                "error": "OpenAI API key not configured",
                "response": None
            }
        
        agent = AIChatService.get_agent(agent_id)
        if not agent:
            agent = AI_AGENTS_CONFIG.get("travel_consultant")
        
        system_prompt = agent.get("prompt", DEFAULT_SYSTEM_PROMPT)
        
        if context:
            if context.get("customer_name"):
                system_prompt += f"\n\nИмя клиента: {context['customer_name']}"
            if context.get("channel"):
                system_prompt += f"\nКанал связи: {context['channel']}"
        
        messages = [{"role": "system", "content": system_prompt}]
        
        for msg in conversation_history[-10:]:
            role = "assistant" if msg.get("direction") == "outgoing" else "user"
            content = msg.get("content", msg.get("text", ""))
            if content:
                messages.append({"role": role, "content": content})
        
        try:
            settings = agent.get("settings", {})
            max_tokens = settings.get("max_tokens", 500)
            model = get_ai_model()
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens
            )
            
            ai_response = response.choices[0].message.content
            
            AIChatService._track_usage(agent_id, success=True)
            
            return {
                "success": True,
                "response": ai_response,
                "agent_id": agent_id,
                "agent_name": agent.get("name", "AI Agent"),
                "model": model,
                "tokens_used": response.usage.total_tokens if response.usage else 0
            }
            
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            AIChatService._track_usage(agent_id, success=False)
            
            return {
                "success": False,
                "error": str(e),
                "response": None
            }
    
    @staticmethod
    def _track_usage(agent_id: str, success: bool):
        """Track agent usage statistics"""
        try:
            from models import AIAgentService
            AIAgentService.track_usage(agent_id, success=success)
        except Exception as e:
            logger.debug(f"Could not track usage: {e}")
    
    @staticmethod
    def suggest_response(
        last_message: str,
        agent_id: str = "travel_consultant"
    ) -> Dict:
        """Generate a suggested response for manual mode
        
        Returns multiple suggestions for the manager to choose from
        """
        client = get_openai_client()
        if not client:
            return {
                "success": False,
                "error": "OpenAI API key not configured",
                "suggestions": []
            }
        
        agent = AIChatService.get_agent(agent_id)
        system_prompt = agent.get("prompt", DEFAULT_SYSTEM_PROMPT) if agent else DEFAULT_SYSTEM_PROMPT
        model = get_ai_model()
        
        suggestion_prompt = f"""{system_prompt}

Клиент написал: "{last_message}"

Предложите 3 варианта ответа разной длины:
1. Краткий (1-2 предложения)
2. Средний (3-4 предложения)  
3. Подробный (5-6 предложений)

Ответьте в формате JSON:
{{"suggestions": ["краткий ответ", "средний ответ", "подробный ответ"]}}"""
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": suggestion_prompt}],
                response_format={"type": "json_object"},
                max_tokens=600
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "suggestions": result.get("suggestions", []),
                "agent_id": agent_id
            }
            
        except Exception as e:
            logger.error(f"Failed to generate suggestions: {e}")
            return {
                "success": False,
                "error": str(e),
                "suggestions": []
            }
    
    @staticmethod
    def analyze_conversation(conversation_history: List[Dict]) -> Dict:
        """Analyze a conversation for lead qualification"""
        client = get_openai_client()
        if not client:
            return {"success": False, "error": "OpenAI not configured"}
        
        messages_text = "\n".join([
            f"{'Клиент' if m.get('direction') == 'incoming' else 'Менеджер'}: {m.get('content', '')}"
            for m in conversation_history[-20:]
        ])
        
        model = get_ai_model()
        
        analysis_prompt = f"""Проанализируй диалог и предоставь информацию в JSON:

{messages_text}

Верни JSON:
{{
  "lead_temperature": "hot|warm|cold",
  "budget_estimate": "low|medium|high|unknown",
  "urgency": "immediate|soon|later|unknown",
  "interests": ["список направлений или типов туров"],
  "next_actions": ["рекомендуемые действия"],
  "summary": "краткое резюме диалога"
}}"""
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": analysis_prompt}],
                response_format={"type": "json_object"},
                max_tokens=400
            )
            
            result = json.loads(response.choices[0].message.content)
            return {"success": True, "analysis": result}
            
        except Exception as e:
            logger.error(f"Conversation analysis failed: {e}")
            return {"success": False, "error": str(e)}


def get_ai_status() -> Dict:
    """Get current AI system status"""
    return {
        "openai_configured": bool(get_openai_api_key()),
        "agents_available": len(AI_AGENTS_CONFIG),
        "default_agent": "travel_consultant",
        "model": get_ai_model()
    }


# Module-level instances for easy import
ai_chat_service = AIChatService
conversation_manager = AIConversationManager()
