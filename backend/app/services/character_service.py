import os
import json
import uuid
from typing import Dict, List, Optional
from datetime import datetime
from app.services.story_service import StoryService
from app.services.image_service import ImageService
from app.core.config import settings


class CharacterService:
    def __init__(self):
        self.story_service = StoryService()
        self.image_service = ImageService()
        self.characters_file = f"{settings.STORAGE_PATH}/characters.json"
        self._ensure_characters_file()
    
    def _ensure_characters_file(self):
        """Characters dosyasının var olduğundan emin olur."""
        if not os.path.exists(self.characters_file):
            with open(self.characters_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def _load_characters(self) -> List[Dict]:
        """Tüm karakterleri yükler."""
        try:
            with open(self.characters_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_characters(self, characters: List[Dict]):
        """Karakterleri kaydeder."""
        with open(self.characters_file, 'w', encoding='utf-8') as f:
            json.dump(characters, f, ensure_ascii=False, indent=2)
    
    async def create_character(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        age: Optional[int] = None,
        personality: Optional[str] = None,
        appearance: Optional[str] = None,
        character_type: str = "hero",
        language: str = "tr"
    ) -> Dict:
        """
        Yeni bir karakter oluşturur.
        
        Args:
            name: Karakter ismi (opsiyonel, AI üretebilir)
            description: Karakter açıklaması (opsiyonel)
            age: Yaş (opsiyonel)
            personality: Kişilik özellikleri (opsiyonel)
            appearance: Görünüm (opsiyonel)
            character_type: Karakter türü (hero, villain, sidekick, etc.)
            language: Dil
        
        Returns:
            Oluşturulan karakter verisi
        """
        character_id = str(uuid.uuid4())
        
        # Eğer bilgiler verilmemişse AI ile üret
        if not name or not description:
            generated_info = await self._generate_character_info(
                description or f"{character_type} karakter",
                character_type,
                language
            )
            name = name or generated_info.get('name', 'Karakter')
            description = description or generated_info.get('description', '')
            personality = personality or generated_info.get('personality', '')
            appearance = appearance or generated_info.get('appearance', '')
            age = age or generated_info.get('age', 25)
        
        # Karakter görseli üret
        image_prompt = f"{name}, {appearance or description}, {character_type} character, detailed portrait"
        character_image_url = await self.image_service.generate_image(
            description or name,
            f"{name} - {character_type}",
            image_style="realistic",
            image_size="1024x1024"
        )
        
        character = {
            'character_id': character_id,
            'name': name,
            'description': description,
            'age': age,
            'personality': personality,
            'appearance': appearance,
            'character_type': character_type,
            'image_url': character_image_url,
            'language': language,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }
        
        # Karakteri kaydet
        characters = self._load_characters()
        characters.append(character)
        self._save_characters(characters)
        
        return character
    
    async def _generate_character_info(
        self,
        base_description: str,
        character_type: str,
        language: str
    ) -> Dict:
        """AI ile karakter bilgileri üretir."""
        if language == "tr":
            prompt = f"""Aşağıdaki açıklamaya göre bir {character_type} karakter oluştur:
            
Açıklama: {base_description}

Lütfen şu bilgileri JSON formatında ver:
- name: Karakter ismi
- age: Yaş (sayı)
- personality: Kişilik özellikleri (3-5 özellik)
- appearance: Görünüm açıklaması (detaylı)
- description: Karakter hakkında kısa açıklama

JSON formatında sadece veriyi döndür, başka açıklama yapma."""
        else:
            prompt = f"""Create a {character_type} character based on the following description:
            
Description: {base_description}

Please provide the following information in JSON format:
- name: Character name
- age: Age (number)
- personality: Personality traits (3-5 traits)
- appearance: Appearance description (detailed)
- description: Short description about the character

Return only the data in JSON format, no other explanation."""
        
        try:
            if self.story_service.openai_client:
                response = self.story_service.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Sen bir karakter tasarımcısısın. JSON formatında karakter bilgileri üretirsin."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.8
                )
                import re
                json_str = response.choices[0].message.content.strip()
                # JSON'u temizle
                json_str = re.sub(r'```json\n?', '', json_str)
                json_str = re.sub(r'```\n?', '', json_str)
                return json.loads(json_str)
        except Exception as e:
            print(f"Karakter bilgisi üretim hatası: {e}")
        
        # Fallback
        return {
            'name': f"{character_type.capitalize()} Karakter",
            'age': 25,
            'personality': 'Cesur, zeki, yardımsever',
            'appearance': 'Orta boylu, güçlü yapılı, dost canlısı yüz',
            'description': base_description
        }
    
    def get_all_characters(self, user_id: Optional[str] = None) -> List[Dict]:
        """Tüm karakterleri getirir."""
        characters = self._load_characters()
        if user_id:
            characters = [c for c in characters if c.get('user_id') == user_id]
        return characters
    
    def get_character(self, character_id: str) -> Optional[Dict]:
        """Belirli bir karakteri getirir."""
        characters = self._load_characters()
        return next((c for c in characters if c.get('character_id') == character_id), None)
    
    def update_character(self, character_id: str, updates: Dict) -> Optional[Dict]:
        """Karakteri günceller."""
        characters = self._load_characters()
        character = next((c for c in characters if c.get('character_id') == character_id), None)
        
        if not character:
            return None
        
        character.update(updates)
        character['updated_at'] = datetime.now().isoformat()
        self._save_characters(characters)
        return character
    
    def delete_character(self, character_id: str) -> bool:
        """Karakteri siler."""
        characters = self._load_characters()
        initial_count = len(characters)
        characters = [c for c in characters if c.get('character_id') != character_id]
        
        if len(characters) < initial_count:
            self._save_characters(characters)
            return True
        return False

