# Visa Assist

Visa Assist is an open-source, citation-first Retrieval-Augmented Generation
(RAG) chatbot for visa questions. The initial portfolio release is deliberately
narrow: it supports Indian passport holders asking in English about the United
Kingdom Standard Visitor visa.

> **Status:** design phase. No application has been implemented and no source
> material has been approved or indexed.

Visa Assist is an informational tool, not a lawyer, immigration adviser, or
decision-maker. It must never predict or guarantee that a visa will be approved.

## Product principles

- Use only allowlisted official government, immigration authority, embassy,
  consulate, and authorized visa application-centre sources.
- Cite every substantive visa answer and show when each source was last
  verified.
- Clearly separate official requirements from general recommendations.
- Abstain when the indexed evidence is missing, weak, stale, or conflicting.
- Treat retrieved documents as untrusted evidence, never as instructions.
- Avoid collecting sensitive or unnecessary personal information.

## MVP scope

| Dimension | Scope |
|---|---|
| Passport nationality | India |
| Destination | United Kingdom |
| Visa category | Standard Visitor visa |
| Language | English |
| Interface | Public Streamlit application |
| Generation | Gemini in deployment; optional Ollama locally |
| Retrieval | Sentence Transformer embeddings and a local vector index |

Out of scope initially: other nationalities, destinations, visa categories,
application submission, document review, eligibility decisions, legal advice,
payments, user accounts, and persistent chat history.

## Proposed repository structure

```text
visa-assist-rag/
├── README.md
├── AGENTS.md
├── docs/
│   ├── architecture.md
│   ├── backlog.md
│   ├── data-governance.md
│   ├── evaluation-plan.md
│   ├── product-requirements.md
│   ├── whiteboard.md
│   └── decisions/
│       └── 001-initial-stack.md
├── src/visa_assist/          # Future application package
├── tests/                    # Future unit, integration, and evaluation tests
├── data/                     # Future manifests; no personal data
├── scripts/                  # Future controlled ingestion utilities
├── pyproject.toml            # Future dependency and tool configuration
└── .streamlit/               # Future deployment configuration, no secrets
```

The proposed structure describes future implementation; directories are not
created until implementation begins.

## Documentation

- [Product requirements](docs/product-requirements.md)
- [Architecture](docs/architecture.md)
- [Whiteboard diagrams](docs/whiteboard.md)
- [Data governance](docs/data-governance.md)
- [Evaluation plan](docs/evaluation-plan.md)
- [Delivery backlog](docs/backlog.md)
- [Initial stack decision](docs/decisions/001-initial-stack.md)

## Planned development workflow

The intended toolchain is Python 3.11+, Pydantic, Pytest, and Ruff. Once an
implementation and `pyproject.toml` exist, this section will contain verified
setup, test, lint, and Streamlit commands. No commands are documented as working
before the corresponding implementation exists.

## Safety and privacy

Do not enter passport numbers, identity documents, payment or bank details, or
other unnecessary personal information. The public application will provide
source-linked guidance and direct users to official channels for authoritative
decisions and case-specific help.

## License

An open-source license has not yet been selected. See the unresolved decisions
in [architecture.md](docs/architecture.md).
