from typing import Dict, List


class SearchFiltersService:
    """
    Gelişmiş filtre/sıralama için sahte sonuç sağlayıcı.
    """

    async def advanced_filter(self, query: str, tags: List[str], sort: str = "relevance") -> Dict:
        return {
            "query": query,
            "tags": tags,
            "sort": sort,
            "results": [{"id": f"s{idx}", "score": 0.9 - idx * 0.1} for idx in range(3)],
        }


