from sqlalchemy.orm import Session
from app.models import Character, Story
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.core.config import settings
from app.services.wiro_client import wiro_client

class CharacterChatService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)

    def _build_prompt(self, persona: str, history: list, user_message: str) -> str:
        """Single prompt string for Wiro (persona + history + user message)."""
        parts = [persona, "\n\nKonuşma geçmişi (son mesajlar):"]
        for msg in history[-5:]:
            role = "Kullanıcı" if msg.get("role") == "user" else "Sen"
            parts.append(f"{role}: {msg.get('content', '')}")
        parts.append(f"\nKullanıcı: {user_message}\n\nSen (karakter olarak kısa ve rolünde yanıt ver):")
        return "\n".join(parts)

    async def chat_with_character(
        self, db: Session, character_id: str, user_message: str, history: list = [], use_wiro: bool = False
    ):
        """
        Simulates a chat with a character.
        use_wiro: if True and WIRO_API_KEY is set, use Wiro gpt-5-nano instead of OpenAI.
        """
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            return "Karakter bulunamadı."

        persona = f"""
        Sen bir masal kahramanısın.
        Adın: {character.name}
        Kişiliğin: {character.personality or "Sevimli ve yardımsever"}
        Görünüşün: {character.appearance or "Bilinmiyor"}
        Rolün: {character.character_type or "Kahraman"}
        
        Çocuklarla konuşuyorsun. Yanıtların kısa, eğlenceli ve yaşa uygun olsun.
        Asla yapay zeka olduğunu söyleme. Rolünden asla çıkma.
        """

        if use_wiro and getattr(settings, "WIRO_API_KEY", None):
            try:
                prompt = self._build_prompt(persona, history, user_message)
                inputs = {
                    "prompt": prompt,
                    "reasoning": "low",
                    "verbosity": "medium",
                    "webSearch": "false",
                }
                result = await wiro_client.run_and_wait(
                    "openai", "gpt-5-nano", inputs, is_json=False
                )
                if result.get("error_message"):
                    return "Karakter şu an yanıt veremiyor. Lütfen tekrar dene."
                detail = result.get("detail") or {}
                tasklist = detail.get("tasklist") or []
                if tasklist:
                    task = tasklist[0]
                    text = (task.get("debugoutput") or "").strip()
                    if not text and task.get("outputs"):
                        first = task["outputs"][0] if isinstance(task.get("outputs"), list) else None
                        if first and isinstance(first, dict) and first.get("url"):
                            text = first.get("text", "") or "[URL]"
                    if text:
                        return text
                return "Karakter yanıtı alınamadı. Lütfen tekrar dene."
            except Exception:
                return "Karakter şu an yanıt veremiyor. Lütfen tekrar dene."

        messages = [SystemMessage(content=persona)]
        for msg in history[-5:]:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg.get("content", "")))
            else:
                messages.append(AIMessage(content=msg.get("content", "")))
        messages.append(HumanMessage(content=user_message))
        response = self.llm.invoke(messages)
        return response.content

character_chat_service = CharacterChatService()
