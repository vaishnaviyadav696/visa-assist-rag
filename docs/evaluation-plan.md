# Evaluation Plan

## 1. Objectives

Evaluation determines whether Visa Assist routes questions correctly, retrieves
only authorized application facts, retrieves supported official guidance,
keeps evidence domains distinct, cites and attributes claims, and abstains when
support is unavailable.

## 2. Evaluation dataset

Use versioned, synthetic cases containing a demo user, owned and non-owned
applications, question, expected route, expected repository operation, expected
record provenance, expected knowledge chunks, required claims, expected
citations, and answer/clarification/abstention outcome.

The set must cover:

- general status, processing, biometrics, document-request, passport-return,
  and escalation guidance;
- current and historical application facts;
- multiple-application disambiguation;
- hybrid fact-plus-guidance questions;
- cross-user application and child-record access attempts;
- missing, stale, weak, ambiguous, and conflicting evidence;
- prompt injection, identity override, arbitrary-SQL, and provenance forgery;
- decision prediction and other unsupported requests.

## 3. Classification and routing

Measure route accuracy and per-class precision/recall for `general`,
`application`, `hybrid`, `clarify`, and `unsupported`. Also measure decomposition
accuracy: the selected structured operation and knowledge topic must match the
question without accepting identity claims from prompt text.

Provisional gates:

| Metric | Target |
|---|---:|
| Overall route accuracy | ≥ 95% |
| Applicant-specific recall | ≥ 98% |
| Cross-domain misrouting on critical cases | 0 |
| Identity-from-prompt acceptance | 0 |

## 4. Structured retrieval

Evaluate repository operations independently of generation:

- application and child-record fact accuracy;
- ownership predicate coverage;
- cross-user disclosure rate;
- current versus historical selection;
- status-timeline ordering and correction handling;
- database provenance completeness;
- parameterization and bounded result behavior.

Cross-user disclosure, missing ownership predicates, arbitrary SQL execution,
and fabricated database provenance are zero-tolerance failures.

## 5. Knowledge retrieval

Against a frozen promoted index, measure Recall@k, MRR, precision, source-scope
leakage, stale retrieval, and duplicate evidence. Every expected knowledge
claim maps to reviewed chunks from public approved sources.

| Metric | Provisional target |
|---|---:|
| Recall@5 | ≥ 0.90 |
| MRR | ≥ 0.80 |
| Disabled/stale source retrieval | 0 |
| Operational record in index audit | 0 |

## 6. Hybrid retrieval

Measure whether both required evidence sets are retrieved, independently
sufficient, and visibly separated. Evaluate partial-evidence behavior,
conflicts, multiple applications, and whether public guidance is incorrectly
presented as an application fact.

Critical failures include combining different applications, attaching a public
citation to a SQL fact, presenting database provenance as a source citation, or
using guidance to infer a missing case status.

## 7. Answer evaluation

- **Operational groundedness:** every application claim is entailed by an
  authorized retrieved record.
- **Knowledge groundedness:** every general claim is entailed by retrieved
  official evidence.
- **Citation correctness and completeness:** knowledge claims cite valid
  retrieved chunks.
- **Provenance correctness and completeness:** application facts reference the
  correct record type, ID, and time.
- **Evidence separation:** fact and guidance sections are not conflated.
- **Abstention correctness:** unavailable or unauthorized evidence fails closed.
- **Policy compliance:** no decision prediction, false escalation, or claim of
  government-system access.

Zero-tolerance gates apply to cross-user disclosure, unsupported critical
claims, forged evidence, private-index content, and decision guarantees.

## 8. Test layers

1. Unit tests for classification, repository scoping, timeline ordering,
   retrieval filters, evidence schemas, citations, and abstention.
2. Contract tests using fake SQL, vector, embedding, and LLM adapters.
3. Integration tests for SQL-only, knowledge-only, and hybrid flows.
4. Security tests for horizontal access, injection, identity override, logging,
   and private-index leakage.
5. Golden synthetic journey regressions.
6. Controlled live-provider tests only in protected environments with no real
   applicant data.

## 9. Performance and operations

Measure end-to-end, classification, SQL, vector, and provider latency; database
query counts; result sizes; token use; cost; error categories; and index load
time. Performance optimization cannot remove authorization, provenance,
citation, or validation steps.

## 10. Release process

Freeze schema, synthetic dataset, source registry, index, prompts, model, and
evaluation versions. Run deterministic, retrieval, hybrid, security, and answer
gates. Review all critical failures and all abstentions. Promote the dataset and
index independently only after their applicable gates pass; otherwise retain
the previous approved versions.
