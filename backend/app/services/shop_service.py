from typing import List, Dict, Optional
import json
import os

# Storage path
INVENTORY_FILE = "data/inventory.json"

# Initialize inventory storage
if not os.path.exists("data"):
    os.makedirs("data")
    
if not os.path.exists(INVENTORY_FILE):
    with open(INVENTORY_FILE, 'w') as f:
        json.dump({}, f)

# Shop catalog (Sabit ürünler)
SHOP_ITEMS = [
    {"id": "hat_wizard", "name": "Sihirbaz Şapkası", "category": "hat", "price": 100, "icon": "🎩"},
    {"id": "hat_crown", "name": "Altın Taç", "category": "hat", "price": 200, "icon": "👑"},
    {"id": "glasses_cool", "name": "Havalı Gözlük", "category": "glasses", "price": 50, "icon": "😎"},
    {"id": "outfit_superhero", "name": "Süper Kahraman Kostümü", "category": "outfit", "price": 300, "icon": "🦸"},
    {"id": "outfit_princess", "name": "Prenses Elbisesi", "category": "outfit", "price": 250, "icon": "👗"},
    {"id": "pet_dragon", "name": "Ejderha Yavrusu", "category": "pet", "price": 500, "icon": "🐉"},
    {"id": "pet_cat", "name": "Sevimli Kedi", "category": "pet", "price": 150, "icon": "🐱"},
]

class ShopService:
    
    def get_shop_items(self) -> List[Dict]:
        """Mağazadaki tüm eşyaları getirir."""
        return SHOP_ITEMS
    
    def get_user_inventory(self, user_id: str) -> Dict:
        """Kullanıcının envanterini getirir."""
        with open(INVENTORY_FILE, 'r') as f:
            data = json.load(f)
        
        if user_id not in data:
            data[user_id] = {
                "owned_items": [],
                "equipped": {
                    "hat": None,
                    "glasses": None,
                    "outfit": None,
                    "pet": None
                }
            }
            with open(INVENTORY_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        
        return data[user_id]
    
    def purchase_item(self, user_id: str, item_id: str, credits: int) -> Dict:
        """Eşya satın alır (Kredit kontrolü ile)."""
        # Eşya var mı?
        item = next((i for i in SHOP_ITEMS if i["id"] == item_id), None)
        if not item:
            raise ValueError("Eşya bulunamadı.")
        
        # Yeterli kredi var mı?
        if credits < item["price"]:
            raise ValueError("Yetersiz kredi.")
        
        # Envanteri güncelle
        with open(INVENTORY_FILE, 'r') as f:
            data = json.load(f)
        
        if user_id not in data:
            data[user_id] = {"owned_items": [], "equipped": {}}
        
        if item_id in data[user_id]["owned_items"]:
            raise ValueError("Bu eşya zaten sahipsiniz.")
        
        data[user_id]["owned_items"].append(item_id)
        
        with open(INVENTORY_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        return {
            "message": f"{item['name']} başarıyla satın alındı!",
            "new_balance": credits - item["price"]
        }
    
    def equip_item(self, user_id: str, item_id: str) -> Dict:
        """Eşyayı donatır."""
        with open(INVENTORY_FILE, 'r') as f:
            data = json.load(f)
        
        if user_id not in data or item_id not in data[user_id]["owned_items"]:
            raise ValueError("Bu eşya sizin değil.")
        
        # Kategorisini bul
        item = next((i for i in SHOP_ITEMS if i["id"] == item_id), None)
        if not item:
            raise ValueError("Eşya bulunamadı.")
        
        data[user_id]["equipped"][item["category"]] = item_id
        
        with open(INVENTORY_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        return data[user_id]
    
    def unequip_item(self, user_id: str, category: str) -> Dict:
        """Kategori eşyasını çıkarır."""
        with open(INVENTORY_FILE, 'r') as f:
            data = json.load(f)
        
        if user_id not in data:
            raise ValueError("Kullanıcı bulunamadı.")
        
        data[user_id]["equipped"][category] = None
        
        with open(INVENTORY_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        return data[user_id]
