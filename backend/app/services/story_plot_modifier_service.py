from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryPlotModifierService:
    """Hikaye içerik olay değiştirme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.plot_modifications_file = os.path.join(settings.STORAGE_PATH, "plot_modifications.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.plot_modifications_file):
            with open(self.plot_modifications_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def modify_plot(
        self,
        story_id: str,
        story_text: str,
        modification_type: str,  # "add_conflict", "add_twist", "change_ending"
        modification_details: str
    ) -> Dict:
        """Olay örgüsünü değiştirir."""
        modification_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki hikayenin olay örgüsünü değiştir:
{modification_type}: {modification_details}

Hikaye:
{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir olay örgüsü değiştirme uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )
        
        modified_text = response.choices[0].message.content
        
        return {
            "modification_id": modification_id,
            "modified_text": modified_text,
            "modification_type": modification_type
        }
    
    def _load_modifications(self) -> List[Dict]:
        """Değişiklikleri yükler."""
        try:
            with open(self.plot_modifications_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_modifications(self, modifications: List[Dict]):
        """Değişiklikleri kaydeder."""
        with open(self.plot_modifications_file, 'w', encoding='utf-8') as f:
            json.dump(modifications, f, ensure_ascii=False, indent=2)

