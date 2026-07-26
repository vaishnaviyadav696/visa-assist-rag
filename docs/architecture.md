# Architecture

## 1. Goal

Visa Assist combines a synthetic operational portal with a citation-first
post-application knowledge assistant. The architecture must answer general,
applicant-specific, and hybrid questions without crossing user or data-domain
boundaries.

## 2. Architectural principles

1. Authorize before retrieval and enforce ownership again in the repository.
2. Keep operational SQL data and public vector data physically and logically
   separate.
3. Never embed private application records into a shared vector index.
4. Treat SQL rows and retrieved documents as evidence, not instructions.
5. Use predefined parameterized queries rather than unrestricted generated SQL.
6. Preserve database provenance and knowledge citations independently.
7. Abstain when evidence is absent, unauthorized, stale, weak, or conflicting.
8. Use synthetic applicant data only.

## 3. Logical components

| Component | Responsibility |
|---|---|
| Portal UI | Select a synthetic identity, show applications/timelines, accept questions, and render evidence |
| Session identity | Resolve the active demo user; never accept ownership from prompt text |
| Query classifier | Label general, applicant-specific, hybrid, ambiguous, or unsupported questions |
| Policy router | Select permitted retrieval paths and required evidence contracts |
| Operational repository | Execute predefined parameterized SQL scoped by `user_id` and optional `application_id` |
| Knowledge retriever | Search only the promoted official-guidance vector index |
| Hybrid orchestrator | Run both paths, reconcile evidence, and keep fact/guidance boundaries explicit |
| Evidence assembler | Produce bounded SQL evidence and knowledge evidence with provenance |
| Answer generator | Draft only from supplied evidence through a provider-neutral LLM gateway |
| Answer validator | Verify ownership, provenance, citations, claim support, and abstention policy |
| Knowledge ingestion | Offline allowlisted fetching, parsing, chunking, embedding, evaluation, and promotion |
| Audit telemetry | Record privacy-safe route, timing, versions, counts, and failure categories |

The [whiteboard](whiteboard.md) contains the complete Mermaid views.

## 4. Query lifecycle

1. Resolve the active synthetic user from the trusted session.
2. Validate the question and detect unsafe or unsupported requests.
3. Classify it into a retrieval route.
4. For SQL retrieval, select a repository operation and bind the trusted
   `user_id`; an application ID is an additional filter, never proof of access.
5. For knowledge retrieval, apply source, topic, freshness, and score filters.
6. For hybrid retrieval, run both independently and preserve their evidence
   types.
7. Assemble a bounded evidence package.
8. Generate a response or deterministic abstention.
9. Validate every operational claim against database provenance and every
   knowledge claim against a citation.
10. Render facts, guidance, limitations, and evidence separately.

## 5. Structured retrieval

The application layer calls narrow operations such as:

- list applications owned by a user;
- retrieve one owned application;
- reconstruct status history in event order;
- retrieve owned appointments, biometric events, document metadata, requests,
  decisions, and tracking events.

Repositories use parameterized SQL and include `user_id` in ownership joins or
predicates. Results carry entity type, stable synthetic record ID, application
ID, and recorded/observed timestamps. The LLM never receives a database
connection or arbitrary query tool.

## 6. Knowledge retrieval

Only approved public post-application sources pass through the offline
ingestion pipeline. Chunks retain source ID, canonical URL, heading path,
verification time, content hash, and index version. Online retrieval filters
disabled or stale sources and rejects evidence below the configured relevance
threshold. Citations point only to promoted knowledge chunks.

## 7. Hybrid retrieval

Hybrid questions are decomposed into an application-fact need and a guidance
need. The two retrieval paths run under their own policies. Evidence is not
silently fused into an unlabeled blob: the answer presents recorded facts under
**Your application** and public explanations under **Official guidance**. A
failure in either required half causes a partial-answer warning or abstention,
according to the question's intent. See [hybrid-retrieval.md](hybrid-retrieval.md).

## 8. Data and trust boundaries

The relational store contains synthetic operational records. The vector index
contains public official text only. Applicant-document records contain metadata
for the demo; real uploaded files are out of scope. Session identity, repository
authorization, provider calls, and index promotion are explicit trust
boundaries. See [data-model.md](data-model.md) and
[security-and-privacy.md](security-and-privacy.md).

## 9. Deployment

The public process loads a read-only synthetic dataset and a separately built,
promoted knowledge index. It uses server-side secrets for the LLM provider.
Knowledge ingestion and index building never run in the public request path.
The operational database identity has minimum read permissions for the MVP.
Reset and migration workflows must be separate from user requests.

## 10. Proposed module boundaries

```text
src/visa_assist/
├── domain/          # Data contracts, evidence, provenance, policies
├── application/     # Classification, routing, orchestration, answers
├── operational/     # User-scoped repositories and SQL adapters
├── knowledge/       # Ingestion, embeddings, vector retrieval, citations
├── generation/      # Prompt construction and provider adapters
├── security/        # Identity, authorization, redaction, validation
├── evaluation/      # Synthetic datasets, metrics, regression runners
├── observability/   # Privacy-safe telemetry
└── ui/              # Thin portal presentation
```

Domain and application code own interfaces; infrastructure adapters point
inward. The UI, LLM provider, SQL engine, and vector implementation remain
replaceable.

## 11. Failure behavior

- Missing identity or ownership mismatch: return `not_authorized` without
  confirming whether a record exists.
- No matching application or evidence: abstain or request clarification.
- Weak or stale knowledge evidence: abstain from the unsupported guidance.
- Conflicting database events: report the conflict without inventing a current
  state.
- Provider failure or invalid output: return a safe failure, never an uncited
  fallback.
- Database or index outage: identify the unavailable evidence domain and avoid
  substituting the other domain for it.

## 12. Open implementation decisions

The relational engine, vector index, embedding model, authentication mechanism,
deployment host, and model provider require implementation-specific decisions.
For the MVP, any choice must preserve read-only synthetic operational data,
offline index promotion, repository-level isolation, and evidence contracts.
