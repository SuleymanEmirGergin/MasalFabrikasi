"""
Search Service - Semantic search using Gemini embeddings (google-genai)
"""
from sqlalchemy.orm import Session
from app.models import Story
from typing import List
from google import genai
from google.genai import types
from app.core.config import settings
from sqlalchemy import text


class SearchService:
    def __init__(self, db: Session):
        self.db = db
        self.client = None
        
        # Configure Gemini client for embeddings
        if settings.EMBEDDING_API_KEY:
            self.client = genai.Client(api_key=settings.EMBEDDING_API_KEY)
        
    def update_story_embedding(self, story_id: str):
        """
        Generate and store embedding for a story using Gemini.
        """
        if not self.client:
            print("Embedding client not configured.")
            return

        try:
            story = self.db.query(Story).filter(Story.id == story_id).first()
            if not story:
                return
            
            # Gemini embedding API (new google-genai syntax)
            response = self.client.models.embed_content(
                model=settings.EMBEDDING_MODEL,
                contents=story.story_text[:8000],
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT"
                )
            )
            
            embedding = response.embeddings[0].values
            
            # Store embedding in database
            story.embedding = embedding
            self.db.commit()
            
            print(f"✅ Embedding generated and saved for story {story_id} using {settings.EMBEDDING_MODEL}")
        except Exception as e:
            print(f"❌ Embedding generation failed: {e}")
            self.db.rollback()
    
    def search_stories(self, query: str, limit: int = 5) -> List[Story]:
        """
        Semantic search using vector similarity with Gemini embeddings.
        """
        if not self.client:
            # Fallback to simple text search
            print("⚠️ Embedding not configured, using text search fallback")
            return self.db.query(Story).filter(Story.story_text.ilike(f"%{query}%")).limit(limit).all()

        try:
            # Generate query embedding
            response = self.client.models.embed_content(
                model=settings.EMBEDDING_MODEL,
                contents=query,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_QUERY"
                )
            )
            query_embedding = response.embeddings[0].values
            
            # Vector similarity search using pgvector cosine distance
            # <=> is the cosine distance operator in pgvector
            # Lower distance = more similar
            results = self.db.query(Story).filter(
                Story.embedding.isnot(None)
            ).order_by(
                text(f"embedding <=> '{query_embedding}'")
            ).limit(limit).all()
            
            print(f"✅ Found {len(results)} similar stories for query: '{query[:50]}...'")
            return results
            
        except Exception as e:
            print(f"❌ Vector search failed: {e}, falling back to text search")
            # Fallback to text search
            return self.db.query(Story).filter(
                Story.story_text.ilike(f"%{query}%")
            ).limit(limit).all()
    
    def update_all_embeddings(self, batch_size: int = 10):
        """
        Batch update embeddings for all stories that don't have one.
        Useful for initial setup or migration.
        """
        if not self.client:
            print("❌ Embedding client not configured")
            return 0
        
        stories_without_embedding = self.db.query(Story).filter(
            Story.embedding.is_(None)
        ).limit(batch_size).all()
        
        updated_count = 0
        for story in stories_without_embedding:
            try:
                self.update_story_embedding(str(story.id))
                updated_count += 1
            except Exception as e:
                print(f"⚠️ Failed to update embedding for story {story.id}: {e}")
                continue
        
        print(f"✅ Updated {updated_count}/{len(stories_without_embedding)} story embeddings")
        return updated_count
