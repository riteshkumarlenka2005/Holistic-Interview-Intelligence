"""
Telemetry — Request Tracking + LLM Cost Tracking.

Tracks:
    - Request latency per endpoint
    - LLM model usage and estimated token costs
    - WebSocket frame processing rates

All metrics are exposed on the /metrics endpoint (Prometheus format via prometheus_client).
Cost tracking records model name, input tokens, and output tokens per call.

Usage (latency):
    from app.core.telemetry import telemetry

    with telemetry.track_latency("llm_evaluation"):
        result = await llm.generate_json(...)

Usage (LLM cost):
    telemetry.record_llm_call(
        model="gemini/gemini-2.5-flash",
        input_tokens=450,
        output_tokens=120,
        task="technical_evaluation",
    )
"""
import time
from contextlib import contextmanager
from typing import Dict, Optional
from datetime import datetime, timezone

try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


# LLM cost estimates (USD per 1M tokens) — approximate, update as pricing changes
LLM_COST_PER_1M_TOKENS: Dict[str, Dict[str, float]] = {
    "gemini/gemini-2.5-flash": {"input": 0.075, "output": 0.30},
    "gemini/gemini-2.5-pro":   {"input": 1.25,  "output": 5.00},
    "gemini/gemini-2.0-flash": {"input": 0.075, "output": 0.30},
    "gpt-4o-mini":             {"input": 0.15,  "output": 0.60},
    "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.00},
}


class Telemetry:
    def __init__(self):
        self._latency_records: Dict[str, list] = {}
        self._llm_calls: list = []
        self._total_llm_cost_usd: float = 0.0
        self._session_count: int = 0
        self._ws_frames_processed: int = 0

        # Prometheus metrics (if available)
        if PROMETHEUS_AVAILABLE:
            self._llm_latency = Histogram(
                "llm_request_duration_seconds",
                "LLM request duration",
                labelnames=["model", "task"],
            )
            self._endpoint_latency = Histogram(
                "http_request_duration_seconds",
                "HTTP endpoint latency",
                labelnames=["endpoint"],
            )
            self._llm_cost_counter = Counter(
                "llm_estimated_cost_usd_total",
                "Estimated cumulative LLM cost in USD",
                labelnames=["model"],
            )
            self._active_sessions = Gauge(
                "active_interview_sessions",
                "Number of currently active interview sessions",
            )

    @contextmanager
    def track_latency(self, label: str):
        """Context manager to measure and record latency of a code block."""
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            self._latency_records.setdefault(label, []).append(elapsed)
            if PROMETHEUS_AVAILABLE and hasattr(self, "_endpoint_latency"):
                self._endpoint_latency.labels(endpoint=label).observe(elapsed)

    def record_llm_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        task: str,
        latency_seconds: Optional[float] = None,
    ) -> float:
        """
        Records an LLM API call and estimates its cost.
        Returns the estimated cost for this call in USD.
        """
        costs = LLM_COST_PER_1M_TOKENS.get(model, {"input": 0.15, "output": 0.60})
        cost = (input_tokens / 1_000_000) * costs["input"] + \
               (output_tokens / 1_000_000) * costs["output"]

        self._total_llm_cost_usd += cost
        self._llm_calls.append({
            "timestamp":      datetime.now(timezone.utc).isoformat(),
            "model":          model,
            "task":           task,
            "input_tokens":   input_tokens,
            "output_tokens":  output_tokens,
            "cost_usd":       round(cost, 6),
            "latency_s":      latency_seconds,
        })

        if PROMETHEUS_AVAILABLE and hasattr(self, "_llm_cost_counter"):
            self._llm_cost_counter.labels(model=model).inc(cost)

        return round(cost, 6)

    def increment_session(self) -> None:
        self._session_count += 1
        if PROMETHEUS_AVAILABLE and hasattr(self, "_active_sessions"):
            self._active_sessions.inc()

    def decrement_session(self) -> None:
        if PROMETHEUS_AVAILABLE and hasattr(self, "_active_sessions"):
            self._active_sessions.dec()

    def increment_ws_frames(self, count: int = 1) -> None:
        self._ws_frames_processed += count

    def get_summary(self) -> Dict:
        """Returns telemetry summary for the /system/telemetry endpoint."""
        latency_summary = {}
        for label, times in self._latency_records.items():
            if times:
                latency_summary[label] = {
                    "avg_ms":  round(sum(times) / len(times) * 1000, 2),
                    "max_ms":  round(max(times) * 1000, 2),
                    "calls":   len(times),
                }

        return {
            "total_llm_calls":        len(self._llm_calls),
            "total_llm_cost_usd":     round(self._total_llm_cost_usd, 4),
            "total_sessions":         self._session_count,
            "ws_frames_processed":    self._ws_frames_processed,
            "latency":                latency_summary,
            "recent_llm_calls":       self._llm_calls[-10:],  # last 10 calls
        }


# Shared singleton
telemetry = Telemetry()
