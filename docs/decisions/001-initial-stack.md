# ADR 001: Initial Technology Stack and Data Separation

- **Status:** Accepted for MVP design, revised for post-application support
- **Date:** 2026-07-26
- **Decision owners:** Project maintainers

## Context

Visa Assist has changed from a general pre-application RAG chatbot into a
post-application portal assistant. It must answer general guidance questions and
questions about current or historical synthetic applications. That requires
both structured operational retrieval and semantic knowledge retrieval without
mixing private-style records into a shared index.

## Decision

Use:

- Python 3.11 or newer and framework-light application services;
- Pydantic models at configuration and evidence boundaries;
- a relational SQL database for synthetic users and application records;
- predefined, parameterized, user-scoped repositories for structured retrieval;
- Sentence Transformer embeddings and a locally persisted vector index for
  approved public guidance only;
- a typed classifier/router for SQL, knowledge, hybrid, clarification, and
  unsupported paths;
- Gemini behind a provider-neutral gateway for public deployment, with an
  optional local provider adapter;
- a thin portal UI, initially suitable for Streamlit if deployment constraints
  remain acceptable;
- Pytest for tests and Ruff for linting/formatting;
- separate, versioned synthetic-database and knowledge-index artifacts.

The concrete SQL engine, vector index, embedding model, and hosting platform
remain implementation decisions. An embedded relational database is acceptable
for a read-only portfolio MVP if it preserves constraints and repository-level
authorization; production use would require a new decision.

## Data-boundary decision

Operational records are never embedded into the shared vector index. Hybrid
retrieval means running authorized SQL retrieval and public semantic retrieval
as separate operations, then assembling typed evidence in memory. It does not
mean vectorizing private application histories.

The LLM receives neither database credentials nor a general SQL execution tool.
Application services select narrow repository operations, and repositories bind
the trusted session user to parameterized queries.

## Rationale

Relational storage fits ownership, temporal events, referential integrity, and
precise application lookups. Vector retrieval fits variable-language questions
over curated public guidance. Keeping them separate makes access control,
provenance, citations, evaluation, deletion, and incident response clearer.

Framework-light services expose the routing and evidence logic for review.
Pydantic validates boundaries, while project-owned interfaces keep SQL, vector,
LLM, and UI implementations replaceable.

## Consequences

### Positive

- Exact, auditable user-scoped operational retrieval.
- Semantic guidance retrieval with conventional citations.
- No shared-vector leakage of applicant-style records.
- Independent dataset and index builds, evaluation, promotion, and rollback.
- Clear evidence contracts for hybrid answers.

### Negative

- Two stores and retrieval paths increase testing and orchestration work.
- Demo identity selection is not production authentication.
- SQL and vector evidence require different freshness and provenance policies.
- Streamlit may limit production-grade sessions, concurrency, and authorization
  integration.
- Local artifacts require explicit versioning and deployment procedures.

## Guardrails

- Synthetic applicant data only.
- Repository-level ownership checks on every operational lookup.
- Parameterized predefined SQL; no unrestricted model-generated SQL.
- Public approved guidance only in the shared vector index.
- Database provenance for application facts and citations for knowledge claims.
- Offline ingestion and artifact promotion.
- Safe clarification or abstention when evidence is unavailable or unauthorized.
- No raw applicant-style content in logs or provider telemetry.

## Alternatives considered

- **Vectorize all data:** rejected because it weakens isolation, deletion,
  temporal precision, and provenance.
- **Use SQL for public guidance:** rejected because natural-language semantic
  retrieval over guidance is a core capability.
- **Let the model generate arbitrary SQL:** rejected because schema exposure,
  authorization bypass, injection, and unpredictable query cost are
  unacceptable for the MVP.
- **One combined evidence store:** rejected because public and private-style
  data have incompatible access and citation rules.
- **Managed databases immediately:** deferred until measured scale or deployment
  requirements justify credentials, networking, and operational complexity.

## Follow-up decisions

Record the relational engine and migrations, synthetic identity mechanism,
repository query catalog, vector implementation, embedding model, provider,
deployment platform, and artifact promotion process in focused ADRs before
their implementations are treated as production-ready.
