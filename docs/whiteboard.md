# Architecture Whiteboard

These diagrams describe the approved post-application design. SQL evidence and
knowledge evidence remain separate until answer assembly.

## Overall architecture

```mermaid
flowchart LR
    User[Synthetic applicant] --> Portal[Portal UI]
    Portal --> Identity[Trusted session identity]
    Identity --> Router[Classifier and policy router]
    Router --> SQLService[Structured retrieval service]
    Router --> KBService[Knowledge retrieval service]
    SQLService --> Authz[Repository authorization]
    Authz --> DB[(Synthetic operational database)]
    KBService --> Vector[(Official-guidance vector index)]
    DB --> SQLEvidence[Application facts and DB provenance]
    Vector --> KBEvidence[Guidance chunks and citations]
    SQLEvidence --> Orchestrator[Evidence assembler]
    KBEvidence --> Orchestrator
    Orchestrator --> LLM[Provider-neutral LLM gateway]
    LLM --> Validator[Answer and evidence validator]
    Validator --> Portal
```

## Structured-data retrieval

```mermaid
sequenceDiagram
    actor User as Synthetic applicant
    participant UI as Portal
    participant Session as Session identity
    participant App as Application service
    participant Repo as Scoped repository
    participant DB as Operational SQL database

    User->>UI: Ask about my application
    UI->>Session: Resolve trusted user_id
    Session-->>App: user_id plus question
    App->>App: Select predefined operation
    App->>Repo: Operation(user_id, optional application_id)
    Repo->>DB: Parameterized SQL with ownership predicate
    DB-->>Repo: Authorized synthetic rows
    Repo-->>App: Facts plus entity IDs and timestamps
    App-->>UI: Application facts plus DB provenance
    Note over App,DB: An application ID never replaces user_id authorization
```

## Knowledge retrieval

```mermaid
flowchart LR
    Q[General post-application question] --> Filters[Topic and scope filters]
    Filters --> Embed[Query embedding]
    Embed --> Search[Vector similarity search]
    Search --> Index[(Promoted public KB index)]
    Index --> Rank[Score, freshness, and source checks]
    Rank -->|Sufficient| Evidence[Chunks with source provenance]
    Rank -->|Insufficient| Abstain[Evidence unavailable abstention]
    Evidence --> Answer[Cited guidance]
```

## Hybrid question flow

```mermaid
flowchart TD
    Q[Hybrid question] --> Classify[Classify and decompose]
    Classify --> FactNeed[Application fact need]
    Classify --> GuidanceNeed[Guidance need]
    FactNeed --> ScopedSQL[User-scoped SQL retrieval]
    GuidanceNeed --> Semantic[Official KB retrieval]
    ScopedSQL --> FactCheck{Authorized facts found?}
    Semantic --> GuideCheck{Supported guidance found?}
    FactCheck -->|No| Abstain[Abstain or clarify]
    GuideCheck -->|No| Partial[Partial answer warning or abstention]
    FactCheck -->|Yes| Merge[Typed evidence assembly]
    GuideCheck -->|Yes| Merge
    Merge --> Generate[Generate bounded answer]
    Generate --> Validate[Validate DB provenance and citations]
    Validate --> Render[Render Your application and Official guidance]
```

## Application status timeline

```mermaid
stateDiagram-v2
    [*] --> Submitted
    Submitted --> BiometricsScheduled: appointment created
    BiometricsScheduled --> BiometricsCompleted: biometric event recorded
    BiometricsCompleted --> UnderReview: processing event
    UnderReview --> AdditionalDocumentsRequested: request issued
    AdditionalDocumentsRequested --> UnderReview: synthetic response recorded
    UnderReview --> DecisionRecorded: decision event
    DecisionRecorded --> PassportDispatch: return tracking created
    PassportDispatch --> Closed: delivery or collection recorded
    Closed --> [*]
    note right of UnderReview
      Timeline is reconstructed from immutable,
      timestamped status events; not every
      synthetic scenario uses every state.
    end note
```

## Ingestion and indexing

```mermaid
flowchart LR
    Registry[Approved source registry] --> Fetch[Bounded allowlisted fetch]
    Fetch --> Parse[HTML or PDF parsing]
    Parse --> Normalize[Normalize and preserve headings]
    Normalize --> Chunk[Structure-aware chunks]
    Chunk --> Review[Provenance, freshness, and safety checks]
    Review --> Embed[Embed public guidance only]
    Embed --> Build[Build versioned index]
    Build --> Evaluate[Retrieval and citation evaluation]
    Evaluate -->|Pass| Promote[Atomic promotion]
    Evaluate -->|Fail| Reject[Retain prior index]
    Promote --> Index[(Public-guidance vector index)]
    Private[Operational application records] -. prohibited .-> Embed
```

## Public deployment

```mermaid
flowchart TB
    Browser[User browser] --> App[Public portal process]
    App --> Session[Demo session identity]
    App --> Router[Application services]
    Router --> ReadOnlyDB[(Read-only synthetic SQL data)]
    Router --> ReadOnlyIndex[(Promoted KB index artifact)]
    Router --> Provider[External LLM API]
    Secrets[Server-side secrets] --> Provider
    Build[Offline ingestion and index build] --> Artifact[Versioned index artifact]
    Artifact --> ReadOnlyIndex
    Reset[Controlled synthetic-data reset] --> ReadOnlyDB
    App --> Telemetry[Privacy-safe operational telemetry]
    Browser -. no direct access .-> ReadOnlyDB
    Browser -. no direct access .-> ReadOnlyIndex
```
