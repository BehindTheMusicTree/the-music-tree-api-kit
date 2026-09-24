# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## Guidelines for Contributors

- Add entries to the `[Unreleased]` section under the appropriate category: `Added`, `Changed`, `Improved`, `Deprecated`, `Removed`, `Fixed`.
- Group related changes together; write clear, user-focused descriptions rather than raw git log dumps.
- Mention tests within the related feature or fix entry — "Test" is not its own category.
- On release, move `[Unreleased]` entries into a dated `## [X.Y.Z] - YYYY-MM-DD` section and leave an empty `[Unreleased]` above it.

## [Unreleased]

### Added

- Added `AppModelViewSet._get_manager_write_kwargs(request)`, an overridable hook (default `{}`) spread into every `create`/`update_instance`/`delete_instance` manager call, so subclasses can thread request-derived context (e.g. an acting-admin identifier) down to a manager without every manager needing to accept it.
- Local knowledge-graph tooling (`graphify`) wired up for Claude Code: `CLAUDE.md` section and
  `.claude/settings.json` PreToolUse hooks so Claude queries the graph before raw file searches.
  Graph output (`graphify-out/`) is gitignored, dev-only.

### Changed

- Renamed the `test.yml` GitHub Actions workflow to `validate.yml`.
- Configured the validation workflow to run on pushes to `main` and `develop`, in addition to pull requests targeting these branches.

## [0.5.0] - 2026-08-28

### Added

- `add_loopback_hosts`, a shared helper appending the loopback hosts (`127.0.0.1`,
  `127.0.0.1:<port>`, `localhost`, `localhost:<port>`) that Docker/Coolify healthchecks hit
  from inside the container, to `ALLOWED_HOSTS`. Both `hear-the-music-tree-api` and
  `grow-the-music-tree-api` need these regardless of their externally exposed hosts, since
  two independent healthcheck mechanisms (the Dockerfile's own `HEALTHCHECK` and Coolify's
  built-in container healthcheck) hit different loopback hosts and neither is configurable.

## [0.4.0] - 2026-08-25

### Added

- `CamelToSnakeMiddleware`, hoisted from `hear-the-music-tree-api`, plus a
  `djangorestframework-camel-case` dependency, so both `hear-the-music-tree-api` and
  `grow-the-music-tree-api` can share one camelCase JSON contract instead of only `hear`
  having it. `grow-the-music-tree-api` previously rendered snake_case JSON with no
  conversion layer at all, which diverged from `@behindthemusictree/app-kit`'s Zod schemas
  (written to the camelCase contract) and caused schema validation failures on every
  genre-playlist response.

## [0.3.0] - 2026-08-24

### Added

- `HostValidationMiddleware`, hoisted from `hear-the-music-tree-api`, fixing a bug where the
  middleware manually re-checked the full `host:port` string against `ALLOWED_HOSTS` after
  Django's own `HttpRequest.get_host()` already checked it (correctly, with the port stripped).
  That redundant check required every `ALLOWED_HOSTS` entry to be duplicated with and without its
  port to satisfy both checks; the shared version relies solely on `get_host()`.

## [0.2.0] - 2026-08-20

### Added

- `TrackablePlayCount` abstract model, hoisted from the identical implementations in `grow-the-music-tree-api` and `hear-the-music-tree-api`.

## [0.1.0] - 2026-08-11

- Initial release.
