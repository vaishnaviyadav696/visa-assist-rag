"""Unit tests for local HTML and PDF document parsing."""

import sys
from pathlib import Path

import pymupdf
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures"
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from visa_assist.document_parser import (  # noqa: E402
    DocumentParseError,
    parse_html,
    parse_pdf,
)
from visa_assist.schemas import OfficialSource  # noqa: E402


@pytest.fixture
def source() -> OfficialSource:
    """Return source metadata shared by local parsing fixtures."""
    return OfficialSource(
        source_id="uk_standard_visitor_test",
        title="UK Standard Visitor visa",
        url="https://www.gov.uk/standard-visitor",
        destination_country="GB",
        passport_country="ALL",
        visa_type="standard_visitor",
        content_type="web_page",
        last_verified_at=None,
        enabled=True,
    )


@pytest.fixture
def sample_pdf() -> bytes:
    """Build a local in-memory PDF fixture with a heading and body text."""
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Standard Visitor visa", fontsize=18)
    page.insert_text((72, 110), "Bring a valid passport.", fontsize=11)
    document.set_toc([[1, "Standard Visitor visa", 1]])
    content = document.tobytes()
    document.close()
    return content


def test_parse_html_fixture(source: OfficialSource) -> None:
    """HTML parsing returns normalized visible text and headings."""
    html = (FIXTURE_DIR / "sample.html").read_text(encoding="utf-8")

    result = parse_html(html, source)

    assert result.headings == ["Standard Visitor visa", "What you need"]
    assert result.text == "\n".join(
        (
            "Standard Visitor visa",
            "You can visit the UK for tourism.",
            "What you need",
            "A valid passport",
            "Evidence of your plans",
        )
    )
    assert "window.tracking" not in result.text
    assert result.metadata.source_id == source.source_id
    assert result.metadata.page_count is None


def test_parse_pdf_fixture(source: OfficialSource, sample_pdf: bytes) -> None:
    """PDF parsing returns normalized page text, headings, and page metadata."""
    pdf_source = source.model_copy(update={"content_type": "pdf"})

    result = parse_pdf(sample_pdf, pdf_source)

    assert result.headings == ["Standard Visitor visa"]
    assert result.text == "Standard Visitor visa\nBring a valid passport."
    assert result.metadata.content_type == "pdf"
    assert result.metadata.page_count == 1


def test_parse_pdf_rejects_invalid_fixture(source: OfficialSource) -> None:
    """Invalid local PDF bytes produce a parser-specific error."""
    with pytest.raises(DocumentParseError, match="Unable to parse PDF"):
        parse_pdf(b"not a pdf", source)
