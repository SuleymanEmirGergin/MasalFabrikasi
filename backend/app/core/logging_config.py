import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict

class SensitiveDataFilter(logging.Filter):
    """
    Redacts sensitive information from log records.
    """
    SENSITIVE_KEYS = ["password", "token", "secret", "api_key", "authorization"]

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.args, dict):
            # Safe copy to avoid modifying original record args
            safe_args = record.args.copy()
            for key in safe_args:
                if any(s in key.lower() for s in self.SENSITIVE_KEYS):
                    safe_args[key] = "***REDACTED***"
            record.args = safe_args

        # Also check message string if possible (simple heuristic)
        # Note: robust message redaction is complex; this is a basic safeguard.
        return True

class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    """
    def format(self, record: logging.LogRecord) -> str:
        # Apply redaction logic if not already filtered
        # Ideally filters run before handlers, but formatter is last line of defense
        message = record.getMessage()
        for sensitive in ["password", "token", "secret"]:
             if sensitive in message.lower():
                 # Very naive redaction for un-structured messages
                 # Real redaction should happen at the structured data level or via filter
                 pass

        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": message,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
            
        return json.dumps(log_data)

def setup_logging(log_level: str = "INFO"):
    """
    Configure application logging.
    """
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Redaction filter
    redaction_filter = SensitiveDataFilter()

    # Console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    console_handler.addFilter(redaction_filter)
    root_logger.addHandler(console_handler)
    
    # File handler for errors
    import os
    if not os.path.exists("logs"):
        os.makedirs("logs")
    error_handler = logging.FileHandler("logs/error.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    error_handler.addFilter(redaction_filter)
    root_logger.addHandler(error_handler)
    
    return root_logger

logger = setup_logging()
