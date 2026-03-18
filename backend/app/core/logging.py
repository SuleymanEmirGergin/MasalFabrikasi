"""
Structured JSON Logging Configuration
"""
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict
import traceback


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add any custom extra fields
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName",
                "relativeCreated", "thread", "threadName", "exc_info",
                "exc_text", "stack_info"
            ]:
                if not key.startswith("_"):
                    log_data[key] = value
        
        return json.dumps(log_data, default=str)


def setup_logging(
    level: str = "INFO",
    log_file: str = None,
    use_json: bool = True
) -> logging.Logger:
    """
    Setup structured logging
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for file logging
        use_json: Use JSON formatter (True) or standard (False)
    
    Returns:
        Configured logger
    """
    
    # Create logger
    logger = logging.getLogger("masal_fabrikasi")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    if use_json:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
    
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JSONFormatter() if use_json else logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)
    
    return logger


# Request/Response logging helper
class RequestLogger:
    """Helper for logging HTTP requests"""
    
    @staticmethod
    def log_request(
        logger: logging.Logger,
        method: str,
        path: str,
        request_id: str = None,
        user_id: str = None,
        **kwargs
    ):
        """Log incoming HTTP request"""
        logger.info(
            f"Incoming request: {method} {path}",
            extra={
                "event": "request_started",
                "method": method,
                "path": path,
                "request_id": request_id,
                "user_id": user_id,
                **kwargs
            }
        )
    
    @staticmethod
    def log_response(
        logger: logging.Logger,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        request_id: str = None,
        **kwargs
    ):
        """Log HTTP response"""
        level = logging.INFO if status_code < 400 else logging.WARNING if status_code < 500 else logging.ERROR
        
        logger.log(
            level,
            f"Request completed: {method} {path} - {status_code}",
            extra={
                "event": "request_completed",
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "request_id": request_id,
                **kwargs
            }
        )


# Application-specific loggers
def get_logger(name: str) -> logging.Logger:
    """Get a child logger"""
    return logging.getLogger(f"masal_fabrikasi.{name}")
