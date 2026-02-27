"""
Memory Profiling Endpoint
Provides memory usage statistics for production monitoring
"""
from fastapi import APIRouter, Depends
from typing import Dict
import psutil
import os
import gc

router = APIRouter(prefix="/debug", tags=["Debug"])

@router.get("/memory")
async def get_memory_stats() -> Dict:
    """
    Get current memory usage statistics.
    Use this endpoint to monitor for memory leaks in production.
    """
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    
    # Force garbage collection
    gc.collect()
    
    return {
        "rss_mb": round(mem_info.rss / 1024 / 1024, 2),  # Resident Set Size
        "vms_mb": round(mem_info.vms / 1024 / 1024, 2),  # Virtual Memory Size
        "percent": round(process.memory_percent(), 2),
        "available_mb": round(psutil.virtual_memory().available / 1024 / 1024, 2),
        "total_mb": round(psutil.virtual_memory().total / 1024 / 1024, 2),
        "gc_stats": {
            "collections_gen0": gc.get_count()[0],
            "collections_gen1": gc.get_count()[1],
            "collections_gen2": gc.get_count()[2],
        }
    }

@router.get("/connections")
async def get_connection_stats() -> Dict:
    """
    Get active connection statistics.
    """
    from app.core.socket_manager import socket_manager
    
    return {
        "websocket_connections": socket_manager.active_connections,
        "max_websocket_connections": socket_manager.max_connections,
        "websocket_usage_percent": round(
            (socket_manager.active_connections / socket_manager.max_connections) * 100, 2
        )
    }
