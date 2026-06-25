"""
Logging configuration
"""
import logging
import sys
import json
from datetime import datetime
import contextvars
import uuid

# Context variable to track request ID across async boundaries
request_id_ctx_var = contextvars.ContextVar('request_id', default=None)

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        
        # Inject request_id if present
        req_id = request_id_ctx_var.get()
        if req_id:
            log_record["request_id"] = req_id
            
        # Add any extra attributes passed to the log record
        if hasattr(record, "extra"):
            if isinstance(record.extra, dict):
                log_record.update(record.extra)
                
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure application structured logging"""
    logger = logging.getLogger("interview_api")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Prevent duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        
    return logger

logger = setup_logging()

def set_request_id(req_id: str = None) -> str:
    """Set the request_id context variable and return it"""
    if not req_id:
        req_id = str(uuid.uuid4())
    request_id_ctx_var.set(req_id)
    return req_id

def get_request_id() -> str:
    """Get the current request_id"""
    return request_id_ctx_var.get()
