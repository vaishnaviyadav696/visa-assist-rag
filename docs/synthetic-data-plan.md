# Synthetic Data Plan

## 1. Objective

Provide realistic, reproducible demo journeys without using or resembling real
applicant records. Synthetic data exists to exercise authorization, timelines,
retrieval routes, provenance, and UI states—not to simulate government systems
perfectly.

## 2. Generation principles

- Use invented names or clearly labeled personas such as “Demo Applicant A”.
- Use reserved example domains, non-routable contact values, and visibly
  synthetic identifiers.
- Never copy production exports, support tickets, screenshots, documents, or
  analytics into fixtures.
- Generate from a fixed seed and versioned scenario definitions.
- Keep scenarios small enough for human review and deterministic reset.
- Scan fixtures for plausible secrets, real passport formats, and unexpected
  personal data before release.

## 3. Minimum scenario set

| Scenario | Purpose |
|---|---|
| Newly submitted | Submission confirmation and early processing guidance |
| Biometrics scheduled | Appointment lookup and general preparation guidance |
| Under review | Current status and processing-guidance abstention boundaries |
| Additional documents requested | Hybrid status/request plus official guidance |
| Decision recorded | Decision-notification facts without unsupported interpretation |
| Passport return in progress | Courier/collection facts plus return guidance |
| Closed historical application | Historical lookup and timeline reconstruction |
| Multiple applications | Explicit disambiguation between current and historical cases |
| Cross-user target | Mandatory authorization-denial regression case |
| Inconsistent or incomplete evidence | Abstention and operational-integrity testing |

## 4. Data construction

Scenario templates define relative times and state transitions. A deterministic
builder resolves them against a fixed reference date, assigns stable IDs, and
loads the relational schema transactionally. Foreign keys and domain checks run
before the dataset is promoted. The reset command replaces only approved demo
data and is unavailable through public question handling.

## 5. Documents and free text

Application-document rows contain safe metadata only, such as fictional
document category and receipt state. The MVP does not store synthetic passport
images or realistic identity documents. Operational free text is minimized and
never indexed. Official guidance fixtures are managed through the separate
knowledge ingestion process.

## 6. Review and release

Each dataset version records its seed, schema version, scenario version, build
time, record counts, and validation results. Review checks:

1. all people and identifiers are visibly fictional;
2. lifecycle sequences are internally consistent;
3. every child record resolves to its application;
4. every application resolves to one user;
5. cross-user test targets exist but are never returned;
6. current and historical scenarios cover intended query families;
7. no operational content is included in vector-index inputs.

## 7. Production prohibition

The synthetic builder is not a de-identification tool. Real data cannot be made
acceptable by renaming fields or hashing identifiers. Any future production
integration requires a new privacy, security, legal, and operational design.
