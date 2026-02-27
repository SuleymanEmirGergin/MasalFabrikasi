from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryChooseYourAdventureService:
    """Hikaye interaktif seçimler ve dallanma servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.adventures_file = os.path.join(settings.STORAGE_PATH, "choose_adventures.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.adventures_file):
            with open(self.adventures_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_choose_adventure(
        self,
        story_id: str,
        initial_story: str,
        num_choices_per_node: int = 3
    ) -> Dict:
        """Seçimli macera hikayesi oluşturur."""
        adventure_id = str(uuid.uuid4())
        
        # İlk düğümü oluştur
        root_node = await self._create_story_node(
            initial_story,
            num_choices_per_node,
            parent_id=None
        )
        
        adventure = {
            "adventure_id": adventure_id,
            "story_id": story_id,
            "root_node_id": root_node["node_id"],
            "nodes": [root_node],
            "created_at": datetime.now().isoformat()
        }
        
        adventures = self._load_adventures()
        adventures.append(adventure)
        self._save_adventures(adventures)
        
        return {
            "adventure_id": adventure_id,
            "root_node_id": root_node["node_id"],
            "message": "Seçimli macera oluşturuldu"
        }
    
    async def _create_story_node(
        self,
        story_text: str,
        num_choices: int,
        parent_id: Optional[str]
    ) -> Dict:
        """Hikaye düğümü oluşturur."""
        node_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki hikaye bölümü için {num_choices} farklı seçenek oluştur.
Her seçenek farklı bir sonuca götürmeli:

{story_text}

Seçenekleri ve her seçeneğin kısa açıklamasını ver."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir interaktif hikaye uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=1000
        )
        
        choices_text = response.choices[0].message.content
        
        # Seçenekleri parse et
        choices = self._parse_choices(choices_text, num_choices)
        
        node = {
            "node_id": node_id,
            "story_text": story_text,
            "choices": choices,
            "parent_id": parent_id,
            "created_at": datetime.now().isoformat()
        }
        
        return node
    
    async def add_choice_path(
        self,
        adventure_id: str,
        from_node_id: str,
        choice_index: int,
        continuation_story: str
    ) -> Dict:
        """Seçim yolunu genişletir."""
        adventures = self._load_adventures()
        adventure = next((a for a in adventures if a["adventure_id"] == adventure_id), None)
        
        if not adventure:
            raise ValueError("Macera bulunamadı")
        
        from_node = next((n for n in adventure["nodes"] if n["node_id"] == from_node_id), None)
        if not from_node:
            raise ValueError("Düğüm bulunamadı")
        
        # Yeni düğüm oluştur
        new_node = await self._create_story_node(
            continuation_story,
            3,  # Varsayılan seçenek sayısı
            from_node_id
        )
        
        # Seçeneği bağla
        if choice_index < len(from_node["choices"]):
            from_node["choices"][choice_index]["next_node_id"] = new_node["node_id"]
        
        adventure["nodes"].append(new_node)
        self._save_adventures(adventures)
        
        return {
            "new_node_id": new_node["node_id"],
            "message": "Yol eklendi"
        }
    
    async def make_choice(
        self,
        adventure_id: str,
        current_node_id: str,
        choice_index: int
    ) -> Dict:
        """Seçim yapar ve sonraki düğüme geçer."""
        adventures = self._load_adventures()
        adventure = next((a for a in adventures if a["adventure_id"] == adventure_id), None)
        
        if not adventure:
            raise ValueError("Macera bulunamadı")
        
        current_node = next((n for n in adventure["nodes"] if n["node_id"] == current_node_id), None)
        if not current_node:
            raise ValueError("Düğüm bulunamadı")
        
        if choice_index >= len(current_node["choices"]):
            raise ValueError("Geçersiz seçim")
        
        choice = current_node["choices"][choice_index]
        next_node_id = choice.get("next_node_id")
        
        if not next_node_id:
            # Sonuç düğümü
            return {
                "is_end": True,
                "ending": choice.get("description", "Hikaye sona erdi"),
                "message": "Hikaye tamamlandı"
            }
        
        next_node = next((n for n in adventure["nodes"] if n["node_id"] == next_node_id), None)
        
        return {
            "is_end": False,
            "next_node": next_node,
            "message": "Sonraki bölüme geçildi"
        }
    
    def _parse_choices(self, choices_text: str, num_choices: int) -> List[Dict]:
        """Seçenekleri parse eder."""
        choices = []
        lines = choices_text.split('\n')
        
        current_choice = None
        for line in lines:
            if line.strip() and (line[0].isdigit() or line.startswith('-')):
                if current_choice:
                    choices.append(current_choice)
                choice_text = line.strip().lstrip('1234567890.- ').strip()
                current_choice = {
                    "choice_id": str(uuid.uuid4()),
                    "description": choice_text,
                    "next_node_id": None
                }
            elif current_choice and line.strip():
                current_choice["description"] += " " + line.strip()
        
        if current_choice:
            choices.append(current_choice)
        
        return choices[:num_choices] if choices else [
            {"choice_id": str(uuid.uuid4()), "description": f"Seçenek {i+1}", "next_node_id": None}
            for i in range(num_choices)
        ]
    
    def _load_adventures(self) -> List[Dict]:
        """Maceraları yükler."""
        try:
            with open(self.adventures_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_adventures(self, adventures: List[Dict]):
        """Maceraları kaydeder."""
        with open(self.adventures_file, 'w', encoding='utf-8') as f:
            json.dump(adventures, f, ensure_ascii=False, indent=2)

