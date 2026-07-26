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


class ParsedDocumentMetadata(BaseModel):
    """Source metadata retained with normalized document text."""

    model_config = ConfigDict(extra="forbid")

    source_id: str
    title: str
    url: HttpUrl
    destination_country: str
    passport_country: str
    visa_type: str
    content_type: str
    last_verified_at: datetime | None
    page_count: int | None = None


class ParsedDocument(BaseModel):
    """Normalized text and headings extracted from one source document."""

    model_config = ConfigDict(extra="forbid")

    text: str
    headings: list[str]
    metadata: ParsedDocumentMetadata


class DocumentChunk(BaseModel):
    """A bounded text segment retaining its source document metadata."""

    model_config = ConfigDict(extra="forbid")

    chunk_id: str
    text: str
    token_count: int = Field(ge=1)
    headings: list[str]
    metadata: ParsedDocumentMetadata
