"""
Database Query Performance Monitor
Logs slow queries for debugging and optimization
"""
import logging
import time
from sqlalchemy import event
from sqlalchemy.engine import Engine

logger = logging.getLogger("query_performance")

# Set threshold for slow queries (in seconds)
SLOW_QUERY_THRESHOLD = 1.0


def setup_query_logging(engine: Engine):
    """Setup query performance logging on SQLAlchemy engine."""
    
    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault("query_start_time", []).append(time.time())
    
    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total_time = time.time() - conn.info["query_start_time"].pop(-1)
        
        if total_time > SLOW_QUERY_THRESHOLD:
            logger.warning(
                f"⚠️ SLOW QUERY ({total_time:.2f}s): {statement[:200]}..."
            )
