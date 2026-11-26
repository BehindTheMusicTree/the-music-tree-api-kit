"""Route a PR to the full `Pytest` job or to a skip (#52, BehindTheMusicTree/github-config#85).

Reads NUL-separated changed paths on stdin (`git diff --no-renames -z --name-only`, so a rename lists both names)
and prints `applicable=false` (skip the suite) or `applicable=true`, the scope output the `Tests success` gate reads.
Skip only when every path is explicitly known to have no effect on the
suite; anything unknown, an empty input or a mixed diff runs in full. Stdlib only: runs on the runner's system python.
Add a path here only after checking that `tests/`, `pyproject.toml` and what they import do not read it.
"""

import sys

SKIP_SUFFIXES = (".md",)
SKIP_FILES = frozenset(
    {
        "LICENSE",
        ".release-please-manifest.json",
        "release-please-config.json",
        ".github/release-policy.json",
        ".github/workflows/agent-drift.yml",
        ".github/workflows/org-conformance.yml",
        ".github/workflows/pr-title.yml",
        ".github/workflows/release.yml",
    }
)
SKIP_PREFIXES = (".github/skills/", ".pr-descriptions/")


def is_skippable(path: str) -> bool:
    return path in SKIP_FILES or path.endswith(SKIP_SUFFIXES) or path.startswith(SKIP_PREFIXES)


def classify(paths: list[str]) -> tuple[bool, list[str]]:
    """Return (whether the suite applies, the paths that made it apply)."""
    if not paths:
        return True, []
    offending = [p for p in paths if not is_skippable(p)]
    return bool(offending), offending


def main() -> None:
    paths = [p for p in sys.stdin.buffer.read().decode("utf-8", "surrogateescape").split("\0") if p]
    applicable, offending = classify(paths)
    if applicable:
        print(f"pytest_route: full run ({'; '.join(offending[:5]) or 'no changed files reported'})", file=sys.stderr)
    print(f"applicable={str(applicable).lower()}")


if __name__ == "__main__":
    main()
