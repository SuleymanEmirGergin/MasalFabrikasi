from typing import List, Dict, Optional
import json
import os
import uuid
from datetime import datetime
from app.core.config import settings
from app.services.story_storage import StoryStorage


class MarketplaceService:
    def __init__(self):
        self.story_storage = StoryStorage()
        self.marketplace_file = os.path.join(settings.STORAGE_PATH, "marketplace.json")
        self.transactions_file = os.path.join(settings.STORAGE_PATH, "transactions.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """Dosyaları oluşturur."""
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        if not os.path.exists(self.marketplace_file):
            with open(self.marketplace_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        if not os.path.exists(self.transactions_file):
            with open(self.transactions_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def list_story_for_sale(
        self,
        story_id: str,
        user_id: str,
        price: float,
        currency: str = "TRY",
        description: Optional[str] = None
    ) -> Dict:
        """
        Hikâyeyi pazara ekler.
        
        Args:
            story_id: Hikâye ID'si
            user_id: Satıcı kullanıcı ID'si
            price: Fiyat
            currency: Para birimi
            description: Açıklama
        
        Returns:
            Pazar listesi objesi
        """
        story = self.story_storage.get_story(story_id)
        if not story:
            raise ValueError("Hikâye bulunamadı")
        
        if story.get('user_id') != user_id:
            raise ValueError("Bu hikâye size ait değil")
        
        listing = {
            "listing_id": str(uuid.uuid4()),
            "story_id": story_id,
            "seller_id": user_id,
            "price": price,
            "currency": currency,
            "description": description,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "purchase_count": 0,
            "rating": 0.0,
            "reviews": []
        }
        
        self._save_listing(listing)
        return listing
    
    def _save_listing(self, listing: Dict):
        """Listeyi kaydeder."""
        with open(self.marketplace_file, 'r', encoding='utf-8') as f:
            listings = json.load(f)
        
        listings.append(listing)
        
        with open(self.marketplace_file, 'w', encoding='utf-8') as f:
            json.dump(listings, f, ensure_ascii=False, indent=2)
    
    def purchase_story(
        self,
        listing_id: str,
        buyer_id: str
    ) -> Dict:
        """
        Hikâyeyi satın alır.
        
        Args:
            listing_id: Liste ID'si
            buyer_id: Alıcı kullanıcı ID'si
        
        Returns:
            Satın alma işlemi bilgisi
        """
        listing = self.get_listing(listing_id)
        if not listing:
            raise ValueError("Liste bulunamadı")
        
        if listing.get('seller_id') == buyer_id:
            raise ValueError("Kendi hikâyenizi satın alamazsınız")
        
        if listing.get('status') != 'active':
            raise ValueError("Bu hikâye artık satışta değil")
        
        # İşlemi kaydet
        transaction = {
            "transaction_id": str(uuid.uuid4()),
            "listing_id": listing_id,
            "story_id": listing.get('story_id'),
            "seller_id": listing.get('seller_id'),
            "buyer_id": buyer_id,
            "price": listing.get('price'),
            "currency": listing.get('currency'),
            "status": "completed",
            "created_at": datetime.now().isoformat()
        }
        
        self._save_transaction(transaction)
        
        # Satış sayısını artır
        listing['purchase_count'] = listing.get('purchase_count', 0) + 1
        self._update_listing(listing)
        
        # Hikâyeyi alıcıya kopyala (yeni bir kopya oluştur)
        story = self.story_storage.get_story(listing.get('story_id'))
        if story:
            new_story = story.copy()
            new_story['story_id'] = str(uuid.uuid4())
            new_story['user_id'] = buyer_id
            new_story['purchased_from'] = listing_id
            new_story['created_at'] = datetime.now().isoformat()
            self.story_storage.save_story(new_story)
        
        return transaction
    
    def _save_transaction(self, transaction: Dict):
        """İşlemi kaydeder."""
        with open(self.transactions_file, 'r', encoding='utf-8') as f:
            transactions = json.load(f)
        
        transactions.append(transaction)
        
        with open(self.transactions_file, 'w', encoding='utf-8') as f:
            json.dump(transactions, f, ensure_ascii=False, indent=2)
    
    def _update_listing(self, listing: Dict):
        """Listeyi günceller."""
        with open(self.marketplace_file, 'r', encoding='utf-8') as f:
            listings = json.load(f)
        
        listings = [l for l in listings if l.get('listing_id') != listing.get('listing_id')]
        listings.append(listing)
        
        with open(self.marketplace_file, 'w', encoding='utf-8') as f:
            json.dump(listings, f, ensure_ascii=False, indent=2)
    
    def get_listing(self, listing_id: str) -> Optional[Dict]:
        """Listeyi getirir."""
        with open(self.marketplace_file, 'r', encoding='utf-8') as f:
            listings = json.load(f)
        
        return next((l for l in listings if l.get('listing_id') == listing_id), None)
    
    def get_marketplace_stories(
        self,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: str = "created_at",
        limit: int = 20
    ) -> List[Dict]:
        """
        Pazardaki hikâyeleri getirir.
        """
        with open(self.marketplace_file, 'r', encoding='utf-8') as f:
            listings = json.load(f)
        
        # Aktif listeleri filtrele
        active_listings = [l for l in listings if l.get('status') == 'active']
        
        # Fiyat filtresi
        if min_price:
            active_listings = [l for l in active_listings if l.get('price', 0) >= min_price]
        if max_price:
            active_listings = [l for l in active_listings if l.get('price', 0) <= max_price]
        
        # Sıralama
        if sort_by == "price":
            active_listings.sort(key=lambda x: x.get('price', 0))
        elif sort_by == "popularity":
            active_listings.sort(key=lambda x: x.get('purchase_count', 0), reverse=True)
        elif sort_by == "rating":
            active_listings.sort(key=lambda x: x.get('rating', 0), reverse=True)
        else:
            active_listings.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Hikâye bilgilerini ekle
        result = []
        for listing in active_listings[:limit]:
            story = self.story_storage.get_story(listing.get('story_id'))
            if story:
                listing_copy = listing.copy()
                listing_copy['story'] = {
                    "story_id": story.get('story_id'),
                    "theme": story.get('theme'),
                    "story_type": story.get('story_type'),
                    "image_url": story.get('image_url')
                }
                result.append(listing_copy)
        
        return result
    
    def add_review(
        self,
        listing_id: str,
        user_id: str,
        rating: float,
        review_text: str
    ) -> Dict:
        """
        Hikâyeye yorum ekler.
        """
        listing = self.get_listing(listing_id)
        if not listing:
            raise ValueError("Liste bulunamadı")
        
        review = {
            "review_id": str(uuid.uuid4()),
            "user_id": user_id,
            "rating": rating,
            "review_text": review_text,
            "created_at": datetime.now().isoformat()
        }
        
        reviews = listing.get('reviews', [])
        reviews.append(review)
        listing['reviews'] = reviews
        
        # Ortalama puanı güncelle
        if reviews:
            avg_rating = sum(r.get('rating', 0) for r in reviews) / len(reviews)
            listing['rating'] = round(avg_rating, 1)
        
        self._update_listing(listing)
        
        return review
    
    def get_seller_stats(self, user_id: str) -> Dict:
        """Satıcı istatistiklerini getirir."""
        with open(self.marketplace_file, 'r', encoding='utf-8') as f:
            listings = json.load(f)
        
        user_listings = [l for l in listings if l.get('seller_id') == user_id]
        
        total_sales = sum(l.get('purchase_count', 0) for l in user_listings)
        total_revenue = sum(l.get('price', 0) * l.get('purchase_count', 0) for l in user_listings)
        avg_rating = sum(l.get('rating', 0) for l in user_listings) / len(user_listings) if user_listings else 0
        
        return {
            "seller_id": user_id,
            "total_listings": len(user_listings),
            "active_listings": len([l for l in user_listings if l.get('status') == 'active']),
            "total_sales": total_sales,
            "total_revenue": round(total_revenue, 2),
            "average_rating": round(avg_rating, 1)
        }

