"""
JSON to PostgreSQL Data Migration Script

Migrates existing data from JSON files to PostgreSQL database.
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal, Base, engine
from app.models.database import User, Story, Character

def migrate_users():
    """Migrate users from JSON to PostgreSQL."""
    print("\n📦 Migrating Users...")
    print("-" * 50)
    
    json_path = Path("data/users.json")
    if not json_path.exists():
        print("   ⏭️  No users.json found, skipping")
        return 0
    
    users_data = json.loads(json_path.read_text())
    db = SessionLocal()
    migrated = 0
    
    try:
        for user_id, user_info in users_data.items():
            # Check if already exists
            existing = db.query(User).filter(User.id == user_id).first()
            if existing:
                print(f"   ⏭️  User {user_id[:8]}... already exists")
                continue
            
            # Create user
            user = User(
                id=user_id,
                username=user_info.get("username", f"user_{user_id[:8]}"),
                email=user_info.get("email"),
                is_premium=user_info.get("is_premium", False),
                credits=user_info.get("credits", 100),
                level=user_info.get("level", 1),
                xp=user_info.get("xp", 0),
            )
            db.add(user)
            migrated += 1
            print(f"   ✅ Migrated user: {user.username}")
        
        db.commit()
        print(f"\n   📊 Total users migrated: {migrated}")
        return migrated
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

def migrate_stories():
    """Migrate stories from JSON to PostgreSQL."""
    print("\n📚 Migrating Stories...")
    print("-" * 50)
    
    json_path = Path("data/stories.json")
    if not json_path.exists():
        print("   ⏭️  No stories.json found, skipping")
        return 0
    
    stories_data = json.loads(json_path.read_text())
    db = SessionLocal()
    migrated = 0
    
    try:
        for story_id, story_info in stories_data.items():
            # Check if already exists
            existing = db.query(Story).filter(Story.id == story_id).first()
            if existing:
                print(f"   ⏭️  Story {story_id[:8]}... already exists")
                continue
            
            # Get or create default user
            user_id = story_info.get("user_id", "default_user")
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                user = User(
                    id=user_id,
                    username="default_user",
                    credits=100,
                    level=1,
                    xp=0
                )
                db.add(user)
                db.flush()
            
            # Create story
            story = Story(
                id=story_id,
                user_id=user_id,
                theme=story_info.get("theme", "Unknown"),
                story_text=story_info.get("story_text", ""),
                language=story_info.get("language", "tr"),
                story_type=story_info.get("story_type", "masal"),
                image_url=story_info.get("image_url"),
                audio_url=story_info.get("audio_url"),
                is_favorite=story_info.get("is_favorite", False),
            )
            db.add(story)
            migrated += 1
            
            if migrated % 10 == 0:
                print(f"   📝 Migrated {migrated} stories...")
        
        db.commit()
        print(f"\n   📊 Total stories migrated: {migrated}")
        return migrated
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

def migrate_characters():
    """Migrate characters from JSON to PostgreSQL."""
    print("\n👤 Migrating Characters...")
    print("-" * 50)
    
    json_path = Path("data/characters.json")
    if not json_path.exists():
        print("   ⏭️  No characters.json found, skipping")
        return 0
    
    chars_data = json.loads(json_path.read_text())
    db = SessionLocal()
    migrated = 0
    
    try:
        for char_id, char_info in chars_data.items():
            # Check if already exists
            existing = db.query(Character).filter(Character.id == char_id).first()
            if existing:
                print(f"   ⏭️  Character {char_id[:8]}... already exists")
                continue
            
            # Get or create default user
            user_id = char_info.get("user_id", "default_user")
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                user = User(
                    id=user_id,
                    username="default_user",
                    credits=100,
                    level=1,
                    xp=0
                )
                db.add(user)
                db.flush()
            
            # Create character
            character = Character(
                id=char_id,
                user_id=user_id,
               name=char_info.get("name", "Unknown"),
                description=char_info.get("description"),
                age=char_info.get("age"),
                personality=char_info.get("personality"),
                appearance=char_info.get("appearance"),
                character_type=char_info.get("character_type", "hero"),
                voice_id=char_info.get("voice_id", "alloy"),
                image_url=char_info.get("image_url"),
            )
            db.add(character)
            migrated += 1
            print(f"   ✅ Migrated character: {character.name}")
        
        db.commit()
        print(f"\n   📊 Total characters migrated: {migrated}")
        return migrated
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

def main():
    """Run migration."""
    print("=" * 60)
    print("🚀 JSON TO POSTGRESQL MIGRATION")
    print("=" * 60)
    
    # Check if database is accessible
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        print("✅ Database connection successful\n")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nMake sure PostgreSQL is running:")
        print("  docker-compose up -d postgres")
        print("\nAnd migrations are applied:")
        print("  alembic upgrade head")
        return 1
    
    # Run migrations
    total_migrated = 0
    total_migrated += migrate_users()
    total_migrated += migrate_stories()
    total_migrated += migrate_characters()
    
    print("\n" + "=" * 60)
    print(f"✅ MIGRATION COMPLETE - {total_migrated} records migrated")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit(main())
