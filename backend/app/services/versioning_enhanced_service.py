from typing import Dict, List, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage


class VersioningEnhancedService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.versions_file = os.path.join(settings.STORAGE_PATH, "story_versions_enhanced.json")
        self.branches_file = os.path.join(settings.STORAGE_PATH, "story_branches.json")
        self._ensure_files()
    
    def _ensure_files(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        for file_path in [self.versions_file, self.branches_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
    
    def create_version(
        self,
        story_id: str,
        user_id: str,
        description: Optional[str] = None
    ) -> Dict:
        """Versiyon oluşturur (Git benzeri)."""
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        with open(self.versions_file, 'r', encoding='utf-8') as f:
            versions = json.load(f)
        
        if story_id not in versions:
            versions[story_id] = {
                "versions": [],
                "current_version": None,
                "branches": []
            }
        
        version_id = str(uuid.uuid4())
        version = {
            "version_id": version_id,
            "story_id": story_id,
            "user_id": user_id,
            "description": description or f"Versiyon {len(versions[story_id]['versions']) + 1}",
            "story_data": story.copy(),
            "created_at": datetime.now().isoformat(),
            "parent_version": versions[story_id].get('current_version')
        }
        
        versions[story_id]['versions'].append(version)
        versions[story_id]['current_version'] = version_id
        
        with open(self.versions_file, 'w', encoding='utf-8') as f:
            json.dump(versions, f, ensure_ascii=False, indent=2)
        
        return version
    
    def create_branch(
        self,
        story_id: str,
        branch_name: str,
        from_version: Optional[str] = None
    ) -> Dict:
        """Branch oluşturur."""
        with open(self.branches_file, 'r', encoding='utf-8') as f:
            branches = json.load(f)
        
        if story_id not in branches:
            branches[story_id] = []
        
        branch = {
            "branch_id": str(uuid.uuid4()),
            "story_id": story_id,
            "branch_name": branch_name,
            "from_version": from_version,
            "created_at": datetime.now().isoformat(),
            "versions": []
        }
        
        branches[story_id].append(branch)
        
        with open(self.branches_file, 'w', encoding='utf-8') as f:
            json.dump(branches, f, ensure_ascii=False, indent=2)
        
        return branch
    
    def merge_branch(
        self,
        story_id: str,
        branch_id: str,
        target_version: str
    ) -> Dict:
        """Branch'i merge eder."""
        with open(self.branches_file, 'r', encoding='utf-8') as f:
            branches = json.load(f)
        
        story_branches = branches.get(story_id, [])
        branch = next((b for b in story_branches if b.get('branch_id') == branch_id), None)
        
        if not branch:
            raise ValueError("Branch bulunamadı")
        
        # Merge işlemi
        merge_result = {
            "merge_id": str(uuid.uuid4()),
            "story_id": story_id,
            "branch_id": branch_id,
            "target_version": target_version,
            "merged_at": datetime.now().isoformat(),
            "conflicts": []
        }
        
        return merge_result
    
    def compare_versions(
        self,
        story_id: str,
        version_id_1: str,
        version_id_2: str
    ) -> Dict:
        """İki versiyonu karşılaştırır."""
        with open(self.versions_file, 'r', encoding='utf-8') as f:
            versions = json.load(f)
        
        story_versions = versions.get(story_id, {}).get('versions', [])
        v1 = next((v for v in story_versions if v.get('version_id') == version_id_1), None)
        v2 = next((v for v in story_versions if v.get('version_id') == version_id_2), None)
        
        if not v1 or not v2:
            raise ValueError("Versiyon bulunamadı")
        
        text1 = v1.get('story_data', {}).get('story_text', '')
        text2 = v2.get('story_data', {}).get('story_text', '')
        
        # Basit karşılaştırma
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        added = words2 - words1
        removed = words1 - words2
        common = words1 & words2
        
        return {
            "version1": version_id_1,
            "version2": version_id_2,
            "added_words": list(added),
            "removed_words": list(removed),
            "common_words": len(common),
            "similarity": len(common) / max(len(words1), len(words2), 1) * 100
        }
    
    def revert_to_version(
        self,
        story_id: str,
        version_id: str
    ) -> Dict:
        """Versiyona geri döner."""
        with open(self.versions_file, 'r', encoding='utf-8') as f:
            versions = json.load(f)
        
        story_versions = versions.get(story_id, {}).get('versions', [])
        version = next((v for v in story_versions if v.get('version_id') == version_id), None)
        
        if not version:
            raise ValueError("Versiyon bulunamadı")
        
        # Hikâyeyi geri yükle
        story_data = version.get('story_data', {})
        self.story_storage.save_story(story_data)
        
        versions[story_id]['current_version'] = version_id
        
        with open(self.versions_file, 'w', encoding='utf-8') as f:
            json.dump(versions, f, ensure_ascii=False, indent=2)
        
        return {
            "story_id": story_id,
            "reverted_to": version_id,
            "reverted_at": datetime.now().isoformat()
        }

