from typing import List, Optional, Dict
from datetime import datetime
import json
import os

# Veri kalıcılığı için JSON dosyası kullanıyoruz (Gerçek DB yerine)
MARKET_DB_PATH = "data/market_data.json"

class MarketService:
    def __init__(self):
        self._ensure_db()

    def _ensure_db(self):
        if not os.path.exists("data"):
            os.makedirs("data")
        if not os.path.exists(MARKET_DB_PATH):
            with open(MARKET_DB_PATH, "w") as f:
                json.dump({"users": {}, "transactions": []}, f)

    def _load_db(self):
        with open(MARKET_DB_PATH, "r") as f:
            return json.load(f)

    def _save_db(self, data):
        with open(MARKET_DB_PATH, "w") as f:
            json.dump(data, f, indent=2)

    async def get_user_balance(self, user_id: str) -> int:
        data = self._load_db()
        user = data["users"].get(user_id, {"credits": 10}) # Yeni kullanıcılara 10 kredi hediye
        return user.get("credits", 10)

    async def get_user_premium_status(self, user_id: str) -> bool:
        data = self._load_db()
        user = data["users"].get(user_id, {})
        # Basitlik için premium hep False veya hardcoded bir logic olabilir.
        # Gerçekte bitiş tarihi kontrolü yapılır.
        return user.get("is_premium", False)

    async def add_credits(self, user_id: str, amount: int) -> int:
        data = self._load_db()
        if user_id not in data["users"]:
            data["users"][user_id] = {"credits": 10, "is_premium": False}
        
        data["users"][user_id]["credits"] += amount
        
        # Transaction kaydı
        data["transactions"].append({
            "user_id": user_id,
            "type": "deposit",
            "amount": amount,
            "date": datetime.now().isoformat()
        })
        
        self._save_db(data)
        return data["users"][user_id]["credits"]

    async def spend_credits(self, user_id: str, amount: int, item_name: str) -> bool:
        data = self._load_db()
        if user_id not in data["users"]:
            data["users"][user_id] = {"credits": 10, "is_premium": False}
            
        current_credits = data["users"][user_id]["credits"]
        
        if current_credits >= amount:
            data["users"][user_id]["credits"] -= amount
             # Transaction kaydı
            data["transactions"].append({
                "user_id": user_id,
                "type": "purchase",
                "item": item_name,
                "amount": -amount,
                "date": datetime.now().isoformat()
            })
            self._save_db(data)
            return True
        else:
            return False

    async def upgrade_to_premium(self, user_id: str) -> bool:
        data = self._load_db()
        if user_id not in data["users"]:
            data["users"][user_id] = {"credits": 10, "is_premium": False}
            
        # Premium ücreti 100 kredi olsun
        if data["users"][user_id]["credits"] >= 100:
            data["users"][user_id]["credits"] -= 100
            data["users"][user_id]["is_premium"] = True
            
            data["transactions"].append({
                "user_id": user_id,
                "type": "subscription",
                "item": "premium_upgrade",
                "amount": -100,
                "date": datetime.now().isoformat()
            })
            self._save_db(data)
            return True
        return False
