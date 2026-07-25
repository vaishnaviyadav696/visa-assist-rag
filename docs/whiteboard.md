# Architecture Whiteboard

These diagrams capture the intended system shape. They are design aids rather
than deployed-state documentation and should evolve with implementation.

## Overall architecture

```mermaid
flowchart LR
    User[User] --> UI[Streamlit UI]
    UI --> App[RAG orchestrator]
    App --> Guardrails[Scope and safety guardrails]
    App --> Retriever[Retriever]
    Retriever --> Index[(Local vector index)]
    App --> Prompt[Prompt builder]
    Prompt --> LLM[Gemini gateway]
    LLM --> Validator[Answer and citation validator]
    Validator --> UI

    Registry[(Approved source registry)] --> Ingestion[Offline ingestion]
    Ingestion --> Index
    Index -. retrieved evidence .-> Prompt
```

The public request path is separate from ingestion. The UI delegates policy,
retrieval, generation, and validation to application services.

## RAG query flow

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit UI
    participant RAG as RAG orchestrator
    participant Guard as Guardrails
    participant Search as Retriever
    participant Index as Local index
    participant LLM as Gemini
    participant Check as Answer validator

    User->>UI: Ask a question
    UI->>RAG: Submit question
    RAG->>Guard: Validate length, scope, and privacy
    alt Invalid or out of scope
        Guard-->>RAG: Reject safely
        RAG-->>UI: Scoped guidance or abstention
    else Valid question
        Guard-->>RAG: Approved normalized query
        RAG->>Search: Retrieve scoped evidence
        Search->>Index: Similarity search with filters
        Index-->>Search: Ranked chunks and provenance
        Search-->>RAG: Relevant, fresh evidence
        alt Evidence is insufficient
            RAG-->>UI: Evidence-based abstention
        else Evidence is sufficient
            RAG->>LLM: Bounded prompt and evidence
            LLM-->>RAG: Structured draft answer
            RAG->>Check: Validate schema, claims, and citations
            alt Validation fails
                Check-->>RAG: Safe failure
                RAG-->>UI: Abstention or error message
            else Validation passes
                Check-->>RAG: Validated answer
                RAG-->>UI: Answer, citations, and verification dates
            end
        end
    end
    UI-->>User: Render result
```

## Ingestion pipeline

```mermaid
flowchart TD
    Registry[Reviewed source registry] --> Fetch[Bounded source fetch]
    Fetch --> Metadata[Record metadata and content hash]
    Metadata --> Parse[Parse and normalize]
    Parse --> Inspect{Valid and safe to review?}
    Inspect -- No --> Quarantine[Reject or quarantine]
    Inspect -- Yes --> Chunk[Structure-aware chunking]
    Chunk --> Provenance[Attach immutable provenance]
    Provenance --> Embed[Sentence Transformer embeddings]
    Embed --> Build[Build versioned local index]
    Build --> Evaluate[Run ingestion checks and evaluation]
    Evaluate --> Gate{Approved for promotion?}
    Gate -- No --> Retain[Retain current production index]
    Gate -- Yes --> Promote[Atomically promote index version]
    Promote --> Production[(Production index artifact)]
```

Fetching a document does not make it available to users. Validation, evaluation,
and explicit promotion form the publication gate.

## Deployment architecture

```mermaid
flowchart TB
    subgraph Build["Offline build or CI environment"]
        Sources[Approved official sources] --> Pipeline[Ingestion and evaluation]
        Pipeline --> Artifact[Versioned index artifact]
        Tests[Pytest and Ruff checks] --> ReleaseGate{Release gate}
        Artifact --> ReleaseGate
    end

    ReleaseGate -->|approved artifact| Deploy[Streamlit deployment]

    subgraph Cloud["Streamlit Community Cloud"]
        Deploy --> App[Streamlit application]
        App --> LocalIndex[(Read-only local index)]
        App --> Config[Pydantic-validated config]
        Secrets[Secret management] --> App
        App --> Logs[Privacy-safe operational logs]
    end

    Browser[User browser] <-->|HTTPS| App
    App -->|server-side API call| Gemini[Gemini API]
```

The deployed application loads a prebuilt index and never performs ingestion in
response to a user request. Provider credentials remain server-side.

