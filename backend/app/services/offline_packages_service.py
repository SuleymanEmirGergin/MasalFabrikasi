from typing import Dict, List


class OfflinePackagesService:
    """
    Çevrimdışı paket hazırlama için basit listeleyici.
    """

    async def build_package(self, story_ids: List[str]) -> Dict:
        return {
            "stories": story_ids,
            "assets": [f"/storage/assets/{sid}.zip" for sid in story_ids],
            "status": "ready",
        }


