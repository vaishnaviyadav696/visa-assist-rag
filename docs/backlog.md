# Product Backlog

This backlog is ordered around the post-application MVP and its two isolated
data domains.

## Foundation

- [ ] Align package layout, dependency manifests, linting, tests, and CI.
- [x] Add validated environment configuration.
- [ ] Define typed identity, routing, evidence, provenance, and answer contracts.
- [ ] Add privacy-safe structured telemetry and trace IDs.

## Operational data model

- [ ] Select and record the relational database and migration approach.
- [ ] Implement users, applications, status history, appointments, biometrics,
  document metadata, requests, decisions, and tracking tables.
- [ ] Add foreign keys, lifecycle constraints, and indexes for user-scoped
  application access.
- [ ] Implement deterministic status-timeline reconstruction.
- [ ] Define database provenance returned by every repository operation.

## Synthetic demo data

- [ ] Implement versioned, seeded scenario definitions and a controlled reset.
- [ ] Add current, historical, multiple-application, request, decision, and
  passport-return journeys.
- [ ] Add cross-user and inconsistent-evidence security scenarios.
- [ ] Validate referential integrity, fictional values, and lifecycle order.
- [ ] Add automated checks that no operational content enters index inputs.

## Identity and authorization

- [ ] Define clearly labeled demo identity selection.
- [ ] Propagate trusted `user_id` outside question text.
- [ ] Implement predefined parameterized repository operations.
- [ ] Apply ownership joins to application and every child-record lookup.
- [ ] Make unauthorized and nonexistent responses indistinguishable.
- [ ] Add horizontal-access and prompt-identity-override tests.

## Official knowledge ingestion

- [x] Define an initial source registry and local loader.
- [x] Add bounded HTML fetching with mocked tests.
- [x] Add HTML/PDF parsing and structure-aware chunking.
- [ ] Expand the registry with reviewed post-application sources and freshness
  ownership.
- [ ] Select and version the embedding model and vector index.
- [ ] Add public-only index audits, evaluation, promotion, and rollback.

## Retrieval and routing

- [ ] Define classifier labels and typed route decisions.
- [ ] Implement deterministic rules or a bounded classifier with confidence and
  clarification behavior.
- [ ] Implement structured operations for current/historical status,
  appointments, biometrics, requests, decisions, and tracking.
- [ ] Implement semantic search with topic, source, freshness, and score filters.
- [ ] Implement hybrid decomposition and typed evidence assembly.
- [ ] Prevent unrestricted natural-language-to-SQL and cross-application joins.

## Answer generation and validation

- [ ] Define provider-neutral generation and structured answer schemas.
- [ ] Present **Your application** facts separately from **Official guidance**.
- [ ] Validate every SQL claim against retrieved database provenance.
- [ ] Validate every knowledge claim against retrieved citations.
- [ ] Implement deterministic clarification, partial-evidence, conflict, and
  abstention behavior.
- [ ] Block decision prediction, unsupported escalation, and claims of case
  modification.

## Portal experience

- [ ] Show that identities and applications are synthetic demo data.
- [ ] Add current and historical application views and accessible timelines.
- [ ] Render provenance, citations, limitations, and authorization-safe errors.
- [ ] Add empty, ambiguous, unavailable, and conflicting evidence states.
- [ ] Keep the UI thin; it must not implement authorization or direct SQL.

## Evaluation and security

- [ ] Create reviewed synthetic datasets for every route and lifecycle scenario.
- [ ] Measure classification, SQL fact accuracy, knowledge retrieval, hybrid
  separation, citations, provenance, and abstention.
- [ ] Add cross-user, SQL injection, prompt injection, evidence-forgery, logging,
  and private-index leakage tests.
- [ ] Establish zero-tolerance critical gates and regression reports.

## Deployment

- [ ] Package the synthetic relational dataset and promoted public index as
  separate read-only artifacts.
- [ ] Configure least-privilege database access and server-side provider secrets.
- [ ] Keep ingestion, index building, migrations, and dataset reset outside the
  public request path.
- [ ] Add health diagnostics, artifact integrity checks, rollback, rate limits,
  and cost controls.
- [ ] Publish limitations: synthetic data, no government integration, no case
  action, and no decision prediction.

## Deferred beyond MVP

- Production identity and real applicant integration.
- Application submission, payment, document upload, messaging, or case changes.
- Additional jurisdictions, languages, or visa routes.
- Managed vector or operational databases unless scale justifies them.
- Automated actions or unrestricted model-generated SQL.
