# ADR 001: Initial Technology Stack

- **Status:** Accepted for MVP design
- **Date:** 2026-07-25
- **Decision owners:** Project maintainers

## Context

Visa Assist is a public portfolio RAG chatbot focused on one bounded use case:
Indian passport holders asking English-language questions about the UK Standard
Visitor visa. The stack should be understandable in interviews, inexpensive to
operate, easy to run locally, and modular enough to demonstrate production
engineering without premature infrastructure.

## Decision

Use:

- Python 3.11 or newer;
- Streamlit for the public user interface;
- framework-light modular Python services;
- Pydantic for configuration and domain boundary validation;
- Sentence Transformer embeddings;
- a locally persisted vector index, with the concrete implementation selected
  after a benchmark;
- Gemini as the generation provider for public deployment;
- an optional Ollama adapter for local development;
- Pytest for testing and Ruff for linting and formatting;
- GitHub for source control and continuous integration;
- Streamlit Community Cloud for the public MVP.

The Streamlit layer will call application services rather than containing
retrieval or generation logic. Embedding, vector index, and LLM dependencies
will implement project-owned interfaces.

## Rationale

### Python

Python is the common language across document processing, machine learning,
retrieval, evaluation, and web-service tooling. Its ecosystem lets the project
use mature libraries without crossing language boundaries, while type hints and
clear package boundaries keep the framework-light codebase maintainable.

### Streamlit

Streamlit provides a usable, publicly deployable chat interface with little
front-end infrastructure. That keeps MVP effort focused on retrieval quality,
grounding, citations, and safety. Application logic remains outside Streamlit
so a dedicated API or frontend can replace it if concurrency, customization, or
operational requirements outgrow the platform.

### Gemini

Gemini supplies managed text generation without requiring the public deployment
to host a large model. It is suitable for a resource-constrained portfolio demo
and supports server-side API access. A project-owned gateway limits provider
coupling and allows timeouts, quota controls, structured-response validation,
and a future provider replacement.

### Local vector index

The initial corpus is deliberately small and curated, so a managed vector
database would add credentials, networking, cost, and operational complexity
before those capabilities are needed. A locally persisted index is inexpensive,
inspectable, reproducible, and can be shipped as a versioned, prebuilt artifact.
The concrete index implementation will be chosen by benchmark.

### Sentence Transformers

Sentence Transformers offers locally runnable embedding models with broad model
choice and no per-query embedding API dependency. Local embeddings improve cost
predictability and make index builds reproducible. The selected model will be
recorded and versioned after evaluation of retrieval quality, memory use,
license, artifact size, and Streamlit startup time.

### Pydantic

Pydantic gives configuration, source metadata, chunks, citations, and model
responses explicit runtime-validated contracts. These boundaries are especially
useful where untrusted document content and external model output enter the
system. Validation failures can therefore become deterministic safe failures
instead of leaking malformed data deeper into the application.

### Pytest

Pytest supports small unit tests, reusable fixtures, parametrized evaluation
cases, and explicit integration-test markers. Its fixture and mocking ecosystem
also makes it straightforward to test retrieval and generation without making
network calls or exposing applicant data.

### Ruff

Ruff provides fast linting and formatting through one tool with minimal
configuration. Consistent automated checks reduce style churn and catch common
Python defects locally and in continuous integration without adding several
overlapping developer dependencies.

Avoiding a heavy orchestration framework initially makes retrieval, prompts,
guardrails, and data flow visible to reviewers. Such a framework may be adopted
later only if evidence shows that it removes meaningful complexity.

## Consequences

### Positive

- Low operational complexity and a short path to a public demonstration.
- Clear module boundaries and provider replacement points.
- Reproducible local retrieval without a managed vector database.
- Familiar, interview-ready tooling.

### Negative

- Streamlit offers limited control over concurrency, background work, and UI.
- Local index artifacts require explicit build, versioning, and deployment
  procedures.
- Gemini introduces an external dependency, quota, privacy, and cost concerns.
- Ollama and Gemini may differ in output behavior.
- Streamlit Community Cloud imposes resource and availability constraints.

## Guardrails

- Ingestion is offline and cannot run from public chat requests.
- Only reviewed, allowlisted sources enter a promoted index.
- Secrets remain outside Git.
- Provider and vector-index details do not leak into domain models.
- Every release pins and records model, embedding, prompt, and index versions.
- A failed provider call or invalid model response produces a safe failure, not
  an uncited fallback answer.

## Deferred decisions

Before implementation, benchmark FAISS, Chroma, or another embedded index using
representative chunks. Select the embedding model using retrieval quality,
memory, artifact size, license, and Streamlit startup time. Decide whether
hybrid retrieval and reranking are necessary after a vector-only baseline.
Confirm Gemini model, quota, data handling, and cost controls; verify Streamlit
deployment constraints. These choices should become follow-up ADRs.

## Alternatives considered

- **Managed vector database:** rejected for MVP because it adds credentials,
  cost, networking, and operational surface without demonstrated need.
- **Custom web API and JavaScript frontend:** deferred because it expands
  deployment work without improving the core RAG demonstration.
- **Single-provider implementation:** rejected because provider boundaries are
  important for local development, testing, and portability.
- **Heavy RAG framework:** deferred until concrete orchestration complexity
  justifies the abstraction.
