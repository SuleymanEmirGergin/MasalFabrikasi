from typing import List, Dict, Optional
from app.services.story_service import StoryService
from app.services.character_service import CharacterService


class DialogueService:
    def __init__(self):
        self.story_service = StoryService()
        self.character_service = CharacterService()
    
    async def generate_dialogue(
        self,
        characters: List[Dict],
        context: str,
        dialogue_type: str = "conversation",
        language: str = "tr"
    ) -> List[Dict]:
        """
        Karakterler arası diyalog üretir.
        
        Args:
            characters: Diyaloğa katılacak karakterler listesi
            context: Diyalog bağlamı (hikâye durumu)
            dialogue_type: Diyalog türü (conversation, argument, planning, etc.)
            language: Dil
        
        Returns:
            Diyalog listesi [{"character": "İsim", "text": "Konuşma metni"}]
        """
        if len(characters) < 2:
            raise ValueError("En az 2 karakter gerekli")
        
        # Karakter isimlerini al
        character_names = [c.get('name', 'Karakter') for c in characters]
        character_descriptions = [
            f"{c.get('name')}: {c.get('personality', '')} - {c.get('description', '')}"
            for c in characters
        ]
        
        # Diyalog prompt'u oluştur
        prompt = self._create_dialogue_prompt(
            character_names,
            character_descriptions,
            context,
            dialogue_type,
            language
        )
        
        # AI ile diyalog üret
        dialogue_text = await self._generate_dialogue_text(prompt, language)
        
        # Diyalog metnini parse et
        dialogues = self._parse_dialogue(dialogue_text, character_names)
        
        return dialogues
    
    def _create_dialogue_prompt(
        self,
        character_names: List[str],
        character_descriptions: List[str],
        context: str,
        dialogue_type: str,
        language: str
    ) -> str:
        """Diyalog üretimi için prompt oluşturur."""
        if language == "tr":
            type_descriptions = {
                "conversation": "doğal bir sohbet",
                "argument": "tartışma",
                "planning": "planlama konuşması",
                "emotional": "duygusal bir konuşma",
                "action": "aksiyon sırasında konuşma",
            }
            type_desc = type_descriptions.get(dialogue_type, "doğal bir sohbet")
            
            return f"""Aşağıdaki karakterler arasında {type_desc} oluştur:

Karakterler:
{chr(10).join(f"- {name}: {desc}" for name, desc in zip(character_names, character_descriptions))}

Bağlam: {context}

Diyalog formatı:
[Karakter İsmi]: "Konuşma metni"

Lütfen 3-5 diyalog satırı oluştur. Her karakter en az bir kez konuşmalı."""
        else:
            type_descriptions = {
                "conversation": "a natural conversation",
                "argument": "an argument",
                "planning": "a planning discussion",
                "emotional": "an emotional conversation",
                "action": "dialogue during action",
            }
            type_desc = type_descriptions.get(dialogue_type, "a natural conversation")
            
            return f"""Create {type_desc} between the following characters:

Characters:
{chr(10).join(f"- {name}: {desc}" for name, desc in zip(character_names, character_descriptions))}

Context: {context}

Dialogue format:
[Character Name]: "Dialogue text"

Please create 3-5 dialogue lines. Each character should speak at least once."""
    
    async def _generate_dialogue_text(self, prompt: str, language: str) -> str:
        """AI ile diyalog metni üretir."""
        try:
            if self.story_service.openai_client:
                response = self.story_service.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Sen bir diyalog yazarısın. Karakterler arası doğal ve ilgi çekici konuşmalar yazarsın."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.8
                )
                return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Diyalog üretim hatası: {e}")
        
        # Fallback
        return f"[{self.story_service._generate_fallback_story(prompt, language)[:50]}]: \"Merhaba!\""
    
    def _parse_dialogue(self, dialogue_text: str, character_names: List[str]) -> List[Dict]:
        """Diyalog metnini parse eder."""
        dialogues = []
        lines = dialogue_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or not ':' in line:
                continue
            
            # Format: [İsim]: "Metin" veya İsim: "Metin"
            parts = line.split(':', 1)
            if len(parts) == 2:
                character = parts[0].strip().replace('[', '').replace(']', '')
                text = parts[1].strip().replace('"', '').replace("'", '')
                
                # Karakter ismini kontrol et
                matched_character = next(
                    (name for name in character_names if name.lower() in character.lower() or character.lower() in name.lower()),
                    character_names[0] if character_names else "Karakter"
                )
                
                if text:
                    dialogues.append({
                        "character": matched_character,
                        "text": text
                    })
        
        # Eğer parse edilemediyse basit bir diyalog oluştur
        if not dialogues:
            for i, name in enumerate(character_names[:2]):
                dialogues.append({
                    "character": name,
                    "text": f"Merhaba! Ben {name}."
                })
        
        return dialogues
    
    async def add_dialogue_to_story(
        self,
        story_text: str,
        dialogues: List[Dict],
        position: str = "middle"  # beginning, middle, end
    ) -> str:
        """
        Hikâye metnine diyalog ekler.
        
        Args:
            story_text: Mevcut hikâye metni
            dialogue: Eklenecek diyalog
            position: Diyalogun ekleneceği pozisyon
        """
        # Diyalog metnini formatla
        dialogue_text = "\n\n".join([
            f"{d['character']}: \"{d['text']}\""
            for d in dialogues
        ])
        
        if position == "beginning":
            return f"{dialogue_text}\n\n{story_text}"
        elif position == "end":
            return f"{story_text}\n\n{dialogue_text}"
        else:  # middle
            # Hikâyeyi ikiye böl ve ortaya ekle
            paragraphs = story_text.split('\n\n')
            if len(paragraphs) > 1:
                mid_point = len(paragraphs) // 2
                first_half = '\n\n'.join(paragraphs[:mid_point])
                second_half = '\n\n'.join(paragraphs[mid_point:])
                return f"{first_half}\n\n{dialogue_text}\n\n{second_half}"
            else:
                return f"{story_text}\n\n{dialogue_text}"

