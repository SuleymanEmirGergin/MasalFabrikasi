from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryCharacterDevelopmentService:
    """Hikaye karakter geliştirme araçları servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.characters_file = os.path.join(settings.STORAGE_PATH, "developed_characters.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.characters_file):
            with open(self.characters_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_character_profile(
        self,
        character_name: str,
        character_type: str = "protagonist",
        initial_description: Optional[str] = None
    ) -> Dict:
        """Karakter profili oluşturur."""
        character_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki karakter için detaylı bir profil oluştur:
İsim: {character_name}
Tür: {character_type}
{f"Açıklama: {initial_description}" if initial_description else ""}

Şunları ekle:
1. Fiziksel özellikler
2. Kişilik özellikleri
3. Geçmiş ve arka plan
4. Motivasyonlar ve hedefler
5. Güçlü ve zayıf yönler"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir karakter geliştirme uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        profile = response.choices[0].message.content
        
        character = {
            "character_id": character_id,
            "name": character_name,
            "type": character_type,
            "profile": profile,
            "traits": [],
            "relationships": [],
            "created_at": datetime.now().isoformat()
        }
        
        characters = self._load_characters()
        characters.append(character)
        self._save_characters(characters)
        
        return {
            "character_id": character_id,
            "name": character_name,
            "profile": profile
        }
    
    async def develop_character_arc(
        self,
        character_id: str,
        story_context: str
    ) -> Dict:
        """Karakter gelişim yayı oluşturur."""
        characters = self._load_characters()
        character = next((c for c in characters if c["character_id"] == character_id), None)
        
        if not character:
            raise ValueError("Karakter bulunamadı")
        
        prompt = f"""Aşağıdaki karakter için bir gelişim yayı oluştur:
{character['name']}
Profil: {character['profile']}

Hikaye bağlamı: {story_context}

Karakterin başlangıç, orta ve son durumunu göster."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye yapısı uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        character_arc = response.choices[0].message.content
        
        character["character_arc"] = character_arc
        character["updated_at"] = datetime.now().isoformat()
        
        self._save_characters(characters)
        
        return {
            "character_id": character_id,
            "character_arc": character_arc
        }
    
    async def add_character_trait(
        self,
        character_id: str,
        trait_name: str,
        trait_description: str
    ) -> Dict:
        """Karaktere özellik ekler."""
        characters = self._load_characters()
        character = next((c for c in characters if c["character_id"] == character_id), None)
        
        if not character:
            raise ValueError("Karakter bulunamadı")
        
        trait = {
            "trait_id": str(uuid.uuid4()),
            "name": trait_name,
            "description": trait_description,
            "added_at": datetime.now().isoformat()
        }
        
        character["traits"].append(trait)
        character["updated_at"] = datetime.now().isoformat()
        
        self._save_characters(characters)
        
        return {
            "trait_id": trait["trait_id"],
            "message": "Özellik eklendi"
        }
    
    async def create_character_relationship(
        self,
        character1_id: str,
        character2_id: str,
        relationship_type: str,
        description: str
    ) -> Dict:
        """Karakter ilişkisi oluşturur."""
        characters = self._load_characters()
        char1 = next((c for c in characters if c["character_id"] == character1_id), None)
        char2 = next((c for c in characters if c["character_id"] == character2_id), None)
        
        if not char1 or not char2:
            raise ValueError("Karakter bulunamadı")
        
        relationship = {
            "relationship_id": str(uuid.uuid4()),
            "character1_id": character1_id,
            "character2_id": character2_id,
            "type": relationship_type,
            "description": description,
            "created_at": datetime.now().isoformat()
        }
        
        char1["relationships"].append(relationship)
        char2["relationships"].append(relationship)
        
        self._save_characters(characters)
        
        return {
            "relationship_id": relationship["relationship_id"],
            "message": "İlişki oluşturuldu"
        }
    
    async def get_character(self, character_id: str) -> Optional[Dict]:
        """Karakteri getirir."""
        characters = self._load_characters()
        return next((c for c in characters if c["character_id"] == character_id), None)
    
    def _load_characters(self) -> List[Dict]:
        """Karakterleri yükler."""
        try:
            with open(self.characters_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_characters(self, characters: List[Dict]):
        """Karakterleri kaydeder."""
        with open(self.characters_file, 'w', encoding='utf-8') as f:
            json.dump(characters, f, ensure_ascii=False, indent=2)

