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
