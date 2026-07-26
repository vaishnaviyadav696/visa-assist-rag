# Data Governance

## 1. Scope

Visa Assist processes two governed data domains: synthetic operational records
and approved public knowledge. They have different access, retrieval,
provenance, and retention rules and must not be merged at rest.

## 2. Data classification

| Class | Examples | Storage and use |
|---|---|---|
| Synthetic operational | Demo users, applications, statuses, appointments, biometrics, document metadata, requests, decisions, tracking | Relational database; user-scoped retrieval only |
| Public approved knowledge | Official FAQs and post-application guidance | Reviewed source pipeline and shared vector index |
| Secrets | Provider keys, deployment credentials | Secret manager or ignored local environment only |
| Operational telemetry | Trace ID, route, timings, counts, versions, error categories | Restricted structured logs with defined retention |
| Prohibited | Real applicant records, identity documents, passport or payment details | Must not be collected, committed, indexed, logged, or transmitted |

Synthetic does not mean unrestricted. Demo records still model private data and
must obey user-level isolation so the architecture can be evaluated honestly.

## 3. Domain separation

- The operational database is the sole store for application-specific facts.
- The vector index contains approved public guidance only.
- Operational rows, timelines, questions, answers, and application-document
  metadata are never embedded into the shared index.
- Hybrid retrieval combines authorized evidence in request memory only.
- Database backups and vector artifacts are versioned and promoted separately.

## 4. Collection and generation

All operational records come from reviewed, deterministic synthetic scenarios
defined in [synthetic-data-plan.md](synthetic-data-plan.md). Real records are not
acceptable input to a synthetic-data builder. Application-document records use
safe metadata only; realistic identity-document files are out of scope.

Knowledge content enters through an allowlisted, offline workflow. Each source
has ownership, approval, canonical URL, scope, verification metadata, and
content hashes. Fetching does not imply approval or index promotion.

## 5. Access and use

Repositories bind the trusted session `user_id` to every operational lookup.
Child records inherit ownership through their application. The model has no
database credentials and cannot select a user through prompt text. Knowledge
retrieval is shared because it contains public content, but still applies
source, freshness, and topic policy.

Only the minimum evidence needed to answer is sent to an LLM provider.
Application facts and knowledge excerpts remain labeled by evidence type.

## 6. Provenance and accountability

Operational facts retain entity type, synthetic record ID, application ID,
event time, and repository operation. Knowledge claims retain chunk ID, source
ID, URL, verification time, and index version. Answer validation rejects claims
whose provenance is absent or does not match retrieved evidence.

Dataset, schema, source registry, index, prompt, model, and evaluation versions
are recorded for reproducibility without logging raw record contents.

## 7. Retention and deletion

- The synthetic database can be reset to an approved seed version.
- Obsolete synthetic artifacts are removed according to documented release
  retention; they are not treated as production archives.
- Revoked knowledge sources are blocked immediately and removed from the next
  promoted index.
- Build outputs, telemetry, and backups receive explicit owners and retention
  periods before public release.
- Secrets accidentally committed or logged require rotation and history
  cleanup; deletion from the current file is insufficient.

## 8. Logging and feedback

Logs may contain route, operation name, counts, latency, versions, validation
status, and generic errors. They exclude raw questions, answers, applicant
facts, record identifiers, SQL parameters, document text, and secrets. User
feedback is not retained in the MVP unless a separate synthetic-only design is
approved.

## 9. Quality and review

Release review checks referential integrity, fictional values, lifecycle
consistency, cross-user isolation, public-only index contents, source freshness,
provenance completeness, citation correctness, and privacy-safe telemetry.
Governance failures block dataset or index promotion.

## 10. Incidents

Disable the affected route, dataset, index, or deployment; preserve only
privacy-safe diagnostics; identify impacted versions; remove prohibited data;
rotate secrets if relevant; correct the control; rerun security and evaluation
gates; and document cause and prevention. Discovery of real applicant data is a
material incident.
