from typing import Dict, List, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage


class StoryWorkflowService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.workflows_file = os.path.join(settings.STORAGE_PATH, "story_workflows.json")
        self.workflow_templates_file = os.path.join(settings.STORAGE_PATH, "workflow_templates.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        for file_path in [self.workflows_file, self.workflow_templates_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
    
    def create_workflow(
        self,
        story_id: str,
        workflow_name: str,
        stages: List[Dict],
        user_id: str
    ) -> Dict:
        """İş akışı oluşturur."""
        workflow = {
            "workflow_id": str(uuid.uuid4()),
            "story_id": story_id,
            "workflow_name": workflow_name,
            "stages": stages,
            "current_stage": stages[0].get("stage_id") if stages else None,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        with open(self.workflows_file, 'r', encoding='utf-8') as f:
            workflows = json.load(f)
        if story_id not in workflows:
            workflows[story_id] = []
        workflows[story_id].append(workflow)
        with open(self.workflows_file, 'w', encoding='utf-8') as f:
            json.dump(workflows, f, ensure_ascii=False, indent=2)
        
        return workflow
    
    def move_to_stage(
        self,
        story_id: str,
        workflow_id: str,
        new_stage_id: str,
        user_id: str
    ) -> Dict:
        """Aşamayı değiştirir."""
        with open(self.workflows_file, 'r', encoding='utf-8') as f:
            workflows = json.load(f)
        
        story_workflows = workflows.get(story_id, [])
        workflow = next((w for w in story_workflows if w.get('workflow_id') == workflow_id), None)
        
        if not workflow:
            raise ValueError("İş akışı bulunamadı")
        
        # Aşama geçişi
        workflow['current_stage'] = new_stage_id
        workflow['updated_at'] = datetime.now().isoformat()
        workflow['last_updated_by'] = user_id
        
        with open(self.workflows_file, 'w', encoding='utf-8') as f:
            json.dump(workflows, f, ensure_ascii=False, indent=2)
        
        return workflow
    
    def create_workflow_template(
        self,
        template_name: str,
        stages: List[Dict],
        user_id: str
    ) -> Dict:
        """İş akışı şablonu oluşturur."""
        template = {
            "template_id": str(uuid.uuid4()),
            "template_name": template_name,
            "stages": stages,
            "creator_id": user_id,
            "created_at": datetime.now().isoformat(),
            "usage_count": 0
        }
        
        with open(self.workflow_templates_file, 'r', encoding='utf-8') as f:
            templates = json.load(f)
        templates.append(template)
        with open(self.workflow_templates_file, 'w', encoding='utf-8') as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)
        
        return template
    
    def get_workflow_status(
        self,
        story_id: str,
        workflow_id: str
    ) -> Dict:
        """İş akışı durumunu getirir."""
        with open(self.workflows_file, 'r', encoding='utf-8') as f:
            workflows = json.load(f)
        
        story_workflows = workflows.get(story_id, [])
        workflow = next((w for w in story_workflows if w.get('workflow_id') == workflow_id), None)
        
        if not workflow:
            raise ValueError("İş akışı bulunamadı")
        
        current_stage_id = workflow.get('current_stage')
        current_stage = next(
            (s for s in workflow.get('stages', []) if s.get('stage_id') == current_stage_id),
            None
        )
        
        return {
            "workflow_id": workflow_id,
            "current_stage": current_stage,
            "status": workflow.get('status'),
            "progress": self._calculate_progress(workflow)
        }
    
    def _calculate_progress(self, workflow: Dict) -> float:
        """İlerleme yüzdesini hesaplar."""
        stages = workflow.get('stages', [])
        current_stage_id = workflow.get('current_stage')
        
        if not stages:
            return 0.0
        
        current_index = next(
            (i for i, s in enumerate(stages) if s.get('stage_id') == current_stage_id),
            -1
        )
        
        if current_index == -1:
            return 0.0
        
        return ((current_index + 1) / len(stages)) * 100

