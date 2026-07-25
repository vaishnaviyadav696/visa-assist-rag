# Repository Guidelines

## Project Structure & Module Organization

This repository is currently an initial Python scaffold: it contains a local `.venv/` but no application or test modules yet. As the visa-assistance RAG service is developed, keep importable code under `src/visa_assist_rag/` and mirror that structure under `tests/`. Store prompt templates and checked-in, non-sensitive fixtures in `assets/` or `tests/fixtures/`; keep ingestion scripts in `scripts/`. Do not commit `.venv/`, generated vector indexes, uploaded documents, caches, or credentials.

## Build, Test, and Development Commands

Activate the existing environment before running Python tools:

```bash
source .venv/bin/activate
python --version
```

No dependency manifest, build target, or runnable entry point exists yet. When dependencies are introduced, record them in `pyproject.toml` and install the project with `python -m pip install -e ".[dev]"`. Prefer stable project-level commands, such as `python -m pytest`, over IDE-specific workflows. Update this guide whenever a CLI, web server, or ingestion pipeline is added.

## Coding Style & Naming Conventions

Use four-space indentation and standard Python naming: `snake_case` for modules, functions, and variables; `PascalCase` for classes; and `UPPER_SNAKE_CASE` for constants. Add type hints to public interfaces and short docstrings where intent is not obvious. Keep retrieval, embedding, document loading, and response-generation concerns in separate modules. If Ruff is configured in `pyproject.toml`, run `ruff check .` and `ruff format .` before submitting changes.

## Testing Guidelines

Use `pytest` for new tests. Name files `test_*.py` and tests `test_<behavior>()`; place reusable setup in `tests/conftest.py`. Unit tests should mock network-based model and embedding calls. Mark integration tests explicitly and keep fixtures small, synthetic, and free of personal or visa-applicant data. Run the suite with `python -m pytest`.

## Commit & Pull Request Guidelines

The repository has no commit history, so no local convention is established. Use concise, imperative subjects such as `Add document chunking pipeline`; keep each commit focused. Pull requests should explain the user-visible change, list verification commands, link relevant issues, and call out configuration or schema changes. Include sample request/response output for API changes and screenshots only for UI changes.

## Security & Configuration

Read secrets from environment variables or an untracked `.env` file. Commit a sanitized `.env.example` when configuration is added. Never log passports, application records, API keys, or raw user documents.
