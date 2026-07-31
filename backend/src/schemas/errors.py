"""`ProblemDetail` error schema (T013).

RFC 7807-style structured error payload used across all API error responses so clients
get a consistent, machine-readable error shape (validation errors, rate-limit 429s,
edit-lock 409s, etc.).
"""

from pydantic import BaseModel, Field


class ProblemDetail(BaseModel):
    type: str = Field(default="about:blank", description="URI reference identifying the error type")
    title: str = Field(description="Short, human-readable summary of the problem")
    status: int = Field(description="HTTP status code")
    detail: str | None = Field(
        default=None, description="Human-readable explanation specific to this occurrence"
    )
    instance: str | None = Field(
        default=None, description="URI reference identifying this specific occurrence"
    )
    errors: dict[str, list[str]] | None = Field(
        default=None, description="Field-level validation errors, keyed by field name"
    )
