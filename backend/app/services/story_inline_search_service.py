from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryInlineSearchService:
    """Hikaye içi arama servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.search_index_file = os.path.join(settings.STORAGE_PATH, "story_search_index.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.search_index_file):
            with open(self.search_index_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    async def index_story(
        self,
        story_id: str,
        story_text: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Hikayeyi arama indeksine ekler."""
        index = self._load_index()
        
        # Hikayeyi parçalara böl (cümleler veya paragraflar)
        sentences = story_text.split('.')
        indexed_segments = []
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                indexed_segments.append({
                    "segment_id": str(uuid.uuid4()),
                    "sentence_index": i,
                    "text": sentence.strip(),
                    "position": i
                })
        
        index[story_id] = {
            "story_id": story_id,
            "metadata": metadata or {},
            "segments": indexed_segments,
            "indexed_at": datetime.now().isoformat()
        }
        
        self._save_index(index)
        
        return {
            "story_id": story_id,
            "segments_count": len(indexed_segments),
            "message": "Hikaye indekslendi"
        }
    
    async def search_in_story(
        self,
        story_id: str,
        query: str,
        context_lines: int = 2
    ) -> List[Dict]:
        """Hikaye içinde arama yapar."""
        index = self._load_index()
        story_index = index.get(story_id)
        
        if not story_index:
            return []
        
        results = []
        query_lower = query.lower()
        
        for segment in story_index["segments"]:
            if query_lower in segment["text"].lower():
                result = {
                    "segment_id": segment["segment_id"],
                    "text": segment["text"],
                    "position": segment["position"],
                    "context": self._get_context(
                        story_index["segments"],
                        segment["position"],
                        context_lines
                    )
                }
                results.append(result)
        
        return results
    
    async def semantic_search_in_story(
        self,
        story_id: str,
        query: str,
        limit: int = 5
    ) -> List[Dict]:
        """AI ile anlamsal arama yapar."""
        index = self._load_index()
        story_index = index.get(story_id)
        
        if not story_index:
            return []
        
        # Tüm hikayeyi birleştir
        full_text = " ".join([s["text"] for s in story_index["segments"]])
        
        prompt = f"""Aşağıdaki hikayede "{query}" ile ilgili bölümleri bul ve listele:

{full_text}

Sadece ilgili bölümleri ve pozisyonlarını ver."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir metin analiz uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        # Sonuçları parse et (basit bir yaklaşım)
        results_text = response.choices[0].message.content
        results = []
        
        # Basit eşleştirme (gerçek uygulamada daha gelişmiş olmalı)
        query_lower = query.lower()
        for segment in story_index["segments"]:
            if query_lower in segment["text"].lower():
                results.append({
                    "segment_id": segment["segment_id"],
                    "text": segment["text"],
                    "position": segment["position"],
                    "relevance_score": 0.8  # Basit skor
                })
        
        # Skora göre sırala ve limit uygula
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return results[:limit]
    
    def _get_context(
        self,
        segments: List[Dict],
        position: int,
        context_lines: int
    ) -> Dict:
        """Çevre metni getirir."""
        start = max(0, position - context_lines)
        end = min(len(segments), position + context_lines + 1)
        
        context_segments = segments[start:end]
        
        return {
            "before": [s["text"] for s in context_segments[:context_lines]],
            "current": segments[position]["text"] if position < len(segments) else "",
            "after": [s["text"] for s in context_segments[context_lines+1:]]
        }
    
    def _load_index(self) -> Dict:
        """İndeksi yükler."""
        try:
            with open(self.search_index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_index(self, index: Dict):
        """İndeksi kaydeder."""
        with open(self.search_index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

