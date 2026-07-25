# Data Governance

## 1. Purpose

This policy defines what Visa Assist may ingest, retain, process, and expose.
The MVP covers Indian passport holders, the UK Standard Visitor visa, and
English content. Safety and provenance take priority over answer coverage.

## 2. Data classes

| Class | Examples | Handling |
|---|---|---|
| Approved public source data | Official guidance pages and authorized centre instructions | May enter a reviewed production index with provenance |
| Operational metadata | URL, hash, timestamps, index version, latency, error category | Retain only as needed for quality and operations |
| User query data | Chat questions and session context | Process transiently; do not persist or log by default |
| Prohibited sensitive data | Passport numbers, identity documents, bank/payment details | Do not request, store, index, or intentionally transmit |
| Secrets | Gemini keys and deployment credentials | Secret manager or ignored local environment only |
| Evaluation data | Synthetic or reviewed questions and expected evidence | Version-controlled only when free of personal data |

## 3. Source admission policy

A source may enter the production index only when:

1. Its canonical URL or constrained URL pattern is recorded in the source
   registry.
2. The publisher is an approved government, immigration authority, embassy,
   consulate, or authorized visa application centre.
3. Its permitted role is documented. Application-centre sources may support
   operational guidance but cannot override government eligibility rules.
4. It is relevant to the MVP scope and is in English.
5. A reviewer records approval, last-verified date, content hash, and next
   review date.
6. Parsing and injection-resistance checks pass.

Discovery does not imply approval. Redirects must resolve to an allowed domain.
Third-party blogs, forums, search summaries, model-generated text, and copied
official content on unofficial domains are excluded.

## 4. Provenance and freshness

Each source and derived chunk must retain:

- stable source and chunk identifiers;
- publisher and authority type;
- canonical URL and document title;
- scope and permitted use;
- retrieval timestamp and content hash;
- last automated check and last human-verified date;
- effective or publication date when present;
- next review date and lifecycle status;
- parser, chunker, and embedding versions.

Proposed initial policy, subject to source research:

| Content type | Maximum verification age |
|---|---:|
| Fees, processing times, service availability | 7 days |
| Application procedure and appointment operations | 14 days |
| Eligibility, permitted activities, required evidence | 30 days |
| Stable explanatory content | 90 days |

“Last checked” means a successful automated comparison. “Last verified” means a
human confirmed the content and its interpretation. The UI shows the latter.
Expired content is excluded or causes abstention; it is never silently presented
as current.

## 5. Change management

The monitor compares response status, canonical URL, selected metadata, and
normalized content hash. A change creates a review item. Time-sensitive or
material rule changes immediately quarantine affected chunks until review.
Approved changes produce a new immutable index version and evaluation run.
Rollback restores the previous approved artifact and manifest.

## 6. Privacy and minimization

The UI must tell users not to submit sensitive information. Visa Assist must not
ask for or accept uploads of passports, financial records, identity documents,
or application forms. It should avoid requesting exact dates of birth,
addresses, reference numbers, or other identifiers when a generalized question
is sufficient.

Chat state is session-only and has a short operational lifetime. Raw prompts,
answers, and retrieved excerpts are excluded from normal logs and analytics.
Any future research logging requires explicit consent, redaction, a retention
limit, access controls, and a documented policy change.

## 7. Untrusted content and model providers

Fetched text is untrusted even when hosted on an allowlisted domain. It is
normalized, delimited, and supplied only as evidence. Instructions found inside
documents cannot modify system policy, request secrets, invoke tools, or select
new sources.

Only the minimum query and evidence needed to answer may be sent to Gemini.
Prohibited sensitive data should be blocked before provider calls. Ollama may be
used locally under the same data rules.

## 8. Access, retention, and deletion

- Only maintainers responsible for ingestion may approve or promote sources.
- Secrets are never committed.
- Index artifacts contain public source text and provenance, not user data.
- Build logs and operational metadata receive explicit retention periods before
  production release.
- Revoked sources are removed from the next index and blocked immediately by
  registry status.
- Repository history must not be used to retain accidentally committed secrets
  or personal data; incidents require credential rotation and history cleanup.

## 9. Incident response

For a privacy, source-integrity, or harmful-answer incident:

1. Disable the affected source, index, or public application.
2. Preserve privacy-safe diagnostic metadata.
3. Identify impacted versions and evaluation cases.
4. Correct or revoke the data and rotate secrets where relevant.
5. rebuild and re-evaluate before restoration.
6. Record the root cause, user impact, and preventive action.

Final retention values, source reviewers, and incident contacts remain release
decisions.
