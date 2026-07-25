# Architecture

## 1. Context and goals

Visa Assist is a citation-first RAG system for English questions about the UK
Standard Visitor visa from Indian passport holders. The architecture prioritizes
traceability, constrained data provenance, safe failure, modularity, and a
portfolio-friendly public deployment.

## 2. Architectural principles

1. **Evidence before generation:** the model answers only from retrieved,
   approved evidence.
2. **Fail closed:** missing, stale, conflicting, or weak evidence causes
   abstention.
3. **Provenance throughout:** source identity and verification metadata survive
   every processing stage.
4. **Untrusted retrieval:** source text is data, never executable policy or
   model instruction.
5. **Replaceable infrastructure:** LLMs, embeddings, parsers, and indexes sit
   behind narrow interfaces.
6. **Thin UI:** Streamlit handles interaction; application services own policy
   and orchestration.

## 3. Logical components

| Component | Responsibility |
|---|---|
| Source registry | Allowlisted URLs/domains, authority type, scope, owner, freshness policy, and approval state |
| Source fetcher | Controlled retrieval with limits, audit metadata, and no link-following outside policy |
| Document processor | Parse, normalize, remove boilerplate, preserve headings, and compute content hashes |
| Chunker | Produce coherent evidence units with inherited provenance |
| Embedder | Generate Sentence Transformer vectors deterministically |
| Index repository | Persist vectors, chunk metadata, and index version locally |
| Retriever | Apply scope filters, similarity search, optional lexical search, and ranking |
| RAG orchestrator | Validate query, retrieve evidence, construct bounded prompt, call provider, and validate output |
| LLM gateway | Common interface for Gemini and optional Ollama |
| Answer validator | Check citation presence, citation-to-context mapping, prohibited claims, and response schema |
| Freshness monitor | Detect overdue verification and content changes; block stale sources according to policy |
| Evaluation runner | Execute versioned retrieval, generation, safety, and regression datasets |
| Streamlit UI | Render scope, privacy notice, answer, abstention, citations, and feedback |

## 4. Proposed module structure

```text
src/visa_assist/
├── domain/          # Pydantic models, policies, and domain errors
├── application/     # Ingestion and answer use cases
├── ingestion/       # Fetching, parsing, chunking, validation
├── retrieval/       # Embeddings, indexes, ranking, filters
├── generation/      # Prompt construction and LLM adapters
├── guardrails/      # Scope, privacy, injection, citation checks
├── evaluation/      # Dataset schemas, metrics, runners
├── observability/   # Structured, privacy-safe events
├── config/          # Validated environment configuration
└── ui/              # Streamlit entry point and presentation
```

Dependency direction should point inward: infrastructure adapters implement
interfaces owned by domain/application modules. Domain code must not import
Streamlit, Gemini, Ollama, or a concrete vector store.

## 5. Ingestion and indexing

Ingestion is an explicit offline workflow, separate from user queries:

1. Select an approved registry entry.
2. Confirm URL, domain, source type, and permitted scope.
3. Fetch with bounded timeouts and size limits.
4. Store fetch metadata and a content hash; avoid raw archives unless justified.
5. Parse and normalize while preserving headings and effective-date language.
6. Flag suspicious instructions and other prompt-injection patterns for review;
   never promote them to instructions.
7. Chunk and attach immutable provenance.
8. Embed, index, and emit a versioned manifest.
9. Run ingestion checks and the evaluation suite before promotion.
10. Atomically promote the approved index version or retain the previous one.

Raw content does not enter production retrieval merely because it was fetched.
Source approval and index promotion are separate controls.

## 6. Online query lifecycle

1. Apply length, scope, and sensitive-data checks.
2. Normalize the query without adding unsupported applicant facts.
3. Retrieve using fixed MVP filters: India, UK, Standard Visitor, English.
4. Reject results below relevance or freshness policy.
5. Assemble a token-bounded context with stable chunk identifiers.
6. Instruct the LLM to use only supplied evidence, distinguish requirements
   from recommendations, and abstain when necessary.
7. Parse the response into a Pydantic answer schema.
8. Verify each citation refers to a retrieved chunk and required claims have
   citations.
9. Block approval guarantees and unsupported time-sensitive statements.
10. Return a validated answer or deterministic abstention.

## 7. Data contracts

The future domain models should include:

- `SourceRecord`: stable ID, canonical URL, organization, authority type,
  allowlist status, scope, owner, last checked, last human verified, next review,
  content hash, and status.
- `Document`: source ID, title, retrieved time, effective-date text, language,
  content hash, and normalized content.
- `Chunk`: stable ID, document/source IDs, heading path, text, ordinal, token
  count, and embedding version.
- `Citation`: chunk ID, source ID, title, URL, supporting excerpt locator, and
  last-verified date.
- `Answer`: status, answer sections, citations, limitations, and trace ID.

Exact schemas belong to implementation, not this design phase.

## 8. Deployment and operations

The public Streamlit process loads a prebuilt, approved local index artifact at
startup. It calls Gemini through a server-side secret. Optional Ollama support is
local-only and must not affect deployment behavior. Index building should occur
outside the public request path.

Configuration is validated at startup. Secrets remain in Streamlit secret
management or local ignored environment files. Logs should contain trace IDs,
timings, index/model versions, result counts, and error categories—not raw
questions, answers, or personal data.

## 9. Threats and controls

| Threat | Control |
|---|---|
| Arbitrary or compromised source | Explicit allowlist, review state, content hash, promotion gate |
| Indirect prompt injection | Delimited evidence, fixed system policy, no tools from document instructions, adversarial tests |
| Unsupported claim | Evidence-only prompt, structured citations, deterministic citation validation, abstention |
| Stale fee or timeline | Per-source freshness policy, visible verification date, stale-source exclusion |
| Sensitive-data disclosure | Up-front warning, input detection, no query logging, no persistent chat |
| Provider outage or malformed output | Timeouts, bounded retry policy, schema validation, safe error/abstention |
| Public-demo abuse | Input limits, session throttling, quota/cost controls, generic failure messages |

## 10. Unresolved decisions

The following require spikes or source research before implementation:

- Concrete local index: FAISS versus Chroma (or a smaller embedded alternative).
- Embedding model and its quality/resource trade-off.
- Vector-only versus hybrid retrieval; whether MVP includes reranking.
- HTML-only ingestion versus HTML and PDF.
- Curated URL manifest versus constrained sitemap discovery.
- Automated fetching policy and compliance with source terms.
- Human verification meaning, ownership, and review intervals by source type.
- Index artifact storage, versioning, integrity checks, and CI promotion.
- Gemini model, quotas, rate limiting, and public cost ceiling.
- Deterministic versus model-assisted groundedness validation.
- Citation granularity: page, section, paragraph, or excerpt locator.
- Whether anonymous feedback is stored and, if so, for how long.
- Open-source license and contribution governance.

The initial stack choices and consequences are recorded in
[decisions/001-initial-stack.md](decisions/001-initial-stack.md). Diagrams are
maintained in [whiteboard.md](whiteboard.md).
