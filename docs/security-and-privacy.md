# Security and Privacy

## 1. Scope

The MVP is a public demonstration using synthetic applicant data. Its controls
demonstrate sound boundaries but do not make it suitable for production visa
records. Production identity, consent, regulatory, retention, and incident
requirements require a separate assessment.

## 2. Trust boundaries

- The browser and question text are untrusted.
- Demo session identity is the only source of active `user_id`.
- The application service can request only predefined repository operations.
- The operational database and knowledge index are separate stores.
- Retrieved rows, documents, and model output are untrusted data.
- LLM and hosting providers are external processors with minimum-data rules.

## 3. Authentication and authorization

The demo may offer predefined fictional identities, but the UI must label this
as demo identity selection rather than production authentication. Authorization
is enforced in repositories with the trusted `user_id`. Every application child
lookup joins through the owning application. Responses to unauthorized and
nonexistent identifiers are deliberately indistinguishable.

## 4. SQL safety

- Use least-privilege, preferably read-only database credentials.
- Expose narrow repository methods instead of an unrestricted SQL tool.
- Parameterize every value and allowlist sort/filter fields.
- Apply ownership predicates in the same query that retrieves data.
- Bound result counts and query duration.
- Do not put database schemas, credentials, or raw rows into logs.
- Do not let prompts override authorization or select a different user.

## 5. Vector and model safety

Only public approved guidance is embedded. Application records, timelines,
documents, questions, and answers never enter the shared index. Retrieved text
is delimited as evidence and cannot alter system policy. Send providers only
the minimum authorized evidence needed for the answer. Secrets remain
server-side.

## 6. Data minimization and logging

Operational telemetry may contain a random trace ID, selected route, repository
operation name, result count, latency, model/index versions, validation result,
and error category. It excludes raw questions, answers, names, application
facts, record identifiers, document content, provider secrets, and SQL values.

Synthetic database and index artifacts are versioned independently. Retention
and deletion apply to artifacts, build outputs, telemetry, and backups. A demo
reset restores the reviewed seed dataset.

## 7. Threats and controls

| Threat | Primary controls |
|---|---|
| Cross-user object reference | Trusted session identity, ownership join, indistinguishable denial, regression tests |
| Prompt asks to impersonate another user | Ignore prompt identity, repository authorization |
| SQL injection | Predefined operations, parameters, allowlisted fields, least privilege |
| Model-generated arbitrary SQL | No general SQL tool or database credentials for the model |
| Private-data vector leakage | Public-only ingestion contract and index-content audit |
| Indirect prompt injection | Untrusted evidence delimiters, fixed policy, output validation |
| Citation or provenance forgery | Validate identifiers against the retrieved evidence set |
| Sensitive logging | Structured allowlisted telemetry fields and automated tests |
| Synthetic data mistaken for real | Visible demo labels and obviously fictional values |
| Provider compromise or outage | Minimum disclosure, timeouts, bounded retries, safe failure |

## 8. Security tests

Release gates include horizontal-access attempts, guessed application IDs,
cross-user child-record lookups, prompt-based identity override, SQL metacharacter
inputs, oversized filters, provenance forgery, citation forgery, stale evidence,
private-data index scans, and logging snapshots.

## 9. Incident response

Disable the affected demo route, dataset, index, or provider; preserve
privacy-safe diagnostic metadata; identify impacted versions; rotate secrets if
needed; correct the artifact or policy; rerun security and evaluation gates; and
record cause and prevention. Discovery of real applicant data requires
immediate removal and escalation rather than attempted anonymization.
