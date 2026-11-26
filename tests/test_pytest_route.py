import pytest

from scripts.pytest_route import classify


@pytest.mark.parametrize(
    "paths",
    [["README.md"], ["CHANGELOG.md", "LICENSE"], [".github/skills/code-review/SKILL.md", ".pr-descriptions/x.md"]],
)
def test_documentation_only_skips(paths):
    assert classify(paths) == ("skip", [])


@pytest.mark.parametrize(
    "paths",
    [
        [],
        ["src/the_music_tree_api_kit/filters.py"],
        ["tests/test_smoke.py"],
        ["pyproject.toml"],
        ["uv.lock"],
        [".github/workflows/validate.yml"],
        ["baselines/ruff.toml"],
        ["README.md", "pyproject.toml"],
    ],
)
def test_anything_else_runs_full(paths):
    assert classify(paths)[0] == "full"
