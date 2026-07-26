"""Split parsed documents into overlapping, boundary-aware text chunks."""

import hashlib
import re

from visa_assist.schemas import DocumentChunk, ParsedDocument


MIN_TARGET_TOKENS = 300
MAX_TARGET_TOKENS = 500
MIN_OVERLAP_TOKENS = 50
MAX_OVERLAP_TOKENS = 80
DEFAULT_TARGET_TOKENS = 400
DEFAULT_OVERLAP_TOKENS = 64


def chunk_document(
    document: ParsedDocument,
    *,
    target_tokens: int = DEFAULT_TARGET_TOKENS,
    overlap_tokens: int = DEFAULT_OVERLAP_TOKENS,
) -> list[DocumentChunk]:
    """Chunk a parsed document while preferring headings and paragraph lines."""
    if not MIN_TARGET_TOKENS <= target_tokens <= MAX_TARGET_TOKENS:
        raise ValueError("target_tokens must be between 300 and 500")
    if not MIN_OVERLAP_TOKENS <= overlap_tokens <= MAX_OVERLAP_TOKENS:
        raise ValueError("overlap_tokens must be between 50 and 80")
    if overlap_tokens >= target_tokens:
        raise ValueError("overlap_tokens must be smaller than target_tokens")

    paragraphs = [line.strip() for line in document.text.splitlines() if line.strip()]
    if not paragraphs:
        return []

    heading_set = set(document.headings)
    drafts: list[tuple[str, list[str]]] = []
    current_lines: list[str] = []
    current_tokens: list[str] = []
    current_headings: list[str] = []

    def emit(*, keep_overlap: bool) -> None:
        nonlocal current_lines, current_tokens, current_headings
        if not current_tokens:
            return

        drafts.append(("\n".join(current_lines), current_headings.copy()))
        if keep_overlap:
            overlap = current_tokens[-overlap_tokens:]
            current_tokens = overlap.copy()
            current_lines = [" ".join(overlap)]
            current_headings = []
        else:
            current_tokens = []
            current_lines = []
            current_headings = []

    for paragraph in paragraphs:
        paragraph_tokens = _tokens(paragraph)
        if not paragraph_tokens:
            continue

        is_heading = paragraph in heading_set
        if is_heading and len(current_tokens) >= MIN_TARGET_TOKENS:
            emit(keep_overlap=True)
        elif (
            len(current_tokens) >= MIN_TARGET_TOKENS
            and len(current_tokens) + len(paragraph_tokens) > target_tokens
        ):
            emit(keep_overlap=True)

        remaining = paragraph_tokens
        while remaining:
            capacity = MAX_TARGET_TOKENS - len(current_tokens)
            if capacity == 0:
                emit(keep_overlap=True)
                capacity = MAX_TARGET_TOKENS - len(current_tokens)

            part = remaining[:capacity]
            remaining = remaining[capacity:]
            current_tokens.extend(part)
            current_lines.append(" ".join(part))
            if is_heading and not current_headings:
                current_headings.append(paragraph)

            if remaining:
                emit(keep_overlap=True)

    emit(keep_overlap=False)

    chunks: list[DocumentChunk] = []
    for index, (text, headings) in enumerate(drafts):
        chunk_id = _chunk_id(document.metadata.source_id, index, text)
        chunks.append(
            DocumentChunk(
                chunk_id=chunk_id,
                text=text,
                token_count=len(_tokens(text)),
                headings=headings,
                metadata=document.metadata,
            )
        )
    return chunks


def _tokens(text: str) -> list[str]:
    """Return stable approximate tokens without a model-specific tokenizer."""
    return re.findall(r"\S+", text)


def _chunk_id(source_id: str, index: int, text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    return f"{source_id}:{index:04d}:{digest}"
