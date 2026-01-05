from typing import Dict, List


class AdvancedVisualPipelineService:
    """
    Storyboard ve çoklu kare önerisi için sahte pipeline.
    """

    async def generate_storyboard(self, story_text: str, frames: int = 4) -> Dict:
        items: List[Dict] = []
        parts = story_text.split(".")
        for idx in range(min(frames, len(parts))):
            snippet = parts[idx].strip() or f"Sahne {idx + 1}"
            items.append(
                {
                    "frame": idx + 1,
                    "prompt": f"Sahne {idx + 1}: {snippet[:120]}",
                    "style": "storybook",
                    "resolution": "1024x1024",
                }
            )
        return {"frames": items}


