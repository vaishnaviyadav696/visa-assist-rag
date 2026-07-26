"""Unit tests for boundary-aware document chunking."""

import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from visa_assist.document_chunker import chunk_document  # noqa: E402
from visa_assist.schemas import (  # noqa: E402
    ParsedDocument,
    ParsedDocumentMetadata,
)


@pytest.fixture
def metadata() -> ParsedDocumentMetadata:
    """Return source metadata that every produced chunk must retain."""
    return ParsedDocumentMetadata(
        source_id="uk_standard_visitor_test",
        title="UK Standard Visitor visa",
        url="https://www.gov.uk/standard-visitor",
        destination_country="GB",
        passport_country="ALL",
        visa_type="standard_visitor",
        content_type="web_page",
        last_verified_at=None,
    )


def test_short_document_stays_in_one_chunk(
    metadata: ParsedDocumentMetadata,
) -> None:
    """A short document remains intact with headings and metadata."""
    document = ParsedDocument(
        text="Standard Visitor visa\nApply online before travelling.",
        headings=["Standard Visitor visa"],
        metadata=metadata,
    )

    chunks = chunk_document(document)

    assert len(chunks) == 1
    assert chunks[0].text == document.text
    assert chunks[0].headings == document.headings
    assert chunks[0].metadata == metadata
    assert chunks[0].token_count == 7


def test_long_document_uses_target_sizes_and_overlap(
    metadata: ParsedDocumentMetadata,
) -> None:
    """Long content stays bounded and carries a 64-token overlap."""
    paragraphs = [
        " ".join(f"section{section}_word{word}" for word in range(100))
        for section in range(12)
    ]
    document = ParsedDocument(
        text="\n".join(paragraphs),
        headings=[],
        metadata=metadata,
    )

    chunks = chunk_document(document)

    assert len(chunks) > 1
    assert all(300 <= chunk.token_count <= 500 for chunk in chunks[:-1])
    assert chunks[-1].token_count <= 500
    assert len({chunk.chunk_id for chunk in chunks}) == len(chunks)
    assert all(chunk.metadata == metadata for chunk in chunks)
    for previous, current in zip(chunks, chunks[1:]):
        assert previous.text.split()[-64:] == current.text.split()[:64]


def test_chunker_prefers_heading_boundary(
    metadata: ParsedDocumentMetadata,
) -> None:
    """A heading starts a new chunk once the current chunk reaches 300 tokens."""
    introduction = " ".join(f"intro{index}" for index in range(320))
    body = " ".join(f"body{index}" for index in range(100))
    heading = "Eligibility requirements"
    document = ParsedDocument(
        text=f"{introduction}\n{heading}\n{body}",
        headings=[heading],
        metadata=metadata,
    )

    chunks = chunk_document(document)

    assert len(chunks) == 2
    assert chunks[1].headings == [heading]
    assert heading in chunks[1].text


@pytest.mark.parametrize(
    ("option", "value", "message"),
    (
        ("target_tokens", 299, "between 300 and 500"),
        ("target_tokens", 501, "between 300 and 500"),
        ("overlap_tokens", 49, "between 50 and 80"),
        ("overlap_tokens", 81, "between 50 and 80"),
    ),
)
def test_chunker_rejects_values_outside_required_ranges(
    metadata: ParsedDocumentMetadata,
    option: str,
    value: int,
    message: str,
) -> None:
    """Chunk sizing options remain within the required ranges."""
    document = ParsedDocument(text="content", headings=[], metadata=metadata)

    with pytest.raises(ValueError, match=message):
        chunk_document(document, **{option: value})
