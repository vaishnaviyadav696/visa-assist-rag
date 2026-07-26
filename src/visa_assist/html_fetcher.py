"""Download raw HTML from allowlisted official sources."""

from datetime import UTC, datetime

import httpx

from visa_assist.schemas import (
    FetchedHtml,
    FetchMetadata,
    OfficialSource,
    SourceRegistry,
)


class FetchError(RuntimeError):
    """Raised when an official source cannot be fetched safely."""


class DomainNotAllowedError(FetchError):
    """Raised when a source URL is outside the registry domain allowlist."""


class SourceDisabledError(FetchError):
    """Raised when a disabled source is passed to the fetcher."""


class HtmlFetcher:
    """Fetch raw HTML with domain checks, timeouts, and transient retries."""

    def __init__(
        self,
        registry: SourceRegistry,
        *,
        timeout_seconds: float = 10.0,
        max_retries: int = 2,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")
        if max_retries < 0:
            raise ValueError("max_retries cannot be negative")

        self.allowed_domains = frozenset(
            source.url.host.lower()
            for source in registry.sources
            if source.url.host is not None
        )
        self.timeout = httpx.Timeout(timeout_seconds)
        self.max_retries = max_retries
        self.transport = transport

    def fetch(self, source: OfficialSource) -> FetchedHtml:
        """Download a source without parsing or transforming its HTML."""
        if not source.enabled:
            raise SourceDisabledError(f"Source is disabled: {source.source_id}")

        source_domain = source.url.host
        if source_domain is None or source_domain.lower() not in self.allowed_domains:
            raise DomainNotAllowedError(f"Domain is not allowlisted: {source_domain}")

        with httpx.Client(
            timeout=self.timeout,
            transport=self.transport,
            follow_redirects=False,
        ) as client:
            response = self._request_with_retries(client, str(source.url))

        return FetchedHtml(
            html=response.text,
            metadata=FetchMetadata(
                source_id=source.source_id,
                url=str(response.url),
                status_code=response.status_code,
                content_type=response.headers.get("content-type"),
                fetched_at=datetime.now(UTC),
            ),
        )

    def _request_with_retries(
        self,
        client: httpx.Client,
        url: str,
    ) -> httpx.Response:
        attempts = self.max_retries + 1

        for attempt in range(attempts):
            try:
                response = client.get(url)
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                if attempt == self.max_retries:
                    raise FetchError(f"Request failed after {attempts} attempts") from exc
                continue

            if 500 <= response.status_code < 600 and attempt < self.max_retries:
                continue
            if 300 <= response.status_code < 400:
                raise FetchError("Redirect responses are not followed")

            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise FetchError(
                    f"Source returned HTTP {response.status_code}"
                ) from exc

            return response

        raise FetchError("Request failed")
