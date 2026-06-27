"""
Observability — Structured JSON Logging + Request IDs.

Replaces print() with structured JSON logs that include:
    - timestamp
    - level (DEBUG | INFO | WARNING | ERROR | CRITICAL)
    - request_id (from context var — unique per HTTP request)
    - service (component name)
    - message
    - extra fields (arbitrary key-value pairs)

Usage:
    from app.core.observability import logger, set_request_id

    logger.info("session_started", session_id=sid, user_id=uid)
    logger.error("llm_failed", model=model, error=str(e))
"""
import json
import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

# Context variable to carry request_id across the async call chain
_request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def set_request_id(request_id: str = "") -> str:
    """Set the request ID for this async context. Generates one if not provided."""
    rid = request_id or str(uuid.uuid4())[:8]
    _request_id_var.set(rid)
    return rid


def get_request_id() -> str:
    return _request_id_var.get() or "-"


class StructuredLogger:
    """
    Emits JSON log lines to stdout.
    Structured logs are machine-parseable by Datadog, Grafana Loki, and ELK.
    """

    def __init__(self, service: str):
        self.service = service

    def _emit(self, level: str, message: str, **kwargs: Any) -> None:
        record = {
            "timestamp":  datetime.now(timezone.utc).isoformat(),
            "level":      level,
            "request_id": get_request_id(),
            "service":    self.service,
            "message":    message,
            **{k: v for k, v in kwargs.items() if v is not None},
        }
        print(json.dumps(record, default=str), file=sys.stdout, flush=True)

    def debug(self, message: str, **kwargs: Any)    -> None: self._emit("DEBUG",    message, **kwargs)
    def info(self, message: str, **kwargs: Any)     -> None: self._emit("INFO",     message, **kwargs)
    def warning(self, message: str, **kwargs: Any)  -> None: self._emit("WARNING",  message, **kwargs)
    def error(self, message: str, **kwargs: Any)    -> None: self._emit("ERROR",    message, **kwargs)
    def critical(self, message: str, **kwargs: Any) -> None: self._emit("CRITICAL", message, **kwargs)


# Shared global logger — import this everywhere
logger = StructuredLogger(service="holistic-interview")
