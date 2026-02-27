from typing import Dict, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.services.image_service import ImageService
import json
import os
import uuid
from datetime import datetime


class StoryAiVisualizationService:
    """Hikaye AI görselleştirme servisi"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.image_service = ImageService()
        self.visualizations_file = os.path.join(settings.STORAGE_PATH, "ai_visualizations.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.visualizations_file):
            with open(self.visualizations_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    async def create_story_visualization(
        self,
        story_id: str,
        story_text: str,
        visualization_type: str = "scene"
    ) -> Dict:
        """Hikaye görselleştirmesi oluşturur."""
        visualization_id = str(uuid.uuid4())
        
        # Hikayeyi görselleştirilebilir bölümlere ayır
        scenes = self._extract_visual_scenes(story_text)
        
        # Her sahne için görsel oluştur
        visualizations = []
        for i, scene in enumerate(scenes):
            image_url = await self.image_service.generate_image(
                story_text=scene,
                theme="visualization",
                image_style="detailed",
                image_size="1024x1024"
            )
            
            visualizations.append({
                "scene_number": i + 1,
                "description": scene,
                "image_url": image_url,
                "visualization_type": visualization_type
            })
        
        visualization = {
            "visualization_id": visualization_id,
            "story_id": story_id,
            "type": visualization_type,
            "scenes": visualizations,
            "created_at": datetime.now().isoformat()
        }
        
        visualizations_list = self._load_visualizations()
        visualizations_list.append(visualization)
        self._save_visualizations(visualizations_list)
        
        return {
            "visualization_id": visualization_id,
            "scenes_count": len(visualizations),
            "scenes": visualizations
        }
    
    async def create_character_visualization(
        self,
        character_description: str,
        character_name: str
    ) -> Dict:
        """Karakter görselleştirmesi oluşturur."""
        visualization_id = str(uuid.uuid4())
        
        image_url = await self.image_service.generate_image(
            story_text=f"{character_name}: {character_description}",
            theme="character",
            image_style="portrait",
            image_size="1024x1024"
        )
        
        visualization = {
            "visualization_id": visualization_id,
            "type": "character",
            "character_name": character_name,
            "description": character_description,
            "image_url": image_url,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "visualization_id": visualization_id,
            "character_name": character_name,
            "image_url": image_url
        }
    
    async def create_storyboard(
        self,
        story_id: str,
        story_text: str,
        num_panels: int = 6
    ) -> Dict:
        """Storyboard oluşturur."""
        storyboard_id = str(uuid.uuid4())
        
        # Hikayeyi panellere böl
        panels = self._split_into_panels(story_text, num_panels)
        
        storyboard_panels = []
        for i, panel_text in enumerate(panels):
            image_url = await self.image_service.generate_image(
                story_text=panel_text,
                theme="storyboard",
                image_style="sketch",
                image_size="1024x512"
            )
            
            storyboard_panels.append({
                "panel_number": i + 1,
                "text": panel_text,
                "image_url": image_url
            })
        
        storyboard = {
            "storyboard_id": storyboard_id,
            "story_id": story_id,
            "panels": storyboard_panels,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "storyboard_id": storyboard_id,
            "panels_count": len(storyboard_panels),
            "panels": storyboard_panels
        }
    
    def _extract_visual_scenes(self, text: str) -> List[str]:
        """Görselleştirilebilir sahneleri çıkarır."""
        paragraphs = text.split('\n\n')
        scenes = [p.strip() for p in paragraphs if p.strip() and len(p.strip()) > 50]
        
        if not scenes:
            sentences = text.split('.')
            scenes = [s.strip() + '.' for s in sentences if s.strip() and len(s.strip()) > 20][:10]
        
        return scenes[:8]  # Maksimum 8 sahne
    
    def _split_into_panels(self, text: str, num_panels: int) -> List[str]:
        """Metni panellere böl."""
        sentences = text.split('.')
        panels = []
        sentences_per_panel = max(1, len(sentences) // num_panels)
        
        for i in range(0, len(sentences), sentences_per_panel):
            panel_text = '. '.join(sentences[i:i + sentences_per_panel])
            if panel_text.strip():
                panels.append(panel_text.strip() + '.')
            if len(panels) >= num_panels:
                break
        
        return panels if panels else [text]
    
    def _load_visualizations(self) -> List[Dict]:
        """Görselleştirmeleri yükler."""
        try:
            with open(self.visualizations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_visualizations(self, visualizations: List[Dict]):
        """Görselleştirmeleri kaydeder."""
        with open(self.visualizations_file, 'w', encoding='utf-8') as f:
            json.dump(visualizations, f, ensure_ascii=False, indent=2)

