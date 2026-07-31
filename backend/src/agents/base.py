"""Shared agent wrapper base (used by T054, T106, T107).

Constitution II/V: agents enrich explanations/narration but never make the underlying
policy decision, and their output must be auditable/testable independent of LLM
behavior (Constitution III, harness-first). Each concrete explainer:

1. Accepts the deterministic factors already computed by domain logic.
2. Attempts to enrich them into human-readable narration via Microsoft Agent Framework
   (MAF) + Copilot SDK, if configured/available.
3. Falls back to a deterministic, template-based narration when the agent runtime is not
   configured (e.g. local dev without credentials, or the package is not installed) so
   the API never fails or blocks a business decision because of agent-layer issues.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.infrastructure.observability import get_logger

logger = get_logger(__name__)


class ExplanationAgent(ABC):
    """Common interface for MAF/Copilot SDK-backed explanation agents."""

    @abstractmethod
    def explain(self, factors: dict[str, Any]) -> str:
        """Return a human-readable narration for the given deterministic factors."""


class DeterministicFallbackExplainer(ExplanationAgent):
    """Template-based narration used when the MAF/Copilot SDK runtime is unavailable."""

    def __init__(self, template: str) -> None:
        self._template = template

    def explain(self, factors: dict[str, Any]) -> str:
        try:
            return self._template.format(**factors)
        except (KeyError, IndexError):
            return f"Contributing factors: {factors}"


def try_load_maf_agent(*, name: str, instructions: str) -> Any | None:
    """Best-effort import of Microsoft Agent Framework. Returns None if unavailable so
    callers can fall back to deterministic narration instead of failing the request."""
    try:
        from agent_framework import ChatAgent  # type: ignore[import-not-found]
    except ImportError:
        logger.info(
            "agent_framework not installed; using deterministic fallback narration",
            extra={"context": {"agent_name": name}},
        )
        return None

    try:
        return ChatAgent(name=name, instructions=instructions)
    except Exception:
        logger.exception(
            "Failed to initialize MAF agent; using deterministic fallback narration",
            extra={"context": {"agent_name": name}},
        )
        return None
