---
name: code-review
description: Review context for the-music-tree-api-kit, a shared Django/DRF library consumed by hear-the-music-tree-api and grow-the-music-tree-api. Use this when reviewing any pull request in this repository.
---

# the-music-tree-api-kit review context

This repo ships generic HTTP-layer infrastructure (error handling, pagination, filtering, viewsets) as an installable Python package — it is a library, not a deployable service. It has zero genre/tag/criteria/tree coupling; that logic lives in the sibling package `the-music-tree-genre-kit`, which depends on this one.

## Things to check on every PR

- **No consumer-specific coupling.** This package must stay usable by both `hear-the-music-tree-api` and `grow-the-music-tree-api`. Reject anything that assumes a specific consumer's models, settings constants, or auth scheme (e.g. Spotify/Google OAuth, JWT) — those stay local to the consuming service and get wired in via extension points (e.g. `ErrorResponse.register_handler`), not hardcoded here.
- **Exception/type identity matters.** Code such as `ErrorResponse.handle_exception()` relies on `isinstance` checks against this package's own exception types (e.g. `AppValidationException`). A consumer that only partially adopts this package (keeps some local copies of these classes while importing others) will see `isinstance` silently stop matching. Flag any change that could encourage partial adoption across a class family — these should move together.
- **Abstract base classes need the fixture app.** Django can't validate an abstract model class without a concrete subclass. New abstract models/mixins should come with a fixture app addition under `tests/` (see `tests/settings.py`) so `makemigrations --check --dry-run` and pytest actually exercise them in CI — not just import-level smoke coverage.
- **Migrations.** No migration files should ship in this package's own `migrations/` beyond what the fixture app needs for CI; concrete services generate their own independent migration history against these abstract bases.
- **Lint/type baseline.** `pyproject.toml`'s `[tool.ruff]` extends the vendored `baselines/ruff.toml` — don't relax rules per-file without a comment explaining why; prefer fixing the code. `mypy` runs with `django-stubs` against `tests.settings`; new modules should type-check cleanly under the existing `disable_error_code` list rather than growing it.
- **Dependencies stay minimal.** Only add a dependency if a moved/new module actually needs it — this package is meant to be a thin, generic layer, not a place for consumer conveniences to accumulate.
