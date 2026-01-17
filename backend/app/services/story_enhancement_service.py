from typing import Dict, Optional, Any
from openai import OpenAI
from app.core.config import settings
from app.core.story_enhancement_config import STORY_ENHANCEMENT_CONFIG
import json
import uuid
import logging
import re

logger = logging.getLogger(__name__)

class StoryEnhancementService:
    """
    Unified service for story enhancements, replacements, and analysis.
    Replaces hundreds of individual service classes.
    """

    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)

    async def process(self, feature_key: str, story_text: str, **kwargs) -> Dict:
        """
        Process a story enhancement request.

        Args:
            feature_key: The key in STORY_ENHANCEMENT_CONFIG (e.g., 'amazement-enhancer')
            story_text: The content of the story
            **kwargs: Additional arguments needed for the specific prompt (e.g., target_age, style)
        """
        if feature_key not in STORY_ENHANCEMENT_CONFIG:
            raise ValueError(f"Feature '{feature_key}' is not configured.")

        config = STORY_ENHANCEMENT_CONFIG[feature_key]
        system_role = config["system_role"]
        prompt_template = config["prompt_template"]

        # Prepare context for template evaluation
        context = kwargs.copy()
        context['story_text'] = story_text
        # Support templates that use 'session' dict
        context['session'] = kwargs

        # Helper dictionaries with defaults to restore functionality
        # These map parameters to specific prompt instructions
        defaults = {
            'style_descriptions': {
                'fantasy': 'Fantasik ve büyülü bir anlatım', 'sci-fi': 'Bilim kurgu ve fütüristik',
                'mystery': 'Gizemli ve merak uyandıran', 'horror': 'Korku ve gerilim dolu',
                'romance': 'Romantik ve duygusal', 'adventure': 'Macera dolu',
                'comedy': 'Komik ve eğlenceli', 'drama': 'Dramatik ve ciddi'
            },
            'tone_descriptions': {
                'happy': 'Mutlu ve neşeli', 'sad': 'Üzgün ve melankolik',
                'excited': 'Heyecanlı ve coşkulu', 'calm': 'Sakin ve huzurlu',
                'tense': 'Gergin ve stresli', 'hopeful': 'Umutlu ve iyimser',
                'dark': 'Karanlık ve karamsar'
            },
            'format_instructions': {
                'script': 'Senaryo formatında', 'poem': 'Şiir formatında',
                'blog': 'Blog yazısı formatında', 'news': 'Haber formatında',
                'diary': 'Günlük formatında'
            },
            'expansion_prompts': {
                'general': 'Genel olarak genişlet', 'descriptive': 'Betimlemeleri artır',
                'dialogue': 'Diyalog ekle'
            },
            'conflict_descriptions': {
                'internal': 'İç çatışma', 'external': 'Dış çatışma', 'nature': 'Doğa ile çatışma'
            },
            'level_descriptions': {
                'low': 'Düşük seviye', 'medium': 'Orta seviye', 'high': 'Yüksek seviye'
            },
            'time_descriptions': {
                'past': 'Geçmiş zaman', 'present': 'Şimdiki zaman', 'future': 'Gelecek zaman'
            },
            'enhancement_descriptions': {
                'description': 'Betimleme', 'dialogue': 'Diyalog', 'pacing': 'Tempo'
            },
            'ending_descriptions': {
                'happy': 'Mutlu son', 'sad': 'Hüzünlü son',
                'cliffhanger': 'Merak uyandıran son', 'open': 'Açık uçlu son'
            },
            'mystery_descriptions': {
                'crime': 'Suç gizemi', 'supernatural': 'Doğaüstü gizem'
            },
            'perspective_descriptions': {
                'first': 'Birinci şahıs', 'third': 'Üçüncü şahıs'
            },
            'format_styles': {
                'standard': 'Standart', 'modern': 'Modern', 'classic': 'Klasik'
            },
            'enrichment_prompts': {
                'descriptive': 'Betimleyici', 'emotional': 'Duygusal'
            },
            'style_instructions': {
                'creative': 'Yaratıcı', 'formal': 'Resmi', 'casual': 'Günlük'
            },
            'length_instructions': {
                'short': 'Kısa', 'medium': 'Orta', 'long': 'Uzun'
            },
            'resolution_descriptions': {
                'positive': 'Olumlu çözüm', 'negative': 'Olumsuz çözüm'
            },
            'entertainment_descriptions': {
                'humor': 'Mizah', 'action': 'Aksiyon'
            }
        }

        for key, value in defaults.items():
            if key not in context:
                context[key] = value

        # Construct the prompt
        try:
            # We treat the template from config as the body of an f-string.
            # We evaluate it within the context.
            # Note: prompt_template in config is the string representation, so we wrap it in f"""..."""

            # Escape existing braces if they are meant to be literal?
            # The regex extraction captured the string content.
            # If the original was f"Hello {name}", we captured "Hello {name}".
            # So eval(f'f"""Hello {name}"""') works.

            # Use three quotes to handle multiline strings safely
            expression = f'f"""{prompt_template}"""'
            prompt = eval(expression, {}, context)

        except Exception as e:
            logger.warning(f"Template evaluation failed for {feature_key}: {e}. Falling back to simple replacement.")
            # Fallback: simple text replacement for story_text
            prompt = prompt_template.replace("{story_text}", story_text)

        # Call OpenAI
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_role},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            result_text = response.choices[0].message.content

            # Attempt JSON parsing if it looks like JSON
            if result_text.strip().startswith("{") or "JSON" in system_role or "JSON" in prompt:
                try:
                    # Clean markdown code blocks
                    clean_text = result_text
                    if "```json" in clean_text:
                        match = re.search(r"```json\n(.*?)\n```", clean_text, re.DOTALL)
                        if match:
                            clean_text = match.group(1)
                    elif "```" in clean_text:
                        match = re.search(r"```\n(.*?)\n```", clean_text, re.DOTALL)
                        if match:
                            clean_text = match.group(1)

                    parsed_json = json.loads(clean_text)
                    return {
                        "id": str(uuid.uuid4()),
                        "feature": feature_key,
                        "result": parsed_json
                    }
                except json.JSONDecodeError:
                    pass # Not valid JSON, return text

            return {
                "id": str(uuid.uuid4()),
                "feature": feature_key,
                "result": result_text
            }

        except Exception as e:
            logger.error(f"OpenAI call failed for {feature_key}: {e}")
            raise e
