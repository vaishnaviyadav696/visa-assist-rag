# Evaluation Plan

## 1. Objectives

Evaluation determines whether Visa Assist retrieves the right official evidence,
answers only from that evidence, cites claims correctly, abstains safely, and
remains usable within public-deployment constraints. Evaluation is a release
gate, not only a model comparison exercise.

## 2. Evaluation dataset

Create a versioned, human-reviewed dataset with:

- question and category;
- expected scope classification;
- expected source and relevant chunk identifiers;
- reference facts or required answer points;
- time-sensitivity flag;
- expected answer versus abstention;
- prohibited claims and acceptable caveats;
- reviewer and review date.

The initial set should include at least 100 questions, balanced across:

| Category | Examples |
|---|---|
| Eligibility and permitted activities | Visit purpose, study or work boundaries |
| Evidence and application steps | Supporting evidence, sequence, biometrics |
| Fees and processing guidance | Time-sensitive factual queries |
| India-specific operations | Questions supported by approved India-facing sources |
| Recommendations | Optional preparation distinct from requirements |
| Ambiguous or underspecified | Missing facts that require clarification or abstention |
| Out of scope | Other visas, countries, nationalities, languages |
| Adversarial | Prompt injection, source override, approval guarantees |
| Privacy | Passport, bank, payment, or identity-document requests |
| Unanswerable/conflicting | No approved evidence or inconsistent sources |

Use synthetic questions and public official facts only; do not include real
applicant records.

## 3. Retrieval evaluation

Run retrieval independently from generation against a frozen index:

- **Recall@k:** expected evidence appears in the first `k` results.
- **MRR:** expected evidence ranks early.
- **Precision@k:** retrieved chunks are relevant to the question.
- **Scope leakage rate:** results outside India/UK/Standard Visitor/English.
- **Stale retrieval rate:** returned chunks violate freshness policy.
- **Duplicate rate:** redundant chunks reduce useful context diversity.

Provisional release targets:

| Metric | Target |
|---|---:|
| Recall@5 | ≥ 0.90 |
| MRR | ≥ 0.80 |
| Scope leakage | 0 |
| Stale retrieval | 0 |

Targets must be recalibrated after dataset review; changes require rationale.

## 4. Answer evaluation

Each answer is assessed at the claim level:

- **Groundedness:** every factual claim is entailed by supplied evidence.
- **Citation completeness:** substantive claims carry citations.
- **Citation correctness:** cited chunks support the attached claims.
- **Answer relevance:** the response addresses the question without unrelated
  detail.
- **Requirement/recommendation separation:** labels reflect source authority.
- **Temporal clarity:** fee and processing claims show source and verification
  date.
- **Abstention correctness:** unsafe or unsupported questions are refused, while
  answerable questions are not needlessly refused.
- **Policy compliance:** no approval guarantees, sensitive-data solicitation, or
  execution of retrieved instructions.

Provisional release gates:

| Metric | Target |
|---|---:|
| Unsupported substantive claim rate | 0% on critical tests; ≤ 2% overall |
| Citation completeness | 100% |
| Citation correctness | ≥ 95% |
| Required abstention recall | ≥ 95% |
| Approval-guarantee violations | 0 |
| Sensitive-data solicitation | 0 |
| Indirect prompt-injection success | 0 |

## 5. Evaluation methods

Use three complementary methods:

1. **Deterministic checks:** response schema, citation IDs, allowlist status,
   freshness, forbidden phrases, scope filters, and latency.
2. **Human review:** claim entailment, usefulness, authority distinction, and
   appropriate abstention. Critical cases require two reviewers or adjudication.
3. **Model-assisted scoring:** optional, used for triage and regression signals
   only until validated against human labels. It cannot be the sole release
   gate.

Record the model, prompt, index, embedding, dataset, and code version for every
run.

## 6. Test layers

- Unit tests for parsing, metadata propagation, filters, answer schema, and
  deterministic guardrails.
- Contract tests for LLM and index adapters using fakes.
- Integration tests for ingestion-to-retrieval and retrieval-to-answer flows.
- Golden-set regression tests with provider calls mocked where determinism is
  required.
- Live provider tests on a small controlled set, run manually or in protected
  CI with budget limits.
- Security tests for indirect prompt injection, citation forgery, malicious
  HTML/PDF text, oversized inputs, and sensitive-data handling.

## 7. Performance and operations

Measure end-to-end latency, retrieval latency, provider latency, error rate,
token use, estimated cost per answer, index load time, memory, and artifact
size. Initial candidate targets for the public demo are p95 response latency
under 12 seconds and a documented per-session/provider budget. Final thresholds
depend on measured Streamlit Community Cloud and Gemini behavior.

## 8. Release process

1. Freeze source manifest, index, prompts, and model configuration.
2. Run deterministic, retrieval, safety, and offline answer evaluations.
3. Review all failures and all critical/time-sensitive questions.
4. Run the controlled live-provider suite.
5. Publish a concise evaluation report with known limitations.
6. Promote only when every critical gate passes; otherwise block release.

Production feedback may identify evaluation gaps, but raw user questions are not
retained by default. New regression cases must be synthetic or explicitly
consented and redacted.
