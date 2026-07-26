# Visa Assist

Visa Assist is a post-application visa-support assistant presented as a
visa-processing portal. Fictional applicants can ask about their current and
historical applications and can request general guidance about what happens
after an application is submitted.

> **Safety boundary:** the demo uses synthetic applicant and application data
> only. It is not connected to an immigration authority, cannot change an
> application, and does not predict or influence a visa decision.

## MVP question families

1. **General post-application questions**, such as what a status means, what to
   expect after biometrics, or how additional-document requests work.
2. **Applicant-specific questions**, such as the current status of a signed-in
   user's application, appointment history, outstanding document requests,
   decision history, or passport-return tracking.

## Two data domains

| Domain | Contents | Retrieval | Evidence shown |
|---|---|---|---|
| Operational database | Synthetic users, applications, status history, appointments, biometrics, documents, requests, decisions, and tracking | User-scoped SQL | Database record provenance |
| Knowledge base | Approved official post-application FAQs and guidance | Semantic vector retrieval | Source citations and verification metadata |

Questions that require both an application fact and an explanation use hybrid
retrieval. Operational records are never embedded into the shared vector index.

## Product principles

- Enforce user ownership in every structured-data operation.
- Use only synthetic demo records.
- Cite official knowledge-base claims.
- Show database provenance for application-specific facts.
- Keep SQL and vector evidence separate through the answer pipeline.
- Abstain when evidence is missing, conflicting, stale, or unauthorized.
- Never claim to predict, accelerate, or alter an application outcome.

## Current scope

The MVP models a public portfolio demonstration of post-application support.
The knowledge corpus is limited to allowlisted official sources, while the
portal database contains deliberately fictional lifecycle scenarios. Submission,
payments, real document uploads, case modification, legal advice, and access to
government systems are out of scope.

## Documentation

- [Product requirements](docs/product-requirements.md)
- [Architecture](docs/architecture.md)
- [Architecture diagrams](docs/whiteboard.md)
- [Data model](docs/data-model.md)
- [Synthetic data plan](docs/synthetic-data-plan.md)
- [Hybrid retrieval](docs/hybrid-retrieval.md)
- [Security and privacy](docs/security-and-privacy.md)
- [Data governance](docs/data-governance.md)
- [Evaluation plan](docs/evaluation-plan.md)
- [Delivery backlog](docs/backlog.md)
- [Initial stack decision](docs/decisions/001-initial-stack.md)

## Repository layout

```text
config/                 Approved source configuration
docs/                   Product, architecture, security, and delivery design
src/visa_assist/        Application package
tests/                  Unit tests and synthetic fixtures
requirements*.txt       Runtime and development dependencies
```

## Development

```bash
source .venv/bin/activate
python -m pytest
```

Do not enter real names, passport details, application identifiers, documents,
addresses, or contact information. See [security and privacy](docs/security-and-privacy.md)
for the trust boundaries and [synthetic data plan](docs/synthetic-data-plan.md)
for acceptable demo data.
