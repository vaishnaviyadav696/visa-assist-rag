"""Validated application data models."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class OfficialSource(BaseModel):
    """Metadata for an official immigration information source."""

    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1, pattern=r"^[a-z0-9_]+$")
    title: str = Field(min_length=1)
    url: HttpUrl
    destination_country: str = Field(min_length=2)
    passport_country: str = Field(min_length=2)
    visa_type: str = Field(min_length=1)
    content_type: str = Field(min_length=1)
    last_verified_at: datetime | None
    enabled: bool


class SourceRegistry(BaseModel):
    """Collection of validated official source definitions."""

    model_config = ConfigDict(extra="forbid")

    sources: list[OfficialSource]


class FetchMetadata(BaseModel):
    """Metadata captured while downloading an HTML source."""

    model_config = ConfigDict(extra="forbid")

    source_id: str
    url: HttpUrl
    status_code: int
    content_type: str | None
    fetched_at: datetime


class FetchedHtml(BaseModel):
    """Raw downloaded HTML and its fetch metadata."""

    model_config = ConfigDict(extra="forbid")

    html: str
    metadata: FetchMetadata
