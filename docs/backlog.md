# Product Backlog

This backlog is ordered by delivery phase. Items are intentionally outcome
focused; implementation details should be refined as the related architecture
decisions are made.

## Project setup

- [ ] Create the `src/visa_assist_rag/` package and mirrored `tests/` structure.
- [ ] Add `pyproject.toml` with runtime and development dependencies.
- [ ] Configure Ruff for linting and formatting and Pytest for tests.
- [ ] Add validated environment-based configuration and a sanitized
  `.env.example`.
- [ ] Add continuous integration checks for formatting, linting, and tests.
- [ ] Define project-level commands for running the UI, ingestion, and
  evaluation.

## Data ingestion

- [ ] Define a Pydantic source-registry schema with scope, ownership, approval,
  freshness, and provenance metadata.
- [ ] Create a reviewed allowlist of official sources.
- [ ] Implement bounded HTTP fetching with timeouts, size limits, and safe
  failure behavior.
- [ ] Record canonical URLs, retrieval timestamps, response metadata, and
  content hashes.
- [ ] Keep ingestion offline and separate from public query handling.
- [ ] Add tests for disallowed domains, failed fetches, and unchanged content.

## Document parsing

- [ ] Implement HTML parsing and boilerplate removal while preserving headings,
  links, lists, and effective-date language.
- [ ] Decide whether PDF support is required for the MVP.
- [ ] Normalize text without losing source or section provenance.
- [ ] Detect malformed, empty, duplicate, and unsupported documents.
- [ ] Flag suspicious embedded instructions for review.
- [ ] Add small, synthetic parser fixtures and regression tests.

## Chunking

- [ ] Define the chunk data contract, including stable IDs, heading paths,
  ordinals, token counts, and source metadata.
- [ ] Implement structure-aware chunking with configurable size and overlap.
- [ ] Keep related requirements, exceptions, and qualifiers together.
- [ ] Benchmark chunk sizes against representative questions.
- [ ] Test determinism, provenance inheritance, and boundary behavior.

## Embeddings

- [ ] Select and record a Sentence Transformers model after measuring retrieval
  quality, memory use, license, artifact size, and startup time.
- [ ] Implement a project-owned embedding interface and local adapter.
- [ ] Batch embedding work and make device selection configurable.
- [ ] Version the model and embedding configuration in the index manifest.
- [ ] Cache or skip embeddings for unchanged chunks.
- [ ] Test deterministic contracts without downloading models in unit tests.

## Retrieval

- [ ] Benchmark candidate local vector indexes and record the selection in an
  ADR.
- [ ] Persist vectors, chunk metadata, and a versioned index manifest.
- [ ] Implement scope and freshness filters before ranking.
- [ ] Establish a vector-only similarity-search baseline.
- [ ] Tune top-k and relevance thresholds using the evaluation set.
- [ ] Add deterministic abstention when evidence is weak, stale, or conflicting.
- [ ] Evaluate whether lexical search, hybrid retrieval, or reranking is needed.

## LLM integration

- [ ] Define a provider-neutral LLM gateway and Gemini adapter.
- [ ] Build a bounded prompt that treats retrieved text only as evidence.
- [ ] Define Pydantic answer and citation schemas.
- [ ] Validate citations against retrieved chunk IDs.
- [ ] Add timeouts, bounded retries, quota handling, and safe error messages.
- [ ] Prevent approval guarantees and unsupported claims.
- [ ] Unit test generation with mocked provider responses.
- [ ] Consider an optional Ollama adapter for local development.

## Streamlit UI

- [ ] Build a thin chat interface backed by application services.
- [ ] Display scope and privacy guidance before accepting a question.
- [ ] Render answers, abstentions, citations, and last-verified dates clearly.
- [ ] Distinguish official requirements from general recommendations.
- [ ] Add loading, empty, provider-error, and out-of-scope states.
- [ ] Check keyboard navigation, contrast, and descriptive link text.
- [ ] Avoid storing chat history or sensitive content beyond the active session.

## Evaluation

- [ ] Create versioned, synthetic datasets for retrieval, generation,
  abstention, citation, and safety behavior.
- [ ] Implement retrieval metrics such as hit rate and reciprocal rank.
- [ ] Measure groundedness, citation validity, completeness, and answer
  correctness.
- [ ] Add adversarial cases for prompt injection, sensitive data, and approval
  guarantees.
- [ ] Establish release thresholds and regression reports.
- [ ] Capture model, prompt, embedding, corpus, and index versions with results.

## Deployment

- [ ] Confirm Gemini quotas, cost controls, and data-handling requirements.
- [ ] Package a prebuilt, reviewed local index for deployment.
- [ ] Configure Streamlit Community Cloud secrets and startup validation.
- [ ] Add privacy-safe structured logging and health diagnostics.
- [ ] Define index build, integrity check, promotion, and rollback procedures.
- [ ] Document deployment and operational runbooks.
- [ ] Verify the public demo against latency, quality, and cost targets.

## Future enhancements

- [ ] Add more visa routes, nationalities, destinations, or languages through
  explicitly scoped corpora.
- [ ] Add hybrid retrieval and reranking if evaluation supports the complexity.
- [ ] Automate source-change detection and review notifications.
- [ ] Add a reviewer workflow for source and index promotion.
- [ ] Explore a dedicated API and web frontend if Streamlit becomes limiting.
- [ ] Add privacy-preserving feedback and evaluation triage.
- [ ] Evaluate a managed vector service when corpus size or operations justify
  it.

