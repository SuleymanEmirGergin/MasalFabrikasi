import json
import os
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from app.core.config import settings
from app.core.database import get_db_context
from app.models import Story
from sqlalchemy import update
from sqlalchemy.future import select

class StoryEnhancementService:
    """
    Unified service for story enhancements (joy, irony, horror, etc.).
    Replaces multiple standalone service files.
    """

    def __init__(self):
        self.config = self._load_config()
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )

    def _load_config(self) -> Dict[str, Any]:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "core", "story_enhancement_config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file not found at {config_path}")
            return {}

    async def process_enhancement(self, story_id: str, enhancement_type: str, current_text: str) -> Dict[str, Any]:
        """
        Applies a specific enhancement to the story.
        """
        if enhancement_type not in self.config:
            raise ValueError(f"Enhancement type '{enhancement_type}' not supported.")

        config = self.config[enhancement_type]
        prompt = config["prompt_template"].replace("{text}", current_text)

        try:
            response = await self.client.chat.completions.create(
                model=config.get("model", "gpt-4"),
                messages=[
                    {"role": "system", "content": config["system_role"]},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.get("temperature", 0.7),
                max_tokens=2000
            )

            enhanced_text = response.choices[0].message.content.strip()

            # Save to Database
            await self._save_to_db(story_id, enhancement_type, enhanced_text)

            return {
                "story_id": story_id,
                "enhancement_type": enhancement_type,
                "enhanced_text": enhanced_text
            }

        except Exception as e:
            print(f"Error processing enhancement {enhancement_type}: {e}")
            raise

    async def _save_to_db(self, story_id: str, enhancement_type: str, result_text: str):
        """
        Updates the story in the database with the enhanced text and metadata.
        """
        async with get_db_context() as session:
            # Fetch story to ensure it exists
            result = await session.execute(select(Story).where(Story.id == story_id))
            story = result.scalar_one_or_none()

            if story:
                # Update story text or store in a separate column/table if preferred
                # For now, we update the main text and add to metadata
                metadata = story.meta_data or {}

                # Update history in metadata
                history = metadata.get("enhancement_history", [])
                history.append({
                    "type": enhancement_type,
                    "timestamp": str(os.getenv("TIMESTAMP", "")), # Simplified timestamp
                    "preview": result_text[:50] + "..."
                })
                metadata["enhancement_history"] = history

                await session.execute(
                    update(Story)
                    .where(Story.id == story_id)
                    .values(
                        story_text=result_text,
                        meta_data=metadata
                    )
                )
                await session.commit()
            else:
                print(f"Story {story_id} not found in DB, skipping save.")

# Singleton instance
story_enhancement_service = StoryEnhancementService()
