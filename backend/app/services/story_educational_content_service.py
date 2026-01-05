from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class StoryEducationalContentService:
    """Hikaye eğitim içeriği ve öğrenme materyalleri servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.educational_content_file = os.path.join(settings.STORAGE_PATH, "educational_content.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.educational_content_file):
            with open(self.educational_content_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_learning_materials(
        self,
        story_id: str,
        story_text: str,
        subject: str,
        grade_level: str
    ) -> Dict:
        """Öğrenme materyalleri oluşturur."""
        material_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki hikayeyi {subject} dersi için {grade_level} seviyesinde öğrenme materyali haline getir.
Şunları ekle:
1. Öğrenme hedefleri
2. Anahtar kavramlar
3. Sorular ve aktiviteler
4. Değerlendirme ölçütleri

Hikaye:
{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir eğitim uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        materials = response.choices[0].message.content
        
        content = {
            "material_id": material_id,
            "story_id": story_id,
            "subject": subject,
            "grade_level": grade_level,
            "materials": materials,
            "created_at": datetime.now().isoformat()
        }
        
        contents = self._load_contents()
        contents.append(content)
        self._save_contents(contents)
        
        return {
            "material_id": material_id,
            "subject": subject,
            "grade_level": grade_level,
            "message": "Öğrenme materyali oluşturuldu"
        }
    
    async def create_vocabulary_list(
        self,
        story_id: str,
        story_text: str,
        difficulty_level: str = "beginner"
    ) -> Dict:
        """Kelime listesi oluşturur."""
        vocabulary_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki hikayedeki önemli kelimeleri {difficulty_level} seviyesinde listele.
Her kelime için:
1. Anlamı
2. Örnek cümle
3. Eş anlamlıları (varsa)

Hikaye:
{story_text}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir dil öğretmenisin."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1500
        )
        
        vocabulary = response.choices[0].message.content
        
        vocab_list = {
            "vocabulary_id": vocabulary_id,
            "story_id": story_id,
            "difficulty_level": difficulty_level,
            "vocabulary": vocabulary,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "vocabulary_id": vocabulary_id,
            "words_count": len(vocabulary.split('\n')),
            "message": "Kelime listesi oluşturuldu"
        }
    
    async def create_comprehension_questions(
        self,
        story_id: str,
        story_text: str,
        question_types: List[str] = ["multiple_choice", "short_answer"]
    ) -> Dict:
        """Anlama soruları oluşturur."""
        questions_id = str(uuid.uuid4())
        
        prompt = f"""Aşağıdaki hikaye için anlama soruları oluştur.
Sorular şu türlerde olsun: {', '.join(question_types)}

Hikaye:
{story_text}

Her soru için doğru cevabı da ver."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen bir eğitim uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=1500
        )
        
        questions = response.choices[0].message.content
        
        question_set = {
            "questions_id": questions_id,
            "story_id": story_id,
            "question_types": question_types,
            "questions": questions,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "questions_id": questions_id,
            "questions_count": len(questions.split('?')),
            "message": "Anlama soruları oluşturuldu"
        }
    
    def _load_contents(self) -> List[Dict]:
        """İçerikleri yükler."""
        try:
            with open(self.educational_content_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_contents(self, contents: List[Dict]):
        """İçerikleri kaydeder."""
        with open(self.educational_content_file, 'w', encoding='utf-8') as f:
            json.dump(contents, f, ensure_ascii=False, indent=2)

