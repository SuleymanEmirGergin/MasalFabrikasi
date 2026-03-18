import json
import os
import sys
import asyncio
import uuid
from datetime import datetime

# Backend dizinini path'e ekle
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal
from app.repositories.story_repository import StoryRepository
from app.repositories.user_repository import UserRepository
from app.services.cloud_storage_service import cloud_storage

STORAGE_PATH = "storage"
JSON_FILE = os.path.join(STORAGE_PATH, "stories.json")

async def migrate_stories():
    print("🚀 Migration başlatılıyor...")
    
    # 1. JSON dosyasını oku
    if not os.path.exists(JSON_FILE):
        print(f"❌ {JSON_FILE} bulunamadı!")
        return

    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            stories = json.load(f)
    except Exception as e:
        print(f"❌ JSON okuma hatası: {e}")
        return

    print(f"📄 {len(stories)} hikaye bulundu.")
    
    # DB session
    db = SessionLocal()
    story_repo = StoryRepository(db)
    user_repo = UserRepository(db)
    
    # Varsayılan kullanıcıyı al veya oluştur (Migrasyon için)
    # Auth olmadığı için "default" bir kullanıcı kullanıyoruz
    default_auth_id = uuid.UUID("00000000-0000-0000-0000-000000000000") 
    user_profile = user_repo.get_profile_by_auth_id(default_auth_id)
    if not user_profile:
        user_profile = user_repo.create_profile(default_auth_id)
    
    user_id = user_profile.id
    
    success_count = 0
    
    for story_data in stories:
        try:
            story_id = story_data.get('story_id')
            print(f"🔄 Migrating story: {story_id}")
            
            # Zaten var mı kontrol et
            existing_story = story_repo.get_story_by_id(story_id)
            if existing_story:
                print(f"⚠️ Story {story_id} zaten var, atlanıyor.")
                continue

            # --- Image Migration ---
            image_url = story_data.get('image_url')
            if image_url and not image_url.startswith("http"):
                # Local path ise Supabase'e yükle
                local_image_path = os.path.join(STORAGE_PATH, "images", os.path.basename(image_url))
                if os.path.exists(local_image_path):
                    print(f"   ⬆️ Uploading image: {local_image_path}")
                    image_url = await cloud_storage.upload_image(
                        local_image_path, 
                        public_id=f"migrated_{story_id}"
                    )
                else:
                    print(f"   ⚠️ Local image not found: {local_image_path}")

            # --- Audio Migration ---
            audio_url = story_data.get('audio_url')
            if audio_url and not audio_url.startswith("http"):
                local_audio_path = os.path.join(STORAGE_PATH, "audio", os.path.basename(audio_url))
                if os.path.exists(local_audio_path):
                    print(f"   ⬆️ Uploading audio: {local_audio_path}")
                    audio_url = await cloud_storage.upload_audio(
                        local_audio_path,
                        public_id=f"migrated_{story_id}"
                    )
                else:
                    print(f"   ⚠️ Local audio not found: {local_audio_path}")

            # --- DB Insert ---
            new_story_data = {
                'story_id': story_id,
                'theme': story_data.get('theme'),
                'story_text': story_data.get('story_text'),
                'language': story_data.get('language', 'tr'),
                'story_type': story_data.get('story_type', 'masal'),
                'image_url': image_url,
                'audio_url': audio_url,
                'is_favorite': story_data.get('is_favorite', False),
                'created_at': story_data.get('created_at', datetime.now())
            }
            
            story_repo.create_story(new_story_data, user_id)
            success_count += 1
            print(f"✅ Story {story_id} migrated successfully.")

        except Exception as e:
            print(f"❌ Story {story_data.get('story_id')} migration error: {e}")

    print(f"\n🎉 Migration tamamlandı! {success_count}/{len(stories)} hikaye aktarıldı.")
    db.close()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(migrate_stories())
