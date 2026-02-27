from typing import List, Dict, Any, Optional
from math import ceil

class PaginationHelper:
    """
    Utility for consistent pagination across the application.
    """
    
    @staticmethod
    def paginate(items: List[Any], page: int = 1, per_page: int = 20) -> Dict:
        """
        Paginate a list of items.
        
        Args:
            items: List of items to paginate
            page: Current page number (1-indexed)
            per_page: Items per page
            
        Returns:
            Dictionary with paginated data and metadata
        """
        total_items = len(items)
        total_pages = ceil(total_items / per_page) if total_items > 0 else 1
        
        # Validate page number
        page = max(1, min(page, total_pages))
        
        # Calculate slice indices
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        paginated_items = items[start_idx:end_idx]
        
        return {
            "items": paginated_items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }

class QueryOptimizer:
    """
    Query optimization utilities.
    """
    
    @staticmethod
    def optimize_sort(items: List[Dict], sort_by: str, reverse: bool = False) -> List[Dict]:
        """
        Optimize sorting for common patterns.
        """
        sort_field = sort_by
        
        # Map common sort patterns
        sort_map = {
            "date_desc": ("created_at", True),
            "date_asc": ("created_at", False),
            "alpha_asc": ("theme", False),
            "alpha_desc": ("theme", True),
        }
        
        if sort_by in sort_map:
            sort_field, reverse = sort_map[sort_by]
        
        try:
            return sorted(items, key=lambda x: x.get(sort_field, ""), reverse=reverse)
        except:
            return items
    
    @staticmethod
    def optimize_filter(items: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """
        Apply filters efficiently.
        """
        filtered = items
        
        for key, value in filters.items():
            if value is not None:
                if isinstance(value, bool):
                    filtered = [item for item in filtered if item.get(key) == value]
                elif isinstance(value, str):
                    # Case-insensitive search
                    filtered = [
                        item for item in filtered 
                        if value.lower() in str(item.get(key, "")).lower()
                    ]
                else:
                    filtered = [item for item in filtered if item.get(key) == value]
        
        return filtered

# Export utilities
__all__ = ['PaginationHelper', 'QueryOptimizer']
