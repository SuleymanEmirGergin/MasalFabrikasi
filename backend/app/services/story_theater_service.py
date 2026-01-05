from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryTheaterService:
    """Hikaye performans ve tiyatro formatı servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.theater_scripts_file = os.path.join(settings.STORAGE_PATH, "theater_scripts.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.theater_scripts_file):
            with open(self.theater_scripts_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_theater_script(
        self,
        story_id: str,
        story_text: str,
        num_actors: int = 3
    ) -> Dict:
        """Hikayeden tiyatro senaryosu oluşturur."""
        script_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki hikayeyi {num_actors} kişilik bir tiyatro oyununa dönüştür. 
Diyaloglar, sahne talimatları ve karakter tanımlamaları ekle:

{story_text}

Tiyatro formatında döndür."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir tiyatro senaryo yazarısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        script_text = response.choices[0].message.content
        
        # Karakterleri ve sahneleri çıkar
        characters = self._extract_characters(script_text)
        scenes = self._extract_scenes(script_text)
        
        script = {
            "script_id": script_id,
            "story_id": story_id,
            "script_text": script_text,
            "characters": characters,
            "scenes": scenes,
            "num_actors": num_actors,
            "estimated_duration": len(scenes) * 5,  # Dakika
            "created_at": datetime.now().isoformat()
        }
        
        scripts = self._load_scripts()
        scripts.append(script)
        self._save_scripts(scripts)
        
        return {
            "script_id": script_id,
            "characters_count": len(characters),
            "scenes_count": len(scenes),
            "estimated_duration": script["estimated_duration"]
        }
    
    async def create_puppet_show(
        self,
        story_id: str,
        story_text: str
    ) -> Dict:
        """Kukla gösterisi oluşturur."""
        show_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki hikayeyi kukla gösterisi için uyarla. 
Basit diyaloglar ve görsel talimatlar ekle:

{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir kukla gösterisi yazarısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        puppet_script = response.choices[0].message.content
        
        show = {
            "show_id": show_id,
            "story_id": story_id,
            "script": puppet_script,
            "puppets_needed": self._count_characters(story_text),
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "show_id": show_id,
            "puppets_needed": show["puppets_needed"],
            "message": "Kukla gösterisi oluşturuldu"
        }
    
    def _extract_characters(self, script: str) -> List[str]:
        """Karakterleri çıkarır."""
        characters = []
        lines = script.split('\n')
        
        for line in lines:
            if ':' in line and len(line) < 100:
                character = line.split(':')[0].strip()
                if character and character not in characters:
                    characters.append(character)
        
        return characters[:10]
    
    def _extract_scenes(self, script: str) -> List[Dict]:
        """Sahneleri çıkarır."""
        scenes = []
        lines = script.split('\n')
        current_scene = None
        
        for line in lines:
            if 'SAHNE' in line.upper() or 'SCENE' in line.upper():
                if current_scene:
                    scenes.append(current_scene)
                current_scene = {
                    "scene_number": len(scenes) + 1,
                    "title": line.strip(),
                    "content": ""
                }
            elif current_scene:
                current_scene["content"] += line + "\n"
        
        if current_scene:
            scenes.append(current_scene)
        
        return scenes if scenes else [{"scene_number": 1, "title": "Tek Sahne", "content": script}]
    
    def _count_characters(self, text: str) -> int:
        """Karakter sayısını sayar."""
        words = text.split()
        characters = set()
        for i, word in enumerate(words):
            if word and word[0].isupper() and len(word) > 2:
                if i == 0 or words[i-1][-1] in '.!?':
                    characters.add(word.strip('.,!?;:'))
        return min(len(characters), 5)
    
    def _load_scripts(self) -> List[Dict]:
        """Senaryoları yükler."""
        try:
            with open(self.theater_scripts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_scripts(self, scripts: List[Dict]):
        """Senaryoları kaydeder."""
        with open(self.theater_scripts_file, 'w', encoding='utf-8') as f:
            json.dump(scripts, f, ensure_ascii=False, indent=2)

