"""Request and response schemas for JWT bearer authentication."""

from typing import Literal

from pydantic import BaseModel, Field


class TokenPair(BaseModel):
    """Access and refresh tokens returned to an API client."""

    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"


class RefreshTokenRequest(BaseModel):
    """Body accepted by the refresh endpoint."""

    refresh_token: str = Field(min_length=1)


class OAuthExchangeRequest(BaseModel):
    """One-time code received by the frontend after an OAuth redirect."""

    code: str = Field(min_length=1)


class OAuthExchangeRecord(BaseModel):
    """Short-lived server-side record behind an OAuth exchange code."""

    user_id: int
