import io
import sys

import pytest

from scripts.pytest_route import classify, main


@pytest.mark.parametrize(
    "paths",
    [["README.md"], ["CHANGELOG.md", "LICENSE"], [".github/skills/code-review/SKILL.md", ".pr-descriptions/x.md"]],
)
def test_documentation_only_skips(paths):
    assert classify(paths) == (False, [])


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
    assert classify(paths)[0] is True


@pytest.mark.parametrize(
    ("stdin", "expected"), [(b"README.md\0", "applicable=false"), (b"src/x.py\0", "applicable=true")]
)
def test_main_prints_the_applicable_output(monkeypatch, capsys, stdin, expected):
    # The `Tests success` gate compares this GITHUB_OUTPUT line to "true"/"false" exactly.
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(stdin)))
    main()
    assert capsys.readouterr().out == f"{expected}\n"
