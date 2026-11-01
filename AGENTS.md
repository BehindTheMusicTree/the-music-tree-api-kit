# Project guidance

`the-music-tree-api-kit` is an installable Django/DRF library for generic HTTP
infrastructure, consumed by Hear and Grow APIs. Keep consumer-specific models,
authentication and genre/tree logic out of this package. The sibling genre kit
builds on it.

Read `CONTRIBUTING.md` for setup, validation and releases. Work branches start
from and target `main` through a PR. Use the fixture app under `tests/` to exercise
abstract models and migrations; consumers own their concrete migrations.

When reviewing changes, consult `.github/skills/code-review/SKILL.md` for
package-specific risks. Graphify is optional when installed and useful.
