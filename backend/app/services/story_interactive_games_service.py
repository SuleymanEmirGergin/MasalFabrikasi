from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryInteractiveGamesService:
    """Çocuklar için interaktif oyunlar servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.games_file = os.path.join(settings.STORAGE_PATH, "story_games.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.games_file):
            with open(self.games_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_memory_game(
        self,
        story_id: str,
        story_text: str
    ) -> Dict:
        """Hikayeden hafıza oyunu oluşturur."""
        game_id = str(uuid.uuid4())
        
        # Hikayedeki karakterleri ve nesneleri çıkar
        characters = self._extract_characters(story_text)
        objects = self._extract_objects(story_text)
        
        # Kart çiftleri oluştur
        cards = []
        all_items = characters + objects[:6]  # İlk 6 nesne
        
        for item in all_items[:8]:  # Maksimum 8 çift
            cards.append({
                "id": str(uuid.uuid4()),
                "content": item,
                "pair_id": str(uuid.uuid4())
            })
            cards.append({
                "id": str(uuid.uuid4()),
                "content": item,
                "pair_id": cards[-1]["pair_id"]
            })
        
        game = {
            "game_id": game_id,
            "story_id": story_id,
            "game_type": "memory",
            "cards": cards,
            "created_at": datetime.now().isoformat()
        }
        
        games = self._load_games()
        games.append(game)
        self._save_games(games)
        
        return {
            "game_id": game_id,
            "game_type": "memory",
            "cards_count": len(cards)
        }
    
    async def create_word_search(
        self,
        story_id: str,
        story_text: str,
        grid_size: int = 10
    ) -> Dict:
        """Kelime bulmaca oluşturur."""
        game_id = str(uuid.uuid4())
        
        # Hikayedeki önemli kelimeleri çıkar
        words = self._extract_keywords(story_text)
        
        game = {
            "game_id": game_id,
            "story_id": story_id,
            "game_type": "word_search",
            "grid_size": grid_size,
            "words": words[:10],  # İlk 10 kelime
            "created_at": datetime.now().isoformat()
        }
        
        games = self._load_games()
        games.append(game)
        self._save_games(games)
        
        return {
            "game_id": game_id,
            "game_type": "word_search",
            "words_count": len(game["words"])
        }
    
    async def create_quiz_game(
        self,
        story_id: str,
        story_text: str,
        num_questions: int = 5
    ) -> Dict:
        """Hikayeden quiz oyunu oluşturur."""
        game_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki hikayeden {num_questions} adet çoktan seçmeli soru oluştur:

{story_text}

Her soru için 4 seçenek ver."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir eğitim uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Basit parse (gerçek uygulamada daha gelişmiş olmalı)
        questions = self._parse_questions(response.choices[0].message.content)
        
        game = {
            "game_id": game_id,
            "story_id": story_id,
            "game_type": "quiz",
            "questions": questions,
            "created_at": datetime.now().isoformat()
        }
        
        games = self._load_games()
        games.append(game)
        self._save_games(games)
        
        return {
            "game_id": game_id,
            "game_type": "quiz",
            "questions_count": len(questions)
        }
    
    def _extract_characters(self, text: str) -> List[str]:
        """Karakterleri çıkarır."""
        # Basit yaklaşım
        words = text.split()
        characters = []
        for i, word in enumerate(words):
            if word and word[0].isupper() and len(word) > 2:
                if i == 0 or words[i-1][-1] in '.!?':
                    characters.append(word.strip('.,!?;:'))
        return list(set(characters))[:10]
    
    def _extract_objects(self, text: str) -> List[str]:
        """Nesneleri çıkarır."""
        # Basit yaklaşım - gerçek uygulamada NLP kullanılmalı
        common_objects = ["kitap", "kalem", "masa", "sandalye", "kapı", "pencere", "araba", "ev"]
        found = [obj for obj in common_objects if obj in text.lower()]
        return found
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Önemli kelimeleri çıkarır."""
        # Basit yaklaşım
        words = text.lower().split()
        # Stop words'leri filtrele
        stop_words = {"ve", "ile", "bir", "bu", "şu", "o", "de", "da", "ki", "mi", "mu"}
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        return list(set(keywords))[:15]
    
    def _parse_questions(self, content: str) -> List[Dict]:
        """Soruları parse eder."""
        # Basit parse - gerçek uygulamada daha gelişmiş olmalı
        questions = []
        lines = content.split('\n')
        current_question = None
        
        for line in lines:
            if line.strip() and ('?' in line or line[0].isdigit()):
                if current_question:
                    questions.append(current_question)
                current_question = {
                    "question_id": str(uuid.uuid4()),
                    "question": line.strip(),
                    "options": [],
                    "correct_answer": None
                }
            elif current_question and line.strip():
                current_question["options"].append(line.strip())
        
        if current_question:
            questions.append(current_question)
        
        return questions
    
    def _load_games(self) -> List[Dict]:
        """Oyunları yükler."""
        try:
            with open(self.games_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_games(self, games: List[Dict]):
        """Oyunları kaydeder."""
        with open(self.games_file, 'w', encoding='utf-8') as f:
            json.dump(games, f, ensure_ascii=False, indent=2)

