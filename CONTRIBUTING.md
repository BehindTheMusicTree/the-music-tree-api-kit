# Contributing Guidelines

Thank you for your interest in contributing! This project is currently maintained by a solo developer, but contributions, suggestions, and improvements are welcome.

## Table of Contents

- [Contributors vs Maintainers](#contributors-vs-maintainers)
- [Development Workflow](#development-workflow)
  - [1. Environment Setup](#1-environment-setup)
  - [2. Branching](#2-branching)
  - [3. Testing](#3-testing)
  - [4. Committing](#4-committing)
  - [5. Pull Request Process](#5-pull-request-process)
  - [6. Releasing (For Maintainers)](#6-releasing-for-maintainers)
- [License & Attribution](#license--attribution)

## Contributors vs Maintainers

**Contributors** can submit bug reports and feature requests via GitHub Issues, propose changes via Pull Requests, improve documentation, and participate in discussions.

**Maintainers** review and merge Pull Requests, manage repository configuration, and are responsible for project direction.

**Important:** No direct commits to `main` — all changes, including from maintainers, go through Pull Requests.

Currently this project has a solo maintainer, but the role may expand as the project grows.

## Development Workflow

### 1. Environment Setup

#### Prerequisites

- Python 3.14
- [uv](https://docs.astral.sh/uv/)

#### Installation

```bash
git clone https://github.com/BehindTheMusicTree/the-music-tree-api-kit.git
cd the-music-tree-api-kit
uv sync --all-extras
```

This is an installable Python package (Django abstract base classes, generic HTTP-layer scaffolding) consumed by `hear-the-music-tree-api` and `grow-the-music-tree-api` — not a deployable service, so there's no server to run locally. New abstractions are exercised against `tests/fixture_app/`, a minimal in-repo Django app backed by SQLite.

### 2. Branching

- **`main`** — the only long-lived branch. No direct commits — only merges from PRs.
- **`feature/<name>`** — new features, branched from `main`, merged back via PR.
- **`fix/<name>`** — bug fixes, branched from `main`, merged back via PR.
- **`chore/<name>`** — maintenance, tooling, CI/CD, dependency updates, branched from `main`, merged back via PR.

There is no automated branch-name enforcement — these prefixes are a convention, not a CI-checked rule.

### 3. Testing

```bash
uv run pytest
```

Also run before opening a PR — these are the same checks CI runs (`.github/workflows/test.yml`, jobs `Lint`, `Fixture makemigrations check`, `Pytest`):

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run django-admin makemigrations the_music_tree_api_kit --check --dry-run
```

### 4. Committing

Structured commit format inspired by [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

```
<type>(<scope>): <summary>
```

Types: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`, `style`, `perf`, `ci`.

Examples:

- `feat(trackable-play-count): hoist TrackablePlayCount from grow/hear`
- `fix(base-model): preserve modified_fields across nested saves`
- `chore: update dependencies`

Use imperative mood, keep the summary under ~70 characters, include issue IDs when applicable.

### 5. Pull Request Process

Before opening a PR:

- ✅ `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`, and `uv run pytest` all pass
- ✅ New abstractions have corresponding coverage in `tests/fixture_app/`
- ✅ The PR title is a valid Conventional Commit (it drives the release notes; do not edit `CHANGELOG.md` by hand)
- ✅ `README.md` updated if the package's scope or usage changed
- ✅ No secrets, large files, or accidental commits
- ✅ Branch targets `main`

**PR title** follows the same `<type>(<scope>): <summary>` format as commits, e.g. `feat(trackable-play-count): hoist TrackablePlayCount from grow/hear`.

### 6. Releasing (For Maintainers)

Releases are automated with [release-please](https://github.com/googleapis/release-please) on `main`:

1. Merging Conventional-Commit PRs into `main` makes the `Release` workflow open or update a single
   release PR. It bumps `pyproject.toml` and `uv.lock` and writes `CHANGELOG.md`.
2. CI arms squash auto-merge on the release PR, so it merges once the required checks pass, with no
   human review (to hold a release, disable auto-merge on the PR or close it). The `Release` workflow
   then creates the annotated `vX.Y.Z` tag. Investigate or rerun a failed workflow ("Re-run failed jobs").
3. Do not create or push tags locally.
4. Consumers (`grow-the-music-tree-api`, `hear-the-music-tree-api`, `the-music-tree-genre-kit`) re-pin their dependency on this package to the new tag.

## License & Attribution

All contributions are made under the project's Apache License 2.0. You retain authorship of your code; the project retains redistribution rights under the same license. See the [LICENSE](LICENSE) file for details.
