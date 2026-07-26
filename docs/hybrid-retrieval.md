# Hybrid Retrieval

## 1. Purpose

Hybrid retrieval answers questions that need both an authorized application
fact and an official explanation. It does not blend private records into the
knowledge index or treat general guidance as proof of an application's state.

## 2. Route taxonomy

| Route | Evidence path | Example |
|---|---|---|
| `general` | Knowledge only | “What happens after biometrics?” |
| `application` | SQL only | “When did I complete biometrics?” |
| `hybrid` | SQL and knowledge | “I completed biometrics; what happens next?” |
| `clarify` | No retrieval until resolved | “What is happening with it?” when several applications exist |
| `unsupported` | Abstention | Decision prediction or action outside portal scope |

Classification output includes the route, requested application facts,
knowledge topic, optional application reference, confidence, and safe
clarification prompt. User identity is supplied by the trusted session, never
extracted from the question.

## 3. Structured evidence contract

SQL evidence contains normalized facts plus entity type, record ID, application
ID, event time, and repository operation. The repository binds the active
`user_id` to every query. Empty results do not reveal whether another user's
record exists.

## 4. Knowledge evidence contract

Knowledge evidence contains chunk ID, source ID, title, canonical URL, heading,
verified time, relevance score, and index version. Only promoted, enabled,
in-scope public guidance is eligible.

## 5. Orchestration

1. Classify and decompose the question.
2. Authorize and retrieve structured facts when required.
3. Retrieve official guidance when required.
4. Apply independent sufficiency checks to each evidence set.
5. Assemble typed, delimited context with separate budgets.
6. Generate an answer using only the supplied evidence.
7. Validate SQL claims against provenance and guidance claims against citations.
8. Render the two evidence classes under separate labels.

No vector-score/SQL-score fusion is needed because the domains answer different
subquestions. Ranking occurs within the knowledge domain; structured operations
use explicit semantics and temporal ordering.

## 6. Conflict and insufficiency

- If status events conflict, report that the available records are
  inconsistent and avoid selecting a preferred status without a deterministic
  rule.
- If guidance is weak or stale, application facts may be returned alone only
  when that still answers a separable part of the question.
- If required application facts are unavailable or unauthorized, public
  guidance must not be phrased as case-specific advice.
- If multiple owned applications match, request clarification rather than
  combining histories.

## 7. Answer presentation

Hybrid answers use:

1. **Your application** — authorized recorded facts with database provenance.
2. **Official guidance** — explanatory claims with inline citations.
3. **Limitations** — missing, stale, conflicting, or non-authoritative evidence.

The validator rejects citations that point to SQL records and rejects database
provenance presented as a public source citation.

## 8. Evaluation

Measure route accuracy, fact-selection accuracy, ownership leakage, knowledge
recall, citation correctness, provenance completeness, cross-domain claim
confusion, clarification quality, and abstention correctness. Hybrid cases must
include partial evidence and contradictory evidence, not only happy paths.
