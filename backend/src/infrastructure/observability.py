"""Structured logging, metrics, and tracing baseline (T017).

A lightweight, dependency-free baseline: JSON structured logs via stdlib `logging`, plus
an in-process metrics registry. Production deployments should wire an OpenTelemetry
exporter (e.g. to Azure Monitor) at the `configure_observability()` call site without
changing call sites elsewhere in the codebase.
"""

from __future__ import annotations

import json
import logging
import sys
import time
from collections import defaultdict
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        extra = getattr(record, "context", None)
        if extra:
            payload["context"] = extra
        return json.dumps(payload)


def configure_observability(level: int = logging.INFO) -> None:
    """Configure the root logger to emit structured JSON logs. Call once at startup."""
    root = logging.getLogger()
    root.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_JsonFormatter())
    root.handlers = [handler]


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


class MetricsRegistry:
    """Minimal in-process counters/timers. Not a substitute for a real metrics backend
    in production, but gives every domain module a consistent place to emit signal that
    can be swapped for an Azure Monitor/OpenTelemetry exporter later."""

    def __init__(self) -> None:
        self._counters: dict[str, int] = defaultdict(int)
        self._timings_ms: dict[str, list[float]] = defaultdict(list)

    def increment(self, metric: str, value: int = 1) -> None:
        self._counters[metric] += value

    def record_timing_ms(self, metric: str, milliseconds: float) -> None:
        self._timings_ms[metric].append(milliseconds)

    @contextmanager
    def timer(self, metric: str) -> Iterator[None]:
        start = time.perf_counter()
        try:
            yield
        finally:
            self.record_timing_ms(metric, (time.perf_counter() - start) * 1000)

    def snapshot(self) -> dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "timings_ms": {k: list(v) for k, v in self._timings_ms.items()},
        }


metrics = MetricsRegistry()
