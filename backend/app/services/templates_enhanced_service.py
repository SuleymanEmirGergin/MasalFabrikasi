from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
import json
import os
import uuid
from datetime import datetime


class TemplatesEnhancedService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.templates_file = os.path.join(settings.STORAGE_PATH, "templates_enhanced.json")
        self.marketplace_file = os.path.join(settings.STORAGE_PATH, "template_marketplace.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        for file_path in [self.templates_file, self.marketplace_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_ai_template(
        self,
        user_id: str,
        template_name: str,
        description: str,
        category: str
    ) -> Dict:
        """AI ile özel şablon oluşturur."""
        prompt = f"""
{description} açıklamasına uygun bir hikâye şablonu oluştur.

Kategori: {category}
Şablon Adı: {template_name}

Şablon, kullanıcıların kolayca doldurup hikâye oluşturabileceği bir yapıda olmalı. JSON formatında döndür:
{{
  "template_structure": "Şablon yapısı",
  "placeholders": ["placeholder1", "placeholder2"],
  "instructions": "Kullanım talimatları"
}}
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sen bir şablon uzmanısın. Hikâye şablonları oluşturuyorsun."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            result_text = response.choices[0].message.content
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            
            template = {
                "template_id": str(uuid.uuid4()),
                "name": template_name,
                "description": description,
                "category": category,
                "creator_id": user_id,
                "template_structure": result.get("template_structure", ""),
                "placeholders": result.get("placeholders", []),
                "instructions": result.get("instructions", ""),
                "created_at": datetime.now().isoformat(),
                "usage_count": 0,
                "is_ai_generated": True
            }
            
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            templates.append(template)
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(templates, f, ensure_ascii=False, indent=2)
            
            return template
        except Exception as e:
            return {"error": str(e)}
    
    def get_template_suggestions(
        self,
        user_id: str,
        user_preferences: Optional[Dict] = None
    ) -> List[Dict]:
        """Şablon önerileri getirir."""
        with open(self.templates_file, 'r', encoding='utf-8') as f:
            templates = json.load(f)
        
        # Kullanıcı tercihlerine göre filtrele
        if user_preferences:
            preferred_category = user_preferences.get('preferred_category')
            if preferred_category:
                templates = [t for t in templates if t.get('category') == preferred_category]
        
        # En çok kullanılanları öner
        templates.sort(key=lambda x: x.get('usage_count', 0), reverse=True)
        
        return templates[:10]
    
    def list_template_in_marketplace(
        self,
        template_id: str,
        user_id: str,
        price: float,
        is_premium: bool = False
    ) -> Dict:
        """Şablonu pazara listeler."""
        with open(self.templates_file, 'r', encoding='utf-8') as f:
            templates = json.load(f)
        
        template = next((t for t in templates if t.get('template_id') == template_id), None)
        if not template:
            raise ValueError("Şablon bulunamadı")
        
        listing = {
            "listing_id": str(uuid.uuid4()),
            "template_id": template_id,
            "seller_id": user_id,
            "price": price,
            "is_premium": is_premium,
            "created_at": datetime.now().isoformat()
        }
        
        with open(self.marketplace_file, 'r', encoding='utf-8') as f:
            marketplace = json.load(f)
        marketplace.append(listing)
        with open(self.marketplace_file, 'w', encoding='utf-8') as f:
            json.dump(marketplace, f, ensure_ascii=False, indent=2)
        
        return listing
    
    def get_community_templates(
        self,
        category: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """Topluluk şablonlarını getirir."""
        with open(self.templates_file, 'r', encoding='utf-8') as f:
            templates = json.load(f)
        
        # Topluluk şablonları (herkese açık)
        community = [t for t in templates if t.get('is_public', False)]
        
        if category:
            community = [t for t in community if t.get('category') == category]
        
        community.sort(key=lambda x: x.get('usage_count', 0), reverse=True)
        
        return community[:limit]

