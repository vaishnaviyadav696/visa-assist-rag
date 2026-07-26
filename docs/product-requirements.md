# Product Requirements

## 1. Product summary

Visa Assist is a post-application support assistant presented as a synthetic
visa-processing portal. It helps fictional applicants understand official
post-application guidance and inspect facts about their current or historical
applications. It does not submit, modify, prioritize, predict, or decide cases.

## 2. Users and question families

The primary user is a signed-in synthetic applicant. A portfolio reviewer may
also use predefined demo identities to inspect system behavior.

| Family | Example | Required evidence |
|---|---|---|
| General guidance | “What happens after biometrics?” | Cited official knowledge-base evidence |
| Applicant-specific | “When was my biometric appointment?” | User-owned operational records with database provenance |
| Hybrid | “My status says additional documents requested—what should I do?” | User-owned status/request records plus cited official guidance |

## 3. Data domains

### Structured operational database

The database contains synthetic users, visa applications, application-status
history, appointments, biometric events, application-document metadata,
additional-document requests, application decisions, passport/courier tracking,
and historical applications.

### Unstructured knowledge base

The knowledge base contains approved official post-application FAQs, status
explanations, processing guidance, biometrics guidance, document-request
guidance, passport-return guidance, and escalation guidance.

Operational application records must never be embedded into the shared vector
index.

## 4. Functional requirements

| ID | Requirement |
|---|---|
| FR-01 | Accept a post-application question from a selected synthetic user. |
| FR-02 | Classify the question as general, applicant-specific, hybrid, clarification-needed, or unsupported. |
| FR-03 | Route general questions to semantic knowledge retrieval. |
| FR-04 | Route applicant questions to predefined, parameterized, user-scoped SQL operations. |
| FR-05 | Route hybrid questions to both domains and preserve evidence boundaries. |
| FR-06 | Enforce application ownership before returning any operational fact. |
| FR-07 | Support current and historical applications without mixing their records. |
| FR-08 | Cite every substantive claim derived from the knowledge base. |
| FR-09 | Attach table/entity, record identifier, and observation time to application-specific facts. |
| FR-10 | Abstain when evidence is missing, unauthorized, stale, weak, or conflicting. |
| FR-11 | Never expose another user's records, even when an application identifier is supplied. |
| FR-12 | Never execute arbitrary model-generated SQL or grant the model database credentials. |
| FR-13 | Never place private operational records in the shared vector index. |
| FR-14 | Clearly distinguish recorded application facts from general explanatory guidance. |
| FR-15 | Never claim to predict, expedite, or influence a decision. |

## 5. Answer contract

Every response has a status: `answered`, `clarification_required`, `abstained`,
or `not_authorized`. An answered response contains only the applicable parts:

- a concise answer;
- **Your application** facts with database provenance;
- **Official guidance** with inline citations;
- limitations or freshness warnings;
- a trace identifier that contains no applicant data.

The assistant must not infer missing application facts from general guidance or
present general processing estimates as the user's expected decision date.

## 6. Non-functional requirements

- **Isolation:** cross-user data disclosure rate is zero.
- **Grounding:** every operational fact maps to an authorized record and every
  knowledge claim maps to retrieved evidence.
- **Privacy:** only synthetic applicant data is used; logs exclude raw content.
- **Security:** repositories enforce ownership and least privilege.
- **Traceability:** routing, evidence identifiers, model/index versions, and
  abstention reasons are inspectable without exposing record content.
- **Maintainability:** SQL retrieval, semantic retrieval, routing, generation,
  authorization, and presentation are independently testable.
- **Accessibility:** status histories and answers remain keyboard-usable and
  understandable without relying solely on color.

## 7. MVP acceptance criteria

- Both question families and the hybrid path pass reviewed test scenarios.
- Every SQL result is constrained to the active synthetic user.
- No operational record appears in the vector index or knowledge citations.
- Knowledge claims have valid official citations.
- Application facts have valid database provenance.
- Unsupported, ambiguous, and unauthorized cases fail closed.
- Current and historical timelines are ordered and labeled correctly.
- The public demo can be reset to a known synthetic dataset.

## 8. Out of scope

Real applicants or production personal data, government-system integration,
application submission or editing, payments, real document storage, messaging
caseworkers, decision prediction, legal advice, automated escalation, arbitrary
website ingestion, and unrestricted natural-language-to-SQL are out of scope.

## 9. Risks and assumptions

Demo authentication does not prove production identity assurance. Synthetic
data may accidentally encode unrealistic workflows, so scenarios need domain
review. Official guidance may change and requires freshness controls. Hybrid
answers can blur fact and guidance unless the evidence types remain visibly
separate.
