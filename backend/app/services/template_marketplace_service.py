from typing import List, Dict, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings


class TemplateMarketplaceService:
    def __init__(self):
        self.marketplace_file = os.path.join(settings.STORAGE_PATH, "template_marketplace.json")
        self._ensure_file()
    
    def _ensure_file(self):
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.marketplace_file):
            with open(self.marketplace_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def list_template_for_sale(self, template_id: str, user_id: str, price: float, description: Optional[str] = None) -> Dict:
        listing = {
            "listing_id": str(uuid.uuid4()),
            "template_id": template_id,
            "seller_id": user_id,
            "price": price,
            "description": description,
            "status": "active",
            "purchase_count": 0,
            "rating": 0.0,
            "created_at": datetime.now().isoformat()
        }
        self._save_listing(listing)
        return listing
    
    def _save_listing(self, listing: Dict):
        with open(self.marketplace_file, 'r', encoding='utf-8') as f:
            listings = json.load(f)
        listings.append(listing)
        with open(self.marketplace_file, 'w', encoding='utf-8') as f:
            json.dump(listings, f, ensure_ascii=False, indent=2)
    
    def get_marketplace_templates(self, category: Optional[str] = None, limit: int = 20) -> List[Dict]:
        with open(self.marketplace_file, 'r', encoding='utf-8') as f:
            listings = json.load(f)
        active = [l for l in listings if l.get('status') == 'active']
        return sorted(active, key=lambda x: x.get('purchase_count', 0), reverse=True)[:limit]

