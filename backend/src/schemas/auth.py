"""Authentication API schema scaffolding for feature 003."""

from __future__ import annotations

from pydantic import BaseModel


class LoginRequest(BaseModel):
    identifier: str
    password: str


class LoginResponse(BaseModel):
    status: str
    user_id: str


class LogoutResponse(BaseModel):
    status: str


class SessionSummary(BaseModel):
    authenticated: bool
    user_id: str
