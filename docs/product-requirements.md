# Product Requirements

## 1. Product summary

Visa Assist is a public, English-language RAG chatbot that answers questions
about the UK Standard Visitor visa for Indian passport holders. It retrieves
evidence only from approved official sources and produces cited, bounded
guidance. The product demonstrates production-minded RAG engineering; it does
not replace official guidance or professional advice.

## 2. Users and needs

### Primary user

An Indian passport holder researching a short UK visit who needs to locate and
understand official requirements, costs, timelines, and application steps.

### Portfolio reviewer

An engineer or hiring manager assessing architecture, retrieval quality,
guardrails, testing, observability, and engineering decisions.

## 3. MVP scope

### In scope

- India passport nationality, United Kingdom destination, Standard Visitor
  visa, and English queries.
- Questions covered by approved, indexed evidence: purpose and duration,
  eligibility, required evidence, application steps, official fees, published
  processing guidance, and operational appointment information.
- Citation links, source organization, and last-verified dates.
- Gemini generation for the public deployment and optional Ollama locally.
- Locally persisted retrieval index and a Streamlit interface.

### Out of scope

- Approval predictions, legal advice, application submission, payments,
  document uploads, case tracking, user accounts, and saved conversation
  histories.
- Other nationalities, destinations, visa types, languages, or undocumented
  exceptions.
- Automated browsing or indexing of arbitrary websites.

## 4. Functional requirements

| ID | Requirement |
|---|---|
| FR-01 | Accept a natural-language question and return an English response. |
| FR-02 | Restrict answers to the configured nationality, destination, and visa category. |
| FR-03 | Retrieve only from an approved source registry and production index. |
| FR-04 | Cite every substantive visa claim with a canonical source link. |
| FR-05 | Display a last-verified date for every cited source. |
| FR-06 | Label official requirements separately from optional recommendations. |
| FR-07 | Show source and verification date prominently for fees, processing times, and other time-sensitive claims. |
| FR-08 | Abstain when evidence is insufficient, stale beyond policy, conflicting, or outside scope. |
| FR-09 | Never guarantee or estimate the likelihood of approval. |
| FR-10 | Reject or safely redirect requests involving prohibited sensitive data. |
| FR-11 | Treat retrieved content as quoted evidence and ignore instructions embedded within it. |
| FR-12 | Offer direct links to official sources so users can verify current guidance. |

## 5. Answer contract

An answer should contain:

1. A concise response limited to supported facts.
2. Separate **Official requirements** and **General recommendations** sections
   when both are relevant.
3. Inline citation markers attached to substantive claims.
4. A source list containing title, organization, canonical URL, and
   last-verified date.
5. A targeted disclaimer for time-sensitive or case-specific information.

When the contract cannot be satisfied, the system returns an abstention,
explains why, and points to an appropriate official source.

## 6. Non-functional requirements

- **Quality:** cited claims must be entailed by retrieved source text.
- **Security:** no arbitrary source ingestion; document text cannot alter system
  behavior.
- **Privacy:** no storage of user questions by default and no collection of
  prohibited personal data.
- **Maintainability:** UI, domain logic, retrieval, generation, and source
  ingestion are independently testable.
- **Portability:** LLM and vector-index implementations are replaceable behind
  interfaces.
- **Accessibility:** keyboard-usable interface, readable contrast, descriptive
  link text, and plain-language status messages.
- **Operations:** failures produce safe user messages; logs exclude query text
  and sensitive content by default.

Initial performance and quality thresholds are defined in
[evaluation-plan.md](evaluation-plan.md), then calibrated with a reviewed
evaluation set before release.

## 7. Success criteria

- All production sources are allowlisted and carry verification metadata.
- Release quality gates for retrieval, citations, groundedness, abstention, and
  safety pass.
- No test answer contains an unsupported approval guarantee.
- A reviewer can trace a question through retrieval, generation, validation,
  and citations.
- The public demo operates within agreed latency and provider-cost limits.

## 8. Assumptions and risks

No official source has yet been researched or approved. Source accessibility,
licensing constraints, page structure, update frequency, Gemini quotas, and
Streamlit resource limits require validation. Immigration guidance changes;
freshness and abstention are therefore product behavior, not background
maintenance.
