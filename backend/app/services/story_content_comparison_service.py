from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryContentComparisonService:
    """Hikaye içerik karşılaştırma servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.comparisons_file = os.path.join(settings.STORAGE_PATH, "content_comparisons.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.comparisons_file):
            with open(self.comparisons_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def compare_stories(
        self,
        story1_id: str,
        story1_text: str,
        story2_id: str,
        story2_text: str
    ) -> Dict:
        """İki hikayeyi karşılaştırır."""
        comparison_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki iki hikayeyi karşılaştır:
1. Benzerlikler
2. Farklılıklar
3. Güçlü yönler
4. İyileştirme önerileri

Hikaye 1:
{story1_text}

Hikaye 2:
{story2_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir hikaye karşılaştırma uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1000
        )
        
        comparison_text = response.choices[0].message.content
        
        # Sayısal karşılaştırma
        similarity = self._calculate_similarity(story1_text, story2_text)
        
        comparison = {
            "comparison_id": comparison_id,
            "story1_id": story1_id,
            "story2_id": story2_id,
            "comparison_text": comparison_text,
            "similarity_score": similarity,
            "created_at": datetime.now().isoformat()
        }
        
        comparisons = self._load_comparisons()
        comparisons.append(comparison)
        self._save_comparisons(comparisons)
        
        return {
            "comparison_id": comparison_id,
            "similarity_score": similarity,
            "comparison": comparison_text
        }
    
    async def find_duplicates(
        self,
        story_id: str,
        story_text: str,
        threshold: float = 0.8
    ) -> List[Dict]:
        """Benzer/tekrar eden içerikleri bulur."""
        # Bu basit bir implementasyon, gerçek uygulamada daha gelişmiş olmalı
        duplicates = []
        
        sentences = story_text.split('.')
        for i, sentence1 in enumerate(sentences):
            for j, sentence2 in enumerate(sentences[i+1:], start=i+1):
                similarity = self._calculate_similarity(sentence1, sentence2)
                if similarity >= threshold:
                    duplicates.append({
                        "sentence1_index": i,
                        "sentence2_index": j,
                        "sentence1": sentence1.strip(),
                        "sentence2": sentence2.strip(),
                        "similarity": similarity
                    })
        
        return duplicates[:10]  # İlk 10
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Benzerlik hesaplar."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _load_comparisons(self) -> List[Dict]:
        """Karşılaştırmaları yükler."""
        try:
            with open(self.comparisons_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_comparisons(self, comparisons: List[Dict]):
        """Karşılaştırmaları kaydeder."""
        with open(self.comparisons_file, 'w', encoding='utf-8') as f:
            json.dump(comparisons, f, ensure_ascii=False, indent=2)

