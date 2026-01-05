from sqlalchemy.orm import Session
from app.models import Character, Story
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

class CharacterChatService:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)

    async def chat_with_character(self, db: Session, character_id: str, user_message: str, history: list = []):
        """
        Simulates a chat with a character.
        """
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            return "Karakter bulunamadı."

        # Constuct Persona
        persona = f"""
        Sen bir masal kahramanısın.
        Adın: {character.name}
        Kişiliğin: {character.personality or "Sevimli ve yardımsever"}
        Görünüşün: {character.appearance or "Bilinmiyor"}
        Rolün: {character.character_type or "Kahraman"}
        
        Çocuklarla konuşuyorsun. Yanıtların kısa, eğlenceli ve yaşa uygun olsun.
        Asla yapay zeka olduğunu söyleme. Rolünden asla çıkma.
        """
        
        # Build Context (Simple RAG: Last story summary could be added here)
        # For now, just persona.
        
        messages = [SystemMessage(content=persona)]
        
        # Add history (last 5 messages)
        for msg in history[-5:]:
            if msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['content']))
            else:
                messages.append(AIMessage(content=msg['content']))
                
        messages.append(HumanMessage(content=user_message))
        
        response = self.llm.invoke(messages)
        return response.content

character_chat_service = CharacterChatService()
