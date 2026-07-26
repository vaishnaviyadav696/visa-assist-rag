"""Unit tests for the allowlisted HTML fetcher."""

import sys
from pathlib import Path

import httpx
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from visa_assist.html_fetcher import (  # noqa: E402
    DomainNotAllowedError,
    FetchError,
    HtmlFetcher,
    SourceDisabledError,
)
from visa_assist.schemas import OfficialSource, SourceRegistry  # noqa: E402


def make_source(
    *,
    url: str = "https://www.gov.uk/example",
    enabled: bool = True,
) -> OfficialSource:
    """Build a source record for fetcher tests."""
    return OfficialSource(
        source_id="uk_test_source",
        title="UK test source",
        url=url,
        destination_country="GB",
        passport_country="ALL",
        visa_type="standard_visitor",
        content_type="web_page",
        last_verified_at=None,
        enabled=enabled,
    )


def test_fetch_returns_raw_html_and_metadata() -> None:
    """A successful mocked response is returned without parsing."""
    source = make_source()
    registry = SourceRegistry(sources=[source])
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            text="<html><body>Raw content</body></html>",
            headers={"content-type": "text/html; charset=utf-8"},
            request=request,
        )
    )

    result = HtmlFetcher(registry, transport=transport).fetch(source)

    assert result.html == "<html><body>Raw content</body></html>"
    assert result.metadata.source_id == source.source_id
    assert str(result.metadata.url) == str(source.url)
    assert result.metadata.status_code == 200
    assert result.metadata.content_type == "text/html; charset=utf-8"
    assert result.metadata.fetched_at.tzinfo is not None


def test_fetch_retries_timeout_then_succeeds() -> None:
    """Transient timeout failures are retried."""
    source = make_source()
    registry = SourceRegistry(sources=[source])
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise httpx.ReadTimeout("timed out", request=request)
        return httpx.Response(200, text="<html></html>", request=request)

    result = HtmlFetcher(
        registry,
        max_retries=1,
        transport=httpx.MockTransport(handler),
    ).fetch(source)

    assert result.metadata.status_code == 200
    assert attempts == 2


def test_fetch_rejects_domain_not_in_registry() -> None:
    """A source on a domain absent from the registry is rejected locally."""
    allowed_source = make_source()
    disallowed_source = make_source(url="https://example.com/source")
    registry = SourceRegistry(sources=[allowed_source])

    with pytest.raises(DomainNotAllowedError, match="not allowlisted"):
        HtmlFetcher(registry).fetch(disallowed_source)


def test_fetch_rejects_disabled_source() -> None:
    """Disabled registry entries cannot be fetched."""
    source = make_source(enabled=False)
    registry = SourceRegistry(sources=[source])

    with pytest.raises(SourceDisabledError, match="disabled"):
        HtmlFetcher(registry).fetch(source)


def test_fetch_raises_after_timeout_retries_are_exhausted() -> None:
    """Repeated mocked timeouts produce a fetch-specific error."""
    source = make_source()
    registry = SourceRegistry(sources=[source])

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    with pytest.raises(FetchError, match="after 2 attempts"):
        HtmlFetcher(
            registry,
            max_retries=1,
            transport=httpx.MockTransport(handler),
        ).fetch(source)
