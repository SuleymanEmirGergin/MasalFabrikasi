"""
Pagination Utility - Cursor-based and offset-based pagination
"""
from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Query
from math import ceil

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = 1
    page_size: int = 20
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    
    class Config:
        arbitrary_types_allowed = True


def paginate(
    query: Query,
    page: int = 1,
    page_size: int = 20,
    max_page_size: int = 100
) -> tuple:
    """
    Paginate a SQLAlchemy query
    
    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        page_size: Items per page
        max_page_size: Maximum allowed page size
    
    Returns:
        Tuple of (items, total_count, page, page_size, total_pages)
    """
    # Validate and cap page_size
    page_size = min(page_size, max_page_size)
    page = max(1, page)
    
    # Get total count
    total = query.count()
    
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Get items
    items = query.offset(offset).limit(page_size).all()
    
    # Calculate total pages
    total_pages = ceil(total / page_size) if total > 0 else 1
    
    return items, total, page, page_size, total_pages


def create_paginated_response(
    items: List[T],
    total: int,
    page: int,
    page_size: int
) -> dict:
    """
    Create a standardized paginated response
    
    Returns:
        Dictionary with pagination metadata
    """
    total_pages = ceil(total / page_size) if total > 0 else 1
    
    return {
        "items": items,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }
