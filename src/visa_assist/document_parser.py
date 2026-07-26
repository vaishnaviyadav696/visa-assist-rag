"""Normalize text from HTML and PDF source documents."""

import re
from collections.abc import Iterable

import pymupdf
from bs4 import BeautifulSoup

from visa_assist.schemas import (
    OfficialSource,
    ParsedDocument,
    ParsedDocumentMetadata,
)


HTML_TEXT_ELEMENTS = (
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "p",
    "li",
    "dt",
    "dd",
    "blockquote",
    "th",
    "td",
)
HTML_HEADING_ELEMENTS = ("h1", "h2", "h3", "h4", "h5", "h6")


class DocumentParseError(ValueError):
    """Raised when source content cannot be parsed into normalized text."""


def parse_html(html: str, source: OfficialSource) -> ParsedDocument:
    """Extract normalized visible text and semantic headings from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    for element in soup(("script", "style", "noscript", "template")):
        element.decompose()

    headings = _normalize_parts(
        element.get_text(" ", strip=True)
        for element in soup.find_all(HTML_HEADING_ELEMENTS)
    )
    text_parts = _normalize_parts(
        element.get_text(" ", strip=True)
        for element in soup.find_all(HTML_TEXT_ELEMENTS)
    )

    return ParsedDocument(
        text="\n".join(text_parts),
        headings=headings,
        metadata=_metadata_from_source(source),
    )


def parse_pdf(pdf: bytes, source: OfficialSource) -> ParsedDocument:
    """Extract normalized text and table-of-contents headings from PDF bytes."""
    try:
        with pymupdf.open(stream=pdf, filetype="pdf") as document:
            text_parts = _normalize_parts(
                page.get_text("text", sort=True) for page in document
            )
            headings = _normalize_parts(item[1] for item in document.get_toc())
            page_count = document.page_count
    except (pymupdf.FileDataError, RuntimeError, ValueError) as exc:
        raise DocumentParseError("Unable to parse PDF document") from exc

    return ParsedDocument(
        text="\n".join(text_parts),
        headings=headings,
        metadata=_metadata_from_source(source, page_count=page_count),
    )


def _normalize_parts(parts: Iterable[str]) -> list[str]:
    normalized: list[str] = []
    for part in parts:
        for line in part.splitlines():
            clean_line = re.sub(r"\s+", " ", line).strip()
            if clean_line:
                normalized.append(clean_line)
    return normalized


def _metadata_from_source(
    source: OfficialSource,
    *,
    page_count: int | None = None,
) -> ParsedDocumentMetadata:
    return ParsedDocumentMetadata(
        source_id=source.source_id,
        title=source.title,
        url=source.url,
        destination_country=source.destination_country,
        passport_country=source.passport_country,
        visa_type=source.visa_type,
        content_type=source.content_type,
        last_verified_at=source.last_verified_at,
        page_count=page_count,
    )
